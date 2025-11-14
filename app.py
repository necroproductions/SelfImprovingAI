from flask import Flask, render_template, request, jsonify, session
import threading
import os
import time
from monitor import monitor_resources, get_alerts
from reflect import reflect_and_expand, get_current_phase, PENDING_PATCH, PENDING_PATCH_QUERY, process_patch_decision, PENDING_PATCH_TESTS, PENDING_PATCH_TARGET
from core import process_query
from logger import log_change
from phase import advance_phase, PHASES
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
        tests = [("hello", "Hello! How can I help?"), ("sort 5 3 1", [1, 3, 5]), ("add 2 3", 5)]
        log_change("Reflection triggered by web user")

        # Start reflection in a background thread to prevent blocking the web request
        threading.Thread(target=lambda: reflect_and_expand(tests), daemon=True).start()

        response = "Reflection process initiated. Check the 'Patch Proposal' area for results soon."

    elif user_input.lower() == 'advance':
        advance_phase()
        new_phase = get_current_phase()
        response = f"Advanced to Phase {new_phase}. New Goal: {PHASES[new_phase] if new_phase < len(PHASES) else 'Terminal'}"

    else:
        response = process_query(user_input, history)

    # CRITICAL FIX: Record the interaction in history regardless of whether it was a command or a query.
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

@app.route('/phase', methods=['GET'])
def get_phase_status():
    current = get_current_phase()
    phase_detail = PHASES[current] if current < len(PHASES) else 'Terminal'
    return jsonify({'phase': current, 'detail': phase_detail})

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
    print(f"Current Phase: {get_current_phase()} ({PHASES[get_current_phase()]})")
    app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)

