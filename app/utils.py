from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import socket
from .models import Sequence
from flask import current_app
import time

scheduler = BackgroundScheduler()

def schedule_alarm(alarm):
    # Parse alarm time
    alarm_time = datetime.strptime(alarm.time, '%H:%M')  # Adjust format as needed
    now = datetime.now()
    first_run = now.replace(hour=alarm_time.hour, minute=alarm_time.minute, second=0, microsecond=0)
    if first_run < now:
        first_run += timedelta(days=1)

    scheduler.add_job(
        func=run_sequence,
        trigger='date',
        run_date=first_run,
        args=[alarm],
        id=alarm.id,
        replace_existing=True
    )
    current_app.logger.info(f"Scheduled alarm {alarm.id} at {first_run}")

def run_sequence(alarm):
    sequence = get_sequence_by_id(alarm.sequence_id)
    if not sequence:
        current_app.logger.error(f"Sequence {alarm.sequence_id} not found.")
        return

    # Implement the sequence running logic
    try:
        for waypoint in sequence.waypoints:
            rgbw_string = f"{waypoint['R']} {waypoint['G']} {waypoint['B']} {waypoint['W']}\n"
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('bedroom0.local', 1234))
                s.sendall(rgbw_string.encode())
            current_app.logger.info(f"Sent RGBW: {rgbw_string.strip()}")
            time.sleep(2)  # Adjust the interval as needed
        # Handle repeat if necessary
    except Exception as e:
        current_app.logger.error(f"Error running sequence: {e}")

def get_sequence_by_id(sequence_id):
    from .models import Sequence
    return session.query(Sequence).filter_by(id=sequence_id).first()
