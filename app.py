from flask import Flask, render_template, request, jsonify, session
import threading
import os
import time
from monitor import monitor_resources, get_alerts
from reflect import reflect_and_expand, PENDING_PATCH, PENDING_PATCH_QUERY, process_patch_decision, PENDING_PATCH_TESTS, PENDING_PATCH_TARGET, CONTINUOUS_GOAL # Import the continuous goal for display
from core import process_query
from logger import log_change
# Removed: from phase import advance_phase, get_current_phase, PHASES
from core import process_query

app = Flask(__name__)
app.secret_key = 'self_improving_ai_secret' 

# Start quiet monitoring in background
threading.Thread(target=lambda: monitor_resources(quiet=True), daemon=True).start()

def handle_query(user_input):
    """Wrapper for process_query with history management."""
    history = session.get('conversation_history', [])

    response = ""

    if user_input.lower() == 'reflect':
        # Removed hard-coded tests specific to old phases. Use general tests.
        tests = [("hello", "Hello! How can I help?"), ("sort 5 3 1", [1, 3, 5]), ("add 2 3", 5)]
        log_change("Reflection triggered by web user")

        # Start reflection in a background thread to prevent blocking the web request
        threading.Thread(target=lambda: reflect_and_expand(tests), daemon=True).start()

        response = "Reflection process initiated. Check the 'Patch Proposal' area for results soon."

    elif user_input.lower() == 'advance':
        # Removed phase advancement logic as the system is now continuous.
        response = "The 'advance' command is deprecated. The AI now works continuously towards general intelligence. Use 'reflect' to generate a new idea."

    else:
        response = process_query(user_input, history)

    # Record the interaction in history
    history.append((user_input, response))
    session['conversation_history'] = history

    # Append Alerts (if any)
    alerts = get_alerts()
    if alerts:
        response += f"\n\n[System Alert]: {'; '.join(alerts)}"

    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history', methods=['GET'])
def get_history():
    """Returns the current conversation history from the session."""
    # Only return the most recent 20 entries for performance
    recent_history = session.get('conversation_history', [])[-20:]
    return jsonify({
        'history': [{'user': u, 'ai': a} for u, a in recent_history]
    })

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '').strip()
    if not user_input:
        return jsonify({'error': 'Empty message'})

    response = handle_query(user_input)
    recent_history = session.get('conversation_history', [])[-20:]

    return jsonify({
        'response': response,
        'history': [{'user': u, 'ai': a} for u, a in recent_history]
    })

@app.route('/alerts', methods=['GET'])
def alerts():
    return jsonify({'alerts': get_alerts()})

@app.route('/status', methods=['GET'])
def get_status():
    """Returns the continuous goal status."""
    return jsonify({'goal': CONTINUOUS_GOAL})


@app.route('/patch/proposal', methods=['GET'])
def patch_proposal():
    """Polls for a pending patch proposal."""
    with PENDING_PATCH:
        if PENDING_PATCH_QUERY:
            return jsonify({
                'status': 'pending',
                'query': PENDING_PATCH_QUERY,
                'target': PENDING_PATCH_TARGET,
                'tests_count': len(PENDING_PATCH_TESTS) if PENDING_PATCH_TESTS else 0
            })
        return jsonify({'status': 'none'})

@app.route('/patch/decide', methods=['POST'])
def patch_decide():
    """Accepts the user's decision (approve/reject)."""
    decision = request.json.get('decision', '').lower()

    def run_decision(decision):
        result = process_patch_decision(decision)
        get_alerts().append(result)

    threading.Thread(target=lambda: run_decision(decision), daemon=True).start()

    return jsonify({'message': f'Decision "{decision}" is being processed in the background.'})

if __name__ == '__main__':
    print("Starting web AI interface... Open / in browser.")
    print(f"Continuous Goal: {CONTINUOUS_GOAL}")
    app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)

