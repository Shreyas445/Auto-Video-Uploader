import os
import json
import time
from uploader import InstagramUploader

VIDEOS_DIR = "videos"
CREDENTIALS_FILE = "credentials.json"
CAPTIONS_FILE = "captions.json"
RECORDS_FILE = "upload_record.json"

def load_json(filepath, default_value):
    if not os.path.exists(filepath):
        # Create it with default value if missing
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(default_value, f, indent=2)
        return default_value
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return default_value

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def main():
    print("--- Instagram Video Automator ---")
    
    # 1. Check videos directory
    if not os.path.exists(VIDEOS_DIR) or not os.path.isdir(VIDEOS_DIR):
        print(f"Creating missing directory: {VIDEOS_DIR}")
        os.makedirs(VIDEOS_DIR, exist_ok=True)
    
    video_files = [f for f in os.listdir(VIDEOS_DIR) if f.lower().endswith(('.mp4', '.mov'))]
    
    if not video_files:
        print(f"\n[INFO] No video files found in the '{VIDEOS_DIR}' folder.")
        print('Please add your videos (e.g., video(1).mp4) to the folder and try again.')
        return

    # 2. Load configs
    credentials = load_json(CREDENTIALS_FILE, {"username": "", "password": ""})
    captions = load_json(CAPTIONS_FILE, {})
    upload_records = load_json(RECORDS_FILE, [])

    if not credentials.get("username") or credentials["username"] == "YOUR_INSTAGRAM_USERNAME":
        print(f"\n[WARNING] Please configure your Instagram login details in {CREDENTIALS_FILE}.")
        # Proceeding anyway as they might use the persistent profile if already logged in earlier

    # 3. Determine pending videos
    pending_videos = []
    for v in video_files:
        if v not in upload_records:
            pending_videos.append(v)
            
    if not pending_videos:
        print("\nAll videos in the folder have already been uploaded! Exiting.")
        return
        
    print(f"\nFound {len(pending_videos)} videos to upload.\n")
    
    # 4. Initialize Uploader
    uploader = InstagramUploader(profile_dir="chrome_profile")
    
    try:
        # Perform (or skip) login using credentials
        uploader.login(credentials.get("username", ""), credentials.get("password", ""))
        
        # 5. Upload loop
        for file_name in pending_videos:
            file_path = os.path.join(VIDEOS_DIR, file_name)
            
            # Fetch caption, default to empty string if not found
            caption = captions.get(file_name, "")
            if not caption:
                print(f"[NOTE] No caption found for '{file_name}' in {CAPTIONS_FILE}. Uploading without caption.")

            # Attempt upload
            success = uploader.upload_video(file_path, caption)
            
            if success:
                # Update records and save to JSON immediately
                upload_records.append(file_name)
                save_json(RECORDS_FILE, upload_records)
            else:
                print(f"Stopping execution due to an error uploading {file_name}.")
                break
                
            # Sleep between multiple uploads to avoid rate limits
            if file_name != pending_videos[-1]:
                wait_time = 10
                print(f"Waiting {wait_time} seconds before the next upload to prevent bot tagging...")
                time.sleep(wait_time)
                
    finally:
        print("Leaving browser open as requested...")
        # uploader.close()
        
    print("\nAutomation run completed!")

if __name__ == "__main__":
    main()
