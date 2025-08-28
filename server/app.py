"""
AutoCAD MCP Server - Flask Application
Main server application for architectural floor planning with AutoCAD integration
"""
import logging
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, Any, List

# Import our modules
from config.settings import get_config
from server.autocad_interface import AutoCADInterface
from server.lisp_generator import LispGenerator
from server.models import Point, Wall, Door, Window, Room, Layer, SwingDirection, FurnitureType
from server.utils import (
    setup_logging, validate_point, validate_positive_number, 
    calculate_area_from_points, ValidationError, AutoCADConnectionError
)

# Initialize Flask app
app = Flask(__name__)
config = get_config()
app.config.from_object(config)
CORS(app)

# Setup logging
logger = setup_logging(config.LOG_LEVEL, config.LOG_FILE)

# Initialize AutoCAD interface and LISP generator
autocad_interface = AutoCADInterface(
    application_name=config.AUTOCAD_APPLICATION_NAME,
    timeout=config.AUTOCAD_TIMEOUT
)
lisp_generator = LispGenerator()

# Error handlers
@app.errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify({"error": "Validation Error", "message": str(error)}), 400

@app.errorhandler(AutoCADConnectionError)
def handle_autocad_error(error):
    return jsonify({"error": "AutoCAD Connection Error", "message": str(error)}), 500

@app.errorhandler(500)
def handle_internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred"}), 500

# Helper functions
def validate_request_data(data: Dict[str, Any], required_fields: List[str]) -> None:
    """Validate that required fields are present in request data"""
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")

def parse_point(point_data: Dict[str, float]) -> Point:
    """Parse point data from request"""
    return Point(
        x=float(point_data.get('x', 0)),
        y=float(point_data.get('y', 0)),
        z=float(point_data.get('z', 0))
    )

def parse_points_list(points_data: List[Dict[str, float]]) -> List[Point]:
    """Parse list of points from request"""
    return [parse_point(point_data) for point_data in points_data]

# API Routes

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "AutoCAD MCP Server",
        "version": "1.0.0",
        "connections": len(autocad_interface.connections)
    })

