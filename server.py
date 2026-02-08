# server.py
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import time
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store connected agents
agents = {}

@app.route('/')
def home():
    return "Agent Server is Running!"

# Agent registers itself
@app.route('/register', methods=['POST'])
def register_agent():
    data = request.json
    agent_id = data.get('agent_id')
    ip = request.remote_addr
    
    agents[agent_id] = {
        'last_seen': time.time(),
        'ip': ip,
        'status': 'online',
        'data': data.get('data', {})
    }
    
    print(f"Agent registered: {agent_id}")
    return jsonify({"status": "registered", "agent_id": agent_id})

# Get list of all online agents
@app.route('/agents', methods=['GET'])
def get_agents():
    # Clean old agents (not seen for 30 seconds)
    current_time = time.time()
    to_delete = []
    for agent_id, info in agents.items():
        if current_time - info['last_seen'] > 30:
            to_delete.append(agent_id)
    
    for agent_id in to_delete:
        del agents[agent_id]
    
    return jsonify({
        "count": len(agents),
        "agents": agents
    })

# Agent sends heartbeat
@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    agent_id = request.json.get('agent_id')
    if agent_id in agents:
        agents[agent_id]['last_seen'] = time.time()
        return jsonify({"status": "updated"})
    return jsonify({"error": "agent not found"}), 404

# SocketIO for real-time communication
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('message')
def handle_message(msg):
    print('Message:', msg)
    emit('response', {'data': 'Message received'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
