import os
import requests
from PIL import Image
from io import BytesIO

def run(text, backup_text, politic):
    filepath = os.path.join('politics', politic, 'related_images')

    # Clear the folder of all images
    def clear_folder(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    os.rmdir(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

    clear_folder(filepath)

    query = text
    print('running image finder for:', query, '\n')

    API_KEYS = [
        'your-apikeyhere',
        'your-secondapikeyhere',
        # add more API keys here if available
    ]
    SEARCH_ENGINE_ID = '505cf8c5ec9594c3a'

    # Ensure necessary folders are created if they don't exist
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    def get_image_url(query):
        search_url = "https://www.googleapis.com/customsearch/v1"
        for api_key in API_KEYS:
            params = {
                'q': query,
                'cx': SEARCH_ENGINE_ID,
                'key': api_key,
                'searchType': 'image',
                'num': 1,
            }
            
            try:
                response = requests.get(search_url, params=params)
                response.raise_for_status()
                search_results = response.json()
                if 'items' in search_results and len(search_results['items']) > 0:
                    image_url = search_results['items'][0]['link']
                    return image_url
                else:
                    raise ValueError("No image found for the query.")
            
            except requests.exceptions.HTTPError as http_err:
                if response.status_code == 429:
                    print(f"API key {api_key} exceeded its limit, trying next key...")
                    continue
                else:
                    print(f"HTTP error occurred: {http_err}")
                    return None
            except Exception as e:
                print(f"Error with searching: {e}")
                return None
        print("All API keys have been exhausted.")
        return None

    def fetch_and_save_image(image_url):
        if image_url is None:
            return
        
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            image_data = response.content
            image = Image.open(BytesIO(image_data))

            # Convert image to RGB mode if it's in 'P' or 'RGBA' mode
            if image.mode == 'P' or image.mode == 'RGBA':
                image = image.convert('RGB')

            # Get the current number of files in the 'assets/related_images' folder
            num_existing_images = len(os.listdir(filepath))

            # Save the image with a filename based on the number of existing images
            image_filename = os.path.join(filepath, f"{num_existing_images + 1}.jpg")
            image.save(image_filename)
        
        except Exception as e:
            print(f"Failed to fetch or save image: {e}")

    def process_sentence(sentence):
        image_url = get_image_url(sentence)
        if not image_url:
            print("Attempting to use backup text...")
            image_url = get_image_url(backup_text)
        
        fetch_and_save_image(image_url)

    process_sentence(query)
