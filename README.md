# AutoCAD MCP Server

A comprehensive Flask-based MCP (Model Context Protocol) server that connects to AutoCAD and executes AutoLISP code to facilitate architectural floor plan creation. This server provides a complete suite of tools for efficient creation, modification, and management of architectural drawings through programmatic interfaces.

## Features

- **Flask-based REST API server** with AutoCAD integration
- **AutoLISP code generation** for architectural functions
- **Comprehensive architectural tools** for floor planning
- **Real-time AutoCAD communication** via COM/ActiveX interface
- **Building code compliance checking**
- **Parametric component creation**
- **Multi-format export capabilities**
- **Template-based drawing setup**

## System Requirements

- Windows 10/11 (required for AutoCAD COM interface)
- AutoCAD LT 2022 or newer
- Python 3.8+
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/GaneshHayagrivanM/onyx-CAD-MCP.git
cd onyx-CAD-MCP
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure AutoCAD is installed and accessible on your system

4. Configure the server settings in `config/settings.py` if needed

## Quick Start

1. Start the AutoCAD MCP Server:
```bash
python server/app.py
```

2. The server will start on `http://localhost:5000` by default

3. Connect to AutoCAD:
```bash
curl -X POST http://localhost:5000/api/autocad/connect \
  -H "Content-Type: application/json" \
  -d '{"instance_id": "default"}'
```

4. Create your first wall:
```bash
curl -X POST http://localhost:5000/api/drawing/wall \
  -H "Content-Type: application/json" \
  -d '{
    "start_point": {"x": 0, "y": 0, "z": 0},
    "end_point": {"x": 120, "y": 0, "z": 0},
    "thickness": 6,
    "height": 96
  }'
```

## Core Functions

### Drawing Elements
- **create_wall** - Create walls with specified dimensions
- **insert_door** - Add doors to walls with swing directions
- **insert_window** - Add windows with sill heights
- **create_room** - Define room boundaries with area calculation

### Layout & Organization
- **setup_grid** - Create drawing grid with labels
- **create_layer** - Manage drawing layers with properties
- **set_drawing_scale** - Set drawing scale
- **setup_viewport** - Create viewports

### Annotation & Dimensions
- **add_text_note** - Add text annotations
- **dimension_linear** - Add linear dimensions
- **add_room_label** - Label rooms with area

### Furniture & Fixtures
- **insert_furniture** - Place furniture with rotation and scale
- **create_cabinet** - Create cabinet units
- **create_fixture** - Add architectural fixtures

### Utilities
- **calculate_area** - Calculate polygon areas
- **generate_room_schedule** - Create room schedules
- **check_building_code** - Validate building codes
- **export_to_format** - Export drawings (PDF, DXF, DWG)

### Advanced Features
- **create_parametric_component** - Create parametric objects
- **load_template** - Load drawing templates
- **generate_3d_model** - Generate 3D models from 2D plans
- **create_section** - Create section views

## API Documentation

See [API.md](docs/API.md) for complete API documentation with examples.

## User Guide

See [USER_GUIDE.md](docs/USER_GUIDE.md) for detailed usage instructions.

## Configuration

Edit `config/settings.py` to customize:
- Server host and port
- AutoCAD connection settings
- Default drawing parameters
- Building code requirements
- Logging configuration

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

## Architecture

```
onyx-CAD-MCP/
├── server/
│   ├── app.py                 # Main Flask application
│   ├── autocad_interface.py   # AutoCAD COM interface
│   ├── lisp_generator.py      # AutoLISP code generation
│   ├── models.py              # Data models
│   └── utils.py               # Utility functions
├── lisp/
│   ├── core_functions.lsp     # Core AutoLISP functions
│   ├── architectural_tools.lsp # Architectural functions
│   └── utilities.lsp          # Utility functions
├── config/
│   └── settings.py            # Configuration
├── tests/
│   └── test_functions.py      # Test suite
├── docs/
│   ├── API.md                 # API documentation
│   └── USER_GUIDE.md          # User guide
├── requirements.txt
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation in `/docs`
- Review the test files for usage examples

## Changelog

### Version 1.0.0
- Initial release
- Complete AutoCAD MCP server implementation
- All core architectural functions
- REST API with comprehensive error handling
- AutoLISP code generation engine
- Building code compliance checking
- Template system for different project types