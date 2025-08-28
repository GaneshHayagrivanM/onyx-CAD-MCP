# AutoCAD MCP Server

This project is an MCP (Model Context Protocol) server for AutoCAD that facilitates architectural floor plan creation. The server provides a programmatic interface to execute AutoLISP code in AutoCAD, enabling the creation and modification of architectural drawings.

## Project Overview

The server is built with Python and Flask, providing a RESTful API for interacting with AutoCAD. It is designed to be lightweight, extensible, and easy to use.

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd autocad-mcp-server
   ```

2. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server:**
   ```bash
   python src/main.py
   ```
   The server will start on `http://127.0.0.1:5000`.

## API Usage

### Connect to AutoCAD

Before executing any commands, you must connect to an AutoCAD instance.

- **Endpoint:** `POST /connect_to_autocad`
- **Body:**
  ```json
  {
    "instance_id": "acad-1"
  }
  ```
- **Response:**
  ```json
  {
    "message": "Successfully connected to AutoCAD instance acad-1",
    "instance_id": "acad-1"
  }
  ```

### Execute AutoLISP Code

You can execute arbitrary AutoLISP code on a connected instance.

- **Endpoint:** `POST /execute_lisp`
- **Body:**
  ```json
  {
    "instance_id": "acad-1",
    "lisp_code": "(command \"_CIRCLE\" \"5,5\" \"2\")"
  }
  ```

### Create a Wall

- **Endpoint:** `POST /create_wall`
- **Body:**
  ```json
  {
    "instance_id": "acad-1",
    "start_point": [0, 0],
    "end_point": [10, 5],
    "thickness": 0.2
  }
  ```
