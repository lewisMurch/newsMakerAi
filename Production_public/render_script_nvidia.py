import bpy
import sys
import platform
import pathlib
current_dir = str(pathlib.Path().resolve())
from pxr import Usd, UsdGeom
import os

# Get the cache file from the command-line arguments
argv = sys.argv
argv = argv[argv.index('--') + 1:]  # get all args after "--"
cache_file = argv[0] if len(argv) > 0 else None
politic = argv[1] if len(argv) > 1 else None

filepath_cache = os.path.join(current_dir, 'politics', politic, 'MascotNvidia')
left_cache = filepath_cache + "/cache_left_cache.usd"
centre_cache = filepath_cache + "/cache_centre_cache.usd"
right_cache = filepath_cache + "/cache_right_cache.usd"
ASMR_cache = filepath_cache + "/cache_ASMR_cache.usd"

# Configurable variables
FPS = 24

output_path = os.path.join(current_dir, 'politics', politic, 'mascot_video', "final_mascot.webm")

# Ensure the directory exists
output_dir = os.path.dirname(output_path)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Set the FPS for the scene
bpy.context.scene.render.fps = FPS

# Render settings
bpy.context.scene.render.filepath = output_path
bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
bpy.context.scene.render.ffmpeg.format = 'WEBM'
bpy.context.scene.render.ffmpeg.codec = 'WEBM'
bpy.context.scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
bpy.context.scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
bpy.context.scene.render.ffmpeg.audio_codec = 'VORBIS'

# Enable RGBA (Red, Green, Blue, Alpha)
bpy.context.scene.render.image_settings.color_mode = 'RGBA'

# Enable transparent film
bpy.context.scene.render.film_transparent = True

# Debug print to confirm plugin
print("Plugins loaded:", bpy.context.preferences.addons.keys())

# Set the start frame
bpy.context.scene.frame_start = int(0)

# Function to determine the end frame based on the cache's length
def get_cache_length(cache_file):
    if not cache_file:
        return 0
    try:
        # Open the USD stage
        stage = Usd.Stage.Open(cache_file)
        if not stage:
            return 0

        # Get the time codes available in the USD file
        time_codes = stage.GetTimeCodesPerSecond()

        # Get the range of time samples
        start_time = stage.GetStartTimeCode()
        end_time = stage.GetEndTimeCode()

        # Calculate the number of frames
        num_frames = int((end_time - start_time) * time_codes / FPS) + 1
        return num_frames
    except Exception as e:
        print(f"Error reading cache file {cache_file}: {e}")
        return 0

# Set the end frame based on the cache's length
if cache_file:
    cache_length = get_cache_length(cache_file)
    bpy.context.scene.frame_end = cache_length
else:
    print('cant find end frame, using 360 frame as end')
    bpy.context.scene.frame_end = int(360)

# Function to assign an existing material to an object
def assign_material(obj, material_name):
    if obj:
        # Get the existing material
        mat = bpy.data.materials.get(material_name)
        if not mat:
            print(f"Material {material_name} not found")
            return

        # Assign the material to the object
        if len(obj.data.materials) > 0:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
        
        print(f"Assigned material {material_name} to {obj.name}")

# 1) Import cache
if cache_file:
    try:
        bpy.ops.wm.usd_import(filepath=cache_file)  # Assuming this is the correct operator for the plugin
        print(f"Imported cache file: {cache_file}")
    except Exception as e:
        print(f"Failed to import cache file: {cache_file}")
        print(e)
        sys.exit(1)  # Exit if the import fails

# 2) Select 'world' object
world = bpy.data.objects.get('World', None)
all = bpy.data.objects.get('ALL', None) #can search everything in the pre-cache enviroment (cache is laoded outside this 'ALL' in blender)
if not world:
    print("'World' object not found")

# 3) Move 'world' contents down to fit in camera
if world:
    if cache_file == left_cache:
        world.location.z -= 137
    elif cache_file == right_cache:
        world.location.z -= 150
    elif cache_file == centre_cache:
        world.location.z -= 150
    elif cache_file == ASMR_cache:
        world.location.z -= 137
    else:
        print('Unkown value how much to move mascot down blender, using -145')
        world.location.z -= 145

    world.location.y = 17 #move backwards to fit easier in camera

    print("Moved 'World' object contents down and backwards into camera view")

