import os
import shutil
import random
import sys
import pathlib
current_dir = str(pathlib.Path().resolve())


def is_folder_empty(path):
    for filename in os.listdir(path):
        if not filename.startswith('.'):
            print('not empty')
            return False
    print('empty')
    return True

def check_and_swap_folders(politic):
    attention_footage_folder_path = os.path.join(current_dir, 'politics', politic, 'attention_footage')
    folder_A = os.path.join(attention_footage_folder_path, 'footage_A')
    folder_B = os.path.join(attention_footage_folder_path, 'footage_B')
    temp_footage = attention_footage_folder_path = os.path.join(current_dir, 'politics', politic, 'attention_footage', 'temp_folder')

    # Check if folder_A is empty
    if is_folder_empty(folder_A):
        # Swap folder names
        os.rename(folder_A, temp_footage)
        os.rename(folder_B, folder_A)
        os.rename(temp_footage, folder_B)
        # Re-run the program
        print("Folder A was empty! Swapped folders and now re-running the program.")
        # Get a random clip from folder_A
        clips = [f for f in os.listdir(folder_A) if not f.startswith('.')]
        random_clip = random.choice(clips)
        clip_path = os.path.join(folder_A, random_clip)
        
        # Move the clip to folder_B
        shutil.move(clip_path, folder_B)
        
        # Output the path of the moved clip
        moved_clip_path = os.path.join(folder_B, random_clip)
        return moved_clip_path
    else:
        # Get a random clip from folder_A
        clips = clips = [f for f in os.listdir(folder_A) if not f.startswith('.')]
        random_clip = random.choice(clips)
        clip_path = os.path.join(folder_A, random_clip)
        
        # Move the clip to folder_B
        shutil.move(clip_path, folder_B)
        
        # Output the path of the moved clip
        moved_clip_path = os.path.join(folder_B, random_clip)
        return moved_clip_path
    
