from flask import Flask, request, jsonify
import os
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import time
import threading
import json
import uuid
import logging

# =======================
# Configuration and Setup
# =======================

app = Flask(__name__)
CORS(app)

# Path to the sequences JSON file
SEQUENCES_FILE = 'sequences.json'

# Lock for thread-safe operations
lock = threading.Lock()

# Global variables to track status and ongoing sequence
current_status = {
    "last_rgbw": None,           # Last sent RGBW value
    "sequence_ongoing": False,  # Is a sequence currently running
    "current_sequence_id": None  # ID of the ongoing sequence
}

# Event to signal sequence interruption
interrupt_event = threading.Event()

# Configure logging
logging.basicConfig(
    filename='flask_server.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# =====================
# Utility Functions
# =====================

def load_sequences():
    """Load sequences from the JSON file."""
    if not os.path.exists(SEQUENCES_FILE):
        with open(SEQUENCES_FILE, 'w') as f:
            json.dump({"sequences": []}, f, indent=4)
        logging.info("Created new sequences.json file.")
    with open(SEQUENCES_FILE, 'r') as f:
        try:
            data = json.load(f)
            logging.info("Loaded sequences from sequences.json.")
            return data
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON: {e}")
            return {"sequences": []}

def save_sequences(data):
    """Save sequences to the JSON file."""
    with open(SEQUENCES_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    logging.info("Saved sequences to sequences.json.")

def is_valid_rgbw(rgbw):
    """
    Validate that RGBW values are present and are 15-bit integers.
    :param rgbw: Dictionary with keys 'R', 'G', 'B', 'W'
    :return: Boolean indicating validity
    """
    required_keys = {'R', 'G', 'B', 'W'}
    if not isinstance(rgbw, dict):
        return False
    if not required_keys.issubset(rgbw.keys()):
        return False
    try:
        return all(0 <= int(rgbw[key]) <= 32767 for key in required_keys)
    except (ValueError, TypeError):
        return False

def send_rgbw_command(rgbw):
    """
    Send RGBW values to the device.
    Format: 'R G B W\n' where R, G, B, W are 15-bit integers.
    :param rgbw: Dictionary with keys 'R', 'G', 'B', 'W'
    """
    cmd = f"{rgbw['R']} {rgbw['G']} {rgbw['B']} {rgbw['W']}\n"
    try:
        os.system(f'echo "{cmd}" | nc bedroom0.local 1234')
        logging.info(f"Sent RGBW command: {cmd.strip()}")
        # Update the status
        with lock:
            current_status['last_rgbw'] = rgbw
    except Exception as e:
        logging.error(f"Failed to send RGBW command: {e}")

def interrupt_sequence():
    """
    Interrupt any ongoing sequence.
    """
    if current_status['sequence_ongoing']:
        logging.info(f"Interrupting sequence {current_status['current_sequence_id']}.")
        inter
