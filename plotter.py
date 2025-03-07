import glob
import os
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import concurrent.futures


def plotting(filename, output_folder):
    data = np.loadtxt(filename, delimiter="\t", skiprows=6)
    x_axis = data[:, 0].astype(int)  # First column as integers
    y_axis = data[:, 1]

    x_axis = np.array(x_axis)
    y_axis = np.array(y_axis)

    plt.figure(figsize=(20, 9))
    plt.plot(x_axis, y_axis)
    plt.title(f"Plot for {Path(filename).name}")
    
    plt.grid(which='both', color='green', linestyle='--', linewidth=0.5)

    # Minor Grid LInes
    plt.minorticks_on()  
    plt.grid(which='minor', color='blue', linestyle=':', linewidth=0.5) 

    # Dynamic adjustment based off dataset
    plt.xlim([min(x_axis), max(x_axis)])  
    plt.ylim([min(y_axis), max(y_axis)])
    
    output_file = os.path.join(output_folder, f"{Path(filename).stem}.png")

    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()



# main
curr_dir = os.path.dirname(os.path.realpath(__file__))

for (root, dirs, files) in os.walk(curr_dir):
    # Only read text files and plot it
    # Plots are saved in the same directory as the text files
    for file in files:
        if (file.endswith(".txt")):
            # Print to test efficiency
            print(file)
            filepath = os.path.join(root, file)
            output_folder = os.path.join(root, "Plots")
            Path(output_folder).mkdir(exist_ok=True)
            plotting(filepath, output_folder)
            
# def process_file(file):
#     filepath = os.path.join(root, file)
#     output_folder = os.path.join(root, "Plots")
#     Path(output_folder).mkdir(exist_ok=True)
#     print(filepath)
#     plotting(filepath, output_folder)

# with concurrent.futures.ThreadPoolExecutor() as executor:
#     for (root, dirs, files) in os.walk(curr_dir):
#         txt_files = [file for file in files if file.endswith(".txt")]
#         executor.map(process_file, txt_files)




