import os
import subprocess
from datetime import datetime, timedelta
import time
import requests
import logging
import json
import shutil

# Load configuration parameters
config_file = 'config.json'

def load_config():
    with open(config_file, 'r') as file:
        return json.load(file)

config = load_config()
streamer_name = config["streamer_name"]
stream_url = f"https://www.twitch.tv/{streamer_name}"
output_directory = config["output_directory"]
quality = config["quality"]
webhook_url = config["webhook_url"]
max_recording_duration = timedelta(hours=config["max_recording_duration_hours"])
disk_space_threshold = config["disk_space_threshold_gb"]

# Create the output directory if it does not exist
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Configure logging
logging.basicConfig(
    filename='stream_recorder.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

# Generate the filename based on the current date and time
def get_output_file():
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    date_directory = datetime.now().strftime("%Y-%m-%d")
    full_output_directory = os.path.join(output_directory, date_directory)
    if not os.path.exists(full_output_directory):
        os.makedirs(full_output_directory)
    return os.path.join(full_output_directory, f"{current_time}.mp4")

# Define the command to record the stream with Streamlink
def get_streamlink_command(output_file):
    return [
        "streamlink",
        "--twitch-disable-ads",
        "--twitch-low-latency",
        stream_url,
        quality,
        "-o",
        output_file
    ]

# Function to start recording
def start_recording():
    output_file = get_output_file()
    streamlink_command = get_streamlink_command(output_file)
    start_time = datetime.now()
    try:
        send_discord_notification(f"Recording started for {stream_url} at quality {quality}.")
        logging.info(f"Start recording: {stream_url} at quality {quality}")
        subprocess.run(streamlink_command, check=True)
        end_time = datetime.now()
        duration = end_time - start_time
        file_size = os.path.getsize(output_file)
        logging.info(f"Recording saved to: {output_file}")
        send_discord_notification(f"Recording stopped. File saved to: {output_file}\nDuration: {duration}\nFile size: {file_size / (1024 * 1024):.2f} MB")
        return duration, file_size
    except subprocess.CalledProcessError as e:
        logging.error(f"An error occurred: {e}")
        send_discord_notification(f"An error occurred while recording: {e}")
        return None, None

# Function to check if the stream is online
def is_stream_online():
    try:
        result = subprocess.run(["streamlink", "--stream-url", stream_url, quality], capture_output=True, text=True)
        return result.returncode == 0 and result.stdout.strip() != ''
    except subprocess.CalledProcessError:
        return False

# Function to send a notification to Discord
def send_discord_notification(message, webhook_url=webhook_url):
    payload = {"content": message}
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code != 204:
            logging.warning(f"Failed to send notification. Status code: {response.status_code}")
    except Exception as e:
        logging.error(f"Error sending notification: {e}")

# Function to generate the status message
def generate_status_message(stream_online, recording):
    status = "online" if stream_online else "offline"
    recording_status = "recording" if recording else "not recording"
    return f"Stream is {status}. Recording is {recording_status}."

# Function to check free disk space
def check_disk_space():
    total, used, free = shutil.disk_usage(output_directory)
    free_gb = free / (1024 ** 3)
    if free_gb < disk_space_threshold:
        send_discord_notification(f"Warning: Low disk space. Only {free_gb:.2f} GB left.")
        logging.warning(f"Low disk space. Only {free_gb:.2f} GB left.")
    return free_gb >= disk_space_threshold

# Function to delete old recordings
def delete_old_recordings(days_old=300):
    now = time.time()
    for root, dirs, files in os.walk(output_directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            if os.stat(file_path).st_mtime < now - days_old * 86400:
                os.remove(file_path)
                logging.info(f"Deleted old recording: {file_path}")
                send_discord_notification(f"Deleted old recording: {file_path}")

# Function to check and manage recording
def check_and_record():
    recording = False
    recording_start_time = None
    last_notification_time = time.time()

    while True:
        if not check_disk_space():
            send_discord_notification("Recording stopped due to low disk space.")
            logging.error("Recording stopped due to low disk space.")
            break

        delete_old_recordings(days_old=300)

        stream_online = is_stream_online()

        if stream_online:
            if not recording:
                recording_start_time = datetime.now()
                recording = True
                start_recording()
        else:
            if recording:
                recording = False
                duration, file_size = start_recording()  # End the current recording
                if duration and file_size:
                    send_discord_notification(f"Stream is offline. Recording stopped. Duration: {duration}, File size: {file_size / (1024 * 1024):.2f} MB.")
                    logging.info(f"Stream is offline. Recording stopped. Duration: {duration}, File size: {file_size / (1024 * 1024):.2f} MB.")

        if recording and datetime.now() - recording_start_time > max_recording_duration:
            recording = False
            duration, file_size = start_recording()  # End the current recording
            if duration and file_size:
                send_discord_notification(f"Maximum recording duration reached. Recording stopped. Duration: {duration}, File size: {file_size / (1024 * 1024):.2f} MB.")
                logging.info(f"Maximum recording duration reached. Recording stopped. Duration: {duration}, File size: {file_size / (1024 * 1024):.2f} MB.")

        current_time = time.time()
        if current_time - last_notification_time >= 3600:  # Hourly status update
            status_message = generate_status_message(stream_online, recording)
            send_discord_notification(f"Status Update: {status_message}")
            last_notification_time = current_time

        time.sleep(1)  # Check every second

# Start checking and recording
if __name__ == "__main__":
    check_and_record()
