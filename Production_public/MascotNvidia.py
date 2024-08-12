import os
import requests
import time
import subprocess
import pathlib

# Base URL and paths
player = "/World/audio2face/player"
current_dir = str(pathlib.Path().resolve())
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Function to check server status
def check_server_status(base_url):
    try:
        response = requests.get(base_url + "/status")
        response.raise_for_status()
        status = response.json()
        if status == "OK":
            print("Started cache maker")
            return True
        else:
            print("Error: unable to reach A2F")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return False

# Function to load a USD file
def load_usd_file(file_path, base_url):
    data = {"file_name": file_path}
    response = requests.post(base_url + "/A2F/USD/Load", json=data)
    try:
        response.raise_for_status()
        response_data = response.json()
        if response_data.get("status") == "OK":
            print(f"Loaded USD file: {file_path}")
            return True
        else:
            print(f"Error loading USD file: {response_data.get('message', 'Unknown error')}.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error loading USD file: {e}")
        return False

# Function to get existing player instances
def get_player_instances(base_url):
    response = requests.get(base_url + "/A2F/Player/GetInstances")
    try:
        response.raise_for_status()
        response_data = response.json()
        if response_data.get("status") == "OK":
            players = response_data["result"]
            print("Player instances:", players)
            return players
        else:
            print(f"Error getting player instances: {response_data.get('message', 'Unknown error')}.")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error getting player instances: {e}")
        return []

# Function to set the root path for audio files
def set_root_path(player_instance, root_path, base_url):
    data = {
        "a2f_player": player_instance,
        "dir_path": root_path
    }
    response = requests.post(base_url + "/A2F/Player/SetRootPath", json=data)
    try:
        response.raise_for_status()
        response_data = response.json()
        if response_data.get("status") == "OK":
            print(f"Set root path: {root_path}.")
            return True
        else:
            print(f"Error setting root path: {response_data.get('message', 'Unknown error')}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error setting root path: {e}")
        return False

# Function to get available tracks
def get_tracks(player_instance, base_url):
    data = {"a2f_player": player_instance}
    response = requests.post(base_url + "/A2F/Player/GetTracks", json=data)
    try:
        response.raise_for_status()
        response_data = response.json()
        if response_data.get("status") == "OK":
            tracks = response_data["result"]
            print("Available tracks:", tracks)
            return tracks
        else:
            print(f"Error getting tracks: {response_data.get('message', 'Unknown error')}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error getting tracks: {e}")
        return []

# Function to set the audio track
def set_track(player_instance, track_name, base_url):
    data = {
        "a2f_player": player_instance,
        "file_name": track_name
    }
    response = requests.post(base_url + "/A2F/Player/SetTrack", json=data)
    try:
        response.raise_for_status()
        response_data = response.json()
        if response_data.get("status") == "OK":
            print(f"Set track: {track_name}.")
            return True
        else:
            print(f"Error setting track: {response_data.get('message', 'Unknown error')}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error setting track: {e}")
        return False

# Function to start playback
def start_playback(player_instance, base_url):
    data = {"a2f_player": player_instance}
    response = requests.post(base_url + "/A2F/Player/Play", json=data)
    try:
        response.raise_for_status()
        response_data = response.json()
        if response_data.get("status") == "OK":
            print("Playback started")
            return True
        else:
            print(f"Error starting playback: {response_data.get('message', 'Unknown error')}.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error starting playback: {e}")
        return False

# Function to export geometry cache
def export_geometry_cache(player_instance, output_cache_path, base_url):
    data = {
        "a2f_player": player_instance,
        "file_name": output_cache_path
    }
    response = requests.post(base_url + "/A2F/Exporter/ExportGeometryCache", json=data)
    try:
        response.raise_for_status()
        response_data = response.json()
        if response_data.get("status") == "OK":
            print(f"Exported geometry cache to: {output_cache_path}")
            return True
        else:
            print(f"Error exporting geometry cache: {response_data.get('message', 'Unknown error')}.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error exporting geometry cache: {e}")
        return False

# Main script
def run(bias = 'right'): #EFFECTIVELY ALL THIS CODE JUST GENERATES THE RIGHT CACHE AND NAMES IT
    politic = bias
    if politic == 'right':
        base_url = "http://localhost:8011"
    elif politic == 'left':
        base_url = "http://localhost:8012"
    elif politic == 'centre':
        base_url = "http://localhost:8013"
    elif politic == 'ASMR':
        base_url = "http://localhost:8014"

    filepath_TTS = os.path.join('politics', politic, 'TTS')
    audio_file_path = current_dir + f"/{filepath_TTS}/TTS_output.wav"
    audio_folder_path = current_dir + f"/{filepath_TTS}"

    filepath_USD = os.path.join(current_dir, 'politics', politic, 'MascotNvidia')
    usd_file_path_right = f"{filepath_USD}/right_mascot.usd"
    usd_file_path_left = f"{filepath_USD}/left_mascot.usd"
    output_cache_path = f"{filepath_USD}/cache_"

    if check_server_status(base_url):
        output_cache_path = output_cache_path + bias #set the correct output path (and name) for the cache to be accessed by blender later

        usd_file_path = usd_file_path_right #default just incase
        if bias == 'right':
            usd_file_path = usd_file_path_right
        elif bias == 'left':
            usd_file_path = usd_file_path_left
        elif bias == 'centre':
            usd_file_path = usd_file_path_right
        elif bias == 'ASMR':
            usd_file_path = usd_file_path_left

        if load_usd_file(usd_file_path, base_url):
            players = get_player_instances(base_url)
            if players:
                print(players)
                player_instance = '/World/audio2face/Player'  # Using the first player instance (hardcoded name for now)
                if set_root_path(player_instance, audio_folder_path, base_url):
                    tracks = get_tracks(player_instance, base_url)
                    if tracks:
                        track_name = os.path.basename(audio_file_path)
                        if set_track(player_instance, track_name, base_url):
                            if start_playback(player_instance, base_url):
                                if export_geometry_cache(player_instance, output_cache_path, base_url):
                                    print('All done! cache exported')
