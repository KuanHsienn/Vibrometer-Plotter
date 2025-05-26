import os
from tkinter import filedialog, messagebox, Toplevel, Tk

'''convenience tool, independent of the other laser vibro code. run separately'''


def capitalise_words(words):
    words_without_extension = words[:-4]
    words_array = words_without_extension.split("_")
    new_words_array = []

    for word in words_array:
        if word.isalpha():
            new_words_array.append(word[0].capitalize() + word[1:])

        else:
            new_words_array.append(word)

        #print(new_words_array)
    
    new_word = new_words_array[0]

    for i in range(1, len(new_words_array)):
        new_word = new_word + " " + new_words_array[i]

    new_word = new_word + ".uff"

    return new_word



name = "C:\\Users\\AU0018DS\\OneDrive - WSA\\Desktop\\Luna P\\export 2\\RAI_Diaphragm-Up_ear_hook_left_Lucas.uff"
#print(os.path.dirname("C:\\Users\\AU0018DS\\OneDrive - WSA\\Desktop\\Luna P\\export 2\\RAI_Diaphragm-Up_ear_hook_left_Lucas.uff"))
#print(os.path.basename("C:\\Users\\AU0018DS\\OneDrive - WSA\\Desktop\\Luna P\\export 2\\RAI_Diaphragm-Up_ear_hook_left_Lucas.uff"))

def rename_file(name):

    directory_name = os.path.dirname(name)

    filename = os.path.basename(name)
    #print(filename)

    try:
        new_filename_1 = filename.replace("_Lucas", "")
        #print(new_filename_1)

    except:
         pass

    new_filename_2 = capitalise_words(new_filename_1)

    #print(new_filename_2)

    new_filepath = directory_name + "\\" + new_filename_2

    print(new_filepath)

    return new_filepath

#use this to get the message box and file dialog to show as top windows later
window = Tk()
window.wm_attributes('-topmost', 1)

#suppress the Tk window
window.withdraw()

#display a message box
messagebox.showinfo("Choose Scan Data Measurement Files", "Please hold down CTRL key and select all the files for renaming", parent =window)

#open file explorer for user to select multiple measurement files and get list of filepaths of selected files
#start file explorer in laser_vibrometer_scans folder in current directory
#update the relative path link for initial_dir if the structure of the directory changes
selected_filepaths = filedialog.askopenfilenames(parent = window)

for filepath in selected_filepaths:

    os.rename(filepath, rename_file(filepath))


'''#use this to get the message box and file dialog to show as top windows later
window = Tk()
window.wm_attributes('-topmost', 1)

#suppress the Tk window
window.withdraw()

#display a message box
messagebox.showinfo("Choose Scan Data Measurement Files", "Please hold down CTRL key and select all the measurement files with extension .uff for comparison of their surface averages", parent =window)

#open file explorer for user to select multiple measurement files and get list of filepaths of selected files
#start file explorer in laser_vibrometer_scans folder in current directory
#update the relative path link for initial_dir if the structure of the directory changes
selected_filepaths_concept_rename_1 = filedialog.askopenfilenames(parent = window)

for filepath in selected_filepaths_concept_rename_1:

    new_name = filepath.replace("Receiver Box 1", "Concept B Sample 1")
    os.rename(filepath, new_name)


#use this to get the message box and file dialog to show as top windows later
window = Tk()
window.wm_attributes('-topmost', 1)

#suppress the Tk window
window.withdraw()

#display a message box
messagebox.showinfo("Choose Scan Data Measurement Files", "Please hold down CTRL key and select all the measurement files with extension .uff for comparison of their surface averages", parent =window)

#open file explorer for user to select multiple measurement files and get list of filepaths of selected files
#start file explorer in laser_vibrometer_scans folder in current directory
#update the relative path link for initial_dir if the structure of the directory changes
selected_filepaths_concept_rename_2 = filedialog.askopenfilenames(parent = window)

for filepath in selected_filepaths_concept_rename_2:

    new_name = filepath.replace("Receiver Box 2", "Concept B Sample 2")
    os.rename(filepath, new_name)'''


'''#use this to get the message box and file dialog to show as top windows later
window = Tk()
window.wm_attributes('-topmost', 1)

#suppress the Tk window
window.withdraw()

#display a message box
messagebox.showinfo("Choose Scan Data Measurement Files", "Please hold down CTRL key and select all the measurement files with extension .uff for comparison of their surface averages", parent =window)

#open file explorer for user to select multiple measurement files and get list of filepaths of selected files
#start file explorer in laser_vibrometer_scans folder in current directory
#update the relative path link for initial_dir if the structure of the directory changes
selected_filepaths_concept_rename_2 = filedialog.askopenfilenames(parent = window)

for filepath in selected_filepaths_concept_rename_2:

    new_name = filepath.replace("RAI", "RAI Diaphragm-Side")
    os.rename(filepath, new_name)'''