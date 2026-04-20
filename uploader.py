import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class InstagramUploader:
    def __init__(self, profile_dir="chrome_profile"):
        self.profile_dir = os.path.abspath(profile_dir)
        
        options = Options()
        # persistent profile using user-data-dir
        options.add_argument(f"user-data-dir={self.profile_dir}")
        options.add_argument("--disable-notifications")
        options.add_argument("--start-maximized")
        # Removing automation flags to bypass some bot detections
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        # Keep the browser open after the python script finishes
        options.add_experimental_option("detach", True)
        
        print("Initializing ChromeDriver...")
        # Selenium 4.6+ has built-in Selenium Manager to handle drivers automatically
        self.driver = webdriver.Chrome(options=options)
        # Increased wait to 60 seconds because video uploads can take a while
        self.wait = WebDriverWait(self.driver, 60)
        self.short_wait = WebDriverWait(self.driver, 5)

    def login(self, username, password):
        print("Navigating to Instagram...")
        self.driver.get('https://www.instagram.com/')
        time.sleep(5) # Let basic page structure load
        
        # Check if already logged in by looking for the absolute login fields
        try:
            username_xpath = "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div[1]/div/div[3]/div/div/div/div/div/div/div/div/div[2]/form/div/div[1]/div/div[1]/div/div/div[1]/input"
            password_xpath = "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div[1]/div/div[3]/div/div/div/div/div/div/div/div/div[2]/form/div/div[1]/div/div[2]/div/div/div[1]/input"
            login_btn_xpath = "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div[1]/div/div[3]/div/div/div/div/div/div/div/div/div[2]/form/div/div[1]/div/div[3]/div/div/div/div[1]/div/span/span"
            
            # We use a slight wait, if it fails, we drop to except and assume logged in
            self.short_wait.until(EC.presence_of_element_located((By.XPATH, username_xpath)))
            print("Login fields found via absolute XPath. Attempting to log in...")
            
            # Find inputs
            username_input = self.driver.find_element(By.XPATH, username_xpath)
            password_input = self.driver.find_element(By.XPATH, password_xpath)
            
            # Send keys
            username_input.send_keys(username)
            password_input.send_keys(password)
            
            # Submit
            submit_btn = self.driver.find_element(By.XPATH, login_btn_xpath)
            time.sleep(1)
            submit_btn.click()
            
            print("Login submitted. Waiting for authentication...")
            time.sleep(10)
            
            # Handle "Save your login info" dialog if it pops up
            try:
                save_info_btn = self.short_wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Save info' or text()='Save Info']")))
                save_info_btn.click()
                print("Clicked 'Save info'")
                time.sleep(3)
            except:
                pass
            
            # Handle "Turn on Notifications" dialog
            try:
                not_now_btn = self.short_wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Not Now' or text()='Not now']")))
                not_now_btn.click()
                print("Dismissed Notification prompt")
                time.sleep(2)
            except:
                pass
                
        except Exception:
            print("No login fields found. Assuming already logged in from saved session (persistent profile).")

    def upload_video(self, video_path, caption):
        video_name = os.path.basename(video_path)
        print(f"\n--- Starting upload process for {video_name} ---")
        
        self.driver.get("https://www.instagram.com/")
        time.sleep(3) # Faster load
        
        try:
            # Click "Create" SVG icon on the sidebar
            print("Clicking 'Create'...")
            # Using the new div XPath provided by the User 
            create_btn_xpath = "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/div/div/div/div/div/div[2]/div/div[7]/div/span/div/a/div"
            create_btn = self.wait.until(EC.presence_of_element_located((By.XPATH, create_btn_xpath)))
            self.driver.execute_script("arguments[0].click();", create_btn)
            time.sleep(1)
            
            # If multiple options present (e.g. Post, Reel), click "Post"
            try:
                post_option = self.short_wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Post']")))
                post_option.click()
                time.sleep(2)
            except:
                pass
            
            # Send file to hidden input to bypass OS dialog
            print("Injecting file path...")
            file_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
            file_input.send_keys(os.path.abspath(video_path))
            
            # Wait for file processing (takes longer for videos)
            print("Processing video file... (this may take a few seconds)")
            time.sleep(5)
            
            # Handle possible crop warning (OK got it button)
            try:
                ok_btn = self.short_wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'OK')]")))
                ok_btn.click()
                time.sleep(2)
            except:
                pass

            # Crop to original size
            try:
                print("Setting crop to 'Original' size...")
                
                # 1. Try to find the button using the User's path but stripping the inner SVG/div to hit the button directly
                crop_btn_xpath = "/html/body/div[5]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[2]/div[1]/div/div/div/div/div[1]/div/div[2]/div/button"
                
                try:
                    crop_btn = self.short_wait.until(EC.element_to_be_clickable((By.XPATH, crop_btn_xpath)))
                except:
                    # Fallback generic xpath for the crop aspect ratio button on IG
                    print("Falling back to generic crop button locator...")
                    crop_btn = self.short_wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//svg[@aria-label='Select crop' or @aria-label='Crop']] | //button[@aria-label='Select crop']")))
                
                self.driver.execute_script("arguments[0].click();", crop_btn)
                time.sleep(2)
                
                original_crop_xpath = "/html/body/div[5]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[2]/div[1]/div/div/div/div/div[1]/div/div[1]/div/div[1]/div/div[1]/span"
                try:
                    original_crop_btn = self.short_wait.until(EC.presence_of_element_located((By.XPATH, original_crop_xpath)))
                except:
                    # Fallback generic xpath for the 'Original' crop option
                    print("Falling back to generic original crop locator...")
                    original_crop_btn = self.short_wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='Original'] | //div[text()='Original']")))

                self.driver.execute_script("arguments[0].click();", original_crop_btn)
                time.sleep(1)
                print("Successfully clicked original crop option.")
            except Exception as e:
                print(f"[Warning] Could not set to original crop size: {e}")

            # Click 'Next' (Crop Step -> Edit Step)
            print("Clicking 'Next' (1/2)...")
            next_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and (text()='Next' or text()='Next ')]")))
            next_btn.click()
            time.sleep(1)
            
            # Click 'Next' again (Edit Step -> Details Step)
            print("Clicking 'Next' (2/2)...")
            next_btn_2 = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and (text()='Next' or text()='Next ')]")))
            next_btn_2.click()
            time.sleep(1)
            
            # Enter Caption
            print("Entering caption...")
            caption_area = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Write a caption...']")))
            caption_area.send_keys(caption)
            time.sleep(1)
            
            # Click Share
            print("Clicking 'Share'...")
            share_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and (text()='Share' or text()='Share ')]")))
            share_btn.click()
            
            # Wait for completion checking for text like "Your post has been shared."
            print("Waiting for upload to finish...")
            self.wait.until(EC.presence_of_element_located((
                By.XPATH, "//*[contains(text(), 'Your post has been shared') or contains(text(), 'Your reel has been shared')]"
            )))
            print(f"✅ Success! {video_name} shared successfully.")
            time.sleep(2)
            
            # Close the modal to cleanly loop to the next one
            try:
                close_svg = self.driver.find_element(By.CSS_SELECTOR, "svg[aria-label='Close']")
                self.driver.execute_script("arguments[0].click();", close_svg)
                time.sleep(1)
            except:
                pass

            return True
            
        except Exception as e:
            print(f"❌ Error during upload of {video_name}: {str(e)}")
            # Keep screenshot for debugging
            self.driver.save_screenshot(f"error_{video_name}.png")
            return False

    def close(self):
        self.driver.quit()
