"""
AutoLISP code generation for architectural functions
"""
import logging
from typing import List, Dict, Any, Optional
from server.models import (Point, Wall, Door, Window, Room, Layer, TextNote, Dimension,
                           Furniture, FurnitureType, SwingDirection, DoorType, WindowType, GlassType)
from server.utils import format_lisp_string, format_lisp_point, format_lisp_point_list, sanitize_layer_name

logger = logging.getLogger(__name__)

class LispGenerator:
    """Generates AutoLISP code for architectural functions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_wall(self, start_point: Point, end_point: Point, thickness: float, height: float) -> str:
        """Generate AutoLISP code to create a wall"""
        return f"""(create-architectural-wall {format_lisp_point(start_point)} {format_lisp_point(end_point)} {thickness} {height})"""

    def insert_door(self, wall_reference: str, position: Point, width: float, height: float,
                    swing_direction: SwingDirection, door_type: DoorType = DoorType.SINGLE,
                    wall_thickness: float = 100.0, ref_id: str = None) -> str:
        """Generate AutoLISP code to insert a door with automatic annotation"""
        swing_angle = {
            SwingDirection.LEFT_IN: 0,
            SwingDirection.LEFT_OUT: 180,
            SwingDirection.RIGHT_IN: 90,
            SwingDirection.RIGHT_OUT: 270
        }.get(swing_direction, 90)
        
        ref_id_param = f'"{ref_id}"' if ref_id else 'nil'
        
        return f"""(c:create-door {position.x} {position.y} {width} {height} {wall_thickness} {swing_angle} "{door_type.value}" {ref_id_param})"""

    def insert_window(self, wall_reference: str, position: Point, width: float, height: float,
                     sill_height: float, window_type: WindowType = WindowType.FIXED,
                     glass_type: GlassType = GlassType.DOUBLE, ref_id: str = None) -> str:
        """Generate AutoLISP code to insert a window with automatic annotation"""
        ref_id_param = f'"{ref_id}"' if ref_id else 'nil'
        
        return f"""(c:create-window {position.x} {position.y} {width} {height} {sill_height} "{window_type.value}" "{glass_type.value}" {ref_id_param})"""

    def create_room(self, points: List[Point], height: float) -> str:
        """Generate AutoLISP code to create a room"""
        points_lisp = format_lisp_point_list(points)
        
        return f"""
(defun create-room (points height)
  (setq points {points_lisp})
  (setq height {height})
  
  ; Create polyline for room boundary
  (command "._PLINE")
  (foreach pt points
    (command pt)
  )
  (command "C")  ; Close polyline
  
  (princ "Room created successfully")
)
(create-room {points_lisp} {height})
"""

    def setup_grid(self, origin_point: Point, x_spacing: float, y_spacing: float, x_count: int, y_count: int) -> str:
        """Generate AutoLISP code to setup a drawing grid"""
        return f"""
(defun setup-grid (origin x-spacing y-spacing x-count y-count)
  (setq origin {format_lisp_point(origin_point)})
  (setq x-spacing {x_spacing})
  (setq y-spacing {y_spacing})
  (setq x-count {x_count})
  (setq y-count {y_count})
  
  ; Set grid and snap settings
  (setvar "GRIDMODE" 1)
  (setvar "SNAPMODE" 1)
  (setvar "GRIDUNIT" (list x-spacing y-spacing))
  (setvar "SNAPUNIT" (list x-spacing y-spacing))
  
  ; Draw grid lines
  (setq i 0)
  (repeat x-count
    (setq x-pos (+ (car origin) (* i x-spacing)))
    (command "._LINE" 
             (list x-pos (cadr origin))
             (list x-pos (+ (cadr origin) (* y-count y-spacing)))
             "")
    (setq i (1+ i))
  )
  
  (setq j 0)
  (repeat y-count
    (setq y-pos (+ (cadr origin) (* j y-spacing)))
    (command "._LINE" 
             (list (car origin) y-pos)
             (list (+ (car origin) (* x-count x-spacing)) y-pos)
             "")
    (setq j (1+ j))
  )
  
  (princ "Grid setup completed")
)
(setup-grid {format_lisp_point(origin_point)} {x_spacing} {y_spacing} {x_count} {y_count})
"""

    def create_layer(self, name: str, color: int, line_type: str, line_weight: float) -> str:
        """Generate AutoLISP code to create a layer"""
        safe_name = sanitize_layer_name(name)
        
        return f"""
(defun create-layer (name color linetype lineweight)
  (setq name {format_lisp_string(safe_name)})
  (setq color {color})
  (setq linetype {format_lisp_string(line_type)})
  (setq lineweight {line_weight})
  
  ; Create new layer
  (command "._LAYER" "N" name "C" color name "LT" linetype name "LW" lineweight name "")
  
  (princ (strcat "Layer " name " created successfully"))
)
(create-layer {format_lisp_string(safe_name)} {color} {format_lisp_string(line_type)} {line_weight})
"""

    def add_text_note(self, insertion_point: Point, text_string: str, height: float, rotation: float = 0.0) -> str:
        """Generate AutoLISP code to add text annotation"""
        return f"""
