# AutoCAD MCP Server API Documentation

This document provides comprehensive API documentation for the AutoCAD MCP Server.

## Base URL
```
http://localhost:5000/api
```

## Authentication
Currently, no authentication is required. The server is designed for local use with AutoCAD.

## Common Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "execution_time": 0.1234
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error description",
  "message": "Detailed error message"
}
```

## Endpoints

### Server Management

#### Connect to AutoCAD
**POST** `/autocad/connect`

Connect to an AutoCAD instance.

**Request Body:**
```json
{
  "instance_id": "default"  // Optional, defaults to "default"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Connected to AutoCAD (instance: default)",
  "instance_id": "default",
  "connected": true
}
```

#### Disconnect from AutoCAD
**POST** `/autocad/disconnect`

**Request Body:**
```json
{
  "instance_id": "default"
}
```

#### List Connections
**GET** `/autocad/connections`

**Response:**
```json
{
  "success": true,
  "connections": [
    {
      "instance_id": "default",
      "connected": true,
      "document_name": "Drawing1.dwg"
    }
  ],
  "count": 1
}
```

### Core Drawing Elements

#### Create Wall
**POST** `/drawing/wall`

Create a wall with specified dimensions.

**Request Body:**
```json
{
  "start_point": {"x": 0, "y": 0, "z": 0},
  "end_point": {"x": 120, "y": 0, "z": 0},
  "thickness": 6,
  "height": 96,
  "instance_id": "default"  // Optional
}
```

**Response:**
```json
{
  "success": true,
  "message": "Wall created successfully",
  "execution_time": 0.234
}
```

#### Insert Door
**POST** `/drawing/door`

Insert a door into a wall.

**Request Body:**
```json
{
  "wall_reference": "wall_1",
  "position": {"x": 60, "y": 0, "z": 0},
  "width": 36,
  "height": 84,
  "swing_direction": "left_in",  // Options: left_in, left_out, right_in, right_out
  "instance_id": "default"
}
```

#### Insert Window
**POST** `/drawing/window`

Insert a window into a wall.

**Request Body:**
```json
{
  "wall_reference": "wall_1",
  "position": {"x": 30, "y": 0, "z": 0},
  "width": 48,
  "height": 36,
  "sill_height": 30,
  "instance_id": "default"
}
```

#### Create Room
**POST** `/drawing/room`

Create a room boundary.

**Request Body:**
```json
{
  "points": [
    {"x": 0, "y": 0, "z": 0},
    {"x": 144, "y": 0, "z": 0},
    {"x": 144, "y": 120, "z": 0},
    {"x": 0, "y": 120, "z": 0}
  ],
  "height": 96,
  "instance_id": "default"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Room created successfully",
  "area": 120.0,
  "execution_time": 0.156
}
```

### Layout and Organization

#### Setup Grid
**POST** `/layout/grid`

Create a drawing grid.

**Request Body:**
```json
{
  "origin_point": {"x": 0, "y": 0, "z": 0},
  "x_spacing": 12,
  "y_spacing": 12,
  "x_count": 20,
  "y_count": 15,
  "instance_id": "default"
}
```

#### Create Layer
**POST** `/layout/layer`

Create a new AutoCAD layer.

**Request Body:**
```json
{
  "name": "FURNITURE",
  "color": 5,
  "line_type": "Continuous",
  "line_weight": 0.25,
  "instance_id": "default"
}
```

### Annotation and Dimensions

#### Add Text Note
**POST** `/annotation/text`

Add text annotation to the drawing.

**Request Body:**
```json
{
  "insertion_point": {"x": 50, "y": 50, "z": 0},
  "text_string": "Living Room",
  "height": 18,
  "rotation": 0,  // Optional, in degrees
  "instance_id": "default"
}
```

#### Add Linear Dimension
**POST** `/annotation/dimension`

Add linear dimension between two points.

**Request Body:**
```json
{
  "start_point": {"x": 0, "y": 0, "z": 0},
  "end_point": {"x": 120, "y": 0, "z": 0},
  "offset_distance": 24,
  "instance_id": "default"
}
```

### Furniture and Fixtures

#### Insert Furniture
**POST** `/furniture/insert`

Insert furniture into the drawing.

**Request Body:**
```json
{
  "insertion_point": {"x": 60, "y": 60, "z": 0},
  "furniture_type": "chair",  // Options: chair, table, bed, sofa, desk
  "rotation": 0,  // Optional, in degrees
  "scale": 1.0,   // Optional, scale factor
  "instance_id": "default"
}
```

### Utilities and Calculations

#### Calculate Area
**POST** `/utils/calculate_area`

Calculate the area of a polygon defined by points.

**Request Body:**
```json
{
  "points": [
    {"x": 0, "y": 0, "z": 0},
    {"x": 120, "y": 0, "z": 0},
    {"x": 120, "y": 96, "z": 0},
    {"x": 0, "y": 96, "z": 0}
  ]
}
```

**Response:**
```json
{
  "success": true,
  "area": 8000.0,
  "units": "square units",
  "point_count": 4
}
```

### Server Management

#### Execute Custom AutoLISP
**POST** `/lisp/execute`

Execute custom AutoLISP code.

**Request Body:**
```json
{
  "lisp_code": "(command \"._LINE\" '(0 0) '(100 100) \"\")",
  "instance_id": "default"
}
```

**Response:**
```json
{
  "success": true,
  "result": null,
  "error_message": "",
  "execution_time": 0.089
}
```

#### Save Drawing
**POST** `/drawing/save`

Save the current AutoCAD drawing.

**Request Body:**
```json
{
  "filepath": "C:\\Projects\\Floor_Plan.dwg",
  "instance_id": "default"
}
```

## Error Codes

- **400 Bad Request** - Invalid request data or validation errors
- **500 Internal Server Error** - AutoCAD connection errors or server errors

## Point Format

All points in the API use the following format:
```json
{
  "x": 0.0,  // X coordinate
  "y": 0.0,  // Y coordinate  
  "z": 0.0   // Z coordinate (optional, defaults to 0)
}
```

## Units

- All linear measurements are in inches
- All areas are in square inches
- All angles are in degrees
- Text heights are in drawing units

## Examples

### Complete Floor Plan Creation

1. **Connect to AutoCAD:**
```bash
curl -X POST http://localhost:5000/api/autocad/connect
```

2. **Create exterior walls:**
```bash
curl -X POST http://localhost:5000/api/drawing/wall \
  -H "Content-Type: application/json" \
  -d '{
    "start_point": {"x": 0, "y": 0},
    "end_point": {"x": 300, "y": 0},
    "thickness": 6,
    "height": 96
  }'
```

3. **Add a door:**
```bash
curl -X POST http://localhost:5000/api/drawing/door \
  -H "Content-Type: application/json" \
  -d '{
    "wall_reference": "wall_1",
    "position": {"x": 50, "y": 0},
    "width": 36,
    "height": 84,
    "swing_direction": "left_in"
  }'
```

4. **Add furniture:**
```bash
curl -X POST http://localhost:5000/api/furniture/insert \
  -H "Content-Type: application/json" \
  -d '{
    "insertion_point": {"x": 150, "y": 150},
    "furniture_type": "table",
    "rotation": 0,
    "scale": 1.0
  }'
```

5. **Save the drawing:**
```bash
curl -X POST http://localhost:5000/api/drawing/save \
  -H "Content-Type: application/json" \
  -d '{"filepath": "C:\\Projects\\Floor_Plan.dwg"}'
```

## Rate Limiting

Currently, no rate limiting is implemented. However, AutoCAD operations can be slow, so avoid sending requests faster than AutoCAD can process them.

## WebSocket Support

Future versions may include WebSocket support for real-time drawing updates and notifications.