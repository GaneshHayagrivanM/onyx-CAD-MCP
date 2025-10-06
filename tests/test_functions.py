"""
Test suite for AutoCAD MCP Server
Tests core functionality without requiring AutoCAD connection
"""
import pytest
import json
from server.app import app
from server.models import Point, Wall, Door, Window, SwingDirection, FurnitureType
from server.utils import (
    validate_point, validate_positive_number, calculate_area_from_points,
    convert_units, sanitize_layer_name
)
from server.lisp_generator import LispGenerator

# Test fixtures
@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_points():
    """Sample points for testing"""
    return [
        Point(0, 0, 0),
        Point(100, 0, 0),
        Point(100, 80, 0),
        Point(0, 80, 0)
    ]

@pytest.fixture
def lisp_generator():
    """LISP generator instance"""
    return LispGenerator()

# Utility function tests
class TestUtilityFunctions:
    
    def test_validate_point_valid(self):
        """Test point validation with valid points"""
        point = Point(10.5, 20.3, 0)
        assert validate_point(point) == True
    
    def test_validate_point_invalid(self):
        """Test point validation with invalid points"""
        # Test with None values
        class InvalidPoint:
            def __init__(self):
                self.x = None
                self.y = 10
                self.z = 0
        
        invalid_point = InvalidPoint()
        assert validate_point(invalid_point) == False
    
    def test_validate_positive_number_valid(self):
        """Test positive number validation"""
        assert validate_positive_number(10.5, "test_value") == True
        assert validate_positive_number(1, "test_value") == True
    
    def test_validate_positive_number_invalid(self):
        """Test positive number validation with invalid values"""
        assert validate_positive_number(-5, "test_value") == False
        assert validate_positive_number(0, "test_value") == False
        assert validate_positive_number("invalid", "test_value") == False
    
    def test_calculate_area_rectangle(self, sample_points):
        """Test area calculation for rectangle"""
        area = calculate_area_from_points(sample_points)
        assert area == 8000.0  # 100 * 80
    
    def test_calculate_area_triangle(self):
        """Test area calculation for triangle"""
        points = [Point(0, 0, 0), Point(10, 0, 0), Point(5, 8, 0)]
        area = calculate_area_from_points(points)
        assert area == 40.0  # 0.5 * base * height = 0.5 * 10 * 8
    
    def test_convert_units(self):
        """Test unit conversion"""
        # Feet to inches
        assert convert_units(1, 'feet', 'inches') == 12
        # Inches to feet
        assert convert_units(24, 'inches', 'feet') == 2
        # Meters to inches (approximately)
        result = convert_units(1, 'meters', 'inches')
        assert abs(result - 39.3701) < 0.01
    
    def test_sanitize_layer_name(self):
        """Test layer name sanitization"""
        # Test invalid characters
        assert sanitize_layer_name("WALL<TEST>") == "WALL_TEST_"
        # Test starting with number
        assert sanitize_layer_name("1WALLS") == "_1WALLS"
        # Test empty string
        assert sanitize_layer_name("") == "DEFAULT_LAYER"
        # Test valid name
        assert sanitize_layer_name("WALLS") == "WALLS"

# Model tests
class TestModels:
    
    def test_point_creation(self):
        """Test Point model creation"""
        point = Point(10.5, 20.3, 5.0)
        assert point.x == 10.5
        assert point.y == 20.3
        assert point.z == 5.0
    
    def test_point_to_list(self):
        """Test Point to list conversion"""
        point = Point(1, 2, 3)
        assert point.to_list() == [1, 2, 3]
        assert point.to_2d_list() == [1, 2]
    
    def test_wall_creation(self):
        """Test Wall model creation"""
        start = Point(0, 0, 0)
        end = Point(100, 0, 0)
        wall = Wall(start, end, 6, 96)
        assert wall.thickness == 6
        assert wall.height == 96
        assert wall.layer == "WALLS"
    
    def test_door_creation(self):
        """Test Door model creation"""
        position = Point(50, 0, 0)
        door = Door("wall_1", position, 36, 84, SwingDirection.LEFT_IN)
        assert door.width == 36
        assert door.height == 84
        assert door.swing_direction == SwingDirection.LEFT_IN
    
    def test_swing_direction_enum(self):
        """Test SwingDirection enum"""
        assert SwingDirection.LEFT_IN.value == "left_in"
        assert SwingDirection.RIGHT_OUT.value == "right_out"
    
    def test_furniture_type_enum(self):
        """Test FurnitureType enum"""
        assert FurnitureType.CHAIR.value == "chair"
        assert FurnitureType.TABLE.value == "table"

