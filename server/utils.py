"""
Utility functions for the AutoCAD MCP Server
"""
import logging
import time
import math
from typing import List, Tuple, Dict, Any, Optional
from functools import wraps
from server.models import Point, Room

def setup_logging(log_level: str = 'INFO', log_file: str = 'autocad_mcp.log'):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def timing_decorator(func):
    """Decorator to measure function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        logging.debug(f"{func.__name__} executed in {execution_time:.4f} seconds")
        return result
    return wrapper

def validate_point(point: Point) -> bool:
    """Validate that a point has valid coordinates"""
    try:
        return all(isinstance(coord, (int, float)) and not math.isnan(coord) 
                  for coord in [point.x, point.y, point.z])
    except (TypeError, AttributeError):
        return False

def validate_positive_number(value: float, name: str) -> bool:
    """Validate that a number is positive"""
    if not isinstance(value, (int, float)) or value <= 0:
        logging.error(f"{name} must be a positive number, got: {value}")
        return False
    return True

def calculate_distance(point1: Point, point2: Point) -> float:
    """Calculate distance between two points"""
    return math.sqrt((point2.x - point1.x)**2 + (point2.y - point1.y)**2 + (point2.z - point1.z)**2)

def calculate_area_from_points(points: List[Point]) -> float:
    """Calculate area of a polygon defined by points using shoelace formula"""
    if len(points) < 3:
        return 0.0
    
    area = 0.0
    n = len(points)
    
    for i in range(n):
        j = (i + 1) % n
        area += points[i].x * points[j].y
        area -= points[j].x * points[i].y
    
    return abs(area) / 2.0

def convert_to_autocad_point(point: Point) -> List[float]:
    """Convert Point object to AutoCAD-compatible list"""
    return [point.x, point.y, point.z]

def convert_from_autocad_point(autocad_point: List[float]) -> Point:
    """Convert AutoCAD point list to Point object"""
    if len(autocad_point) >= 3:
        return Point(autocad_point[0], autocad_point[1], autocad_point[2])
    elif len(autocad_point) == 2:
        return Point(autocad_point[0], autocad_point[1], 0.0)
    else:
        raise ValueError("Invalid AutoCAD point format")

def validate_room_points(points: List[Point]) -> bool:
    """Validate that room points form a valid polygon"""
    if len(points) < 3:
        logging.error("Room must have at least 3 points")
        return False
    
    # Check if all points are valid
    if not all(validate_point(point) for point in points):
        logging.error("All room points must be valid")
        return False
    
    # Check if polygon is not self-intersecting (basic check)
    if len(points) > 3:
        # For simplicity, just check if area is positive
        area = calculate_area_from_points(points)
        if area <= 0:
            logging.error("Room points do not form a valid polygon")
            return False
    
    return True

def convert_units(value: float, from_unit: str, to_unit: str) -> float:
    """Convert between different units"""
    # Conversion factors to inches
    to_inches = {
        'mm': 0.0393701,
        'cm': 0.393701,
        'inches': 1.0,
        'feet': 12.0,
        'meters': 39.3701
    }
    
    if from_unit not in to_inches or to_unit not in to_inches:
        raise ValueError(f"Unsupported unit conversion: {from_unit} to {to_unit}")
    
    # Convert to inches first, then to target unit
    inches = value * to_inches[from_unit]
    return inches / to_inches[to_unit]

def format_lisp_string(text: str) -> str:
    """Format a string for use in AutoLISP code"""
    # Escape special characters
    text = text.replace('\\', '\\\\')
    text = text.replace('"', '\\"')
    return f'"{text}"'

def format_lisp_point(point: Point) -> str:
    """Format a point for use in AutoLISP code"""
    return f"'({point.x} {point.y} {point.z})"

def format_lisp_point_list(points: List[Point]) -> str:
    """Format a list of points for use in AutoLISP code"""
    point_strings = [f"({point.x} {point.y} {point.z})" for point in points]
    return f"'({' '.join(point_strings)})"

def sanitize_layer_name(name: str) -> str:
    """Sanitize layer name for AutoCAD compatibility"""
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    
    # Ensure name doesn't start with a number
    if name and name[0].isdigit():
        name = '_' + name
    
    # Limit length
    return name[:255] if name else "DEFAULT_LAYER"

def generate_unique_id() -> str:
    """Generate a unique ID for objects"""
    import uuid
    return str(uuid.uuid4())[:8]

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class AutoCADConnectionError(Exception):
    """Custom exception for AutoCAD connection errors"""
    pass