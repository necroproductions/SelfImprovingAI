from flask import Flask, render_template, request, jsonify, session
import threading
import os
import time
from monitor import monitor_resources, get_alerts  # CORRECTED IMPORT
from reflect import reflect_and_expand, get_current_phase
from core import process_query
from logger import log_change
from phase import advance_phase
from core import process_query

app = Flask(__name__)
# Using a key to enable sessions, which is crucial for per-user history
app.secret_key = 'self_improving_ai_secret' 

# Start quiet monitoring in background (Daemon thread ensures cleanup on exit)
# Note: The monitor only logs/queues alerts; it doesn't crash the server.
threading.Thread(target=lambda: monitor_resources(quiet=True), daemon=True).start()

def handle_query(user_input):
    """Wrapper for process_query with history management."""
    # Retrieve or initialize conversation history from session
    history = session.get('conversation_history', [])

    # 1. Handle Meta-Commands (Reflect/Advance)
    if user_input.lower() == 'reflect':
        tests = [("hello", "Hello! How can I help?"), ("sort 5 3 1", [1, 3, 5])]
        # The web version must be non-interactive (auto-approve=True not implemented in reflect.py, but mock response)
        log_change("Reflection triggered by web user")
        # Since reflection is complex and non-blocking, we mock a brief confirmation.
        threading.Thread(target=lambda: reflect_and_expand(tests), daemon=True).start()
        return "Reflection triggered in background. Check logs for progress. Phase change may happen soon."

    elif user_input.lower() == 'advance':
        advance_phase()
        new_phase = get_current_phase()
        return f"Advanced to Phase {new_phase} manually. New Goal: {PHASES[new_phase] if new_phase < len(PHASES) else 'Terminal'}"

    # 2. Handle Core Query
    else:
        response = process_query(user_input, history)
        history.append((user_input, response))
        session['conversation_history'] = history  # Save updated history

        # 3. Append Alerts (if any)
        alerts = get_alerts()
        if alerts:
            response += f"\n\n[System Alert]: {'; '.join(alerts)}"
        return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handles user messages and returns AI response."""
    user_input = request.json.get('message', '').strip()
    if not user_input:
        return jsonify({'error': 'Empty message'})

    response = handle_query(user_input)

    # Return history only for the current user's session
    recent_history = session.get('conversation_history', [])[-20:]

    return jsonify({
        'response': response,
        'history': [{'user': u, 'ai': a} for u, a in recent_history]
    })

@app.route('/alerts', methods=['GET'])  # Poll for alerts
def alerts():
    """Returns system alerts for the UI to display."""
    return jsonify({'alerts': get_alerts()})

@app.route('/phase', methods=['GET'])
def get_phase_status():
    """Returns the current phase for UI initialization."""
    from phase import PHASES
    current = get_current_phase()
    phase_detail = PHASES[current] if current < len(PHASES) else 'Terminal'
    return jsonify({'phase': current, 'detail': phase_detail})

if __name__ == '__main__':
    from phase import PHASES
    print("Starting web AI interface... Open / in browser.")
    print(f"Current Phase: {get_current_phase()} ({PHASES[get_current_phase()]})")
    app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False) 

