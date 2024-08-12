import os
import sys
import json
import time
import subprocess
from pathlib import Path

#save current path to go back to in a moment
current_dir = os.path.dirname(__file__)

# find the path to parent directory (two levels up)
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# add the parent directory to the sys.path
sys.path.append(parent_dir)

#Import my modules
import News_finder_and_saver
import TTS
import MascotNvidia
import blender_launcher_nvidia
import image_finder
import video_composer

if current_dir not in sys.path:
    sys.path.append(current_dir)

domain_list = ['ASMR_BBC']
domain_amount = len(domain_list)
lines_per_article = 3

domain_bias = {
    'left': ['BBC', 'SKY'],
    'right': ['FOX', 'STIME'],
    'centre': ['IND'],
    'ASMR': ['ASMR_BBC'],
}

# Path to the batch file
bat_file_path = Path(r'C:\Users\username\AppData\Local\ov\pkg\audio2face-2023.2.0\audio2face_headless.bat').resolve()

# Command to execute the batch file with specific arguments
command = f'cmd /c "{bat_file_path}" --/exts/omni.services.transport.server.http/port=8014'

# Start the server process
process = subprocess.Popen(command, shell=True)

def find_bias(value):
    for key, values in domain_bias.items():
        if value in values:
            return key
    return None  # Return None if the value is not found

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

def run(): #Currently working: right, left
    #For each domain of articles (e.g. Once for BBC, once for CNN etc)
    for domain_num in range (0, domain_amount):

        #Find the correct bias (e.g. left, right etc)
        politic = 'centre'
        domain_to_find_bias = domain_list[domain_num]
        found_bias = find_bias(domain_to_find_bias)
        if found_bias:
            politic = found_bias
          
        article_amount = 0
        article_amount = News_finder_and_saver.get_all_news_from_domain(domain_list[domain_num], politic) #made the news getter-function return the number of articles for use here
        print(f"\nSaved {article_amount} articles sucessfully from '{domain_list[domain_num]}' domain")

        #For each article in that domain (e.g. Once for 'UK pledges £84m to stop illegal migration')
        for article_num in range(0, article_amount): 
            try:
                start = time.time()
                index = article_num * lines_per_article

                headline = get_json_line(index, politic)
                URL = get_json_line(index + 1, politic)
                image_link = get_json_line(index + 2, politic)

                #Stage 2
                try:
                    img_headline = headline[:60].rpartition(' ')[0]
                    image_finder.run(image_link, img_headline, politic)
                    print('Image Found Sucessfully\n')
                except:
                    print('Image Not Found Sucessfully\n')
                #Stage 2

                # #Stage 3
                try:
                    TTS.run_TTS(headline, politic)
                    print('TTS Generated Sucessfully\n')
                except Exception as error:
                    print(f'TTS Not Generated Sucessfully: {error}\n')
                #Stage 3

                # #Stage 4
                try:
                    MascotNvidia.run(politic)
                    print('NVIDIA A2F Generated Sucessfully\n')
                except:
                    print('NVIDIA A2F Not Generated Sucessfully\n')
                # #Stage 4

                # Stage 5
                try:
                    blender_launcher_nvidia.run(politic)
                    print('Mascot Video Generated Sucessfully\n')
                except:
                    print('Mascot Video Not Generated Sucessfully\n')
                # Stage 5

                # Stage 6
                try:
                    video_name = ('final_video_' + politic + '_' + str(article_num))
                    video_composer.run(headline, video_name, politic)
                    print('Final Video Generated Sucessfully\n')
                except Exception as error:
                    print(f'Final Video Not Generated Sucessfully: {error}\n')
                end = time.time()
                print(f'        {video_name} took {int(end - start)} seconds to generate!')
                # Stage 6
            except Exception as e:
                try:
                    print(f'Error with generating article number {article_num} in ASMR: ', e)
                except:
                    print('Error with generating article ASMR: ', e)

def custom_run(headline, image_link, politic, choose_article_mode = False, domain = 'BBC', article_amount = 10):

    # # Stage 1
    if choose_article_mode == True:
        x = News_finder_and_saver.get_all_news_from_domain(domain, politic, choose_article_mode, article_amount)
        if x == 'wrong_choice':
            print('Invalid number choice')
            quit()
    # # Stage 1

    if choose_article_mode == True:
        headline = get_json_line(0, politic, True)
        URL = get_json_line(1, politic, True)
        image_link = get_json_line(2, politic, True)
    else:
        headline = headline
        image_link = image_link

    # Stage 2
    try:
        image_finder.run(image_link, headline, politic)
        print('Image Found Sucessfully\n')
    except Exception as e:
        print(f'Image Not Found Sucessfully {e}:\n')
    # Stage 2

    # Stage 3
    try:
        TTS.run_TTS(headline, politic)
        print('TTS Generated Sucessfully\n')
    except Exception as error:
        print(f'TTS Not Generated Sucessfully: {error}\n')
    # Stage 3

    # Stage 4
    try:
        MascotNvidia.run(politic)
        print('NVIDIA A2F Generated Sucessfully\n')
    except Exception as e:
        print(f'NVIDIA A2F Not Generated Sucessfully: {e}\n')
    # Stage 4

    # Stage 5
    try:
        blender_launcher_nvidia.run(politic)
        print('Mascot Video Generated Sucessfully\n')
    except Exception as e:
        print(f'Mascot Video Not Generated Sucessfully: {e}\n')
    # Stage 5

    # Stage 6
    try:
        video_composer.run(headline, f'final_video_custom_{politic}_0', politic)
        print('Final Video Generated Sucessfully\n')
    except Exception as error:
        print(f'Final Video Not Generated Sucessfully: {error}\n')
    # Stage 6

custom_run(' ', ' ', 'ASMR', True, 'BBC', 30)
#custom_run('Mass stabbing - Mostly young girls, eight people stabbed in Southport. Armed police have arrested a man and seized a knife', 'https://cdn.images.express.co.uk/img/dynamic/1/590x/secondary/Southport-5528773.jpg?r=1722260415815', 'ASMR', False, 'BBC', 30)