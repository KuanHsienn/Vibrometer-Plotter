import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import numpy as np
import re
import os
from tkinter import filedialog, messagebox, Tk
from data_tools import array_to_decibel_1, array_to_decibel_2
from graph_plotter import graph_plotter
from hxml_writer import HXMLGenerator

#class for an individual graph for one channel type, one signal type, and one scan point
#takes in a dictionary of data as input parameter
class Graph:

    def __init__(self, graph):
        
        #attributes for graph data
        self.x_data = graph["x"]
        
        #if first element in array of y data is complex, convert all elements in the array to absolute
        #and store as attribute
        if isinstance(graph["data"][0], complex):
            self.y_data = np.abs(graph["data"])

        else:

            #else just store directly as attribute
            self.y_data = graph["data"]

        #attribute for minimum x value in the graph
        self.x_min = graph["abscissa_min"]

        #attributes for graph name
        self.scan_name = str(graph["id4"])
        self.channel_signal = str(graph["id2"])
        self.scan_point_no = int(graph["rsp_node"])      #scan point number attribute as integer
        self.plot_title = self.scan_name[:-4] + ", " + self.channel_signal + ", Scan Point " + str(self.scan_point_no)

        #attributes for x-axis
        self.x_label = str(graph["abscissa_axis_lab"])
        self.x_label_unit = str(graph["abscissa_axis_units_lab"])
        self.x_label_with_unit = self.x_label + " [" + self.x_label_unit + "]" 

        #attributes for y-axis
        self.y_label = str(graph["ordinate_axis_lab"])
        self.y_label_unit = str(graph["ordinate_axis_units_lab"])
        self.y_label_with_unit = self.y_label + " [" + self.y_label_unit + "]"


    def export_graph(self):

        '''Method to export the current graph as HXML
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
            user_filename = filedialog.asksaveasfilename(parent = window, initialdir = "C:\\", initialfile = f"{self.plot_title}.hxml", filetypes = [(".hxml", "*.hxml")], defaultextension = ".hxml", confirmoverwrite = True)

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
        
        #create a list containing the current graph object
        graphs_list = [self]

        #write the current graph object's data to the HXML file
        hxml_object.graphs_to_hxml(graphs_list)

        #get file name without folder directory and extension
        file_name_without_extension = os.path.splitext(os.path.basename(user_filename))[0]

        #return just file name without folder directory and extension
        return file_name_without_extension


    def plot_graph(self):

        '''Method to save as HXML file, save as png and also display the current graph'''

        #export as HXML and get the user chosen file name
        default_file_name = self.export_graph()


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
            user_filename = filedialog.asksaveasfilename(parent = window, initialdir = "C:\\", initialfile = default_file_name, filetypes = [(".png", "*.png")], defaultextension = ".png", confirmoverwrite = True)

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


        #plot the graph using imported graph_plotter functions
        graph_plotter(self)

        #save the plot as a png image, adapted from Kuan Hsien code line for savefig
        plt.savefig(user_filename, dpi=300, bbox_inches="tight")

        #display the graph
        plt.show()


    def gui_export(self):
        '''Export both hxml file and graph png'''
        #export as HXML and get the user chosen file name
        default_file_name = self.export_graph()


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
            user_filename = filedialog.asksaveasfilename(parent = window, initialdir = "C:\\", initialfile = default_file_name, filetypes = [(".png", "*.png")], defaultextension = ".png", confirmoverwrite = True)

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


        #plot the graph using imported graph_plotter functions
        graph_plotter(self)

        #save the plot as a png image, adapted from Kuan Hsien code line for savefig
        plt.savefig(user_filename, dpi=300, bbox_inches="tight")


#class for an individual graph for one channel type, one signal type, and one scan point, converted to decibel
#takes in a Graph object and the decibel reference as input parameters
class Graph_decibel:

    def __init__(self, graph, decibel_type, reference):
        
        #attributes for graph data
        self.x_data = graph.x_data

        #attribute for reference value used for decibel conversion
        self.reference = reference
        
        #if decibel type is 1, meaning no squared units
        if decibel_type == 1:

            #if first element in array of y data is complex, convert all elements in the array to absolute 
            #then convert to decibel and store as attribute
            if isinstance(graph.y_data[0], complex):
                self.y_data = array_to_decibel_1(np.abs(graph.y_data), self.reference)

            else:
                
                #else just convert all elements in the array to decibel and store as attribute
                self.y_data = array_to_decibel_1(graph.y_data, self.reference)


        #if decibel type is 2, meaning there are squared units
        if decibel_type == 2:
            
            #if first element in array of y data is complex, convert all elements in the array to absolute 
            #then convert to decibel and store as attribute
            if isinstance(graph.y_data[0], complex):
                self.y_data = array_to_decibel_2(np.abs(graph.y_data), self.reference)

            else:
                
                #else just convert all elements in the array to decibel and store as attribute
                self.y_data = array_to_decibel_2(graph.y_data, self.reference)


        #attribute for minimum x value in the graph
        self.x_min = graph.x_min


        #attributes for graph name
        self.scan_name = str(graph.scan_name)
        self.channel_signal = str(graph.channel_signal) + " [dB]"
        self.scan_point_no = int(graph.scan_point_no)      #scan point number attribute as integer
        self.plot_title = self.scan_name[:-4] + ", " + self.channel_signal + ", Scan Point " + str(self.scan_point_no)
        
        #attributes for x-axis
        self.x_label = str(graph.x_label)
        self.x_label_unit = str(graph.x_label_unit)
        self.x_label_with_unit = self.x_label + " [" + self.x_label_unit + "]"

        #attributes for y-axis
        self.y_label = str(graph.y_label)
        self.y_label_unit = "0dB = " + str(self.reference) + str(graph.y_label_unit)
        self.y_label_with_unit = self.y_label + " [" + self.y_label_unit + "]"


    
    def export_graph(self):

        '''Method to export the current graph as HXML.
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
            user_filename = filedialog.asksaveasfilename(parent = window, initialdir = "C:\\", initialfile = f"{self.plot_title}.hxml", filetypes = [(".hxml", "*.hxml")], defaultextension = ".hxml", confirmoverwrite = True)

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
        
        #create a list containing the current graph object
        graphs_list = [self]

        #write the current graph object's data to the HXML file
        hxml_object.graphs_to_hxml(graphs_list)

        #get file name without folder directory and extension
        file_name_without_extension = os.path.splitext(os.path.basename(user_filename))[0]

        #return just file name without folder directory and extension
        return file_name_without_extension


    def plot_graph(self):

        '''Method to save as HXML file, save as png and also display the current graph'''

        #export as HXML and get the user chosen file name
        default_file_name = self.export_graph()


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
            user_filename = filedialog.asksaveasfilename(parent = window, initialdir = "C:\\", initialfile = default_file_name, filetypes = [(".png", "*.png")], defaultextension = ".png", confirmoverwrite = True)

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


        #plot the graph using imported graph_plotter functions
        graph_plotter(self)

        #save the plot as a png image, adapted from Kuan Hsien code line for savefig
        plt.savefig(user_filename, dpi=300, bbox_inches="tight")

        #display the graph
        plt.show()



