#import pyuff module to analyse UFF file from Vibrometer
import pyuff
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import numpy as np
import glob
import os
import re
from tkinter import filedialog, messagebox, Tk
from measurement_plane import Measurement_Plane
from scan_point_graph import Graph_average, Graph_average_all
from surface_average_comparison import Compare_Surface_Average
from hxml_writer import HXMLGenerator
import data_tools as dt


class Device:

    def __init__(self, list_planes_filepaths):
        
        #attribute storing list of filepaths of planes
        self.list_filepaths = list_planes_filepaths

        #attribute storing list of filenames
        self.list_filenames = [os.path.basename(filepath) for filepath  in self.list_filepaths]

        #attribute to store list of all the Measurement_Plane objects for the device in predefined order
        self.all_surfaces = []

        #attribute to store list of surface types included in this device not in a particular order
        self.surface_types = []


        #iterate through all the measurement planes
        #filters them and saves them as the respective attribute
        #filter from most complex names to simpler names to prevent falsely identifying ear_hook_top as top for example
        #by checking for ear_hook_top first, if it does not get identified it can only be top upper/lower or top
        #assumes each filepath is a distinct surface of the same device
        for index in range(len(self.list_filepaths)):

            if "ear_hook_top" in self.list_filenames[index].lower() or "ear hook top" in self.list_filenames[index].lower():
                
                #save attribute
                self.ear_hook_top = Measurement_Plane(self.list_filepaths[index])

                #append surface type to self.surface_types list
                self.surface_types.append("ear_hook_top")


            elif "ear_hook_left" in self.list_filenames[index].lower() or "ear hook left" in self.list_filenames[index].lower():
                
                #save attribute
                self.ear_hook_left = Measurement_Plane(self.list_filepaths[index])

                #append surface type to self.surface_types list
                self.surface_types.append("ear_hook_left")


            elif "ear_hook_right" in self.list_filenames[index].lower() or "ear hook right" in self.list_filenames[index].lower():
                
                #save attribute
                self.ear_hook_right = Measurement_Plane(self.list_filepaths[index])

                #append surface type to self.surface_types list
                self.surface_types.append("ear_hook_right")
            

            elif "top_upper" in self.list_filenames[index].lower() or "top upper" in self.list_filenames[index].lower():
                
                #save attribute
                self.top_upper = Measurement_Plane(self.list_filepaths[index])

                #append surface type to self.surface_types list
                self.surface_types.append("top_upper")


            elif "top_lower" in self.list_filenames[index].lower() or "top lower" in self.list_filenames[index].lower():
                
                #save attribute
                self.top_lower = Measurement_Plane(self.list_filepaths[index])

                #append surface type to self.surface_types list
                self.surface_types.append("top_lower")


            #note that this condition will only be possible if no variation of top upper was found in the filename
            elif "top" in self.list_filenames[index].lower():
                
                #save attribute
                self.top = Measurement_Plane(self.list_filepaths[index])

                #append surface type to self.surface_types list
                self.surface_types.append("top")

            
            elif "left" in self.list_filenames[index].lower():
                
                #save attribute
                self.left = Measurement_Plane(self.list_filepaths[index])

                #append surface type to self.surface_types list
                self.surface_types.append("left")

            
            elif "right" in self.list_filenames[index].lower():
                
                #save attribute
                self.right = Measurement_Plane(self.list_filepaths[index])

                #append surface type to self.surface_types list
                self.surface_types.append("right")


            else:

                pass



        #append surface to self.all_surfaces list in correct order and based on what surfaces are provided

        if "top" in self.surface_types:

            #append surface to self.all_surfaces list
            self.all_surfaces.append(self.top)


        if "top_upper" in self.surface_types:

            #append surface to self.all_surfaces list
            self.all_surfaces.append(self.top_upper)


        if "top_lower" in self.surface_types:

            #append surface to self.all_surfaces list
            self.all_surfaces.append(self.top_lower)


        if "left" in self.surface_types:

            #append surface to self.all_surfaces list
            self.all_surfaces.append(self.left)


        if "right" in self.surface_types:

            #append surface to self.all_surfaces list
            self.all_surfaces.append(self.right)


        if "ear_hook_top" in self.surface_types:

            #append surface to self.all_surfaces list
            self.all_surfaces.append(self.ear_hook_top)


        if "ear_hook_left" in self.surface_types:

            #append surface to self.all_surfaces list
            self.all_surfaces.append(self.ear_hook_left)


        if "ear_hook_right" in self.surface_types:

            #append surface to self.all_surfaces list
            self.all_surfaces.append(self.ear_hook_right)
        
         

        #get device name from first scan file
        match_object = re.search("top|left|right|ear", self.all_surfaces[0].scan_name.lower())

        match_index = match_object.start()

        #attribute for device name
        #splice up to one less than the match part in order to remove the space or underscore before the match part as well
        self.device_name = (str(self.all_surfaces[0].scan_name))[:match_index-1]

        #attribute for ref1 device average, only computed when get_ref1_average method is called
        self.ref1_average = None

        #attribute for ref3 device average, only computed when get_ref3_average method is called
        self.ref3_average = None



    def get_ref1_average(self):
        '''Method to create ref1 device average based on all the planes provided. 
        Updates the attribute for ref1 average to a ref1 device average graph object, 
        and also returns the ref1 device average graph object. 
        This averaging assumes no anomalous data for ref1 to save time'''

        #initialise empty list to store all ref1 surface averages
        average_list = []

        #iterate through all the planes to get ref1 surface average of each one
        for plane in self.all_surfaces:
            
            #create a list containing the ref1 graphs for all the scanpoints in the plane
            ref1_average_list = [point.create_ref1_decibel() for point in plane.scanpoints]

            #get ref1 average for the current plane
            #assume no anomalous data
            plane_average = Graph_average(ref1_average_list, [])

            #add the ref1 average for the plane to the list of ref1 averages
            average_list.append(plane_average)


        #get a graph average object that is the average of ref1 for the whole device
        ref1_device_average = Graph_average_all(average_list)

        #save device ref1 average graph object to attribute
        self.ref1_average = ref1_device_average

        #return device ref1 average graph object
        return ref1_device_average
    

    
    def get_ref3_average(self):
        '''Method to create ref3 device average based on all the planes provided. 
        Updates the attribute for ref3 average to a ref3 device average graph object, 
        and also returns the ref3 device average graph object. 
        This averaging assumes no anomalous data for ref3 to save time'''

        #initialise empty list to store all ref3 surface averages
        average_list = []

        #iterate through all the planes to get ref3 surface average of each one
        for plane in self.all_surfaces:
            
            #create a list containing the ref3 graphs for all the scanpoints in the plane
            ref3_average_list = [point.create_ref3_decibel() for point in plane.scanpoints]

            #get ref3 average for the current plane
            #assume no anomalous data
            plane_average = Graph_average(ref3_average_list, [])

            #add the ref3 average for the plane to the list of ref3 averages
            average_list.append(plane_average)


        #get a graph average object that is the average of ref3 for the whole device
        ref3_device_average = Graph_average_all(average_list)

        #save device ref3 average graph object to attribute
        self.ref3_average = ref3_device_average

        #return device ref3 average graph object
        return ref3_device_average



    def export(self):

        '''
        Export into one HXML file with structure (each with anomalous points remarks):
        1. Ref1 (dB) SPL
        
        2. Ref3 (dB) input voltage
        
        3. Vib Vel (dB) surface average top/top upper
        4. Vib Vel (dB) surface average top lower *(if have)
        5. Vib Vel (dB) surface average left
        6. Vib Vel (dB) surface average right
        7. Vib Vel (dB) surface average ear hook top
        8. Vib Vel (dB) surface average ear hook left
        9. Vib Vel (dB) surface average ear hook right
        
        10. VibRef1 (dB) surface average top/top upper
        11. VibRef1 (dB) surface average top lower *(if have)
        12. VibRef1 (dB) surface average left
        13. VibRef1 (dB) surface average right
        14. VibRef1 (dB) surface average ear hook top
        15. VibRef1 (dB) surface average ear hook left
        16. VibRef1 (dB) surface average ear hook right
        
        17. VibRef3 (dB) surface average top/top upper
        18. VibRef3 (dB) surface average top lower *(if have)
        19. VibRef3 (dB) surface average left
        20. VibRef3 (dB) surface average right
        21. VibRef3 (dB) surface average ear hook top
        22. VibRef3 (dB) surface average ear hook left
        23. VibRef3 (dB) surface average ear hook right
        '''

        #initialise empty list for graphs
        graphs_list = []

        #intialise empty list for remarks
        remarks_list = []



        #create ref1 device average
        ref1_average = self.get_ref1_average()

        #append ref1 device average to graphs list
        graphs_list.append(ref1_average)

        #append remarks for ref1 device average to remarks list
        remarks_list.append(ref1_average.remarks)


        #create ref3 device average
        ref3_average = self.get_ref3_average()

        #append ref3 device average to graphs list
        graphs_list.append(ref3_average)

        #append remarks for ref3 device average to remarks list
        remarks_list.append(ref3_average.remarks)


        #create and add all the Vib Vel (dB) surface averages to graphs list and their respective remarks to remarks list
        #iterate through all the surfaces provided
        for surface in self.all_surfaces:
            
            #create vib (dB) surface average for the surface
            surface_vib_average = surface.get_average("vib_db")

            #append vib (dB) surface average to graphs list
            graphs_list.append(surface_vib_average)

            #append remarks for vib (dB) surface average to remarks list
            remarks_list.append(surface_vib_average.remarks)


        #create and add all the VibRef1 (dB) surface averages to graphs list and their respective remarks to remarks list
        #iterate through all the surfaces provided
        for surface in self.all_surfaces:
            
            #create vibref1 (dB) surface average for the surface
            surface_vibref1_average = surface.get_average("vibref1_db")

            #append vibref1 (dB) surface average to graphs list
            graphs_list.append(surface_vibref1_average)

            #append remarks for vibref1 (dB) surface average to remarks list
            remarks_list.append(surface_vibref1_average.remarks)


        #create and add all the VibRef3 (dB) surface averages to graphs list and their respective remarks to remarks list
        #iterate through all the surfaces provided
        for surface in self.all_surfaces:
            
            #create vibref3 (dB) surface average for the surface
            surface_vibref3_average = surface.get_average("vibref3_db")

            #append vibref3 (dB) surface average to graphs list
            graphs_list.append(surface_vibref3_average)

            #append remarks for vibref3 (dB) surface average to remarks list
            remarks_list.append(surface_vibref3_average.remarks)


        #use this to get the message box and file dialog to show as top windows later
        window = Tk()
        window.wm_attributes('-topmost', 1)

        #suppress the Tk window
        window.withdraw()

        #loop until user chooses a filename
        valid_filename = False

        while not valid_filename:

            #display a message box
            messagebox.showinfo("Save HXML Export", "Choose Folder to Save HXML Export in", parent =window)

            #get user to choose name and folder location to save HXML file in
            user_filename = filedialog.asksaveasfilename(parent = window, initialdir = "C:\\", initialfile = f"{self.device_name}.hxml", filetypes = [(".hxml", "*.hxml")], defaultextension = ".hxml", confirmoverwrite = True)

            #valid filename that is not empty
            if user_filename != "":
                
                #exit loop
                valid_filename = True

            #invalid filename
            else:
                
                #repeat the prompt for user to choose a filename
                valid_filename = False


        #create the HXML file with the chosen filename and location
        hxml_object = HXMLGenerator(user_filename)

        #write the current graph object's data to the HXML file
        hxml_object.graphs_to_hxml(graphs_list, remarks_list)



#tester code
if __name__ == "__main__":

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