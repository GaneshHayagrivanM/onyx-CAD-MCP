# AutoCAD MCP Server User Guide

This guide provides step-by-step instructions for using the AutoCAD MCP Server for architectural floor planning.

## Getting Started

### Prerequisites

1. **Windows Operating System** - Required for AutoCAD COM interface
2. **AutoCAD LT 2022 or newer** - Must be installed and licensed
3. **Python 3.8+** - Download from python.org
4. **Administrative privileges** - For COM interface access

### Installation Steps

1. **Clone the repository:**
```bash
git clone https://github.com/GaneshHayagrivanM/onyx-CAD-MCP.git
cd onyx-CAD-MCP
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Test AutoCAD connectivity:**
   - Start AutoCAD manually
   - Verify you can create a new drawing
   - Leave AutoCAD running for initial connection test

4. **Start the server:**
```bash
python server/app.py
```

You should see:
```
Starting AutoCAD MCP Server...
Configuration: DevelopmentConfig
 * Running on http://127.0.0.1:5000
```

## Basic Workflow

### 1. Connect to AutoCAD

First, establish a connection to AutoCAD:

**Using curl:**
```bash
curl -X POST http://localhost:5000/api/autocad/connect \
  -H "Content-Type: application/json" \
  -d '{"instance_id": "project1"}'
```

**Using Python:**
```python
import requests

response = requests.post('http://localhost:5000/api/autocad/connect', 
                        json={'instance_id': 'project1'})
print(response.json())
```

### 2. Setup Drawing Template

Load a predefined template:

```bash
curl -X POST http://localhost:5000/api/lisp/execute \
  -H "Content-Type: application/json" \
  -d '{
    "lisp_code": "(load-drawing-template \"RESIDENTIAL\")",
    "instance_id": "project1"
  }'
```

### 3. Create Drawing Grid

Setup a grid for precise drawing:

```bash
curl -X POST http://localhost:5000/api/layout/grid \
  -H "Content-Type: application/json" \
  -d '{
    "origin_point": {"x": 0, "y": 0, "z": 0},
    "x_spacing": 12,
    "y_spacing": 12,
    "x_count": 30,
    "y_count": 20,
    "instance_id": "project1"
  }'
```

## Creating a Simple Floor Plan

### Step 1: Create Exterior Walls

Create the building perimeter:

```python
import requests

# North wall
requests.post('http://localhost:5000/api/drawing/wall', json={
    "start_point": {"x": 0, "y": 0, "z": 0},
    "end_point": {"x": 300, "y": 0, "z": 0},
    "thickness": 6,
    "height": 96,
    "instance_id": "project1"
})

# East wall  
requests.post('http://localhost:5000/api/drawing/wall', json={
    "start_point": {"x": 300, "y": 0, "z": 0},
    "end_point": {"x": 300, "y": 240, "z": 0},
    "thickness": 6,
    "height": 96,
    "instance_id": "project1"
})

# South wall
requests.post('http://localhost:5000/api/drawing/wall', json={
    "start_point": {"x": 300, "y": 240, "z": 0},
    "end_point": {"x": 0, "y": 240, "z": 0},
    "thickness": 6,
    "height": 96,
    "instance_id": "project1"
})

# West wall
requests.post('http://localhost:5000/api/drawing/wall', json={
    "start_point": {"x": 0, "y": 240, "z": 0},
    "end_point": {"x": 0, "y": 0, "z": 0},
    "thickness": 6,
    "height": 96,
    "instance_id": "project1"
})
```

### Step 2: Add Interior Walls

Create interior partitions:

```python
# Living room / bedroom separation
requests.post('http://localhost:5000/api/drawing/wall', json={
    "start_point": {"x": 150, "y": 0, "z": 0},
    "end_point": {"x": 150, "y": 180, "z": 0},
    "thickness": 4,
    "height": 96,
    "instance_id": "project1"
})

# Kitchen separation
requests.post('http://localhost:5000/api/drawing/wall', json={
    "start_point": {"x": 0, "y": 180, "z": 0},
    "end_point": {"x": 150, "y": 180, "z": 0},
    "thickness": 4,
    "height": 96,
    "instance_id": "project1"
})
```

### Step 3: Add Doors

Insert doors with appropriate swing directions:

```python
# Front door (main entrance)
requests.post('http://localhost:5000/api/drawing/door', json={
    "wall_reference": "wall_1",
    "position": {"x": 140, "y": 0, "z": 0},
    "width": 36,
    "height": 84,
    "swing_direction": "left_in",
    "instance_id": "project1"
})