(defun add-text-note (pos text height rotation)
  (setq pos {format_lisp_point(insertion_point)})
  (setq text {format_lisp_string(text_string)})
  (setq height {height})
  (setq rotation {rotation})
  
  ; Create text entity
  (command "._TEXT" pos height rotation text)
  
  (princ "Text note added successfully")
)
(add-text-note {format_lisp_point(insertion_point)} {format_lisp_string(text_string)} {height} {rotation})
"""

    def dimension_linear(self, start_point: Point, end_point: Point, offset_distance: float) -> str:
        """Generate AutoLISP code to add linear dimension"""
        return f"""
(defun dimension-linear (start-pt end-pt offset)
  (setq start-pt {format_lisp_point(start_point)})
  (setq end-pt {format_lisp_point(end_point)})
  (setq offset {offset_distance})
  
  ; Calculate dimension line position
  (setq dim-line-pt (polar start-pt (+ (angle start-pt end-pt) (/ pi 2)) offset))
  
  ; Create linear dimension
  (command "._DIMLINEAR" start-pt end-pt dim-line-pt)
  
  (princ "Linear dimension added successfully")
)
(dimension-linear {format_lisp_point(start_point)} {format_lisp_point(end_point)} {offset_distance})
"""

    def insert_furniture(self, insertion_point: Point, furniture_type: FurnitureType, rotation: float, scale: float) -> str:
        """Generate AutoLISP code to insert furniture"""
        # Define furniture blocks (simplified representations)
        furniture_blocks = {
            FurnitureType.CHAIR: "CHAIR_BLOCK",
            FurnitureType.TABLE: "TABLE_BLOCK", 
            FurnitureType.BED: "BED_BLOCK",
            FurnitureType.SOFA: "SOFA_BLOCK",
            FurnitureType.DESK: "DESK_BLOCK"
        }
        
        block_name = furniture_blocks.get(furniture_type, "GENERIC_FURNITURE")
        
        return f"""
(defun insert-furniture (pos block-name rotation scale)
  (setq pos {format_lisp_point(insertion_point)})
  (setq block-name {format_lisp_string(block_name)})
  (setq rotation {rotation})
  (setq scale {scale})
  
  ; Insert furniture block
  (command "._INSERT" block-name pos scale scale rotation)
  
  (princ (strcat "Furniture " block-name " inserted successfully"))
)
(insert-furniture {format_lisp_point(insertion_point)} {format_lisp_string(block_name)} {rotation} {scale})
"""

    def calculate_area(self, points: List[Point]) -> str:
        """Generate AutoLISP code to calculate area"""
        points_lisp = format_lisp_point_list(points)
        
        return f"""
(defun calculate-area (points)
  (setq points {points_lisp})
  (setq area 0.0)
  (setq n (length points))
  
  ; Shoelace formula for polygon area
  (setq i 0)
  (repeat n
    (setq j (if (= i (1- n)) 0 (1+ i)))
    (setq pt1 (nth i points))
    (setq pt2 (nth j points))
    (setq area (+ area (- (* (car pt1) (cadr pt2)) (* (car pt2) (cadr pt1)))))
    (setq i (1+ i))
  )
  
  (setq area (/ (abs area) 2.0))
  (princ (strcat "Area calculated: " (rtos area 2 2) " square units"))
  area
)
(calculate-area {points_lisp})
"""

    def save_current_drawing(self, filepath: str) -> str:
        """Generate AutoLISP code to save the current drawing"""
        return f"""
(defun save-drawing (filepath)
  (setq filepath {format_lisp_string(filepath)})
  
  ; Save the current drawing
  (command "._SAVEAS" filepath)
  
  (princ (strcat "Drawing saved to: " filepath))
)
(save-drawing {format_lisp_string(filepath)})
"""

    def insert_door_simple(self, position: Point, width: float, height: float,
                          door_type: DoorType = DoorType.SINGLE, ref_id: str = None) -> str:
        """Generate AutoLISP code for simplified door insertion"""
        ref_id_param = f'"{ref_id}"' if ref_id else 'nil'
        
        type_func_map = {
            DoorType.SINGLE: "c:create-door-single",
            DoorType.DOUBLE: "c:create-door-double",
            DoorType.SLIDING: "c:create-door-sliding"
        }
        
        func_name = type_func_map.get(door_type, "c:create-door-single")
        return f"""({func_name} {position.x} {position.y} {width} {height} {ref_id_param})"""
    
    def insert_window_simple(self, position: Point, width: float, height: float,
                           sill_height: float, window_type: WindowType = WindowType.FIXED,
                           ref_id: str = None) -> str:
        """Generate AutoLISP code for simplified window insertion"""
        ref_id_param = f'"{ref_id}"' if ref_id else 'nil'
        
        type_func_map = {
            WindowType.FIXED: "c:create-window-fixed",
            WindowType.CASEMENT: "c:create-window-casement",
            WindowType.SLIDING: "c:create-window-sliding"
        }
        
        func_name = type_func_map.get(window_type, "c:create-window-fixed")
        return f"""({func_name} {position.x} {position.y} {width} {height} {sill_height} {ref_id_param})"""

    def execute_lisp(self, lisp_code: str) -> str:
        """Prepare AutoLISP code for execution"""
        return f"""
; AutoLISP code execution
{lisp_code}
"""