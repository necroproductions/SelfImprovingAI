# app.py: Flask web interface for self-improving AI (with output redirection)
from flask import Flask, render_template, request, jsonify, session
import threading
import os
from monitor import monitor_resources, get_alerts  # Updated for queue
from reflect import reflect_and_expand, get_current_phase
from core import process_query
from logger import log_change
from phase import advance_phase  # Direct import for simplicity

app = Flask(__name__)
app.secret_key = 'self_improving_ai_secret'  # For session history

# Global history (shared across sessions for simplicity; use DB later)
conversation_history = []

# Start quiet monitoring in background
threading.Thread(target=lambda: monitor_resources(quiet=True), daemon=True).start()

def handle_query(user_input):
    """Wrapper for process_query with history. Returns str or list for web."""
    if user_input.lower() == 'reflect':
        tests = [("hello", "Hello! How can I help?"), ("sort 5 3 1", [1, 3, 5])]
        output_lines = reflect_and_expand(tests, auto_approve=True)  # Auto for web
        # Flatten multi-line to single response (or split in JS)
        return "\n".join(output_lines)
    elif user_input.lower() == 'advance':
        advance_phase()
        return f"Advanced to Phase {get_current_phase()} manually."
    else:
        response = process_query(user_input, conversation_history)
        conversation_history.append((user_input, response))
        # Check for alerts and append
        alerts = get_alerts()
        if alerts:
            response += f"\n\n[System Alert]: {'; '.join(alerts)}"
        return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '').strip()
    if not user_input:
        return jsonify({'error': 'Empty message'})

    response = handle_query(user_input)
    # Keep history to last 20 for UI
    recent_history = conversation_history[-20:]

    return jsonify({
        'response': response,
        'history': [{'user': u, 'ai': a} for u, a in recent_history]
    })

@app.route('/alerts', methods=['GET'])  # Poll for alerts
def alerts():
    alerts = get_alerts()
    return jsonify({'alerts': alerts})

if __name__ == '__main__':
    print("Starting web AI interface... Open / in browser.")
    print(f"Current Phase: {get_current_phase()}")
    app.run(host='0.0.0.0', port=8080, debug=True)  # Replit-friendly