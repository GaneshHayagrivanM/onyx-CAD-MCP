"""
AutoCAD COM interface for connecting and executing commands
"""
import logging
import time
import os
from typing import Optional, Dict, Any, List
from server.models import AutoCADConnection, LispExecutionResult
from server.utils import AutoCADConnectionError, timing_decorator

# Try to import win32com and pythoncom, create mock if not available (for non-Windows systems)
try:
    import win32com.client
    import pythoncom
    WIN32COM_AVAILABLE = True
except ImportError:
    WIN32COM_AVAILABLE = False
    # Create mock win32com and pythoncom for testing on non-Windows systems
    class MockWin32Com:
        @staticmethod
        def GetActiveObject(app_name):
            raise Exception("AutoCAD not found - win32com not available on this system")
        
        @staticmethod  
        def Dispatch(app_name):
            raise Exception("Cannot start AutoCAD - win32com not available on this system")
    
    class MockPythoncom:
        @staticmethod
        def CoInitialize():
            pass
        
        @staticmethod
        def CoUninitialize():
            pass
    
    class win32com:
        client = MockWin32Com()
    
    pythoncom = MockPythoncom()

logger = logging.getLogger(__name__)

class AutoCADInterface:
    """Interface for connecting to and communicating with AutoCAD"""
    
    def __init__(self, application_name: str = "AutoCAD.Application", timeout: int = 30):
        self.application_name = application_name
        self.timeout = timeout
        self.connections: Dict[str, AutoCADConnection] = {}
        self.logger = logging.getLogger(__name__)
        self._com_initialized = False
    
    def _initialize_com(self):
        """Initialize COM library if not already initialized"""
        if WIN32COM_AVAILABLE:
            try:
                # COM initialization is per-thread, so we always try to initialize
                # pythoncom.CoInitialize() will succeed or return S_FALSE if already initialized
                pythoncom.CoInitialize()
                self._com_initialized = True
                self.logger.debug("COM library initialized successfully")
            except Exception as e:
                self.logger.warning(f"COM initialization failed: {str(e)}")
                raise AutoCADConnectionError(f"Failed to initialize COM library: {str(e)}")
        else:
            # For non-Windows systems, just mark as initialized
            self._com_initialized = True
    
    def _uninitialize_com(self):
        """Uninitialize COM library if it was initialized by this instance"""
        if self._com_initialized and WIN32COM_AVAILABLE:
            try:
                pythoncom.CoUninitialize()
                self._com_initialized = False
                self.logger.debug("COM library uninitialized")
            except Exception as e:
                self.logger.warning(f"COM cleanup failed: {str(e)}")
        elif self._com_initialized:
            # For non-Windows systems, just mark as uninitialized
            self._com_initialized = False
    
    @timing_decorator
    def connect_to_autocad(self, instance_id: str = "default") -> AutoCADConnection:
        """
        Connect to AutoCAD application
        
        Args:
            instance_id: Unique identifier for this connection
            
        Returns:
            AutoCADConnection object with connection details
            
        Raises:
            AutoCADConnectionError: If connection fails
        """
        try:
            self.logger.info(f"Attempting to connect to AutoCAD (instance: {instance_id})")
            
            # Initialize COM library before making COM calls
            self._initialize_com()
            
            # Try to get existing AutoCAD application
            try:
                app = win32com.client.GetActiveObject(self.application_name)
                self.logger.info("Connected to existing AutoCAD instance")
            except:
                # Start new AutoCAD instance
                self.logger.info("Starting new AutoCAD instance")
                app = win32com.client.Dispatch(self.application_name)
                app.Visible = True
                time.sleep(5)  # Allow more time for startup
            
            # Add project's LISP folder to AutoCAD's support path
            lisp_path = os.path.abspath("lisp")
            preferences = app.Preferences
            support_path = preferences.Files.SupportPath

            if lisp_path not in support_path:
                self.logger.info(f"Adding LISP path to AutoCAD support paths: {lisp_path}")
                preferences.Files.SupportPath = f"{support_path};{lisp_path}"
            else:
                self.logger.debug(f"LISP path already in AutoCAD support paths: {lisp_path}")

            # Get active document and model space, create new if none exists
            try:
                doc = app.ActiveDocument
                self.logger.info(f"Using active document: {doc.Name}")
            except Exception:
                self.logger.info("No active document, creating new drawing.")
                doc = app.Documents.Add()
                time.sleep(2) # Allow more time for new document to become active

            model_space = doc.ModelSpace
            
            # Create connection object
            connection = AutoCADConnection(
                instance_id=instance_id,
                application=app,
                document=doc,
                model_space=model_space,
                connected=True
            )
            
            self.connections[instance_id] = connection
            self.logger.info(f"Successfully connected to AutoCAD (instance: {instance_id})")
            
            return connection
            
        except Exception as e:
            error_msg = f"Failed to connect to AutoCAD: {str(e)}"
            self.logger.error(error_msg)
            raise AutoCADConnectionError(error_msg)
    
    def get_connection(self, instance_id: str = "default") -> Optional[AutoCADConnection]:
        """Get existing AutoCAD connection"""
        connection = self.connections.get(instance_id)
        if connection and not self.is_connection_alive(connection):
            self.logger.warning(f"Connection {instance_id} is no longer alive, removing")
            del self.connections[instance_id]
            return None
        return connection
    
    def is_connection_alive(self, connection: AutoCADConnection) -> bool:
        """Check if AutoCAD connection is still alive"""
        try:
            if connection.application is None:
                return False
            # Try to access a property to test if connection is alive
            _ = connection.application.Name
            return True
        except:
            return False
    
    @timing_decorator
    def execute_lisp(self, lisp_code: str, instance_id: str = "default") -> LispExecutionResult:
        """
        Execute AutoLISP code in AutoCAD
        
        Args:
            lisp_code: AutoLISP code to execute
            instance_id: AutoCAD instance to use
            
        Returns:
            LispExecutionResult with execution details
        """
        start_time = time.time()
        
        try:
            # Initialize COM library before any COM operations
            self._initialize_com()
            
            connection = self.get_connection(instance_id)
            if not connection:
                # Try to establish connection
                connection = self.connect_to_autocad(instance_id)
            
            # Validate connection before proceeding
            if not connection or not self.is_connection_alive(connection):
                raise AutoCADConnectionError("Failed to establish or validate AutoCAD connection")
            
            self.logger.debug(f"Executing LISP code: {lisp_code[:100]}...")
            
            # Execute the AutoLISP code
            result = connection.document.SendStringToExecute(lisp_code + "\n", True)
            
            execution_time = time.time() - start_time
            
            self.logger.info(f"LISP code executed successfully in {execution_time:.4f}s")
            
            return LispExecutionResult(
                success=True,
                result=result,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Failed to execute LISP code: {str(e)}"
            self.logger.error(error_msg)
            
            return LispExecutionResult(
                success=False,
                error_message=error_msg,
                execution_time=execution_time
            )
    
    def load_lisp_file(self, filepath: str, instance_id: str = "default") -> LispExecutionResult:
        """
        Load AutoLISP file in AutoCAD
        
        Args:
            filepath: Path to the LISP file
            instance_id: AutoCAD instance to use
            
        Returns:
            LispExecutionResult with execution details
        """
        try:
            # Read the LISP file
            with open(filepath, 'r') as f:
                lisp_code = f.read()
            
            self.logger.info(f"Loading LISP file: {filepath}")
            return self.execute_lisp(lisp_code, instance_id)
            
        except FileNotFoundError:
            error_msg = f"LISP file not found: {filepath}"
            self.logger.error(error_msg)
            return LispExecutionResult(
                success=False,
                error_message=error_msg
            )
        except Exception as e:
            error_msg = f"Failed to load LISP file: {str(e)}"
            self.logger.error(error_msg)
            return LispExecutionResult(
                success=False,
                error_message=error_msg
            )
    
    def save_current_drawing(self, filepath: str, instance_id: str = "default") -> LispExecutionResult:
        """
        Save current AutoCAD drawing
        
        Args:
            filepath: Path where to save the drawing
            instance_id: AutoCAD instance to use
            
        Returns:
            LispExecutionResult with execution details
        """
        try:
            # Initialize COM library before any COM operations
            self._initialize_com()
            
            connection = self.get_connection(instance_id)
            if not connection:
                # Try to establish connection if none exists
                connection = self.connect_to_autocad(instance_id)
            
            # Validate connection before proceeding
            if not connection or not self.is_connection_alive(connection):
                raise AutoCADConnectionError("Failed to establish or validate AutoCAD connection")
            
            self.logger.info(f"Saving drawing to: {filepath}")
            
            # Save the drawing
            connection.document.SaveAs(filepath)
            
            return LispExecutionResult(
                success=True,
                result=f"Drawing saved to {filepath}"
            )
            
        except Exception as e:
            error_msg = f"Failed to save drawing: {str(e)}"
            self.logger.error(error_msg)
            return LispExecutionResult(
                success=False,
                error_message=error_msg
            )
    
    def get_active_document_info(self, instance_id: str = "default") -> Dict[str, Any]:
        """Get information about the active AutoCAD document"""
        try:
            connection = self.get_connection(instance_id)
            if not connection:
                return {"error": "No active AutoCAD connection"}
            
            doc = connection.document
            
            return {
                "name": doc.Name,
                "path": doc.FullName if hasattr(doc, 'FullName') else "Untitled",
                "units": doc.Database.Lunits if hasattr(doc.Database, 'Lunits') else "Unknown",
                "saved": doc.Saved,
                "read_only": doc.ReadOnly
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get document info: {str(e)}")
            return {"error": str(e)}
    
    def set_current_layer(self, layer_name: str, instance_id: str = "default") -> LispExecutionResult:
        """Set the current active layer in AutoCAD"""
        lisp_code = f'(setvar "CLAYER" "{layer_name}")'
        return self.execute_lisp(lisp_code, instance_id)
    
    def zoom_extents(self, instance_id: str = "default") -> LispExecutionResult:
        """Zoom to drawing extents"""
        lisp_code = '(command "._ZOOM" "_E")'
        return self.execute_lisp(lisp_code, instance_id)
    
    def regenerate_drawing(self, instance_id: str = "default") -> LispExecutionResult:
        """Regenerate the drawing"""
        lisp_code = '(command "._REGEN")'
        return self.execute_lisp(lisp_code, instance_id)
    
    def disconnect(self, instance_id: str = "default") -> bool:
        """
        Disconnect from AutoCAD instance
        
        Args:
            instance_id: Instance to disconnect from
            
        Returns:
            True if disconnected successfully
        """
        try:
            if instance_id in self.connections:
                connection = self.connections[instance_id]
                connection.connected = False
                del self.connections[instance_id]
                self.logger.info(f"Disconnected from AutoCAD instance: {instance_id}")
                
                # Uninitialize COM if this was the last connection
                if not self.connections:
                    self._uninitialize_com()
                
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error disconnecting from AutoCAD: {str(e)}")
            return False
    
    def disconnect_all(self) -> int:
        """Disconnect from all AutoCAD instances"""
        count = 0
        for instance_id in list(self.connections.keys()):
            if self.disconnect(instance_id):
                count += 1
        
        # Ensure COM is uninitialized after disconnecting all
        if count > 0:
            self._uninitialize_com()
        
        return count
    
    def list_connections(self) -> List[Dict[str, Any]]:
        """List all active AutoCAD connections"""
        connections = []
        for instance_id, conn in self.connections.items():
            connections.append({
                "instance_id": instance_id,
                "connected": self.is_connection_alive(conn),
                "document_name": self.get_active_document_info(instance_id).get("name", "Unknown")
            })
        return connections