# Bedroom door
requests.post('http://localhost:5000/api/drawing/door', json={
    "wall_reference": "wall_interior_1", 
    "position": {"x": 150, "y": 60, "z": 0},
    "width": 32,
    "height": 84,
    "swing_direction": "right_in",
    "instance_id": "project1"
})
```

### Step 4: Add Windows

Insert windows for natural light:

```python
# Living room window
requests.post('http://localhost:5000/api/drawing/window', json={
    "wall_reference": "wall_2",
    "position": {"x": 300, "y": 60, "z": 0},
    "width": 60,
    "height": 48,
    "sill_height": 30,
    "instance_id": "project1"
})

# Bedroom window
requests.post('http://localhost:5000/api/drawing/window', json={
    "wall_reference": "wall_2",
    "position": {"x": 300, "y": 180, "z": 0},
    "width": 48,
    "height": 48,
    "sill_height": 30,
    "instance_id": "project1"
})

# Kitchen window
requests.post('http://localhost:5000/api/drawing/window', json={
    "wall_reference": "wall_4",
    "position": {"x": 60, "y": 240, "z": 0},
    "width": 36,
    "height": 36,
    "sill_height": 42,
    "instance_id": "project1"
})
```

### Step 5: Define Rooms

Create room boundaries and labels:

```python
# Living room
requests.post('http://localhost:5000/api/drawing/room', json={
    "points": [
        {"x": 3, "y": 3, "z": 0},
        {"x": 147, "y": 3, "z": 0},
        {"x": 147, "y": 177, "z": 0},
        {"x": 3, "y": 177, "z": 0}
    ],
    "height": 96,
    "instance_id": "project1"
})

# Bedroom
requests.post('http://localhost:5000/api/drawing/room', json={
    "points": [
        {"x": 153, "y": 3, "z": 0},
        {"x": 297, "y": 3, "z": 0},
        {"x": 297, "y": 237, "z": 0},
        {"x": 153, "y": 237, "z": 0}
    ],
    "height": 96,
    "instance_id": "project1"
})

# Kitchen
requests.post('http://localhost:5000/api/drawing/room', json={
    "points": [
        {"x": 3, "y": 183, "z": 0},
        {"x": 147, "y": 183, "z": 0},
        {"x": 147, "y": 237, "z": 0},
        {"x": 3, "y": 237, "z": 0}
    ],
    "height": 96,
    "instance_id": "project1"
})
```

### Step 6: Add Furniture

Place furniture in appropriate locations:

```python
# Living room furniture
requests.post('http://localhost:5000/api/furniture/insert', json={
    "insertion_point": {"x": 50, "y": 100, "z": 0},
    "furniture_type": "sofa",
    "rotation": 0,
    "scale": 1.0,
    "instance_id": "project1"
})

requests.post('http://localhost:5000/api/furniture/insert', json={
    "insertion_point": {"x": 100, "y": 50, "z": 0},
    "furniture_type": "table",
    "rotation": 0,
    "scale": 0.8,
    "instance_id": "project1"
})

# Bedroom furniture
requests.post('http://localhost:5000/api/furniture/insert', json={
    "insertion_point": {"x": 200, "y": 180, "z": 0},
    "furniture_type": "bed",
    "rotation": 90,
    "scale": 1.0,
    "instance_id": "project1"
})

# Kitchen table
requests.post('http://localhost:5000/api/furniture/insert', json={
    "insertion_point": {"x": 75, "y": 210, "z": 0},
    "furniture_type": "table",
    "rotation": 0,
    "scale": 0.6,
    "instance_id": "project1"
})
```

### Step 7: Add Dimensions

Add dimensions for clarity:

```python
# Overall building width
requests.post('http://localhost:5000/api/annotation/dimension', json={
    "start_point": {"x": 0, "y": 0, "z": 0},
    "end_point": {"x": 300, "y": 0, "z": 0},
    "offset_distance": -24,
    "instance_id": "project1"
})

# Overall building height
requests.post('http://localhost:5000/api/annotation/dimension', json={
    "start_point": {"x": 300, "y": 0, "z": 0},
    "end_point": {"x": 300, "y": 240, "z": 0},
    "offset_distance": 24,
    "instance_id": "project1"
})
```

### Step 8: Add Text Labels

Add room labels and notes:

```python
# Room labels
requests.post('http://localhost:5000/api/annotation/text', json={
    "insertion_point": {"x": 75, "y": 90, "z": 0},
    "text_string": "LIVING ROOM",
    "height": 12,
    "rotation": 0,
    "instance_id": "project1"
})