# LISP Generator tests
class TestLispGenerator:
    
    def test_create_wall_lisp(self, lisp_generator):
        """Test wall creation LISP code generation"""
        start = Point(0, 0, 0)
        end = Point(100, 0, 0)
        lisp_code = lisp_generator.create_wall(start, end, 6, 96)
        
        assert "create-architectural-wall" in lisp_code
        assert "0 0 0" in lisp_code
        assert "100 0 0" in lisp_code
    
    def test_insert_door_lisp(self, lisp_generator):
        """Test door insertion LISP code generation"""
        position = Point(50, 0, 0)
        lisp_code = lisp_generator.insert_door("wall_1", position, 36, 84, SwingDirection.LEFT_IN)
        
        assert "insert-door" in lisp_code
        assert "RECTANGLE" in lisp_code
        assert "ARC" in lisp_code
        assert "50 0 0" in lisp_code
    
    def test_insert_window_lisp(self, lisp_generator):
        """Test window insertion LISP code generation"""
        position = Point(30, 0, 0)
        lisp_code = lisp_generator.insert_window("wall_1", position, 48, 36, 30)
        
        assert "insert-window" in lisp_code
        assert "RECTANGLE" in lisp_code
        assert "30 0 0" in lisp_code
        assert "48" in lisp_code
        assert "36" in lisp_code
        assert "30" in lisp_code
    
    def test_create_room_lisp(self, lisp_generator, sample_points):
        """Test room creation LISP code generation"""
        lisp_code = lisp_generator.create_room(sample_points, 96)
        
        assert "create-room" in lisp_code
        assert "PLINE" in lisp_code
        assert "0 0 0" in lisp_code
        assert "100 0 0" in lisp_code
    
    def test_create_layer_lisp(self, lisp_generator):
        """Test layer creation LISP code generation"""
        lisp_code = lisp_generator.create_layer("TEST_LAYER", 7, "Continuous", 0.25)
        
        assert "create-layer" in lisp_code
        assert "LAYER" in lisp_code
        assert '"TEST_LAYER"' in lisp_code
        assert "7" in lisp_code
    
    def test_insert_furniture_lisp(self, lisp_generator):
        """Test furniture insertion LISP code generation"""
        position = Point(50, 50, 0)
        lisp_code = lisp_generator.insert_furniture(position, FurnitureType.CHAIR, 0, 1.0)
        
        assert "insert-furniture" in lisp_code
        assert "INSERT" in lisp_code
        assert "CHAIR_BLOCK" in lisp_code
        assert "50 50 0" in lisp_code

# API endpoint tests (without AutoCAD connection)
class TestAPIEndpoints:
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'AutoCAD MCP Server'
    
    def test_calculate_area_endpoint(self, client):
        """Test area calculation endpoint"""
        points_data = [
            {"x": 0, "y": 0, "z": 0},
            {"x": 100, "y": 0, "z": 0},
            {"x": 100, "y": 80, "z": 0},
            {"x": 0, "y": 80, "z": 0}
        ]
        
        response = client.post('/api/utils/calculate_area', 
                              json={'points': points_data})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['area'] == 8000.0
    
    def test_calculate_area_invalid_points(self, client):
        """Test area calculation with insufficient points"""
        points_data = [
            {"x": 0, "y": 0, "z": 0},
            {"x": 100, "y": 0, "z": 0}
        ]
        
        response = client.post('/api/utils/calculate_area', 
                              json={'points': points_data})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
    
    def test_wall_creation_validation(self, client):
        """Test wall creation with validation"""
        wall_data = {
            "start_point": {"x": 0, "y": 0, "z": 0},
            "end_point": {"x": 100, "y": 0, "z": 0},
            "thickness": -6,  # Invalid negative thickness
            "height": 96
        }
        
        response = client.post('/api/drawing/wall', json=wall_data)
        assert response.status_code == 400
    
    def test_door_creation_validation(self, client):
        """Test door creation with validation"""
        door_data = {
            "wall_reference": "wall_1",
            "position": {"x": 50, "y": 0, "z": 0},
            "width": 20,  # Below minimum width
            "height": 84,
            "swing_direction": "left_in"
        }
        
        response = client.post('/api/drawing/door', json=door_data)
        assert response.status_code == 400
    
    def test_missing_required_fields(self, client):
        """Test API with missing required fields"""
        incomplete_data = {
            "start_point": {"x": 0, "y": 0, "z": 0},
            # Missing end_point, thickness, height
        }
        
        response = client.post('/api/drawing/wall', json=incomplete_data)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Missing required fields" in data['error']

# Integration tests (mock AutoCAD operations)
class TestIntegration:
    
    def test_complete_room_workflow(self, client):
        """Test complete room creation workflow without AutoCAD"""
        # Test room creation
        room_data = {
            "points": [
                {"x": 0, "y": 0, "z": 0},
                {"x": 144, "y": 0, "z": 0},
                {"x": 144, "y": 120, "z": 0},
                {"x": 0, "y": 120, "z": 0}
            ],
            "height": 96
        }
        
        # This will fail without AutoCAD but we can test validation
        response = client.post('/api/drawing/room', json=room_data)
        # Should fail due to no AutoCAD connection, but validation should pass
        assert "points" in str(response.data) or "AutoCAD" in str(response.data)
    
    def test_furniture_placement_workflow(self, client):
        """Test furniture placement workflow"""
        furniture_data = {
            "insertion_point": {"x": 50, "y": 50, "z": 0},
            "furniture_type": "chair",
            "rotation": 0,
            "scale": 1.0
        }
        
        # This will fail without AutoCAD but we can test validation
        response = client.post('/api/furniture/insert', json=furniture_data)
        # Should fail due to no AutoCAD connection, but validation should pass
        assert "furniture_type" in str(response.data) or "AutoCAD" in str(response.data)

# Performance tests
class TestPerformance:
    
    def test_large_point_list_area_calculation(self, client):
        """Test area calculation with large point list"""
        # Create a large polygon (100 points)
        import math
        points = []
        for i in range(100):
            angle = (2 * math.pi * i) / 100
            x = 50 * math.cos(angle)
            y = 50 * math.sin(angle)
            points.append({"x": x, "y": y, "z": 0})
        
        response = client.post('/api/utils/calculate_area', 
                              json={'points': points})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        # Area should be approximately π * 50² = 7854
        assert abs(data['area'] - 7854) < 100  # Allow some tolerance for approximation
    
    def test_lisp_code_generation_performance(self, lisp_generator):
        """Test LISP code generation performance"""
        import time
        
        start_time = time.time()
        
        # Generate multiple LISP commands
        for i in range(100):
            start = Point(i, 0, 0)
            end = Point(i + 10, 0, 0)
            lisp_generator.create_wall(start, end, 6, 96)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete 100 LISP generations in under 1 second
        assert execution_time < 1.0

if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])