import time
import threading
import json
import random
from openai import OpenAI
import ctypes
import win32gui
import win32process
import psutil
from datetime import datetime

# Shared global variable to store activity data
global_json_data = {}

# Constants
TRACKING_INTERVAL = 10  # Check every 10 seconds
JSON_UPDATE_INTERVAL = 15  # Update JSON every 15 seconds
JSON_FILE = "categorized_output.json"

# Initialize the OpenAI client
client = OpenAI(
    api_key="API_KEY",  # Replace with your actual API key
    base_url="https://api.deepseek.com"  # Replace with the correct base URL if needed
)

# System prompt to instruct the model
system_prompt = """
Categorize application logs into **Work**, **Private**, **Idle**, and **Uncategorized** based on the following rules:
1. **Categories**:
   - **Work**: Activities related to work (e.g., coding, development, work-related browsing).
   - **Private**: Activities related to personal use (e.g., YouTube, LinkedIn, personal browsing).
   - **Idle**: Non-productive activities, including:
     - System locked or sleep time.
     - Task switching or idle time.
   - **Uncategorized**: Activities that do not fit into the above categories. Only show the total duration.
2. **Structure**:
   - **Work**:
     - Break down by application and window title.
     - For each window title, include all sessions with **start time**, **end time**, and **duration**.
     - Calculate total duration for:
       - Each window title.
       - Each application.
       - The entire **Work** category.
   - **Private** and **Idle**:
     - Only show the **total duration** for each category. Do not break down further.
3. **Output Format**:
   - Provide output **strictly in JSON format**.
   - Do not include any additional text, explanations, or single words in the output.
   - Ensure the JSON is well-structured and easy to read.
4. **Example**:
   - **Input**:
     {
       "application": "chrome.exe",
       "window_title": "DeepSeek - Into the Unknown - Google Chrome",
       "start_time": "14:10:00",
       "end_time": "14:15:00",
       "duration": "00:05:00"
     }
   - **Output**:
     {
       "Work": {
         "total_duration": "~15 minutes 30 seconds",
         "applications": [
           {
             "application": "chrome.exe",
             "total_duration": "~9 minutes",
             "windows": [
               {
                 "window_title": "DeepSeek - Into the Unknown - Google Chrome",
                 "sessions": [
                   {
                     "start_time": "13:23:41",
                     "end_time": "13:23:54",
                     "duration": "121.27 seconds"
                   },
                   {
                     "start_time": "14:10:00",
                     "end_time": "14:15:00",
                     "duration": "300 seconds"
                   }
                 ]
               }
             ]
           }
         ]
       },
       "Private": {
         "total_duration": "~5 minutes"
       },
       "Idle": {
         "total_duration": "~2 minutes"
       }
     }
5. **Rules**:
   - If the system is locked or asleep, categorize the duration under **Idle**.
   - Only provide output in JSON format. Do not include any additional text or explanations.
   - Handle any number of logs efficiently and maintain a consistent JSON structure.
   - Don't write even json at start just only data
"""

# Function to check if the PC is locked
def is_pc_locked():
    try:
        desktop_window = ctypes.windll.user32.GetDesktopWindow()
        if desktop_window == 0:
            return True
        return False
    except Exception as e:
        print(f"Error checking lock status: {e}")
        return False

# Function to get the active window title
def get_active_window_title():
    hwnd = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(hwnd)

# Function to get the application name
def get_application_name(hwnd):
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if not pid:
            return "Unknown"
        process = psutil.Process(pid)
        return process.name()
    except Exception as e:
        print(f"Error getting application name: {e}")
        return "Unknown"

# Function to format duration
def format_duration(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

# Function to format timestamp
def format_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")

# Function to track user activity
def track_activity():
    global global_json_data
    previous_title = None
    previous_application_name = None
    start_time = time.time()
    is_locked = False
    lock_start_time = None
    activity_data = {}

    while True:
        try:
            if is_pc_locked():
                if not is_locked:
                    lock_start_time = time.time()
                    is_locked = True
                    print("PC locked.")
                time.sleep(TRACKING_INTERVAL)
                continue
            elif is_locked:
                lock_duration = time.time() - lock_start_time
                print(f"PC unlocked. Locked duration: {lock_duration:.2f} seconds")
                is_locked = False

            hwnd = win32gui.GetForegroundWindow()
            current_title = get_active_window_title()
            current_application_name = get_application_name(hwnd)

            if not current_title or not current_application_name:
                time.sleep(TRACKING_INTERVAL)
                continue

            if current_title != previous_title or current_application_name != previous_application_name:
                end_time = time.time()
                if previous_title and previous_application_name:
                    duration = end_time - start_time
                    key = f"{previous_application_name} - {previous_title}"

                    if key not in activity_data:
                        activity_data[key] = []
                    elif isinstance(activity_data[key], dict):
                        activity_data[key] = [activity_data[key]]

                    activity_data[key].append({
                        "window_title": previous_title,
                        "start_time": format_timestamp(start_time),
                        "end_time": format_timestamp(end_time),
                        "duration": format_duration(duration)
                    })

                previous_title = current_title
                previous_application_name = current_application_name
                start_time = time.time()

            if time.time() - start_time >= JSON_UPDATE_INTERVAL:
                global_json_data = activity_data
                start_time = time.time()

            time.sleep(TRACKING_INTERVAL)
        except Exception as e:
            print(f"Error in tracking loop: {e}")

# Function to categorize activity
def categorize_activity():
    while True:
        try:
            latest_data = global_json_data
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(latest_data)}
                ]
            )
            categorized_json = response.choices[0].message.content

            with open(JSON_FILE, "w", encoding="utf-8") as output_file:
                output_file.write(categorized_json)

            print(f"Categorized JSON data has been saved to {JSON_FILE}")
            time.sleep(JSON_UPDATE_INTERVAL)
        except Exception as e:
            print(f"Error during categorization: {e}")
            time.sleep(JSON_UPDATE_INTERVAL)

# Main function
def main():
    print("Starting activity tracker and categorizer... Press Ctrl+C to stop.")

    # Create threads for tracking and categorization
    tracking_thread = threading.Thread(target=track_activity)
    categorization_thread = threading.Thread(target=categorize_activity)

    # Start the threads
    tracking_thread.start()
    categorization_thread.start()

    # Wait for threads to finish
    tracking_thread.join()
    categorization_thread.join()

if __name__ == "__main__":
    main()