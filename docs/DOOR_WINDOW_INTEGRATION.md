# Door and Window Integration Guide

## Overview

The AutoCAD MCP Server has been enhanced with comprehensive door and window creation capabilities that include automatic annotation with dimensions, types, and reference identifiers. This integration leverages the `advanced_entities.lsp` file to provide professional-grade architectural elements.

## Features

### Door Types
- **SINGLE**: Standard swing door with arc representation
- **DOUBLE**: Double swing doors with dual arcs
- **SLIDING**: Sliding door with track and panel representation
- **POCKET**: Pocket door with wall pocket indication

### Window Types
- **FIXED**: Non-opening window with cross-hatch glass indication
- **CASEMENT**: Hinged window with swing arc
- **SLIDING**: Horizontal sliding window with center mullion
- **DOUBLE-HUNG**: Vertical sliding sashes
- **AWNING**: Top-hinged outward opening window

### Glass Types
- **SINGLE**: Single-pane glass
- **DOUBLE**: Double-pane insulated glass
- **TRIPLE**: Triple-pane insulated glass
- **TEMPERED**: Tempered safety glass

## API Endpoints

### 1. Full Door Creation with Annotation

**Endpoint:** `POST /api/drawing/door`

**Request Body:**
```json
{
  "wall_reference": "WALL-01",
  "position": {"x": 100.0, "y": 200.0, "z": 0.0},
  "width": 900.0,
  "height": 2100.0,
  "swing_direction": "right_in",
  "door_type": "SINGLE",
  "wall_thickness": 100.0,
  "ref_id": "D1",
  "instance_id": "default"
}
```

**Parameters:**
- `wall_reference` (required): Reference to the wall
- `position` (required): Insertion point {x, y, z}
- `width` (required): Door width in mm
- `height` (required): Door height in mm
- `swing_direction` (required): "left_in", "left_out", "right_in", "right_out"
- `door_type` (optional): "SINGLE", "DOUBLE", "SLIDING", "POCKET" (default: "SINGLE")
- `wall_thickness` (optional): Wall thickness in mm (default: 100.0)
- `ref_id` (optional): Reference identifier (auto-generated if not provided)
- `instance_id` (optional): AutoCAD instance ID (default: "default")

**Response:**
```json
{
  "success": true,
  "message": "Door inserted successfully with annotation",
  "door_type": "SINGLE",
  "ref_id": "D1",
  "execution_time": 0.123
}
```

### 2. Simplified Door Creation

**Endpoint:** `POST /api/drawing/door/simple`

**Request Body:**
```json
{
  "position": {"x": 100.0, "y": 200.0, "z": 0.0},
  "width": 900.0,
  "height": 2100.0,
  "door_type": "SINGLE",
  "ref_id": "D1",
  "instance_id": "default"
}
```

Uses default swing angle of 90 degrees and standard wall thickness of 100mm.

### 3. Full Window Creation with Annotation

**Endpoint:** `POST /api/drawing/window`

**Request Body:**
```json
{
  "wall_reference": "WALL-01",
  "position": {"x": 200.0, "y": 300.0, "z": 0.0},
  "width": 1200.0,
  "height": 1000.0,
  "sill_height": 900.0,
  "window_type": "FIXED",
  "glass_type": "DOUBLE",
  "ref_id": "W1",
  "instance_id": "default"
}
```

**Parameters:**
- `wall_reference` (required): Reference to the wall
- `position` (required): Insertion point {x, y, z}
- `width` (required): Window width in mm
- `height` (required): Window height in mm
- `sill_height` (required): Height from floor to window sill in mm
- `window_type` (optional): "FIXED", "CASEMENT", "SLIDING", "DOUBLE-HUNG", "AWNING" (default: "FIXED")
- `glass_type` (optional): "SINGLE", "DOUBLE", "TRIPLE", "TEMPERED" (default: "DOUBLE")
- `ref_id` (optional): Reference identifier (auto-generated if not provided)
- `instance_id` (optional): AutoCAD instance ID (default: "default")

**Response:**
```json
{
  "success": true,
  "message": "Window inserted successfully with annotation",
  "window_type": "FIXED",
  "glass_type": "DOUBLE",
  "ref_id": "W1",
  "execution_time": 0.145
}
```

### 4. Simplified Window Creation

**Endpoint:** `POST /api/drawing/window/simple`

**Request Body:**
```json
{
  "position": {"x": 200.0, "y": 300.0, "z": 0.0},
  "width": 1200.0,
  "height": 1000.0,
  "sill_height": 900.0,
  "window_type": "FIXED",
  "ref_id": "W1",
  "instance_id": "default"
}
```

Uses default double-pane glass.

## AutoLISP Functions

The following AutoLISP functions are available when `advanced_entities.lsp` is loaded:

### Main Functions

1. **`c:create-door`** - Create door with full parameters
   ```lisp
   (c:create-door x y width height wall-thickness swing-angle door-type ref-id)
   ```

2. **`c:create-window`** - Create window with full parameters
   ```lisp
   (c:create-window x y width height sill-height window-type glass-type ref-id)
   ```

### Simplified Wrapper Functions

3. **`c:create-door-single`** - Create single swing door
   ```lisp
   (c:create-door-single x y width height ref-id)
   ```

4. **`c:create-door-double`** - Create double swing door
   ```lisp
   (c:create-door-double x y width height ref-id)
   ```