#class for an individual graph which is the result of the division of 2 input graph data
#for calculating transfer function of vib of a scan point with its ref1, ref2 or ref3
#takes in two Graph objects as input parameters
class Graph_quotient:

    def __init__(self, graph_dividend, graph_divisor):
        
        #store attributes
        self.graph_dividend = graph_dividend
        self.graph_divisor = graph_divisor

        #attribute for dividend graph x data
        self.graph_dividend_x = self.graph_dividend.x_data

        #if first element in array of y data for dividend graph is complex, convert all elements in the array to absolute
        #and store as attribute
        if isinstance(self.graph_dividend.y_data[0], complex):
            self.graph_divident_y = np.abs(self.graph_dividend.y_data)

        else:

            #else just store directly as attribute
            self.graph_divident_y = self.graph_dividend.y_data


        #attribute for divisor graph x data
        self.graph_divisor_x = self.graph_divisor.x_data

        #if first element in array of y data for divisor graph is complex, convert all elements in the array to absolute
        #and store as attribute
        if isinstance(self.graph_divisor.y_data[0], complex):
            self.graph_divisor_y = np.abs(self.graph_divisor.y_data)

        else:

            #else just store directly as attribute
            self.graph_divisor_y = self.graph_divisor.y_data


        #check if dividend graph and divisor graph have exact same x values
        if np.array_equal(self.graph_dividend_x, self.graph_divisor_x):
            
            #attribute for x data of quotient graph, using the x data of dividend graph
            self.x_data = self.graph_dividend_x

            #attribute which is the result of element-wise division of array of dividend y data with array of divisor y data
            self.y_data = np.divide(self.graph_divident_y, self.graph_divisor_y)
        
        else: 

            #else return an error as the x arrays are different for graph1 and graph2
            print("x values do not match for the dividend and divisor graphs")
            
            return False
            

        #attributes for graph name
        
        #check if scan names for dividend graph and divisor graph match
        if self.graph_dividend.scan_name == self.graph_divisor.scan_name:

            #attribute for quotient graph scan name
            self.scan_name = str(self.graph_dividend.scan_name)

        else:
            
            #else return an error as scan point numbers do not match
            print("Scan names do not match for the graphs being divided")

            return False
        
        self.dividend_channel_signal = str(self.graph_dividend.channel_signal)

        self.divisor_channel_signal = str(self.graph_divisor.channel_signal)

        self.channel_signal = self.dividend_channel_signal + " and " + self.divisor_channel_signal


        #check if scan point numbers for dividend graph and divisor graph match
        if self.graph_dividend.scan_point_no == self.graph_divisor.scan_point_no:

            #attribute for scan point number for quotient graph
            self.scan_point_no = int(self.graph_dividend.scan_point_no)      #scan point number attribute as integer

        else:
            
            #else return an error as scan point numbers do not match
            print("Scan point numbers do not match for the graphs being divided")

            return False
        

        self.plot_title = self.scan_name[:-4] + ", " + self.channel_signal + ", Scan Point " + str(self.scan_point_no)


        #check if x labels for dividend graph and divisor graph match
        if self.graph_dividend.x_label == self.graph_divisor.x_label:

            #attribute for x label for quotient graph
            self.x_label = str(self.graph_dividend.x_label)

        else:
            
            #else return an error as x labels do not match
            print("x labels do not match for the graphs being divided")

            return False


        #check if x label units for dividend graph and divisor graph match
        if self.graph_dividend.x_label_unit == self.graph_divisor.x_label_unit:

            #attribute for x label unit for quotient graph
            self.x_label_unit = str(self.graph_dividend.x_label_unit)

        else:
            
            #else return an error as x label units do not match
            print("x label units do not match for the graphs being divided")

            return False

        
        self.x_label_with_unit = self.x_label + " [" + self.x_label_unit + "]" 


        #check if x min for dividend graph and divisor graph match
        if self.graph_dividend.x_min == self.graph_divisor.x_min:

            #attribute for x min for quotient graph
            self.x_min = self.graph_dividend.x_min

        else:
            
            #else return an error as x min do not match
            print("x min do not match for the graphs being divided")

            return False


        self.dividend_y_label = str(self.graph_dividend.y_label)
        self.divisor_y_label = str(self.graph_divisor.y_label)

        #attribute for y label for quotient graph
        self.y_label = self.dividend_y_label + " per " + self.divisor_y_label

        self.dividend_y_label_unit = str(self.graph_dividend.y_label_unit)
        self.divisor_y_label_unit = str(self.graph_divisor.y_label_unit)

        #attribute for y label unit for quotient graph
        self.y_label_unit = self.dividend_y_label_unit + self.divisor_y_label_unit

        #attribute for y label with unit for quotient graph
        self.y_label_with_unit = self.y_label + " [" + self.y_label_unit + "]"



    def export_graph(self):

        '''Method to export the current graph as HXML.
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
            user_filename = filedialog.asksaveasfilename(parent = window, initialdir = "C:\\", initialfile = f"{self.plot_title}.hxml", filetypes = [(".hxml", "*.hxml")], defaultextension = ".hxml", confirmoverwrite = True)

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
        
        #create a list containing the current graph object
        graphs_list = [self]

        #write the current graph object's data to the HXML file
        hxml_object.graphs_to_hxml(graphs_list)

        #get file name without folder directory and extension
        file_name_without_extension = os.path.splitext(os.path.basename(user_filename))[0]

        #return just file name without folder directory and extension
        return file_name_without_extension


    def plot_graph(self):

        '''Method to save as HXML file, save as png and also display the current graph'''

        #export as HXML and get the user chosen file name
        default_file_name = self.export_graph()


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
            user_filename = filedialog.asksaveasfilename(parent = window, initialdir = "C:\\", initialfile = default_file_name, filetypes = [(".png", "*.png")], defaultextension = ".png", confirmoverwrite = True)

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


        #plot the graph using imported graph_plotter functions
        graph_plotter(self)

        #save the plot as a png image, adapted from Kuan Hsien code line for savefig
        plt.savefig(user_filename, dpi=300, bbox_inches="tight")

        #display the graph
        plt.show()


#class for an individual graph which is the result of the division of 2 input graph data
#for calculating transfer function of vib of a scan point with its ref1, ref2 or ref3
#takes in a list of graph objects as input parameters
class Graph_average:

    def __init__(self, graphs_list, anomalous_points_list, scan_name = None):
        
        #store attributes
        self.graphs_list = graphs_list
        self.anomalous_points_list = anomalous_points_list

        #no anomalous points
        if len(self.anomalous_points_list) == 0:

            remarks = "No anomalous points. "

        #there were anomalous points excluded
        else:

            remarks = f"Anomalous point(s) excluded: {(str(self.anomalous_points_list))[1:-1]}. "
        
        #attribute for remarks
        self.remarks = remarks


        #loop through all the graphs in the graph list and check if they all have the same x data
        #by comparing each of their x data to the first graph's x data
        #start from second graph
        for index in range(len(self.graphs_list)-1):

            #index to access the current graph in the list of graphs
            graph_index = index + 1

            #if the x data do not match
            if not np.array_equal(self.graphs_list[0].x_data, self.graphs_list[graph_index].x_data):
                
                #error as x data do not match
                print("x data do not match for the graphs being averaged")

                return False
            
            else:
                pass

        #x data matches for all the graphs
        #store x data from first graph as attribute
        self.x_data = self.graphs_list[0].x_data

        #store a list of all the y data arrays for all the graphs
        y_data_list = []

        #loop through all the graphs in the graphs list and add their y_data to a list
        #if first element in array of y data for dividend graph is complex, convert all elements in the array to absolute
        #and store as attribute
        for graph in self.graphs_list:

            #if first element in array of y data for dividend graph is complex, convert all elements in the array to absolute
            #before appending the array of converted y data to y_data_list
            if isinstance(graph.y_data[0], complex):
                y_data_list.append(np.abs(graph.y_data))

            else:

                #else just append the array of y data to y_data_list
                y_data_list.append(graph.y_data)

        
        #element-wise addition of y data for all the graphs 
        summed_y_data_list = np.sum(y_data_list, axis = 0)
        
        #element-wise division of summed y data
        average_y_data = np.divide(summed_y_data_list, len(y_data_list))

        #attribute for averaged y data of all the graphs using element-wise averaging
        self.y_data = average_y_data

        #attribute storing a list of scan point numbers of all the graphs
        self.scan_point_no = [int(graph.scan_point_no) for graph in self.graphs_list]      #scan point numbers as integer

        first_graph = self.graphs_list[0]

        #assuming that all other attributes are the same across all the graphs

        #attribute for minimum x value in the graph
        self.x_min = first_graph.x_min

        #attributes for graph name

        #if no scan_name was provided
        if scan_name is None:

            self.scan_name = str(first_graph.scan_name)
            self.channel_signal = str(first_graph.channel_signal)
            self.plot_title = self.scan_name[:-4] + ", " + self.channel_signal + ", Surface Average"

        #if scan_name was provided
        else:

            #use provided scan name
            self.scan_name = scan_name
            self.channel_signal = str(first_graph.channel_signal)

            #note there is no .uff extension to remove
            self.plot_title = self.scan_name + ", " + self.channel_signal + ", Average"
        
        #attributes for x-axis
        self.x_label = str(first_graph.x_label)
        self.x_label_unit = str(first_graph.x_label_unit)
        self.x_label_with_unit = self.x_label + " [" + self.x_label_unit + "]"

        #attributes for y-axis
        self.y_label = str(first_graph.y_label)
        self.y_label_unit = str(first_graph.y_label_unit)
        self.y_label_with_unit = self.y_label + " [" + self.y_label_unit + "]"

    
    def export_graph(self):

        '''Method to export the current graph as HXML.
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
            user_filename = filedialog.asksaveasfilename(parent = window, initialdir = "C:\\", initialfile = f"{self.plot_title}.hxml", filetypes = [(".hxml", "*.hxml")], defaultextension = ".hxml", confirmoverwrite = True)

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
    
        #create a list containing the current graph object
        graphs_list = [self]

        #write the current graph object's data to the HXML file
        hxml_object.graphs_to_hxml(graphs_list, remarks_list = [self.remarks])

        #get file name without folder directory and extension
        file_name_without_extension = os.path.splitext(os.path.basename(user_filename))[0]

        #return just file name without folder directory and extension
        return file_name_without_extension
    

    def plot_graph(self):

        '''Method to save as HXML file, save as png and also display the current graph'''

        #export as HXML and get the user chosen file name
        default_file_name = self.export_graph()


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
            user_filename = filedialog.asksaveasfilename(parent = window, initialdir = "C:\\", initialfile = default_file_name, filetypes = [(".png", "*.png")], defaultextension = ".png", confirmoverwrite = True)

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


        #plot the graph using imported graph_plotter functions
        graph_plotter(self)

        #save the plot as a png image, adapted from Kuan Hsien code line for savefig
        plt.savefig(user_filename, dpi=300, bbox_inches="tight")

        #display the graph
        plt.show()



