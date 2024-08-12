import os
import re
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime, timedelta
import json
import youtube_uploader
import X_uploader
import concurrent.futures
import logging
import instagram_uploader
import hashtag_gen

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_json_line(index, politic, custom = False, filename='news_info_to_render'):
    if custom:
        filepath = os.path.join('politics', politic, filename, f'{politic}_custom.json')
    else:
        filepath = os.path.join('politics', politic, filename, f'{politic}.json')  

    # Check if the file exists
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File {filepath} does not exist.")
    
    # Read and load the JSON data
    with open(filepath, 'r') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            raise ValueError(f"File {filepath} is not a valid JSON or is empty.")
    
    # Check if the data is a list
    if not isinstance(data, list):
        raise TypeError("JSON data is not a list. Please provide a file with a list of items.")
    
    # Ensure the index is within the valid range
    if not (0 <= index < len(data)):
        raise IndexError(f"Index {index} is out of range. The JSON list has {len(data)} items.")
    
    # Return the item at the specified index
    return data[index]

def video_uploader(filename, index, politic, custom = False):
    filepath = 'final_videos/' + filename
    title = 'Daily News'
    extra_message = 'Find the full article on Google. '
    tags = '#news #ai #reels #shorts '

    if politic == 'ASMR':
        title = 'Relaxation Report'
        extra_message = "Find the full article on the BBC's website. "
        tags = tags + '#ASMR #BBC'

    elif politic == 'left':
        title = 'Inclusive Informer'
        extra_message = "Find the full article on the BBC's website. "
        tags = tags + '#Democrat #Liberal #Labour'

    elif politic == 'right':
        title = 'Heritage Report'
        extra_message = 'Find the full article on the Fox News website. '
        tags = tags + '#1 #ainews #Truth'

    elif politic == 'centre':
        title = 'Balanced Broadcast'
        extra_message = "Find the full article on the Independent's website. "
        tags = tags + '#Reels #Centre #Balanced'

    headline = get_json_line(index * 3, politic, custom)
    URL = get_json_line((index * 3) + 1, politic, custom)
    comment = f'{title}\nHeadline: {headline}\nWhat do you think? {extra_message}\n{tags}\n'
    twitter_comment = f'Headline: {headline}\nWhat do you think? {extra_message}\n{tags}'
    youtube_headline = headline[0:99]

    if len(twitter_comment) > 280:
        print('Shortening Once')
        twitter_comment = f'Headline: {headline}\n{extra_message}\n{tags}\n'
        print(f'New length: {len(twitter_comment)}')

    if len(twitter_comment) > 280:
        print('Shortening Twice')
        twitter_comment = f'Headline: {headline}\n{tags}\n'
        print(f'New length: {len(twitter_comment)}')

    if len(twitter_comment) > 280:
        print('Shortening Thrice')
        twitter_comment = f'Headline: {headline}\n'
        print(f'New length: {len(twitter_comment)}')

    if len(twitter_comment) > 280:
        print('Shortening Fourth and Final')
        twitter_comment = f'{title}\n{extra_message}\n{tags}'
        print(f'New length: {len(twitter_comment)}')

    #After twitter comment is made, we can re-purpose 'tags' using our own function
    tags = hashtag_gen.run(headline)
    comment = f'{title}\nHeadline: {headline}\nWhat do you think? {extra_message}\n{tags}\n'

    #TEXT ====================================================================================
    f = open("NewsInfo.txt", "a")
    f.write(f"{filename}\n\n{comment}\n{URL}\n\n\n\n")
    print('Written to Text file')
    f.close()
    #TEXT ====================================================================================

    def upload_to_youtube():
        try:
            logging.info(f"Uploading video: {filepath} to {politic} channel.")
            youtube_uploader.upload_video_to_youtube(filepath, youtube_headline, comment, politic)
        except:
            print('Issue with YouTube uploader')
        pass

    def upload_to_twitter():
        try:
            X_uploader.upload_video_to_X(filepath, twitter_comment, filename)
        except:
            print('Issue with Twitter uploader')
        pass

    def upload_to_instagram():
        try:
            instagram_uploader.run(filepath, comment, politic)
        except Exception as e:
            print('Issue with Instagram uploader: ', e)
        pass
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        futures.append(executor.submit(upload_to_youtube))
        futures.append(executor.submit(upload_to_twitter))
        futures.append(executor.submit(upload_to_instagram))
        concurrent.futures.wait(futures)

# Define keywords
KEYWORDS = ['ASMR', 'left', 'right', 'centre']

# Define folder to watch
FOLDER_TO_WATCH = 'final_videos'

# Dictionary to store processed files and their processing times
processed_files = {}

# Event handler for watchdog
class WatcherHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        check_videos_in_folder()

def check_videos_in_folder():
    current_time = datetime.now()
    files_to_process = []
    for filename in os.listdir(FOLDER_TO_WATCH):
        if filename.endswith('.mp4'):
            if filename in processed_files:
                last_processed_time = processed_files[filename]
                if current_time - last_processed_time < timedelta(minutes=200):
                    continue  # Skip this file if it was processed less than 20 minutes ago

            for keyword in KEYWORDS:
                if keyword in filename:
                    match = re.search(r'_(\d+)', filename)
                    if match:
                        digit = int(match.group(1))
                        files_to_process.append((filename, digit, keyword))
                        break

    for filename, digit, keyword in files_to_process:
        # Update processed_files before uploading to avoid race condition
        processed_files[filename] = current_time
        if 'custom' in filename:
            video_uploader(filename, digit, keyword, True)
        else:
            video_uploader(filename, digit, keyword, False)
        time.sleep(1)


def run():
    f = open("NewsInfo.txt", "w")
    f.close()   
    event_handler = WatcherHandler()
    observer = Observer()
    observer.schedule(event_handler, FOLDER_TO_WATCH, recursive=False)
    observer.start()

    try:
        check_videos_in_folder()
    except Exception as e:
        print(f'Error with video_uploader_manager: {e}')

    print('Done All Uploads!')

run()