requests.post('http://localhost:5000/api/annotation/text', json={
    "insertion_point": {"x": 225, "y": 120, "z": 0},
    "text_string": "BEDROOM",
    "height": 12,
    "rotation": 0,
    "instance_id": "project1"
})

requests.post('http://localhost:5000/api/annotation/text', json={
    "insertion_point": {"x": 75, "y": 210, "z": 0},
    "text_string": "KITCHEN",
    "height": 12,
    "rotation": 0,
    "instance_id": "project1"
})
```

### Step 9: Save the Drawing

Save your completed floor plan:

```python
requests.post('http://localhost:5000/api/drawing/save', json={
    "filepath": "C:\\Projects\\Simple_Floor_Plan.dwg",
    "instance_id": "project1"
})
```

## Advanced Features

### Building Code Compliance

Check building code compliance:

```python
# Execute building code check
requests.post('http://localhost:5000/api/lisp/execute', json={
    "lisp_code": """
    (check-building-code-compliance 144 36 20 "BEDROOM")
    """,
    "instance_id": "project1"
})
```

### Creating Parametric Components

Create stairs with specific parameters:

```python
requests.post('http://localhost:5000/api/lisp/execute', json={
    "lisp_code": """
    (create-parametric-component 
      '(50 50) 
      "STAIR" 
      '(("width" . 36) ("run" . 120) ("rise" . 96) ("steps" . 12)))
    """,
    "instance_id": "project1"
})
```

### Generate Room Schedule

Create a room schedule table:

```python
requests.post('http://localhost:5000/api/lisp/execute', json={
    "lisp_code": """
    (generate-room-schedule 
      '(("Living Room" 144) ("Bedroom" 168) ("Kitchen" 72)))
    """,
    "instance_id": "project1"
})
```

### Export to Different Formats

Export to PDF:

```python
requests.post('http://localhost:5000/api/lisp/execute', json={
    "lisp_code": '(export-drawing "PDF" "C:\\\\Projects\\\\Floor_Plan.pdf")',
    "instance_id": "project1"
})
```

## Troubleshooting

### Common Issues

**1. AutoCAD Connection Failed**
- Ensure AutoCAD is running
- Check that you have administrative privileges
- Verify AutoCAD version compatibility (2022+)
- Try restarting both AutoCAD and the server

**2. LISP Execution Errors**
- Check AutoCAD command line for detailed error messages
- Verify all required parameters are provided
- Ensure coordinate values are valid numbers

**3. Drawing Elements Not Appearing**
- Check that the correct layer is current
- Verify zoom extents to see all elements
- Ensure coordinate system is correct

**4. Permission Errors**
- Run the server as administrator
- Check AutoCAD's trust settings for automation
- Verify file system permissions for saving

### Debugging Tips

**Enable Debug Logging:**
Set environment variable:
```bash
set FLASK_ENV=development
```

**Check AutoCAD Command History:**
In AutoCAD, press F2 to open the text window and review command history.

**Validate Coordinates:**
Use the calculate_area endpoint to verify your point coordinates are correct.

### Performance Optimization

**1. Minimize AutoCAD Regeneration:**
- Group related operations
- Use zoom extents sparingly
- Avoid unnecessary layer switching

**2. Batch Operations:**
- Create multiple elements in single requests when possible
- Use the execute_lisp endpoint for complex operations

**3. Connection Management:**
- Reuse connections rather than reconnecting frequently
- Close unused connections to free resources

## Best Practices

### Drawing Organization

1. **Use Consistent Layer Names:**
   - WALLS, DOORS, WINDOWS, FURNITURE, TEXT, DIMENSIONS

2. **Maintain Scale Consistency:**
   - Use appropriate text heights for your scale
   - Keep line weights consistent across similar elements

3. **Logical Coordinate System:**
   - Start at origin (0,0) when possible
   - Use consistent units throughout (inches recommended)

### API Usage

1. **Error Handling:**
   - Always check response success status
   - Implement retry logic for transient failures
   - Log errors for debugging

2. **Resource Management:**
   - Close AutoCAD connections when done
   - Save work frequently
   - Use appropriate timeouts

3. **Code Organization:**
   - Group related API calls into functions
   - Use configuration files for common parameters
   - Document your workflow with comments

## Support and Resources

- **API Reference:** See `docs/API.md`
- **AutoLISP Functions:** See files in `lisp/` directory
- **GitHub Issues:** Report bugs and request features
- **AutoCAD Documentation:** Autodesk official documentation for AutoLISP
- **Building Codes:** Consult local building codes for compliance requirements