#class for an individual graph which is the result of the division of 2 input graph data
#for calculating transfer function of vib of a scan point with its ref1, ref2 or ref3
#takes in a list of graph objects as input parameters
class Graph_average_all:

    def __init__(self, graphs_list):
        
        #store attributes
        self.graphs_list = graphs_list

        #placeholder string for full remarks
        self.remarks = ""

        for graph in graphs_list:

            #add the remarks
            self.remarks += f"{graph.scan_name[:-4]}: {graph.remarks}"


        #loop through all the graphs in the graph list and check if they all have the same x data
        #by comparing each of their x data to the first graph's x data
        #start from second graph
        for index in range(len(self.graphs_list)-1):

            #index to access the current graph in the list of graphs
            graph_index = index + 1

            #if the x data do not match
            if not np.array_equal(self.graphs_list[0].x_data, self.graphs_list[graph_index].x_data):
                
                #error as x data do not match
                print("x data do not match for the graphs being averaged")

                return False
            
            else:
                pass

        #x data matches for all the graphs
        #store x data from first graph as attribute
        self.x_data = self.graphs_list[0].x_data

        #store a list of all the y data arrays for all the graphs
        y_data_list = []

        #loop through all the graphs in the graphs list and add their y_data to a list
        #if first element in array of y data for dividend graph is complex, convert all elements in the array to absolute
        #and store as attribute
        for graph in self.graphs_list:

            #if first element in array of y data for dividend graph is complex, convert all elements in the array to absolute
            #before appending the array of converted y data to y_data_list
            if isinstance(graph.y_data[0], complex):
                y_data_list.append(np.abs(graph.y_data))

            else:

                #else just append the array of y data to y_data_list
                y_data_list.append(graph.y_data)

        
        #element-wise addition of y data for all the graphs 
        summed_y_data_list = np.sum(y_data_list, axis = 0)
        
        #element-wise division of summed y data
        average_y_data = np.divide(summed_y_data_list, len(y_data_list))

        #attribute for averaged y data of all the graphs using element-wise averaging
        self.y_data = average_y_data

        #graphs in the input are already surface average graphs e.g. for use in full device ref1 average
        #attribute storing a list of lists of scan point numbers of all the graphs
        self.scan_point_no = [graph.scan_point_no for graph in self.graphs_list]

        first_graph = self.graphs_list[0]

        #assuming that all other attributes are the same across all the graphs

        #attribute for minimum x value in the graph
        self.x_min = first_graph.x_min

        #get device name
        match_object = re.search("top|left|right|ear", first_graph.scan_name.lower())

        match_index = match_object.start()

        #attribute for device name
        #splice up to one less than the match part in order to remove the space or underscore before the match part as well
        self.device_name = (str(first_graph.scan_name))[:match_index-1]

        #attribute for channel signal
        self.channel_signal = str(first_graph.channel_signal)

        #attribute for plot title
        self.plot_title = self.device_name + ", " + self.channel_signal + ", Average"
        
        #attributes for x-axis
        self.x_label = str(first_graph.x_label)
        self.x_label_unit = str(first_graph.x_label_unit)
        self.x_label_with_unit = self.x_label + " [" + self.x_label_unit + "]"

        #attributes for y-axis
        self.y_label = str(first_graph.y_label)
        self.y_label_unit = str(first_graph.y_label_unit)
        self.y_label_with_unit = self.y_label + " [" + self.y_label_unit + "]"

    
    def export_graph(self):

        '''Method to export the current graph as HXML.
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
            user_filename = filedialog.asksaveasfilename(parent = window, initialdir = "C:\\", initialfile = f"{self.plot_title}.hxml", filetypes = [(".hxml", "*.hxml")], defaultextension = ".hxml", confirmoverwrite = True)

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

        #create a list containing the current graph object
        graphs_list = [self]

        #write the current graph object's data to the HXML file
        hxml_object.graphs_to_hxml(graphs_list, remarks_list = [self.remarks])

        #get file name without folder directory and extension
        file_name_without_extension = os.path.splitext(os.path.basename(user_filename))[0]

        #return just file name without folder directory and extension
        return file_name_without_extension
    

    def plot_graph(self):

        '''Method to save as HXML file, save as png and also display the current graph'''

        #export as HXML and get the user chosen file name
        default_file_name = self.export_graph()


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
            user_filename = filedialog.asksaveasfilename(parent = window, initialdir = "C:\\", initialfile = default_file_name, filetypes = [(".png", "*.png")], defaultextension = ".png", confirmoverwrite = True)

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


        #plot the graph using imported graph_plotter functions
        graph_plotter(self)

        #save the plot as a png image, adapted from Kuan Hsien code line for savefig
        plt.savefig(user_filename, dpi=300, bbox_inches="tight")

        #display the graph
        plt.show()



#class for an individual graph which is the percentage change of the after graph from the before graph
#for calculating transfer function of vib of a scan point with its ref1, ref2 or ref3
#takes in two Graph objects as input parameters
class Graph_perc_change:

    def __init__(self, graph_before, graph_after):
        
        #store attributes
        self.graph_before = graph_before
        self.graph_after = graph_after

        #attribute for before graph x data
        self.graph_before_x = self.graph_before.x_data

        #if first element in array of y data for before graph is complex, convert all elements in the array to absolute
        #and store as attribute
        if isinstance(self.graph_before.y_data[0], complex):
            self.graph_before_y = np.abs(self.graph_before.y_data)

        else:

            #else just store directly as attribute
            self.graph_before_y = self.graph_before.y_data


        #attribute for before graph x data
        self.graph_after_x = self.graph_after.x_data

        #if first element in array of y data for after graph is complex, convert all elements in the array to absolute
        #and store as attribute
        if isinstance(self.graph_after.y_data[0], complex):
            self.graph_after_y = np.abs(self.graph_after.y_data)

        else:

            #else just store directly as attribute
            self.graph_after_y = self.graph_after.y_data


        #check if before graph and before graph have exact same x values
        if np.array_equal(self.graph_before_x, self.graph_after_x):
            
            #attribute for x data of output graph, using the x data of before graph
            self.x_data = self.graph_before_x

            #attribute which is the result of element-wise division of array of before y data with array of before y data
            self.y_difference = np.subtract(self.graph_after_y, self.graph_before_y)
            #self.y_data = np.multiply((np.divide(self.y_difference, self.graph_before_y)), 100)
            self.y_data = self.y_difference
        
        else: 

            #else return an error as the x arrays are different for graph1 and graph2
            print("x values do not match for the before and before graphs")
            
            return False
        
        #attribute for output graph scan name
        self.scan_name = str(self.graph_before.scan_name)
        
        #attribute for channel signal
        self.channel_signal = "Percentage Change"
        
        #attribute for plot title
        self.plot_title = f"Percentage Change of {self.graph_after.scan_name} from {self.graph_after.scan_name}"


        #check if x labels for before graph and before graph match
        if self.graph_before.x_label == self.graph_after.x_label:

            #attribute for x label for output graph
            self.x_label = str(self.graph_before.x_label)

        else:
            
            #else return an error as x labels do not match
            print("x labels do not match for the graphs being divided")

            return False


        #check if x label units for before graph and after graph match
        if self.graph_before.x_label_unit == self.graph_after.x_label_unit:

            #attribute for x label unit for output graph
            self.x_label_unit = str(self.graph_before.x_label_unit)

        else:
            
            #else return an error as x label units do not match
            print("x label units do not match for the graphs being divided")

            return False

        
        self.x_label_with_unit = self.x_label + " [" + self.x_label_unit + "]" 


        #check if x min for before graph and before graph match
        if self.graph_before.x_min == self.graph_after.x_min:

            #attribute for x min for output graph
            self.x_min = self.graph_before.x_min

        else:
            
            #else return an error as x min do not match
            print("x min do not match for the graphs being divided")

            return False


        #attribute for y label for output graph
        self.y_label = "Percentage Change"

        #attribute for y label unit for output graph
        self.y_label_unit = "%"

        #attribute for y label with unit for output graph
        self.y_label_with_unit = self.y_label + " [" + self.y_label_unit + "]"



    def export_graph(self):

        '''Method to export the current graph as HXML.
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
            user_filename = filedialog.asksaveasfilename(parent = window, initialdir = "C:\\", initialfile = f"{self.plot_title}.hxml", filetypes = [(".hxml", "*.hxml")], defaultextension = ".hxml", confirmoverwrite = True)

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

        #create a list containing the current graph object
        graphs_list = [self]

        #write the current graph object's data to the HXML file
        hxml_object.graphs_to_hxml(graphs_list)

        #get file name without folder directory and extension
        file_name_without_extension = os.path.splitext(os.path.basename(user_filename))[0]

        #return just file name without folder directory and extension
        return file_name_without_extension


    def plot_graph(self):

        '''Method to save as HXML file, save as png and also display the current graph'''

        #export as HXML and get the user chosen file name
        default_file_name = self.export_graph()


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
            user_filename = filedialog.asksaveasfilename(parent = window, initialdir = "C:\\", initialfile = default_file_name, filetypes = [(".png", "*.png")], defaultextension = ".png", confirmoverwrite = True)

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


        #plot the graph using imported graph_plotter functions
        graph_plotter(self)

        #save the plot as a png image, adapted from Kuan Hsien code line for savefig
        plt.savefig(user_filename, dpi=300, bbox_inches="tight")

        #display the graph
        plt.show()