# 4) Assign material 'Skin' to c_headWatertight_hi
if world:
    if cache_file == left_cache:
        material = 'skin_left'
    elif cache_file == right_cache:
        material = 'skin_right'
    elif cache_file == centre_cache:
        material = 'skin_right'
    elif cache_file == ASMR_cache:
        material = 'skin_right'

    def find_mesh(obj):
        if obj.name == 'c_headWatertight_hi':
            assign_material(obj, material)
            return True
        for child in obj.children:
            if find_mesh(child):
                return True
        return False

    if not find_mesh(world):
        print("Skin object not found")
        print(cache_file)

# 5) Assign material 'Tongue' to c_tongue_hi/ c_tongue_hi_crop
if world:
    material = 'Tongue'
    material2 = 'Tongue_dark'

    def find_mesh(obj):
        crop_check = False
        normal_check = False

        if cache_file == left_cache or cache_file == ASMR_cache:
            if obj.name == 'c_tongue_hi':
                assign_material(obj, material)
                obj.location.z = -1
                obj.location.y = -1
                return True
            
        elif cache_file == right_cache or cache_file == centre_cache:
            if obj.name == 'c_tongue_hi_crop':
                assign_material(obj, material)
                crop_check = True

            if obj.name == 'c_tongue_hi':
                assign_material(obj, material2)
                normal_check = True

        if normal_check == True & crop_check == True:
            return True

        for child in obj.children:
            if find_mesh(child):
                return True
            
        return False

    if not find_mesh(world):
        print("Tongue object not found")

# 6) Assign material 'Teeth' to dentures
if world:
    material = 'Teeth'

    def find_mesh(obj):
        if cache_file == left_cache or cache_file == ASMR_cache:
            if obj.name == 'c_topDenture_hi_stamp':
                assign_material(obj, material)
                return True
            
        elif cache_file == right_cache or cache_file == centre_cache:
            if obj.name == 'c_topDenture_hi':
                assign_material(obj, material)
                return True

        for child in obj.children:
            if find_mesh(child):
                return True
        return False

    if not find_mesh(world):
        print("Top denture object not found")

if world:
    material = 'Teeth'

    def find_mesh(obj):
        if cache_file == left_cache or cache_file == ASMR_cache:
            if obj.name == 'c_bottomDenture_hi':
                bpy.data.objects.remove(obj, do_unlink=True)
                return True

            
        elif cache_file == right_cache or cache_file == centre_cache:
            if obj.name == 'c_bottomDenture_hi':
                assign_material(obj, material)
                return True

        for child in obj.children:
            if find_mesh(child):
                return True
        return False

    if not find_mesh(world):
        print("Bottom denture object not found")

# 7) Assign material 'Eye' to eyes and other eye related materials
if world:
    material = 'Eye'

    def find_mesh(obj):
        if cache_file == left_cache:
            if obj.name == 'l_cornea_hi':
                assign_material(obj, material)
                return True
            
        elif cache_file == right_cache or cache_file == centre_cache:
            if obj.name == 'l_choroid_hi':
                assign_material(obj, material)
                obj.location.y += 16
                obj.location.x += 0.3
                obj.location.z = 0.5
                obj.scale *= 0.9
                print('SHIFTED EYES')
                return True

        for child in obj.children:
            if find_mesh(child):
                return True
        return False

    if not find_mesh(world):
        print("Eye object not found!")

if world:
    material = 'Eye'

    def find_mesh(obj):
        if cache_file == left_cache:
            if obj.name == 'r_choroid_hi':
                assign_material(obj, material)
                return True

        elif cache_file == right_cache  or cache_file == centre_cache:
            if obj.name == 'r_choroid_hi':
                assign_material(obj, material)
                obj.location.y += 16
                obj.location.x -= 0.3
                obj.location.z = 0.5
                obj.scale *= 0.9
                print('SHIFTED EYES')
                return True

        for child in obj.children:
            if find_mesh(child):
                return True
        return False

    if not find_mesh(world):
        print("Eye object not found!")

if world:
    material = 'Eye'

    def find_mesh(obj):
        if cache_file == left_cache or cache_file == centre_cache:
            if obj.name == 'r_cornea_hi':
                assign_material(obj, material)
                return True

        elif cache_file == right_cache:
            if obj.name == 'r_cornea_hi':
                assign_material(obj, material)
                return True

        for child in obj.children:
            if find_mesh(child):
                return True
        return False

    if not find_mesh(world):
        print("Cornea object not found")

