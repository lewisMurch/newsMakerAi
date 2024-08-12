import os
import subprocess
from moviepy.editor import VideoFileClip, AudioFileClip

def split_media(input_path, num_pieces):
    # Check if the file exists
    if not os.path.isfile(input_path):
        print(f"Error: The file {input_path} does not exist.")
        return
    
    ext = os.path.splitext(input_path)[1].lower()
    if ext not in ['.mp4', '.mp3']:
        print(f"Error: Unsupported file type {ext}. Only .mp4 and .mp3 are supported.")
        return
    
    try:
        # Load the media file to get the duration
        if ext == '.mp4':
            media = VideoFileClip(input_path)
        elif ext == '.mp3':
            media = AudioFileClip(input_path)
        
        duration = media.duration
        media.close()  # Close the media file to release resources
    except Exception as e:
        print(f"Error: Unable to load media file. {e}")
        return

    piece_duration = duration / num_pieces

    # Extract the file name without extension and directory
    base_name = os.path.basename(input_path).rsplit('.', 1)[0]
    
    # Create output directory
    output_dir = f"blend_assets/{base_name}_split"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Split the media into pieces
    for i in range(num_pieces):
        start_time = i * piece_duration
        end_time = (i + 1) * piece_duration
        
        # Ensure the last piece doesn't exceed the media's duration
        if end_time > duration:
            end_time = duration
        
        # Define the output path
        output_path = os.path.join(output_dir, f"{base_name}_part_{i+1}{ext}")
        
        # Use ffmpeg to cut the media clip
        if ext == '.mp4':
            ffmpeg_command = [
                'ffmpeg',
                '-hwaccel', 'cuda',  # Use CUDA for hardware acceleration
                '-ss', str(start_time),
                '-to', str(end_time),
                '-i', input_path,
                '-c:v', 'h264_nvenc',  # Use the NVIDIA encoder
                '-b:v', '5M',  # Bitrate can be adjusted
                output_path
            ]
        elif ext == '.mp3':
            ffmpeg_command = [
                'ffmpeg',
                '-ss', str(start_time),
                '-to', str(end_time),
                '-i', input_path,
                '-acodec', 'copy',
                output_path
            ]
        
        # Run the ffmpeg command
        subprocess.run(ffmpeg_command, check=True)
    
    print(f"Media has been split into {num_pieces} pieces and saved in {output_dir}.")

# Example test
split_media("mc.mp4", 100)


