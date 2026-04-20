import os
import json
import time
from uploader import InstagramUploader

VIDEOS_DIR = "videos"
CREDENTIALS_FILE = "credentials.json"
CAPTIONS_FILE = "captions.json"
RECORDS_FILE = "upload_record.json"

def load_json(filepath, default_value=[]):
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
    print("--- Instagram Video Automator ---\n")
    
    # 1. Setup Phase
    new_setup = False
    
    if not os.path.exists(VIDEOS_DIR) or not os.path.isdir(VIDEOS_DIR):
        os.makedirs(VIDEOS_DIR, exist_ok=True)
        new_setup = True
        
    if not os.path.exists(CREDENTIALS_FILE):
        save_json(CREDENTIALS_FILE, {"username": "YOUR_INSTAGRAM_USERNAME", "password": "YOUR_INSTAGRAM_PASSWORD"})
        new_setup = True
        
    if not os.path.exists(CAPTIONS_FILE):
        save_json(CAPTIONS_FILE, {"video(1).mp4": "Your caption here #reels", "video(2).mp4": "Another caption"})
        new_setup = True
        
    if not os.path.exists(RECORDS_FILE):
        save_json(RECORDS_FILE, [])

    if new_setup:
        print("====== INITIAL SETUP REQUIRED ======")
        print("It looks like you're running this for the first time (or missing core files)!")
        print("I have automatically generated the following templates for you:")
        print(f"  1. A folder named '{VIDEOS_DIR}/'")
        print(f"  2. {CREDENTIALS_FILE}")
        print(f"  3. {CAPTIONS_FILE}")
        print("\n--- INSTRUCTIONS ---")
        print(f"[A] Put your videos inside the '{VIDEOS_DIR}/' folder. Name them clearly, e.g., 'video(1).mp4'.")
        print(f"[B] Open '{CAPTIONS_FILE}' and map your exact video filenames to their desired captions.")
        print(f"[C] Open '{CREDENTIALS_FILE}' and input your Instagram login details.")
        print("\nOnce you have filled these out, run the script (or double-click run.bat) again to start uploading!")
        print("====================================")
        return
    
    video_files = [f for f in os.listdir(VIDEOS_DIR) if f.lower().endswith(('.mp4', '.mov'))]
    
    if not video_files:
        print(f"[INFO] No video files found in the '{VIDEOS_DIR}' folder.")
        print("Please add your videos (e.g., video(1).mp4) to the folder and run again.")
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
