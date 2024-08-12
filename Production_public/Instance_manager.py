import concurrent.futures
import threading
import tkinter as tk
from tkinter import scrolledtext
import queue
import time
import subprocess
import importlib.util
from pathlib import Path
import sys
import io
from contextlib import contextmanager

# Start timing
start = time.time()

# Function to import a module from a file path
def import_module_from_path(module_name, module_path):
    sys.path.append(str(module_path.parent))
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Paths to the batch file and modules
bat_file_path = Path(r'C:\Users\yourname\AppData\Local\ov\pkg\audio2face-2023.2.0\audio2face_headless.bat').resolve()
commands = [
    f'cmd /c "{bat_file_path}" --/exts/omni.services.transport.server.http/port=8011',
    f'cmd /c "{bat_file_path}" --/exts/omni.services.transport.server.http/port=8012',
    f'cmd /c "{bat_file_path}" --/exts/omni.services.transport.server.http/port=8013',
    f'cmd /c "{bat_file_path}" --/exts/omni.services.transport.server.http/port=8014'
]

# Start the servers
processes = [subprocess.Popen(cmd, shell=True) for cmd in commands]

# Paths to the modules
main_right_path = Path('politics/right/Main_right.py').resolve()
main_left_path = Path('politics/left/Main_left.py').resolve()
main_centre_path = Path('politics/centre/Main_centre.py').resolve()
main_ASMR_path = Path('politics/ASMR/Main_ASMR.py').resolve()

# Import the modules
main_right = import_module_from_path('Main_right', main_right_path)
main_left = import_module_from_path('Main_left', main_left_path)
main_centre = import_module_from_path('Main_centre', main_centre_path)
main_ASMR = import_module_from_path('Main_ASMR', main_ASMR_path)

# Task status and output handling
status = {"load_left": "gray", "load_right": "gray", "load_centre": "gray", "load_ASMR": "gray"}
text_widgets = {}
status_lock = threading.Lock()
output_queues = {"load_left": queue.Queue(), "load_right": queue.Queue(), "load_centre": queue.Queue(), "load_ASMR": queue.Queue()}
all_tasks_complete = threading.Event()

# A list to hold after ids for cancelation
after_ids = []

def update_squares():
    with status_lock:
        for task, color in status.items():
            canvas.itemconfig(squares[task], fill=color)
        if all(color == "green" for color in status.values()):
            print("All videos loaded, now starting API upload...")
            all_tasks_complete.set()
            root.quit()
            return
    after_id = root.after(1000, update_squares)
    after_ids.append(after_id)

def create_output_window(task_name):
    new_window = tk.Toplevel(root)
    new_window.title(f"{task_name} Output")
    text_widget = scrolledtext.ScrolledText(new_window, width=50, height=20)
    text_widget.pack()
    text_widgets[task_name] = text_widget

def update_text_widget():
    for task_name, q in output_queues.items():
        while not q.empty():
            text = q.get()
            if task_name in text_widgets and text_widgets[task_name].winfo_exists():
                text_widgets[task_name].insert(tk.END, text)
                text_widgets[task_name].see(tk.END)
    after_id = root.after(100, update_text_widget)
    after_ids.append(after_id)

class StdoutRedirector(io.StringIO):
    def __init__(self, task_name):
        super().__init__()
        self.task_name = task_name

    def write(self, text):
        super().write(text)
        output_queues[self.task_name].put(text)

    def flush(self):
        pass

@contextmanager
def stdout_redirector(task_name):
    original_stdout = sys.stdout
    redirected_stdout = StdoutRedirector(task_name)
    sys.stdout = redirected_stdout
    try:
        yield
    finally:
        sys.stdout = original_stdout

def run_task(task_name, task_func):
    with status_lock:
        status[task_name] = "purple"
    try:
        with stdout_redirector(task_name):
            task_func(lambda text: output_queues[task_name].put(text))
        with status_lock:
            status[task_name] = "green"
    except Exception as e:
        with status_lock:
            status[task_name] = "red"
        output_queues[task_name].put(f"Error in {task_name}: {e}")

def load_left(print_func):
    print_func("Loading Left...\n")
    main_left.run()

def load_right(print_func):
    print_func("Loading Right...\n")
    time.sleep(1)
    main_right.run()

def load_centre(print_func):
    print_func("Loading Centre...\n")
    time.sleep(2)
    main_centre.run()

def load_ASMR(print_func):
    print_func("Loading ASMR...\n")
    time.sleep(3)
    main_ASMR.run()

root = tk.Tk()
root.title("Task Status")

canvas = tk.Canvas(root, width=400, height=150)
canvas.pack()

squares = {
    "load_left": canvas.create_rectangle(10, 10, 90, 90, fill="gray", tags="load_left"),
    "load_right": canvas.create_rectangle(110, 10, 190, 90, fill="gray", tags="load_right"),
    "load_centre": canvas.create_rectangle(210, 10, 290, 90, fill="gray", tags="load_centre"),
    "load_ASMR": canvas.create_rectangle(310, 10, 390, 90, fill="gray", tags="load_ASMR")
}

labels = {
    "load_left": canvas.create_text(50, 100, text="Left"),
    "load_right": canvas.create_text(150, 100, text="Right"),
    "load_centre": canvas.create_text(250, 100, text="Centre"),
    "load_ASMR": canvas.create_text(350, 100, text="ASMR")
}

for task in squares.keys():
    canvas.tag_bind(task, "<Button-1>", lambda event, task=task: create_output_window(task))

root.after(1000, update_squares)
root.after(100, update_text_widget)

def run_tasks():
    for task in squares.keys():
        create_output_window(task)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(run_task, "load_left", load_left),
            executor.submit(run_task, "load_right", load_right),
            executor.submit(run_task, "load_centre", load_centre),
            executor.submit(run_task, "load_ASMR", load_ASMR)
        ]
        concurrent.futures.wait(futures)

def cleanup():
    for after_id in after_ids:
        root.after_cancel(after_id)

threading.Thread(target=run_tasks).start()

# Bind the cleanup function to the root window's close event
root.protocol("WM_DELETE_WINDOW", cleanup)

root.mainloop()
all_tasks_complete.wait()

# Terminate all subprocesses
for process in processes:
    process.terminate()

end = time.time()
print(f'\nAll rendered! Took {int(end - start)} seconds')
input("Press Enter to continue...")
