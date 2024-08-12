import requests
import os
from pydub import AudioSegment
import platform
import time

if platform.system() == 'Windows':
    os.system('cls')
else:
    os.system('clear')

def run_TTS(text, politic='centre'):
    if politic == 'left':
        voice = 'woman'
    elif politic == 'right':
        voice = 'man'
    elif politic == 'centre':
        voice = 'centre_man'
    elif politic == 'ASMR':
        voice = 'ASMR'
    else:
        voice = 'woman'

    text = text.rstrip('!')
    text = text.rstrip('.') + '.'
    text = text.lower()
    CHUNK_SIZE = 1024
    url = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    #I don't condone abusing free api key usage with multiple accounts, this is incase you have different PAID accounts
    api_key_list = ['example_api_key', 'example_api_key', 'example_api_key', 'example_api_key', 'example_api_key', 'example_api_key', 'example_api_key']
    ammount_of_keys = len(api_key_list)

    retry_count = 3
    retry_delay = 5  # seconds

    for key_index in range(0, ammount_of_keys):
        for attempt in range(retry_count):
            try:
                headers = {
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                    "xi-api-key": api_key_list[key_index],
                }
                # Voice configurations
                voices = {
                    'woman': {
                        'voice_id': 'Xb7hH8MSUJpSbSDYk0k2',  # Woman news ID (centre)
                        'voice_settings': {
                            'stability': 0.5,
                            'similarity_boost': 0.5
                        }
                    },
                    'man': {
                        'voice_id': 'onwK4e9ZLuTAKqWW03F9',  # Man news ID (right)
                        'voice_settings': {
                            'stability': 0.45,
                            'similarity_boost': 0.45
                        }
                    },
                    'ASMR': {
                        'voice_id': 'piTKgcLEGmPE4e6mEKli',  # ASMR news ID 
                        'voice_settings': {
                            'stability': 0.45,
                            'similarity_boost': 0.45
                        }
                    },
                    'centre_man': {
                        'voice_id': '5Q0t7uMcjvnagumLfvZi',  # Man news ID (centre)
                        'voice_settings': {
                            'stability': 0.3,
                            'similarity_boost': 0.5
                        }
                    }
                }

                if voice not in voices:
                    print(f"Voice '{voice}' not recognized. Using default 'woman' voice.")
                    voice = 'woman'

                data = {
                    "text": text,
                    "model_id": "eleven_monolingual_v1",
                    "voice_settings": voices[voice]['voice_settings']
                }

                # Use the correct voice ID in the URL
                response = requests.post(url.format(voice_id=voices[voice]['voice_id']), json=data, headers=headers)

                # Check if request was successful
                if response.status_code == 200:
                    # Ensure the folder exists
                    filepath = os.path.join('politics', politic, 'TTS')
                    if not os.path.exists(filepath):
                        os.makedirs(filepath)

                    # Saving the TTS output as an audio file
                    with open(f'{filepath}/TTS_output.mp3', 'wb') as f:
                        f.write(response.content)
                    print("TTS output saved successfully.")

                    # For phoneme detection
                    def mp3_to_wav(mp3_file, wav_file):
                        audio = AudioSegment.from_mp3(mp3_file)
                        audio.export(wav_file, format="wav")

                    mp3_file = f"{filepath}/TTS_output.mp3"
                    wav_file = f"{filepath}/TTS_output.wav"
                    mp3_to_wav(mp3_file, wav_file)
                    return True
                else:
                    print("Error:", response.status_code, response.text)
                    if response.status_code == 429:  # Rate limiting error code
                        print(f"Rate limited. Retrying after {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        continue  # Retry the current key
                    else:
                        raise TypeError('API key fully used!')

            except Exception as e:
                print(f'Key number {key_index + 1} not working, retry attempt {attempt + 1} of {retry_count} failed.\n', str(e))
                if attempt == retry_count - 1:
                    # Move to the next key if max retries reached
                    break
                else:
                    time.sleep(retry_delay)  # Wait before retrying the same key