5. **`c:create-door-sliding`** - Create sliding door
   ```lisp
   (c:create-door-sliding x y width height ref-id)
   ```

6. **`c:create-window-fixed`** - Create fixed window
   ```lisp
   (c:create-window-fixed x y width height sill-height ref-id)
   ```

7. **`c:create-window-casement`** - Create casement window
   ```lisp
   (c:create-window-casement x y width height sill-height ref-id)
   ```

8. **`c:create-window-sliding`** - Create sliding window
   ```lisp
   (c:create-window-sliding x y width height sill-height ref-id)
   ```

## Layer Management

The enhanced functions automatically create and manage the following layers:

### Door Layers
- **A-DOOR**: Main door entities (cyan, continuous)
- **A-DOOR-ANNO**: Door annotations (cyan, continuous)

### Window Layers
- **A-WIND**: Main window entities (blue, continuous)
- **A-WIND-ANNO**: Window annotations (blue, continuous)

### Annotation Layer
- **A-ANNO**: General annotations (yellow, continuous)

## Automatic Annotation

All doors and windows created with these functions include automatic annotation with:

### Door Annotations
- Reference ID (e.g., "D1", "D2")
- Door type (e.g., "SINGLE DOOR", "DOUBLE DOOR")
- Dimensions (width x height in mm)
- Leader line pointing to the door

### Window Annotations
- Reference ID (e.g., "W1", "W2")
- Window type (e.g., "FIXED WINDOW", "CASEMENT WINDOW")
- Dimensions (width x height in mm)
- Sill height (in mm)
- Glass type (e.g., "DOUBLE", "TRIPLE")
- Leader line pointing to the window

## Code Changes Summary

### Modified Files

1. **`server/models.py`**
   - Added `DoorType`, `WindowType`, and `GlassType` enums
   - Enhanced `Door` model with `door_type`, `wall_thickness`, and `ref_id`
   - Enhanced `Window` model with `window_type`, `glass_type`, and `ref_id`

2. **`server/lisp_generator.py`**
   - Updated `insert_door()` to support new parameters
   - Updated `insert_window()` to support new parameters
   - Added `insert_door_simple()` for simplified door creation
   - Added `insert_window_simple()` for simplified window creation

3. **`server/app.py`**
   - Enhanced `/api/drawing/door` endpoint with new parameters
   - Enhanced `/api/drawing/window` endpoint with new parameters
   - Added `/api/drawing/door/simple` endpoint
   - Added `/api/drawing/window/simple` endpoint

4. **`lisp/architectural_tools.lsp`**
   - Added load statement for `advanced_entities.lsp`
   - Added initialization messages for enhanced functions

5. **`lisp/advanced_entities.lsp`** (NEW)
   - Complete implementation of door and window creation with annotation
   - Helper functions for layer management and reference ID generation
   - Support for multiple door and window types

## Usage Examples

### Python Example
```python
import requests

# Create a single swing door
response = requests.post('http://localhost:5000/api/drawing/door', json={
    "wall_reference": "WALL-01",
    "position": {"x": 1000.0, "y": 2000.0, "z": 0.0},
    "width": 900.0,
    "height": 2100.0,
    "swing_direction": "right_in",
    "door_type": "SINGLE",
    "ref_id": "D1"
})

# Create a fixed window
response = requests.post('http://localhost:5000/api/drawing/window', json={
    "wall_reference": "WALL-01",
    "position": {"x": 3000.0, "y": 2000.0, "z": 0.0},
    "width": 1200.0,
    "height": 1000.0,
    "sill_height": 900.0,
    "window_type": "FIXED",
    "glass_type": "DOUBLE",
    "ref_id": "W1"
})
```

### AutoLISP Example
```lisp
; Load the architectural tools (includes advanced_entities.lsp)
(load "architectural_tools.lsp")

; Create a single door at position (100, 200) with 900mm width and 2100mm height
(c:create-door-single 100 200 900 2100 "D1")

; Create a fixed window at position (300, 200) with 1200mm width, 1000mm height, 900mm sill
(c:create-window-fixed 300 200 1200 1000 900 "W1")

; Create a double swing door with full parameters
(c:create-door 500 200 1800 2100 100 90 "DOUBLE" "D2")

; Create a casement window with full parameters
(c:create-window 800 200 1000 1200 900 "CASEMENT" "DOUBLE" "W2")
```

## Benefits

1. **Professional Annotations**: All doors and windows are automatically annotated with relevant information
2. **Standardized Layers**: Consistent layer naming following AIA CAD standards
3. **Multiple Types**: Support for various door and window types commonly used in architecture
4. **Flexible API**: Both full-featured and simplified endpoints for different use cases
5. **Auto-Generated IDs**: Automatic reference ID generation if not specified
6. **Easy Maintenance**: Annotations are linked to their entities through layers

## Notes

- All dimensions are in millimeters
- Swing angles are in degrees (0, 90, 180, 270)
- Reference IDs are auto-generated as D1, D2, W1, W2, etc. if not provided
- Annotations use multi-line text (MTEXT) format for better readability
- Leader lines connect annotations to their respective entities

## Future Enhancements

Potential future improvements:
- Block-based door and window definitions
- Attribute-based annotations for easier editing
- 3D representation support
- Door/window schedule generation
- Building code compliance checking integration