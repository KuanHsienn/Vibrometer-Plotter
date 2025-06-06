# Laser Vibrometer Analyzer 

## Introduction
This GUI application provides a user-friendly interface to analyze and visualize Laser Vibrometer `.uff` scan files. It simplifies interaction with the underlying data processing, allowing users to load scans, view layouts, and export visualizations without using command-line tools.

---

## Requirements

- Python 3.10 or above (tested with Python 3.12)
- Required packages listed in `requirements.txt`
- GUI assets: `house.png`, `Left_Arrow.png`, `Right_Arrow.png`, and `gui.ico` (included in the project folder)

---

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   
## Running the CLI

1. **Start the CLI application:**

   ```bash
   python main.py

## Running the GUI

1. **Start the GUI application:**

   ```bash
   python gui.py

The application window will launch, allowing you to:

- Load and browse Laser Vibrometer scan files
- Visualize scan points and bands with color differentiation
- Annotate points and display anomalous data
- Export visualizations as high-resolution images

 ## Packaging the GUI as an Executable

To distribute the GUI as a standalone executable (no Python install required):

1. Use PyInstaller to build the executable:
   ``` bash
   python -m PyInstaller --clean --onefile --windowed gui.py --icon=gui.ico --add-data "house.png;." --add-data "Left_Arrow.png;." --add-data "Right_Arrow.png;." --name "Laser Vibrometer"
2. The executable will be found in the `dist` folder after the build completes
3. Distribute the `.exe` to users, who can run it directly without installing Python or other dependencies

## Notes on Icons and Assets
- Icon file (`gui.ico`) should be 256*256 pixels or smaller for best compatibility
- Image assets must be included in PyInstaller's `--add-data` option for proper packaging
- The program references images relative to the executable location to ensure they load correctly
