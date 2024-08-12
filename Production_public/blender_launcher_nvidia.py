import subprocess
import os
import platform
import pathlib
current_dir = str(pathlib.Path().resolve())

def run_blender(blender_path, blend_file, script_file, cache_file, politic):
    # Command to run blender with the specified .blend file, and python script
    command = [
        blender_path,    # Path to the Blender executable
        blend_file,      # Path to the .blend file
        '--background',  # Run Blender in the background (no GUI)
        '--python', script_file,  # Run the specified Python script
        '--', cache_file,  # Pass the cache file as an argument to the Python script
        politic       # Pass the politic argument to the Python script
    ]
    
    # Print command for debugging
    print("Running command:", " ".join(command))
    
    # Run the command
    result = subprocess.run(command, capture_output=True, text=True)
    
    #If you want to debug:
    # print("STDOUT:", result.stdout)
    # print("STDERR:", result.stderr)

    # Check if the process completed 
    if result.returncode == 0:
        print("Rendering complete!")
    else:
        print("Rendering failed!")
        print(result.stderr)

def run(politic='centre'):
    blender_path = "E:/SteamLibrary/steamapps/common/Blender/blender.exe" 
    filepath_cache = os.path.join(current_dir, 'politics', politic, 'MascotNvidia')

    if politic == 'right':
        cache_file = filepath_cache + "/cache_right_cache.usd"
        print(f'Using {cache_file}')
    elif politic == 'left':
        cache_file = filepath_cache + "/cache_left_cache.usd"
        print(f'Using {cache_file}')
    elif politic == 'centre': 
        cache_file = filepath_cache + "/cache_centre_cache.usd"
        print(f'Using {cache_file}')
    elif politic == 'ASMR': 
        cache_file = filepath_cache + "/cache_ASMR_cache.usd"
        print(f'Using {cache_file}')
    else:
        cache_file = filepath_cache + "/cache_right_cache.usd"

    blend_file = os.path.join(current_dir, 'politics', politic, 'blender', 'Mascot_staging.blend')
    script_file = "render_script_nvidia.py"
    
    run_blender(blender_path, blend_file, script_file, cache_file, politic)