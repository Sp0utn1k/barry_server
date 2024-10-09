from flask import Blueprint, request, jsonify
import socket
import logging
from .models import Alarm, Sequence
from .utils import schedule_alarm
from flask import current_app

bp = Blueprint('routes', __name__)

# Endpoint to receive RGBW values
@bp.route('/set_rgbw', methods=['POST'])
def set_rgbw():
    data = request.get_json()
    try:
        R = int(data['R'])
        G = int(data['G'])
        B = int(data['B'])
        W = int(data['W'])
        rgbw_string = f"{R} {G} {B} {W}\n"
        
        # Send to bedroom0.local:1234
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('bedroom0.local', 1234))
            s.sendall(rgbw_string.encode())
        
        # Interrupt any ongoing sequence
        # (Implement interruption logic as needed)
        
        current_app.logger.info(f"Set RGBW to: {rgbw_string.strip()}")
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        current_app.logger.error(f"Error setting RGBW: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

# Endpoint to create an alarm
@bp.route('/create_alarm', methods=['POST'])
def create_alarm():
    data = request.get_json()
    try:
        alarm = Alarm.from_dict(data)
        alarm.save()
        schedule_alarm(alarm)
        current_app.logger.info(f"Created alarm: {alarm}")
        return jsonify({'status': 'success', 'alarm_id': alarm.id}), 201
    except Exception as e:
        current_app.logger.error(f"Error creating alarm: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

# Additional endpoints for managing sequences, alarms, etc.
