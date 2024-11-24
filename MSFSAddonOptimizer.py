import os, subprocess
from tkinter import *
from tkinter import messagebox, filedialog, ttk
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed

VERSION = "v1.1"


def validate_addon_folder(folder):
    layout_path = os.path.join(folder, "layout.json")
    manifest_path = os.path.join(folder, "manifest.json")
    return os.path.isfile(layout_path) and os.path.isfile(manifest_path), layout_path


def find_textures(folder):
    images = []
    for dirpath, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(".dds"):
                try:
                    filepath = os.path.join(dirpath, file)
                    with Image.open(filepath) as image:
                        images.append((filepath, image.size))
                except Exception as e:
                    print(f"Error reading {file}: {e}")
    return images


def optimize_texture(filepath):
    try:
        with Image.open(filepath) as image:
            while image.width >= 8192 or image.height >= 8192:
                width = round(image.width / 2)
                height = round(image.height / 2)
                image = image.resize((width, height))

            subprocess.run(
                [
                    "texconv.exe",
                    filepath,
                    "-w", str(image.width),
                    "-h", str(image.height),
                    "-o", os.path.dirname(filepath),
                    "-y",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            return f"{width}x{height}"
    except:
        return None


class TextureResizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"MSFS Addon Optimizer ({VERSION})")
        self.root.geometry("500x500")
        self.root.resizable(False, False)

        self.folder_path = StringVar()
        self.textures = []

        self.create_widgets()

    def create_widgets(self):
        frame = Frame(self.root)
        frame.pack(pady=15)
        Label(frame, text=f"MSFS Addon Optimizer ({VERSION})", font=("Helvetica", 16, "bold")).pack()
        Label(frame, text="Publisher: aaMasih    |    Developed by Creepcomp", font=("Helvetica", 8)).pack()

        folder_frame = Frame(self.root)
        folder_frame.pack(padx=10, pady=5)
        Entry(folder_frame, textvariable=self.folder_path, width=60).pack(side=LEFT, padx=(0, 5))
        Button(folder_frame, text="Browse", command=self.browse_folder).pack(side=LEFT)

        tree_frame = Frame(self.root)
        tree_frame.pack(padx=10, pady=5, fill="both", expand=True)
        tree_scroll = Scrollbar(tree_frame, orient="vertical")
        tree_scroll.pack(side=RIGHT, fill=Y)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Filename", "Size"),
            show="headings",
            yscrollcommand=tree_scroll.set,
        )
        self.tree.heading("Filename", text="Filename")
        self.tree.column("Filename", width=300)
        self.tree.heading("Size", text="Size")
        self.tree.column("Size", width=150)
        self.tree.pack(side=LEFT, fill="both", expand=True)
        tree_scroll.config(command=self.tree.yview)

        self.progress = ttk.Progressbar(self.root, length=500, mode="determinate")
        self.progress.pack(padx=10, pady=5)

        action_frame = Frame(self.root)
        action_frame.pack(pady=(5, 10))
        Button(action_frame, text="Scan", command=self.scan_textures).pack(side=LEFT, padx=(0, 5))
        Button(action_frame, text="Start", command=self.process_textures, width=15).pack(side=LEFT, padx=(0, 5))
        Button(action_frame, text="Clear", command=self.clear_list).pack(side=LEFT)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        self.folder_path.set(folder_selected)

    def scan_textures(self):
        self.clear_list()
        folder = self.folder_path.get()
        if not folder:
            messagebox.showwarning("Warning", "Please select a valid addon folder!")
            return

        valid, _ = validate_addon_folder(folder)
        if not valid:
            messagebox.showwarning("Warning", "Selected folder is not a valid MSFS addon folder!")
            return
        
        textures = find_textures(folder)
        textures.sort(key=lambda x: int(x[1][0]) * int(x[1][1]), reverse=True)
        
        for filepath, size in textures:
            filename = os.path.basename(filepath)
            self.tree.insert("", "end", values=(filename, f"{size[0]}x{size[1]}"))
            if size[0] >= 8192 or size[1] >= 8192:
                self.textures.append((filepath, size))

    def clear_list(self):
        self.textures = []
        for item in self.tree.get_children():
            self.tree.delete(item)

    def process_textures(self):
        folder = self.folder_path.get()
        if not folder:
            messagebox.showwarning("Warning", "Please select a valid addon folder!")
            return

        valid, layout_path = validate_addon_folder(folder)
        if not valid:
            messagebox.showwarning("Warning", "Selected folder is not a valid MSFS addon folder!")
            return

        if not self.textures:
            messagebox.showwarning("Warning", "No large textures to process. Please scan first!")
            return

        total_textures = len(self.textures)
        self.progress["value"] = 0
        self.progress["maximum"] = total_textures

        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(optimize_texture, filepath): (idx, filepath)
                for idx, (filepath, _) in enumerate(self.textures)
            }

            for future in as_completed(futures):
                result = future.result()
                idx, filepath = futures[future]
                filename = os.path.basename(filepath)
                
                if result:
                    self.tree.item(self.tree.get_children()[idx], values=(filename, result))
                    
                self.progress["value"] += 1
                self.progress.update()

        subprocess.run(
            ["MSFSLayoutGenerator.exe", layout_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

        messagebox.showinfo("Success", "Addon has been successfully optimized.")


if __name__ == "__main__":
    root = Tk()
    app = TextureResizerApp(root)
    root.mainloop()
