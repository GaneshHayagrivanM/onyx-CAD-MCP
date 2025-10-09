"""
Data models for the AutoCAD MCP Server
"""
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any
from enum import Enum

@dataclass
class Point:
    """Represents a 2D or 3D point"""
    x: float
    y: float
    z: float = 0.0
    
    def to_list(self) -> List[float]:
        """Convert to list format for AutoLISP"""
        return [self.x, self.y, self.z]
    
    def to_2d_list(self) -> List[float]:
        """Convert to 2D list format"""
        return [self.x, self.y]

@dataclass
class Wall:
    """Represents a wall element"""
    start_point: Point
    end_point: Point
    thickness: float
    height: float
    layer: str = "WALLS"
    
class SwingDirection(Enum):
    """Door swing directions"""
    LEFT_IN = "left_in"
    LEFT_OUT = "left_out"
    RIGHT_IN = "right_in"
    RIGHT_OUT = "right_out"

@dataclass
class Door:
    """Represents a door element"""
    wall_reference: str
    position: Point
    width: float
    height: float
    swing_direction: SwingDirection
    layer: str = "DOORS"

@dataclass
class Window:
    """Represents a window element"""
    wall_reference: str
    position: Point
    width: float
    height: float
    sill_height: float
    layer: str = "WINDOWS"

@dataclass
class Room:
    """Represents a room boundary"""
    points: List[Point]
    height: float
    name: str = ""
    area: float = 0.0
    layer: str = "ROOMS"

@dataclass
class Layer:
    """Represents an AutoCAD layer"""
    name: str
    color: int
    line_type: str
    line_weight: float
    
@dataclass
class TextNote:
    """Represents a text annotation"""
    insertion_point: Point
    text_string: str
    height: float
    rotation: float = 0.0
    layer: str = "TEXT"

@dataclass
class Dimension:
    """Represents a dimension annotation"""
    start_point: Point
    end_point: Point
    offset_distance: float
    dimension_type: str = "linear"
    layer: str = "DIMENSIONS"

class FurnitureType(Enum):
    """Types of furniture"""
    CHAIR = "chair"
    TABLE = "table"
    BED = "bed"
    SOFA = "sofa"
    DESK = "desk"

@dataclass
class Furniture:
    """Represents furniture placement"""
    insertion_point: Point
    furniture_type: FurnitureType
    rotation: float = 0.0
    scale: float = 1.0
    layer: str = "FURNITURE"

@dataclass
class AutoCADConnection:
    """Represents AutoCAD connection information"""
    instance_id: str
    application: Any = None
    connected: bool = False
    
@dataclass
class LispExecutionResult:
    """Result of AutoLISP execution"""
    success: bool
    result: Any = None
    error_message: str = ""
    execution_time: float = 0.0

@dataclass
class DrawingTemplate:
    """Represents a drawing template"""
    name: str
    filepath: str
    units: str = "inches"
    scale: float = 1.0
    layers: List[Layer] = None
    
    def __post_init__(self):
        if self.layers is None:
            self.layers = []