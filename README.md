# Stream Archiver

`stream-archiver` is a Python application designed to record live streams from Twitch using Streamlink. It monitors the stream status, manages disk space, and sends notifications to a Discord channel when recordings start, stop, or when there are issues.

## Features

- Records Twitch streams at a specified quality.
- Creates timestamped recordings with organized directories by date.
- Sends notifications to Discord about recording status, errors, and disk space warnings.
- Automatically deletes old recordings to manage disk space.
- Configurable maximum recording duration and disk space threshold.

## Prerequisites

Before using `stream-archiver`, ensure that you have the following installed:

- **Python 3.6+**: [Download Python](https://www.python.org/downloads/)
- **Streamlink**: [Installation instructions](https://streamlink.github.io/install.html)
- **Requests library**: Install via `pip install requests`

## Installation

1. **Clone the Repository**

   ```sh
   git clone https://github.com/Wasserpuncher/stream-archiver.git
   cd stream-archiver

## Install Dependencies

Install the required Python packages using pip:

```sh
pip install requests
pip install streamlink
```

## Configure the Application

Create a config.json file in the root directory of the repository with the following structure:

```sh
{
    "streamer_name": "example_streamer",
    "output_directory": "./recordings",
    "quality": "best",
    "webhook_url": "https://discord.com/api/webhooks/your-webhook-id",
    "max_recording_duration_hours": 1,
    "disk_space_threshold_gb": 5
}
```

### streamer_name: The Twitch username of the streamer to record.
### output_directory: Directory where recordings will be saved.
### quality: The quality setting for Streamlink (e.g., "best", "720p").
### webhook_url: Your Discord webhook URL for notifications.
### max_recording_duration_hours: Maximum duration (in hours) for each recording.
### disk_space_threshold_gb: Minimum free disk space (in GB) before stopping recordings.

## Usage

Run the application using Python:

```sh
python stream-archiver.py
```

## The script will continuously monitor the specified Twitch stream and start recording when the stream is online. It will handle disk space management, delete old recordings, and send status updates to your Discord webhook.

## Logging
Logs are saved in stream_recorder.log. This file will contain information about recording events, errors, and disk space warnings.

## Contributing
Feel free to submit issues, feature requests, or pull requests. Contributions are welcome!

## License
This project is licensed under the MIT License - see the LICENSE file for details.

