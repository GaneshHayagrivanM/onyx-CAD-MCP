from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "AutoCAD MCP Server is running."})

# In-memory store for AutoCAD connections
autocad_connections = {}

@app.route('/connect_to_autocad', methods=['POST'])
def connect_to_autocad():
    """
    Establishes a simulated connection to an AutoCAD instance.
    """
    data = request.get_json()
    instance_id = data.get('instance_id')
    if not instance_id:
        return jsonify({"error": "instance_id is required"}), 400

    # Simulate connection
    autocad_connections[instance_id] = {"status": "connected"}

    return jsonify({
        "message": f"Successfully connected to AutoCAD instance {instance_id}",
        "instance_id": instance_id
    })

@app.route('/execute_lisp', methods=['POST'])
def execute_lisp():
    """
    Executes an AutoLISP code string on a connected AutoCAD instance.
    """
    data = request.get_json()
    instance_id = data.get('instance_id')
    lisp_code = data.get('lisp_code')

    if not instance_id or not lisp_code:
        return jsonify({"error": "instance_id and lisp_code are required"}), 400

    if instance_id not in autocad_connections:
        return jsonify({"error": f"AutoCAD instance {instance_id} not connected"}), 404

    # Simulate executing LISP code
    print(f"Executing LISP on instance {instance_id}: {lisp_code}")

    return jsonify({
        "message": "LISP code executed successfully",
        "instance_id": instance_id,
        "executed_code": lisp_code
    })

@app.route('/create_wall', methods=['POST'])
def create_wall():
    """
    Creates a wall in AutoCAD by generating and executing AutoLISP code.
    """
    data = request.get_json()
    instance_id = data.get('instance_id')
    start_point = data.get('start_point')
    end_point = data.get('end_point')
    thickness = data.get('thickness')

    if not all([instance_id, start_point, end_point, thickness]):
        return jsonify({"error": "instance_id, start_point, end_point, and thickness are required"}), 400

    if instance_id not in autocad_connections:
        return jsonify({"error": f"AutoCAD instance {instance_id} not connected"}), 404

    # Generate AutoLISP code for creating a wall (as a polyline)
    lisp_code = f'(command "_PLINE" "{start_point[0]},{start_point[1]}" "W" "{thickness}" "{thickness}" "{end_point[0]},{end_point[1]}" "")'

    # Simulate executing LISP code
    print(f"Executing LISP on instance {instance_id}: {lisp_code}")

    return jsonify({
        "message": "Wall created successfully",
        "instance_id": instance_id,
        "lisp_code": lisp_code
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
