from flask import Flask, request, jsonify
import time

app = Flask(__name__)
agents = {}

@app.route('/')
def home():
    return "Agent Server is Running!"

@app.route('/register', methods=['POST'])
def register_agent():
    data = request.json
    agent_id = data.get('agent_id')
    
    agents[agent_id] = {
        'last_seen': time.time(),
        'ip': request.remote_addr,
        'status': 'online',
        'data': data.get('data', {})
    }
    
    print(f"Agent registered: {agent_id}")
    return jsonify({"status": "registered", "agent_id": agent_id})

@app.route('/agents', methods=['GET'])
def get_agents():
    current_time = time.time()
    to_delete = []
    
    for agent_id, info in agents.items():
        if current_time - info['last_seen'] > 30:
            to_delete.append(agent_id)
    
    for agent_id in to_delete:
        del agents[agent_id]
    
    return jsonify({"count": len(agents), "agents": agents})

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    agent_id = request.json.get('agent_id')
    if agent_id in agents:
        agents[agent_id]['last_seen'] = time.time()
        return jsonify({"status": "updated"})
    return jsonify({"error": "agent not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
