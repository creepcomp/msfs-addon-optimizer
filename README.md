# MSFS Addon Optimizer (v1.0)

MSFS Addon Optimizer is a Python-based GUI tool designed to optimize large `.dds` textures in Microsoft Flight Simulator (MSFS) addons. It helps reduce texture sizes while maintaining compatibility, improving performance and storage usage.

---

## Features
- Identifies `.dds` textures in MSFS addon folders with resolutions ≥ 8192x8192.
- Automatically resizes oversized textures to optimize performance.
- Verifies addon folder structure (checks for `layout.json` and `manifest.json`).
- Updates the `layout.json` file using `MSFSLayoutGenerator.exe` for compatibility.
- User-friendly interface with progress tracking.

---

## Requirements
1. **Python** (3.9 or later)
2. **Dependencies**:
   - `Pillow`
   - `tkinter`
   - `concurrent.futures`
3. **Tools**:
   - `texconv.exe` (DirectX Texture Tool)
   - `MSFSLayoutGenerator.exe` (available for MSFS developers)

---

## Installation

1. Clone or download this repository.
2. Install the required Python dependencies using:
   ```bash
   pip install pillow
   ```
3. Ensure `texconv.exe` and `MSFSLayoutGenerator.exe` are in the same directory as the script or accessible via the system PATH.

---

## Usage

1. Run the program:
   ```bash
   python MSFSAddonOptimizer.py
   ```
2. Browse and select the folder containing the MSFS addon you want to optimize.
3. Click **Start** to begin the optimization process.
4. The tool will:
   - Identify oversized textures.
   - Resize them automatically.
   - Update the `layout.json` file.
5. A success message will appear once the process is complete.

---

## File Structure

### Expected MSFS Addon Folder Layout
- `layout.json` (required)
- `manifest.json` (required)
- `SimObjects/` (or other addon-specific subfolders)

### Output
- Resized `.dds` textures saved in their original locations.
- Updated `layout.json`.

---

## Limitations
- Only supports `.dds` textures.
- Textures smaller than 8192x8192 are skipped.
- Requires `texconv.exe` for resizing operations.

---

## Credits
- **Developer**: Coded by `Creepcomp`
- **Publisher**: `aaMasih`

---

## License
This project is open-source. Feel free to modify and share, but please provide attribution to the original authors.

--- 

For any issues or suggestions, please create an issue or reach out. Happy flying! ✈️