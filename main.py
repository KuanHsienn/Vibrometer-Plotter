#import pyuff module to analyse UFF file from Vibrometer
import pyuff
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import numpy as np
import data_tools as dt
import glob
import os
from tkinter import filedialog, messagebox, Tk
from measurement_plane import Measurement_Plane
from surface_average_comparison import Compare_Surface_Average
from device import Device


#types of graphs extracted and also the transfer functions to be produced
graph_types = ["Vibration Displacement", "Vibration Velocity", "Vibration Acceleration", "Ref1", "Ref2", "Ref3", "H1 Vibration Ref1", "H2 Vibration Ref1", "Vibration Ref1", "Vibration Ref2", "Vibration Ref3"]
short_graph_types = ["disp", "vib", "acc", "ref1", "ref2", "ref3", "h1vibref1", "h2vibref1", "vibref1", "vibref2", "vibref3"]

#python terminal user interface

#loop until user gives valid input
valid = False

while not valid:

    valid = True

    #print options
    print()
    print("Chooes what type of measurement to process")
    print("1: Single measurement")
    print("2: Compare measurements")
    print("3: Export all measurements for a device to a HXML file")

    #get user choice
    user_measurement_choice = input("Key in number of the task to perform: ")

    #match case only works for Python 3.10 and above
    #currently using Python 3.12
    match user_measurement_choice:
        
        #single measurement
        case "1":
            
            #use this to get the message box and file dialog to show as top windows later
            window = Tk()
            window.wm_attributes('-topmost', 1)
            
            #suppress the Tk window
            window.withdraw()

            #display a message box
            messagebox.showinfo("Choose Scan Data Measurement File", "Please select the measurement file with extension .uff", parent =window)
            
            #open file explorer for user to select one measurement file and get filepath of selected file
            #start file explorer in laser_vibrometer_scans folder in current directory
            #update the relative path link for initial_dir if the structure of the directory changes
            selected_filepath = filedialog.askopenfilename(parent = window, initialdir = "C:\\Git_Repos_Azure\\EAD_SG\\Measurement\\LaserVibrometerPythonAnalyser\\laser_vibrometer_scans")


            #create measurement object from the measurement file
            measurement = Measurement_Plane(selected_filepath)

            #loop until user gives a valid input
            valid1 = False

            while not valid1:
                
                valid1 = True

                #print options
                print()
                print("Choose what type of task to perform")
                print("1: Display a graph")
                print("2: Export a graph as a HXML file")
                
                #get user choice
                user_task_choice = input("Key in number of the task to perform: ")

                #repeat user input prompt if invalid input
                if user_task_choice not in ("1", "2"):
                    
                    print("Unknown option, please key in a valid option number")

                    valid1 = False


            #create a list of all the scan point numbers
            scan_point_numbers = []
            for index in range(measurement.number_of_scan_points):

                scan_point_numbers.append(index+1)


            #loop until user gives a valid input
            valid2 = False

            while not valid2:
                
                valid2 = True

                #print options
                print()
                print("Choose units for the graph")
                print("1: Raw data in SI Units")
                print("2: Decibel")
                
                #get user choice
                user_unit_choice = input("Key in option number: ")

                #repeat user input prompt if invalid input
                if user_unit_choice not in ("1", "2"):
                    
                    print("Unknown option, please key in a valid option number")

                    valid2 = False


            #loop until user gives a valid input
            valid3 = False

            while not valid3:
            
                valid3 = True

                #print options
                print()
                print("Choose an option")
                print("1: Surface Average Graph")

                #print one option for each scan point in the measurement
                for point_no in scan_point_numbers:

                    option_no = point_no + 1

                    print(f"{option_no}: Scan Point {point_no}")
                
                #get user choice
                user_point_choice = input("Key in number of the task to perform: ")

                match user_point_choice:
                    
                    #surface average graph
                    case "1":
                            
                        #print options
                        print()
                        print("Choose graph")

                        #iterate through all the graph types and print an option for each one
                        for index in range(len(graph_types)):

                            print(f"{index+1}: {graph_types[index]}")

                        #user choice
                        graph_choice = input("Key in number of the graph: ")

                        #array of valid option numbers in integers
                        valid_options_int = range(len(graph_types)+1)

                        #convert all the option numbers into strings and create a list
                        valid_options_str = [str(number) for number in valid_options_int]

                        #if the choice is a valid option number
                        if graph_choice in valid_options_str:

                            #convert the choice number to an integer
                            choice = int(graph_choice)

                            #get index
                            choice_index = choice - 1

                            #display graph
                            if user_task_choice == "1":

                                #raw units
                                if user_unit_choice == "1":

                                    measurement.get_average(short_graph_types[choice_index]).plot_graph()

                                #decibel
                                else:

                                    measurement.get_average(f"{short_graph_types[choice_index]}_db").plot_graph()

                            #export
                            else:

                                #raw units
                                if user_unit_choice == "1":

                                    measurement.get_average(short_graph_types[choice_index]).export_graph()

                                #decibel
                                else:

                                    measurement.get_average(f"{short_graph_types[choice_index]}_db").export_graph()


                        #invalid input
                        else:

                                print("Unknown option, please key in a valid option number")

                                valid3 = False
                        


                    #valid scan point number choice
                    case _ if user_point_choice in [str(scan_p_no+1) for scan_p_no in scan_point_numbers]:
                        
                        #calculate selected scan point number
                        selected_scan_point_no = int(user_point_choice) - 1
                        
                        #get selected scan point object
                        selected_scan_point = measurement.scanpoints[selected_scan_point_no-1]

                        #get list of graphs for selected scan point
                        scan_point_graphs = selected_scan_point.scan_point_all_graphs

                        #loop until user gives a valid input
                        valid4 = False

                        while not valid4:
                        
                            valid4 = True

                            #print options
                            print()
                            print("Choose graph")
                            
                            #iterate through all the graph types and print an option for each one
                            for index in range(len(graph_types)):

                                print(f"{index+1}: {graph_types[index]}")

                            
                            graph_choice = input("Key in number of the graph: ")

                            match graph_choice:
                                
                                #disp
                                case "1":
                                    
                                    #display graph
                                    if user_task_choice == "1":
                                        
                                        #raw units
                                        if user_unit_choice == "1":

                                            selected_scan_point.disp.plot_graph()

                                        #decibel
                                        else:

                                            selected_scan_point.create_disp_decibel().plot_graph()

                                    #export
                                    else:

                                        #raw units
                                        if user_unit_choice == "1":

                                            selected_scan_point.disp.export_graph()

                                        #decibel
                                        else:

                                            selected_scan_point.create_disp_decibel().export_graph()

                                #vib
                                case "2":
                                    
                                    #display graph
                                    if user_task_choice == "1":
                                        
                                        #raw units
                                        if user_unit_choice == "1":

                                            selected_scan_point.vib.plot_graph()

                                        #decibel
                                        else:

                                            selected_scan_point.create_vib_decibel().plot_graph()

                                    #export
                                    else:

                                        #raw units
                                        if user_unit_choice == "1":

                                            selected_scan_point.vib.export_graph()

                                        #decibel
                                        else:

                                            selected_scan_point.create_vib_decibel().export_graph()

                                #acc
                                case "3":
                                    
                                    #display graph
                                    if user_task_choice == "1":
                                        
                                        #raw units
                                        if user_unit_choice == "1":

                                            selected_scan_point.acc.plot_graph()

                                        #decibel
                                        else:

                                            selected_scan_point.create_acc_decibel().plot_graph()

                                    #export
                                    else:

                                        #raw units
                                        if user_unit_choice == "1":

                                            selected_scan_point.acc.export_graph()

                                        #decibel
                                        else:

                                            selected_scan_point.create_acc_decibel().export_graph()

                                #ref1  
                                case "4":
                                    
                                    #display graph
                                    if user_task_choice == "1":
                                        
                                        #raw units
                                        if user_unit_choice == "1":

                                            selected_scan_point.ref1.plot_graph()

                                        #decibel
                                        else:

                                            selected_scan_point.create_ref1_decibel().plot_graph()

                                    #export
                                    else:

                                        #raw units
                                        if user_unit_choice == "1":

                                            selected_scan_point.ref1.export_graph()

                                        #decibel
                                        else:

                                            selected_scan_point.create_ref1_decibel().export_graph()

                                #ref2    
                                case "5":
                                    
                                    #display graph
                                    if user_task_choice == "1":

                                        #raw units
                                        if user_unit_choice == "1":

                                            selected_scan_point.ref2.plot_graph()
                                        
                                        #decibel
                                        else:

                                            selected_scan_point.create_ref2_decibel().plot_graph()

                                    #export
                                    else:

                                        #raw units
                                        if user_unit_choice == "1":

                                            selected_scan_point.ref2.export_graph()

                                        #decibel
                                        else:

                                            selected_scan_point.create_ref2_decibel().export_graph()
                                #ref3
                                case "6": 
                                    
                                    #display graph
                                    if user_task_choice == "1":

                                        #raw units
                                        if user_unit_choice == "1":

                                            selected_scan_point.ref3.plot_graph()

                                        #decibel
                                        else:

                                            selected_scan_point.create_ref3_decibel().plot_graph()

                                    #export
                                    else:

                                        #raw units
                                        if user_unit_choice == "1":

                                            selected_scan_point.ref3.export_graph()
                                        
                                        #decibel
                                        else:

                                            selected_scan_point.create_ref3_decibel().export_graph()

                                #h1vibref1
                                case "7":
                                    
                                    #display graph
                                    if user_task_choice == "1":

                                        #raw units
                                        if user_unit_choice == "1":

                                            selected_scan_point.h1vibref1.plot_graph()

                                        #decibel
                                        else:

                                            selected_scan_point.create_h1vibref1_decibel().plot_graph()

                                    #export
                                    else:

                                        #raw units
                                        if user_unit_choice == "1":

                                            selected_scan_point.h1vibref1.export_graph()

                                        #decibel
                                        else:

                                            selected_scan_point.create_h1vibref1_decibel().export_graph()

                                #h2vibref1    
                                case "8":
                                    
                                    #display graph
                                    if user_task_choice == "1":

                                        #raw units
                                        if user_unit_choice == "1":

                                            selected_scan_point.h2vibref1.plot_graph()

                                        #decibel
                                        else:

                                            selected_scan_point.create_h2vibref1_decibel().plot_graph()

                                    #export
                                    else:

                                        #raw units
                                        if user_unit_choice == "1":

                                            selected_scan_point.h2vibref1.export_graph()

                                        #decibel
                                        else:

                                            selected_scan_point.create_h2vibref1_decibel().export_graph()

                                #vibref1    
                                case "9":
                                    
                                    #display graph
                                    if user_task_choice == "1":

                                        #raw units
                                        if user_unit_choice == "1":

                                            selected_scan_point.create_vibref1().plot_graph()

                                        #decibel
                                        else:

                                            selected_scan_point.create_vibref1_decibel().plot_graph()

                                    #export
                                    else:

                                        #raw units
                                        if user_unit_choice == "1":

                                            selected_scan_point.create_vibref1().export_graph()

                                        #decibel
                                        else:

                                            selected_scan_point.create_vibref1_decibel().export_graph()
                                
                                #vibref2
                                case "10":
                                    
                                    #display graph
                                    if user_task_choice == "1":

                                        #raw units
                                        if user_unit_choice == "1":

                                            selected_scan_point.create_vibref2().plot_graph()

                                        #decibel
                                        else:

                                            selected_scan_point.create_vibref2_decibel().plot_graph()

                                    #export
                                    else:

                                        #raw units
                                        if user_unit_choice == "1":

                                            selected_scan_point.create_vibref2().export_graph()

                                        #decibel
                                        else:

                                            selected_scan_point.create_vibref2_decibel().export_graph()

                                #vibref3    
                                case "11":
                                    
                                    #display graph
                                    if user_task_choice == "1":

                                        #raw units
                                        if user_unit_choice == "1":

                                            selected_scan_point.create_vibref3().plot_graph()

                                        #decibel
                                        else:

                                            selected_scan_point.create_vibref3_decibel().plot_graph()

                                    #export
                                    else:

                                        #raw units
                                        if user_unit_choice == "1":

                                            selected_scan_point.create_vibref3().export_graph()

                                        #decibel
                                        else:

                                            selected_scan_point.create_vibref3_decibel().export_graph()

                                #invalid input
                                case _:

                                    print("Unknown option, please key in a valid option number")

                                    valid4 = False


                    #invalid input
                    case _:

                        print("Unknown option, please key in a valid option number")

                        #get user input again
                        valid3 = False



                        



        #compare measurements
        case "2":

            #loop until user gives a valid input
            valid0 = False

            while not valid0:
                
                valid0 = True

                #print options
                print()
                print("Choose what type of comparison to perform")
                print("1: Surface Average Comparison")
                print("2: Band Average Comparison")
                
                #get user choice
                user_average_choice = input("Key in number of the task to perform: ")

                match user_average_choice:
                    
                    #surface average comparison
                    case "1":

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
                        selected_filepaths = filedialog.askopenfilenames(parent = window, initialdir = "C:\\Git_Repos_Azure\\EAD_SG\\Measurement\\LaserVibrometerPythonAnalyser\\laser_vibrometer_scans")


                        #loop until user gives a valid input
                        valid1 = False

                        while not valid1:
                            
                            valid1 = True

                            #print options
                            print()
                            print("Choose what type of task to perform")
                            print("1: Display comparison graph")
                            print("2: Export all selected surface average graphs in a HXML file for comparison")
                            
                            #get user choice
                            user_task_choice = input("Key in number of the task to perform: ")

                            #repeat user input prompt if invalid input
                            if user_task_choice not in ("1", "2"):
                                
                                print("Unknown option, please key in a valid option number")

                                valid1 = False


                        #loop until user gives a valid input
                        valid2 = False

                        while not valid2:
                            
                            valid2 = True

                            #print options
                            print()
                            print("Choose units for the graph")
                            print("1: Raw data in SI Units")
                            print("2: Decibel")
                            
                            #get user choice
                            user_unit_choice = input("Key in option number: ")

                            #repeat user input prompt if invalid input
                            if user_unit_choice not in ("1", "2"):
                                
                                print("Unknown option, please key in a valid option number")

                                valid2 = False


                        #loop until user gives a valid input
                        valid3 = False

                        while not valid3:
                        
                            valid3 = True

                            #print options
                            print()
                            print("Choose graph to compare")
                            
                            #iterate through all the graph types and print an option for each one
                            for index in range(len(graph_types)):

                                print(f"{index+1}: {graph_types[index]}")

                            #user choice
                            graph_choice = input("Key in number of the graph: ")

                            #array of valid option numbers in integers
                            valid_options_int = range(len(graph_types)+1)

                            #convert all the option numbers into strings and create a list
                            valid_options_str = [str(number) for number in valid_options_int]

                            #if the choice is a valid option number
                            if graph_choice in valid_options_str:

                                #convert the choice number to an integer
                                choice = int(graph_choice)

                                #get index
                                choice_index = choice - 1

                                #display plot
                                if user_task_choice == "1":

                                    #raw units
                                    if user_unit_choice == "1":

                                        comparison_obj = Compare_Surface_Average(selected_filepaths, short_graph_types[choice_index])

                                        comparison_obj.compare_surface_average_plot()

                                    #decibel
                                    else:

                                        comparison_obj = Compare_Surface_Average(selected_filepaths, f"{short_graph_types[choice_index]}_db")

                                        comparison_obj.compare_surface_average_plot()

                                #export
                                else:

                                    #raw units
                                    if user_unit_choice == "1":

                                        comparison_obj = Compare_Surface_Average(selected_filepaths, short_graph_types[choice_index])

                                        comparison_obj.compare_surface_average_export()

                                    #decibel
                                    else:

                                        comparison_obj = Compare_Surface_Average(selected_filepaths, f"{short_graph_types[choice_index]}_db")

                                        comparison_obj.compare_surface_average_export()


                            #invalid input
                            else:

                                    print("Unknown option, please key in a valid option number")

                                    valid3 = False


                    #band average comparison
                    case "2":

                        #use this to get the message box and file dialog to show as top windows later
                        window = Tk()
                        window.wm_attributes('-topmost', 1)
                        
                        #suppress the Tk window
                        window.withdraw()

                        #display a message box
                        messagebox.showinfo("Choose Scan Data Measurement File", "Please select the measurement file with extension .uff", parent =window)
                        
                        #open file explorer for user to select one measurement file and get filepath of selected file
                        #start file explorer in laser_vibrometer_scans folder in current directory
                        #update the relative path link for initial_dir if the structure of the directory changes
                        selected_filepath = filedialog.askopenfilename(parent = window, initialdir = "C:\\Git_Repos_Azure\\EAD_SG\\Measurement\\LaserVibrometerPythonAnalyser\\laser_vibrometer_scans")

                        #create measurement object from the measurement file
                        measurement = Measurement_Plane(selected_filepath)


                        #loop until user gives a valid input
                        valid1 = False

                        while not valid1:
                            
                            valid1 = True

                            #print options
                            print()
                            print("Choose what type of task to perform")
                            print("1: Display comparison graph")
                            print("2: Export all selected surface average graphs in a HXML file for comparison")
                            
                            #get user choice
                            user_task_choice = input("Key in number of the task to perform: ")

                            #repeat user input prompt if invalid input
                            if user_task_choice not in ("1", "2"):
                                
                                print("Unknown option, please key in a valid option number")

                                valid1 = False


                        #loop until user gives a valid input
                        valid2 = False

                        while not valid2:
                            
                            valid2 = True

                            #print options
                            print()
                            print("Choose units for the graph")
                            print("1: Raw data in SI Units")
                            print("2: Decibel")
                            
                            #get user choice
                            user_unit_choice = input("Key in option number: ")

                            #repeat user input prompt if invalid input
                            if user_unit_choice not in ("1", "2"):
                                
                                print("Unknown option, please key in a valid option number")

                                valid2 = False


                        #loop until user gives a valid input
                        valid3 = False

                        while not valid3:
                        
                            valid3 = True

                            #print options
                            print()
                            print("Choose graph to compare")
                            
                            #iterate through all the graph types and print an option for each one
                            for index in range(len(graph_types)):

                                print(f"{index+1}: {graph_types[index]}")

                            #user choice
                            graph_choice = input("Key in number of the graph: ")

                            #array of valid option numbers in integers
                            valid_options_int = range(len(graph_types)+1)

                            #convert all the option numbers into strings and create a list
                            valid_options_str = [str(number) for number in valid_options_int]

                            #if the choice is a valid option number
                            if graph_choice in valid_options_str:

                                #convert the choice number to an integer
                                choice = int(graph_choice)

                                #get index
                                choice_index = choice - 1

                                #display plot
                                if user_task_choice == "1":

                                    #raw units
                                    if user_unit_choice == "1":

                                        measurement.compare_band_averages_plot(f"{short_graph_types[choice_index]}")

                                    #decibel
                                    else:

                                        measurement.compare_band_averages_plot(f"{short_graph_types[choice_index]}_db")

                                #export
                                else:

                                    #raw units
                                    if user_unit_choice == "1":

                                        measurement.compare_band_averages_export(f"{short_graph_types[choice_index]}")

                                    #decibel
                                    else:

                                        measurement.compare_band_averages_export(f"{short_graph_types[choice_index]}_db")


                            #invalid input
                            else:

                                    print("Unknown option, please key in a valid option number")

                                    valid3 = False
                                    

                    #invalid input
                    case _:

                        print("Unknown option, please key in a valid option number")

                        #get user input again
                        valid0 = False


            
        #export all measurements for a device
        case "3":

            #use this to get the message box and file dialog to show as top windows later
            window = Tk()
            window.wm_attributes('-topmost', 1)

            #suppress the Tk window
            window.withdraw()

            #display a message box
            messagebox.showinfo("Choose Scan Data Measurement Files", "Please hold down CTRL key and select the measurement files with extension .uff of all the scan surfaces from the same device", parent =window)

            #open file explorer for user to select multiple measurement files and get list of filepaths of selected files
            #start file explorer in laser_vibrometer_scans folder in current directory
            #update the relative path link for initial_dir if the structure of the directory changes
            device_list_planes_filepaths = filedialog.askopenfilenames(parent = window, initialdir = "C:\\Git_Repos_Azure\\EAD_SG\\Measurement\\LaserVibrometerPythonAnalyser\\laser_vibrometer_scans")

            #create device object
            device = Device(device_list_planes_filepaths)

            #export device data to HXML
            device.export()

        
        #invalid input
        case _:
            
            print("Unknown option, please key in a valid option number")

            #get user input again
            valid = False