if world:
    def find_mesh(obj):
        if cache_file == left_cache or cache_file == centre_cache:
            material = 'skin_left'
            if obj.name == 'l_tearline_hi':
                assign_material(obj, material)
                return True

        elif cache_file == right_cache:
            material = 'skin_right'
            if obj.name == 'l_caruncle_hi':
                assign_material(obj, material)
                return True

        for child in obj.children:
            if find_mesh(child):
                return True
        return False

    if not find_mesh(world):
        print("Tear line object not found")

if world:
    def find_mesh(obj):
        if cache_file == left_cache or cache_file == centre_cache:
            material = 'skin_left'
            if obj.name == 'r_tearline_hi':
                assign_material(obj, material)
                return True

        elif cache_file == right_cache:
            material = 'skin_right'
            if obj.name == 'r_caruncle_hi':
                assign_material(obj, material)
                return True

        for child in obj.children:
            if find_mesh(child):
                return True
        return False

    if not find_mesh(world):
        print("Tear line object not found")

# 7.5) Assign material 'eyebrows' to eyes and other eye related materials
if world:
    def find_mesh(obj):
        if cache_file == right_cache or cache_file == centre_cache: #move the eyebrows up 50 units if right person is selected
            if obj.name == 'right_eyebrows':
                obj.location.z += 48.55
                obj.location.y -= 2.3
                return True
            
        elif cache_file == left_cache:
            if obj.name == 'left_eyebrows':
                obj.location.z += 50
                return True

        for child in obj.children:
            if find_mesh(child):
                return True
            
        return False

    if not find_mesh(all):
        print("Eyebrow not found")

# 8) Load props
#Shirts
if world:
    def find_mesh(obj):
        if cache_file == right_cache: #move the shirt up 50 units if right person is selected
            if obj.name == 'right_shirt':
                obj.location.z += 50
                return True
            
        elif cache_file == left_cache:
            if obj.name == 'left_shirt':
                obj.location.z += 50
                return True
            
        elif cache_file == centre_cache:
            if obj.name == 'centre_shirt':
                obj.location.z += 50
                return True

        for child in obj.children:
            if find_mesh(child):
                return True
            
        return False

    if not find_mesh(all):
        print("Shirt not found")

#Glasses
if world:
    def find_mesh(obj):
        if cache_file == right_cache: #move the shirt up 50 units if right person is selected
            if obj.name == 'right_glasses':
                obj.location.z += 50
                return True
            
        if cache_file == left_cache:
            if obj.name == 'left_glasses':
                obj.location.z += 50
                return True

        for child in obj.children:
            if find_mesh(child):
                return True
            
        return False

    if not find_mesh(all):
        print("Glasses not found")

#Hats
if world:
    def find_mesh(obj):
        if cache_file == right_cache: #move the hat up 50 units if right person is selected
            if obj.name == 'right_hat':
                obj.location.z += 50
                return True
            
        elif cache_file == left_cache:
            if obj.name == 'left_hat':
                obj.location.z += 50
                return True
            
        elif cache_file == centre_cache:
            if obj.name == 'hair_centre':
                obj.location.z += 50
                return True
            
        elif cache_file == ASMR_cache:
            if obj.name == 'hat_ASMR':
                obj.location.z += 50
                obj.location.z += 1.2
                return True

        for child in obj.children:
            if find_mesh(child):
                return True
            
        return False

    if not find_mesh(all):
        print("Hat not found")

#Smoke
if world:
    def find_mesh(obj):
        if cache_file == ASMR_cache:
            if obj.name == 'smoke_ASMR':
                obj.hide_render = False
                return True

        for child in obj.children:
            if find_mesh(child):
                return True
            
        return False

    if not find_mesh(all):
        print("Smoke not found")

#debug to get around rendering the whole thing - basically allows you to see scene setup instantly
# blend_file_path = os.path.join(current_dir, 'politics', politic, "debug.blend")
# bpy.ops.wm.save_as_mainfile(filepath=blend_file_path)

# Render the animation
try:
    bpy.ops.render.render(animation=True)
    print(f"Animation rendered and saved to {output_path}")
except Exception as e:
    print("Rendering failed!")
    print(e)