import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import numpy as np
import os
from tkinter import filedialog, messagebox, Tk
from data_tools import get_short_names, get_short_chan_signal
from measurement_plane import Measurement_Plane
from scan_point_graph import Graph_perc_change
from hxml_writer import HXMLGenerator


class Compare_Surface_Average:

    def __init__(self, list_filenames):
        self.list_filenames = list_filenames
        
        #create a list of Measurement_Plane objects, one object for each scan file
        self.measurement_list = [Measurement_Plane(f"{filename}") for filename in list_filenames]
        self.average_list = []
        self.remarks_list = []
        self.graph_names = []
        self.short_names = []
        self.short_chan_sig = None

        
    def initialize_from_files(self, channel_signal_type=None, is_GUI=False):
        if not is_GUI:
            #create a list of Graph_average objects, one for each surface average
            self.average_list = [measurement.get_average(channel_signal_type) for measurement in self.measurement_list]

        #create a list of anomalous points remarks, one for each surface average
        self.remarks_list = [graph.remarks for graph in self.average_list]

        #create a list of all the average graph names
        self.graph_names = [graph.scan_name[:-4] for graph in self.average_list]

        #get shortened scan name
        self.short_names = get_short_names(self.graph_names)

        #get shortened channel signal name
        self.short_chan_sig = self.extract_short_channel_signal()

    def extract_short_channel_signal(self):
        if not self.average_list:
            return None  # or raise ValueError("No averages to extract channel signal from.")
        return get_short_chan_signal(self.average_list[0].channel_signal)
    
    def compare_surface_average_export(self):

        '''Method to export surface averages of the required channel signal and unit
        on the same graph for comparison. 
        Returns filename to be reused for graph photo name'''


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
            user_filename = filedialog.asksaveasfilename(parent = window, initialdir = "C:\\", initialfile = f"{self.short_names} {self.short_chan_sig}.hxml", filetypes = [(".hxml", "*.hxml")], defaultextension = ".hxml", confirmoverwrite = True)

            #valid filename that is not empty
            if user_filename != "":
                
                #exit loop
                valid_filename = True

            #invalid filename
            else:
                
                #display error message
                print("Please provide a filename to save as")

                #repeat the prompt for user to choose a filename
                valid_filename = False


        #create the HXML file with the user chosen filename and location
        hxml_object = HXMLGenerator(user_filename)

        #write the current graph object's data to the HXML file
        hxml_object.graphs_to_hxml(self.average_list, self.remarks_list)

        #get file name without folder directory and extension
        file_name_without_extension = os.path.splitext(os.path.basename(user_filename))[0]

        #return just file name without folder directory and extension
        return file_name_without_extension

    def create_combined_average_figure(self):
        """
        Create and return a combined matplotlib figure that plots all averages in self.average_list.
        """
        tick_locations = [100, 200, 500, 1000, 2000, 5000, 10000]

        fig, ax = plt.subplots()

        # Plot each surface average line
        for surface_average in self.average_list:
            ax.plot(surface_average.x_data, surface_average.y_data,
                    label=f"{(surface_average.scan_name)[:-4]} Average")

        ax.set_xscale("log", base=2)

        ax.xaxis.set_major_locator(tick.FixedLocator(tick_locations))
        ax.xaxis.set_major_formatter(tick.FuncFormatter(lambda x, _: f'{int(x)}'))

        ax.set_xlabel(self.average_list[0].x_label_with_unit)
        ax.set_ylabel(self.average_list[0].y_label_with_unit)
        ax.set_title(f"{self.average_list[0].channel_signal} Surface Average Comparison")

        ax.set_xlim([self.average_list[0].x_min, 10000])

        # Major grid
        ax.grid(which="major", color="dimgrey", linewidth=0.5)
        # Minor grid
        ax.minorticks_on()
        ax.grid(which="minor", linestyle=":", color="lightgrey", linewidth=1)

        ax.legend(loc="best")  # Or fixed location like 'lower right' if preferred

        return fig


    def gui_export(self):
        """
        Open GUI dialogs to prompt user for file location and save the combined average figure as a PNG.
        """
        file_name_without_extension = self.compare_surface_average_export()

        # Create a hidden topmost root window for dialogs
        window = Tk()
        window.wm_attributes('-topmost', 1)
        window.withdraw()

        valid_filename = False

        while not valid_filename:
            messagebox.showinfo("Save Graph as Photo", "Choose Folder to Save Graph Photo in", parent=window)

            user_photo_filename = filedialog.asksaveasfilename(
                parent=window,
                initialdir="C:\\",
                initialfile=file_name_without_extension,
                filetypes=[(".png", "*.png")],
                defaultextension=".png",
                confirmoverwrite=True
            )

            if user_photo_filename != "":
                valid_filename = True
            else:
                print("Please provide a filename to save as")

        # Generate the figure
        fig = self.create_combined_average_figure()

        # Save figure as PNG
        fig.savefig(user_photo_filename, dpi=300, bbox_inches="tight")

    def compare_surface_average_plot(self):

        '''Method to plot surface averages of the required channel signal and unit
        on the same graph for comparison, export as HXML, save as png and also display'''

        self.gui_export()

        #display the graph
        plt.show()



    def surface_average_perc_change(self):
        
        '''Method to calculate surface averages of scans and calculate their percentage change, 
        export as HXML, save as png and also display'''


        #create a combined remark
        remark = f"{self.remarks_list[0]}; {self.remarks_list[1]}"

        #create percentage change graph
        perc_change = Graph_perc_change(self.average_list[0], self.average_list[1])


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
            user_filename = filedialog.asksaveasfilename(parent = window, initialdir = "C:\\", initialfile = f"{self.short_names} {self.short_chan_sig}.hxml", filetypes = [(".hxml", "*.hxml")], defaultextension = ".hxml", confirmoverwrite = True)

            #valid filename that is not empty
            if user_filename != "":
                
                #exit loop
                valid_filename = True

            #invalid filename
            else:
                
                #display error message
                print("Please provide a filename to save as")

                #repeat the prompt for user to choose a filename
                valid_filename = False


        #create the HXML file with the plot title as the filename in the HXML_exports subfolder
        hxml_object = HXMLGenerator(user_filename)

        #write the current graph object's data to the HXML file
        hxml_object.graphs_to_hxml([perc_change], [remark])

        #get file name without folder directory and extension
        file_name_without_extension = os.path.splitext(os.path.basename(user_filename))[0]


        #use this to get the message box and file dialog to show as top windows later
        window = Tk()
        window.wm_attributes('-topmost', 1)

        #suppress the Tk window
        window.withdraw()

        #loop until user chooses a filename
        valid_filename = False

        while not valid_filename:

            #display a message box
            messagebox.showinfo("Save Graph as Photo", "Choose Folder to Save Graph Photo in", parent =window)

            #get user to choose name and folder location to save photo file in
            user_photo_filename = filedialog.asksaveasfilename(parent = window, initialdir = "C:\\", initialfile = file_name_without_extension, filetypes = [(".png", "*.png")], defaultextension = ".png", confirmoverwrite = True)

            #valid filename that is not empty
            if user_photo_filename != "":
                
                #exit loop
                valid_filename = True

            #invalid filename
            else:
                
                #display error message
                print("Please provide a filename to save as")

                #repeat the prompt for user to choose a filename
                valid_filename = False


        #list containing locations to place ticks
        tick_locations = [100, 200, 500, 1000, 2000, 5000, 10000]

        fig, ax = plt.subplots()

        line_list = [ax.plot(surface_average.x_data, surface_average.y_data, label = f"{(surface_average.scan_name)[:-4]} Average") for surface_average in self.average_list]

        plt.xscale("log", base = 2)

        ax.xaxis.set_major_locator(tick.FixedLocator(tick_locations))

        ax.xaxis.set_major_formatter(tick.FuncFormatter(lambda x, _: f'{int(x)}'))

        plt.xlabel(self.average_list[0].x_label_with_unit)

        plt.ylabel(self.average_list[0].y_label_with_unit)

        plt.title(f"{self.average_list[0].channel_signal} Surface Average Comparison")

        plt.xlim([self.average_list[0].x_min, 10000])

        #display major grid
        plt.grid(which="major", color="dimgrey", linewidth=0.5)

        #display minor grid
        plt.minorticks_on()
        plt.grid(which="minor", linestyle=":", color="lightgrey", linewidth=1)

        #display a legend for the plot
        plt.legend(loc = "best")        #change loc to a fixed location eg lower right for faster speed

        #save the plot as a png image, adapted from Kuan Hsien code line for savefig
        plt.savefig(user_photo_filename, dpi=300, bbox_inches="tight")

        #display the plot
        plt.show()
