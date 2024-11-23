import os, subprocess
from tkinter import *
from tkinter import messagebox, filedialog, ttk
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed

VERSION = "v1.0"

def validate_addon_folder(folder):
    """Check if the selected folder contains layout.json and manifest.json."""
    layout_path = os.path.join(folder, "layout.json")
    manifest_path = os.path.join(folder, "manifest.json")
    return os.path.isfile(layout_path) and os.path.isfile(manifest_path), layout_path

def find_textures(folder):
    """Find all textures in the specified folder with size greater than or equal to 8192x8192."""
    images = []
    for dirpath, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(".dds"):
                try:
                    filepath = os.path.join(dirpath, file)
                    with Image.open(filepath) as image:
                        if image.width >= 8192 or image.height >= 8192:
                            images.append((filepath, image.size))
                except Exception as e:
                    print(f"Error reading {file}: {e}")
    return images

def optimize_texture(filepath):
    """Optimize the texture resolution"""
    try:
        with Image.open(filepath) as image:
            while image.width >= 8192 or image.height >= 8192:
                width = round(image.width / 2)
                height = round(image.height / 2)
                image = image.resize((width, height))
            
            subprocess.run([
                "texconv.exe", filepath, 
                "-w", str(image.width), 
                "-h", str(image.height), 
                "-o", os.path.dirname(filepath), 
                "-y"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                creationflags=subprocess.CREATE_NO_WINDOW
            )
    except:
        pass

class TextureResizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"MSFS Addon Optimizer ({VERSION})")
        self.root.geometry("500x190")
        self.root.resizable(False, False)

        self.folder_path = StringVar()
        self.textures = []

        self.create_widgets()

    def create_widgets(self):
        """Creates the layout of the app."""
        # Header frame
        frame = Frame(self.root)
        frame.pack(pady=10)
        
        Label(frame, text=f"MSFS Addon Optimizer ({VERSION})", font=("Helvetica", 16, "bold")).pack()
        Label(frame, text="Publisher: aaMasih    |    Coded by Creepcomp", font=("Helvetica", 8)).pack()

        # Folder selection frame
        frame = Frame(self.root)
        frame.pack(pady=10)

        self.folder_entry = Entry(frame, textvariable=self.folder_path, width=66, state="readonly")
        self.folder_entry.pack(side=LEFT, padx=(0, 1))

        Button(frame, text="Browse", command=self.browse_folder).pack(side=LEFT)

        # Progress bar
        self.progress = ttk.Progressbar(self.root, length=450, mode='determinate')
        self.progress.pack()

        # Start button
        Button(self.root, text="Start", command=self.process_textures, width=25).pack(pady=10)

    def browse_folder(self):
        """Open file dialog to select a folder."""
        folder_selected = filedialog.askdirectory()
        self.folder_path.set(folder_selected)

    def process_textures(self):
        """Process all found textures."""
        folder = self.folder_path.get()
        if not folder:
            messagebox.showwarning("Warning", "Please select a valid addon folder!")
            return

        valid, layout_path = validate_addon_folder(folder)
        if not valid:
            messagebox.showwarning("Warning", "Selected folder is not a valid MSFS addon folder!")
            return

        self.textures = find_textures(folder)
        if not self.textures:
            messagebox.showwarning("Warning", "This addon is already optimized.")
            return

        total_textures = len(self.textures)
        self.progress["value"] = 0
        self.progress["maximum"] = total_textures

        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(optimize_texture, filepath)
                for filepath, _ in self.textures
            ]

            for future in as_completed(futures):
                future.result()
                self.progress["value"] += 1
                self.progress.update()

        subprocess.run(
            ["MSFSLayoutGenerator.exe", layout_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        messagebox.showinfo("Success", "Addon has been successfully optimized.")

if __name__ == "__main__":
    root = Tk()
    app = TextureResizerApp(root)
    root.mainloop()
