# Instagram Video Automator

An automated Python and Selenium tool designed to sequentially upload videos to Instagram while safely bypassing strict bot-detection mechanisms via a persistent Chrome profile.

## Features
- **Persistent Sessions**: Caches your login state locally inside a `chrome_profile` directory. You only login once!
- **State Tracking**: Never uploads the same video twice. Maintains a real-time `upload_record.json` of successfully posted media.
- **Automated Captions**: Reads from a structured `captions.json` file to inject specific text per video.
- **Original Crop Ratio**: Selects the original video dimensions dynamically, avoiding Instagram's default 1:1 square crop.

## Requirements

Ensure you have Python 3.10+ installed. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Setup & Configuration

1. **Folder Structure**: Add your `.mp4` or `.mov` files into the `videos/` directory.
2. **Credentials**: Create a `credentials.json` file in the root folder with the following structure:
    ```json
    {
      "username": "YOUR_INSTAGRAM_USERNAME",
      "password": "YOUR_INSTAGRAM_PASSWORD"
    }
    ```
3. **Captions**: Create a `captions.json` file to map your video filenames to captions:
    ```json
    {
      "video(1).mp4": "Hello world! #firstpost",
      "video(2).mp4": "Another one #reels"
    }
    ```

> *Note: `credentials.json`, `captions.json`, and the `videos/` folder are ignored by Git for security.*

## Running the Bot

You can execute the automation in two ways:
- **Using the Terminal**: Run `python main.py`
- **Using the Batch File**: Simply double click `run.bat` (Windows only)

## Disclaimer
This project is for educational purposes. Web automation tools can violate Instagram's Terms of Service. Use responsibly and avoid setting delays too low to mitigate account restrictions.