@app.route('/api/autocad/connect', methods=['POST'])
def connect_to_autocad():
    """Connect to AutoCAD instance"""
    try:
        data = request.get_json() or {}
        instance_id = data.get('instance_id', 'default')
        
        connection = autocad_interface.connect_to_autocad(instance_id)
        
        return jsonify({
            "success": True,
            "message": f"Connected to AutoCAD (instance: {instance_id})",
            "instance_id": instance_id,
            "connected": connection.connected
        })
        
    except Exception as e:
        logger.error(f"Failed to connect to AutoCAD: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/autocad/disconnect', methods=['POST'])
def disconnect_from_autocad():
    """Disconnect from AutoCAD instance"""
    try:
        data = request.get_json() or {}
        instance_id = data.get('instance_id', 'default')
        
        success = autocad_interface.disconnect(instance_id)
        
        return jsonify({
            "success": success,
            "message": f"Disconnected from AutoCAD (instance: {instance_id})"
        })
        
    except Exception as e:
        logger.error(f"Failed to disconnect from AutoCAD: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/autocad/connections', methods=['GET'])
def list_connections():
    """List all AutoCAD connections"""
    try:
        connections = autocad_interface.list_connections()
        return jsonify({
            "success": True,
            "connections": connections,
            "count": len(connections)
        })
    except Exception as e:
        logger.error(f"Failed to list connections: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Core Drawing Elements

@app.route('/api/drawing/wall', methods=['POST'])
def create_wall():
    """Create a wall"""
    try:
        data = request.get_json()
        validate_request_data(data, ['start_point', 'end_point', 'thickness', 'height'])
        
        start_point = parse_point(data['start_point'])
        end_point = parse_point(data['end_point'])
        thickness = float(data['thickness'])
        height = float(data['height'])
        instance_id = data.get('instance_id', 'default')
        
        # Validation
        if not validate_positive_number(thickness, 'thickness'):
            raise ValidationError("Thickness must be positive")
        if not validate_positive_number(height, 'height'):
            raise ValidationError("Height must be positive")
        
        # Generate LISP code and execute
        lisp_code = lisp_generator.create_wall(start_point, end_point, thickness, height)
        result = autocad_interface.execute_lisp(lisp_code, instance_id)
        
        return jsonify({
            "success": result.success,
            "message": "Wall created successfully" if result.success else result.error_message,
            "execution_time": result.execution_time
        })
        
    except Exception as e:
        logger.error(f"Failed to create wall: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/drawing/door', methods=['POST'])
def insert_door():
    """Insert a door"""
    try:
        data = request.get_json()
        validate_request_data(data, ['wall_reference', 'position', 'width', 'height', 'swing_direction'])
        
        wall_reference = data['wall_reference']
        position = parse_point(data['position'])
        width = float(data['width'])
        height = float(data['height'])
        swing_direction = SwingDirection(data['swing_direction'])
        instance_id = data.get('instance_id', 'default')
        
        # Validation
        if width < config.MIN_DOOR_WIDTH:
            raise ValidationError(f"Door width must be at least {config.MIN_DOOR_WIDTH} inches")
        
        # Generate LISP code and execute
        lisp_code = lisp_generator.insert_door(wall_reference, position, width, height, swing_direction)
        result = autocad_interface.execute_lisp(lisp_code, instance_id)
        
        return jsonify({
            "success": result.success,
            "message": "Door inserted successfully" if result.success else result.error_message,
            "execution_time": result.execution_time
        })
        
    except Exception as e:
        logger.error(f"Failed to insert door: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/drawing/window', methods=['POST'])
def insert_window():
    """Insert a window"""
    try:
        data = request.get_json()
        validate_request_data(data, ['wall_reference', 'position', 'width', 'height', 'sill_height'])
        
        wall_reference = data['wall_reference']
        position = parse_point(data['position'])
        width = float(data['width'])
        height = float(data['height'])
        sill_height = float(data['sill_height'])
        instance_id = data.get('instance_id', 'default')
        
        # Validation
        if width < config.MIN_WINDOW_WIDTH:
            raise ValidationError(f"Window width must be at least {config.MIN_WINDOW_WIDTH} inches")
        
        # Generate LISP code and execute
        lisp_code = lisp_generator.insert_window(wall_reference, position, width, height, sill_height)
        result = autocad_interface.execute_lisp(lisp_code, instance_id)
        
        return jsonify({
            "success": result.success,
            "message": "Window inserted successfully" if result.success else result.error_message,
            "execution_time": result.execution_time
        })
        
    except Exception as e:
        logger.error(f"Failed to insert window: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/drawing/room', methods=['POST'])
def create_room():
    """Create a room"""
    try:
        data = request.get_json()
        validate_request_data(data, ['points', 'height'])
        
        points = parse_points_list(data['points'])
        height = float(data['height'])
        instance_id = data.get('instance_id', 'default')
        
        # Validation
        if len(points) < 3:
            raise ValidationError("Room must have at least 3 points")
        
        area = calculate_area_from_points(points)
        if area < config.MIN_ROOM_AREA:
            raise ValidationError(f"Room area must be at least {config.MIN_ROOM_AREA} square feet")
        
        # Generate LISP code and execute
        lisp_code = lisp_generator.create_room(points, height)
        result = autocad_interface.execute_lisp(lisp_code, instance_id)
        
        return jsonify({
            "success": result.success,
            "message": "Room created successfully" if result.success else result.error_message,
            "area": area,
            "execution_time": result.execution_time
        })
        
    except Exception as e:
        logger.error(f"Failed to create room: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

# Layout and Organization

@app.route('/api/layout/grid', methods=['POST'])
def setup_grid():
    """Setup drawing grid"""
    try:
        data = request.get_json()
        validate_request_data(data, ['origin_point', 'x_spacing', 'y_spacing', 'x_count', 'y_count'])
        
        origin_point = parse_point(data['origin_point'])
        x_spacing = float(data['x_spacing'])
        y_spacing = float(data['y_spacing'])
        x_count = int(data['x_count'])
        y_count = int(data['y_count'])
        instance_id = data.get('instance_id', 'default')
        
        # Generate LISP code and execute
        lisp_code = lisp_generator.setup_grid(origin_point, x_spacing, y_spacing, x_count, y_count)
        result = autocad_interface.execute_lisp(lisp_code, instance_id)
        
        return jsonify({
            "success": result.success,
            "message": "Grid setup completed" if result.success else result.error_message,
            "execution_time": result.execution_time
        })
        
    except Exception as e:
        logger.error(f"Failed to setup grid: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/layout/layer', methods=['POST'])
def create_layer():
    """Create a new layer"""
    try:
        data = request.get_json()
        validate_request_data(data, ['name', 'color', 'line_type', 'line_weight'])
        
        name = data['name']
        color = int(data['color'])
        line_type = data['line_type']
        line_weight = float(data['line_weight'])
        instance_id = data.get('instance_id', 'default')
        
        # Generate LISP code and execute
        lisp_code = lisp_generator.create_layer(name, color, line_type, line_weight)
        result = autocad_interface.execute_lisp(lisp_code, instance_id)
        
        return jsonify({
            "success": result.success,
            "message": f"Layer '{name}' created successfully" if result.success else result.error_message,
            "execution_time": result.execution_time
        })
        
    except Exception as e:
        logger.error(f"Failed to create layer: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

# Annotation and Dimensions

@app.route('/api/annotation/text', methods=['POST'])
def add_text_note():
    """Add text annotation"""
    try:
        data = request.get_json()
        validate_request_data(data, ['insertion_point', 'text_string', 'height'])
        
        insertion_point = parse_point(data['insertion_point'])
        text_string = data['text_string']
        height = float(data['height'])
        rotation = float(data.get('rotation', 0.0))
        instance_id = data.get('instance_id', 'default')
        
        # Generate LISP code and execute
        lisp_code = lisp_generator.add_text_note(insertion_point, text_string, height, rotation)
        result = autocad_interface.execute_lisp(lisp_code, instance_id)
        
        return jsonify({
            "success": result.success,
            "message": "Text note added successfully" if result.success else result.error_message,
            "execution_time": result.execution_time
        })
        
    except Exception as e:
        logger.error(f"Failed to add text note: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/annotation/dimension', methods=['POST'])
def dimension_linear():
    """Add linear dimension"""
    try:
        data = request.get_json()
        validate_request_data(data, ['start_point', 'end_point', 'offset_distance'])
        
        start_point = parse_point(data['start_point'])
        end_point = parse_point(data['end_point'])
        offset_distance = float(data['offset_distance'])
        instance_id = data.get('instance_id', 'default')
        
        # Generate LISP code and execute
        lisp_code = lisp_generator.dimension_linear(start_point, end_point, offset_distance)
        result = autocad_interface.execute_lisp(lisp_code, instance_id)
        
        return jsonify({
            "success": result.success,
            "message": "Linear dimension added successfully" if result.success else result.error_message,
            "execution_time": result.execution_time
        })
        
    except Exception as e:
        logger.error(f"Failed to add dimension: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

# Furniture and Fixtures

@app.route('/api/furniture/insert', methods=['POST'])
def insert_furniture():
    """Insert furniture"""
    try:
        data = request.get_json()
        validate_request_data(data, ['insertion_point', 'furniture_type'])
        
        insertion_point = parse_point(data['insertion_point'])
        furniture_type = FurnitureType(data['furniture_type'])
        rotation = float(data.get('rotation', 0.0))
        scale = float(data.get('scale', 1.0))
        instance_id = data.get('instance_id', 'default')
        
        # Generate LISP code and execute
        lisp_code = lisp_generator.insert_furniture(insertion_point, furniture_type, rotation, scale)
        result = autocad_interface.execute_lisp(lisp_code, instance_id)
        
        return jsonify({
            "success": result.success,
            "message": "Furniture inserted successfully" if result.success else result.error_message,
            "execution_time": result.execution_time
        })
        
    except Exception as e:
        logger.error(f"Failed to insert furniture: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

# Utilities and Calculations

@app.route('/api/utils/calculate_area', methods=['POST'])
def calculate_area():
    """Calculate area of polygon"""
    try:
        data = request.get_json()
        validate_request_data(data, ['points'])
        
        points = parse_points_list(data['points'])
        
        if len(points) < 3:
            raise ValidationError("Need at least 3 points to calculate area")
        
        area = calculate_area_from_points(points)
        
        return jsonify({
            "success": True,
            "area": area,
            "units": "square units",
            "point_count": len(points)
        })
        
    except Exception as e:
        logger.error(f"Failed to calculate area: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

# Server Management

@app.route('/api/lisp/execute', methods=['POST'])
def execute_lisp():
    """Execute custom AutoLISP code"""
    try:
        data = request.get_json()
        validate_request_data(data, ['lisp_code'])
        
        lisp_code = data['lisp_code']
        instance_id = data.get('instance_id', 'default')
        
        result = autocad_interface.execute_lisp(lisp_code, instance_id)
        
        return jsonify({
            "success": result.success,
            "result": result.result,
            "error_message": result.error_message,
            "execution_time": result.execution_time
        })
        
    except Exception as e:
        logger.error(f"Failed to execute LISP: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/drawing/save', methods=['POST'])
def save_current_drawing():
    """Save current drawing"""
    try:
        data = request.get_json()
        validate_request_data(data, ['filepath'])
        
        filepath = data['filepath']
        instance_id = data.get('instance_id', 'default')
        
        result = autocad_interface.save_current_drawing(filepath, instance_id)
        
        return jsonify({
            "success": result.success,
            "message": result.result if result.success else result.error_message,
            "filepath": filepath
        })
        
    except Exception as e:
        logger.error(f"Failed to save drawing: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

if __name__ == '__main__':
    logger.info("Starting AutoCAD MCP Server...")
    logger.info(f"Configuration: {config.__class__.__name__}")
    
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )