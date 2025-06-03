import pyuff
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import numpy as np
import os
from scan_point import Scan_Point
from scan_point_graph import Graph_average
from annotated_cursor import AnnotatedCursor
from tkinter import filedialog, messagebox, Tk
from data_tools import get_short_names, get_short_chan_signal
from hxml_writer import HXMLGenerator


#class for one measurement file
class Measurement_Plane:

    def __init__(self, filepath, number_graphs = 8):
        '''Change number_graphs to accomodate the 
        number of graphs extracted per scan point'''

        self.filepath = filepath

        #open UFF file
        self.uff_file = pyuff.UFF(self.filepath)

        #load all datasets from UFF file to data object
        self.data = self.uff_file.read_sets()

        #get array of set types
        self.set_types = self.uff_file.get_set_types()

        #search in set_types array for 2411 and get tuple of indexes for search result
        #get the index of 2411 and save as coordinates data index which is where the scan point coordinates data are stored in self.data
        self.coordinates_data_index = (np.where(self.set_types == 2411))[0][0]

        #create a list of scan point numbers with each one converted to integer
        self.scan_point_names = [int(point_no) for point_no in self.data[self.coordinates_data_index]["node_nums"]]

        #create a 2D list of scanpoint coordinates
        #structure is [[point numbers], [x-coordinates], [y-coordinates], [z-coordinates]]
        #also convert scan point numbers to integers
        self.scan_point_coordinates = [self.scan_point_names, self.data[self.coordinates_data_index]["x"], self.data[self.coordinates_data_index]["y"], self.data[self.coordinates_data_index]["z"]]

        #attribute to store list of colours for bands of points
        self.band_colours = ["blue", "orange", "green", "red", "purple", "brown", "pink", "olive", "cyan", "magenta"]
        
        
        #search in set_types array for 58 and get tuple of indexes for search result
        #get the index of the first instance of 58 and save as first data index which is where the first data graph is stored in self.data
        first_data_index = (np.where(self.set_types == 58))[0][0]
        graph_indices = np.where(self.set_types == 58)[0]
        actual_graph_count = len(graph_indices)
        #print(f"graph count: {actual_graph_count}")
        
        self.number_of_scan_points = int(actual_graph_count/number_graphs)

        #dictionary holding all the scan point objects
        self.scanpoints = []

        #default 8 graphs per scan point
        self.number_graphs = number_graphs
        

        #information about the measurement
        self.scan_name = os.path.basename(filepath)

        self.db_app = str(self.data[0]["db_app"])
        self.date_db_created = str(self.data[0]["date_db_created"])
        self.time_db_created = str(self.data[0]["time_db_created"])
        self.units_description = str(self.data[1]["units_description"])

        #access the last graph of the last scan point in the measurement
        last_scan_point = self.data[-1]

        #get number of last scan point which is also total number of scan points
        # self.number_of_scan_points = last_scan_point["rsp_node"]

        #save total number of graphs as an attribute
        #self.total_graphs = self.number_of_scan_points * self.number_graphs

        #iterate through all the graphs in the measurement and update their filename attribute to the current filename
        #start from the index of the first graph data and end at index of last graph data
        #print(f"{actual_graph_count} {first_data_index} {len(self.data)}")
        for i in graph_indices:
            #set filename attribute to current filename
            self.data[i]["id4"] = str(os.path.basename(filepath))


        #iterate through all the scan points in the measurement
        for point in range(self.number_of_scan_points):
            
            #create a list to store all the graphs for the current scan point
            scan_point_all_graphs = []

            #index to start from for this point
            #first 6 items in self.data are not graph data
            #for point 1 start from index 6 to skip the first 6 items to start from item 7 at index 6
            #for point 2 start from index 7 and etc
            index = first_data_index + point


            #iterate through all the graphs for the current scan point
            for graph in range(self.number_graphs):
                if index >= len(self.data):
                    print(f"⚠️ Warning: Not enough graph data for scan point {point + 1}. Expected {self.number_graphs} graphs, found fewer.")
                    break

                #access one graph for the current scan point
                scan_point_graph = self.data[index]

                #append the graph to the list of graphs for current scan point
                scan_point_all_graphs.append(scan_point_graph)

                #increment the index by the number of scan points
                #to access the next graph for this same scan point
                index += self.number_of_scan_points
            
            if len(scan_point_all_graphs) != self.number_graphs:
                continue

            #create instance of scan point object for this scan point 
            #and append this scan point object to list of scan points for this measurement
            self.scanpoints.append(Scan_Point(scan_point_all_graphs))


        #attribute to store anomalous points when get_anomalous method is called
        self.anomalous_points = []

        #attribute to store a 2D list for non-anomalous points when get_anomalous method is called
        #before get_anomalous method is called, it is assumed all points are non-anomalous
        self.scan_point_coordinates_valid = self.scan_point_coordinates

        #attribute to store a 2D list for anomalous points when get_anomalous method is called
        self.scan_point_coordinates_anomalous = [[], [], [], []]

        #attribute to store list of all bands after calling create_bands method
        #each band is a list of point numbers
        self.all_bands = []

        #attribute to store list of all bands after calling create_bands method
        #each band is a list of scan point objects
        self.all_bands_points = []

        #attribute to store list of graph average objects of each band after calling get_band_averages method
        self.band_averages = []

        ##attribute to store a list of remarks, one for for each band
        #indicate color of band as shown on scan layout, as well as the scanpoints included in the band
        #after calling get_band_averages method
        self.band_remarks = []

            

    
    def get_dataset_types(self):
        
        #check datasets used and display
        dataset_types = self.uff_file.get_set_types()
        return dataset_types

        
    def display_dataset_types(self):

        #iterate through the dataset and print out the dictionary keys
        for n in range(len(self.data)): 
            print(self.data[n].keys())

        return
    

    def number_of_measurements(self):
        
        dataset_types = self.get_dataset_types()
        
        #return the number of dataset 58 elements in the list of dataset types
        #each dataset 58 element is a dictionary containing information about one channel measurement at one scan point
        return dataset_types.count(58)
    

    def plot_scan_points_coordinates(self):

        '''Method to display the location of all the scanpoints.'''

        #if all the z coordinates are the same so the points can be represented in a 2D plot
        #since set only stores unique values
        if len(set(self.scan_point_coordinates[3])) == 1:
            
            #plot all valid scanpoints
            plt.scatter(self.scan_point_coordinates_valid[1], self.scan_point_coordinates_valid[2], color = "grey")


            #if there are anomalous scanpoints
            if len(self.scan_point_coordinates_anomalous[0]) > 0:
                
                #plot all anomalous scanpoints as crosses
                plt.scatter(self.scan_point_coordinates_anomalous[1], self.scan_point_coordinates_anomalous[2], marker = "x", color = "red", label = "Anomalous")

                #display legend
                plt.legend(loc = "best")

            #iterate through all the scan points
            for point_index in range(len(self.scan_point_coordinates[0])): 
                
                #label each point with point number
                #annotate at a higher y-value than the point so it does not overlap
                plt.annotate(self.scan_point_coordinates[0][point_index], (self.scan_point_coordinates[1][point_index], self.scan_point_coordinates[2][point_index]))


            #set equal scaling for both axes so that the shape of the group of points will be correct
            plt.axis("equal")

            #allow program to continue executing even when figure is open
            plt.show(block = False)

            
        #not all z-coordinates are the same
        #3D layout
        else:

            print("Have not implemented functionality to display 3D scatter plot")



    def get_anomalous(self, channel_signal_type):

        '''Method to display all the scan point graphs for the chosen channel signal type
        and allow user to specify which points to exclude as anomalous data. 
        Displays graphs for 2 scan points at a time, then allows user to type in whether any of them are anomalous. 
        Returns a list of anomalous points to exclude. '''


        #list containing locations to place ticks
        tick_locations = [100, 200, 500, 1000, 2000, 5000, 10000]

        #create a list to hold integer scan point numbers to exclude
        anomalous_points_to_exclude = []

        #if the measurement only has 1 scan point
        if self.number_of_scan_points == 1:
            
            #create the required channel signal graph for the current scan point
            match channel_signal_type:

                case "disp":
        
                    scan_point_graph = self.scanpoints[0].disp

                case "vib":
        
                    scan_point_graph = self.scanpoints[0].vib

                case "acc":
        
                    scan_point_graph = self.scanpoints[0].acc

                case "ref1":

                    scan_point_graph = self.scanpoints[0].ref1

                case "ref2":
        
                    scan_point_graph = self.scanpoints[0].ref2

                case "ref3":
        
                    scan_point_graph = self.scanpoints[0].ref3

                case "h1vibref1":
        
                    scan_point_graph = self.scanpoints[0].h1vibref1

                case "h2vibref1":
        
                    scan_point_graph = self.scanpoints[0].h2vibref1

                case "vibref1":
        
                    scan_point_graph = self.scanpoints[0].create_vibref1()

                case "vibref2":
        
                    scan_point_graph = self.scanpoints[0].create_vibref2()
         
                case "vibref3":
        
                    scan_point_graph = self.scanpoints[0].create_vibref3()

                case "disp_db":
        
                    scan_point_graph = self.scanpoints[0].create_disp_decibel()

                case "vib_db":
        
                    scan_point_graph = self.scanpoints[0].create_vib_decibel()

                case "acc_db":
        
                    scan_point_graph = self.scanpoints[0].create_acc_decibel()

                case "ref1_db":

                    scan_point_graph = self.scanpoints[0].create_ref1_decibel()

                case "ref2_db":
        
                    scan_point_graph = self.scanpoints[0].create_ref2_decibel()

                case "ref3_db":
        
                    scan_point_graph = self.scanpoints[0].create_ref3_decibel()

                case "h1vibref1_db":
        
                    scan_point_graph = self.scanpoints[0].create_h1vibref1_decibel()

                case "h2vibref1_db":
        
                    scan_point_graph = self.scanpoints[0].create_h2vibref1_decibel()

                case "vibref1_db":
        
                    scan_point_graph = self.scanpoints[0].create_vibref1_decibel()

                case "vibref2_db":
        
                    scan_point_graph = self.scanpoints[0].create_vibref2_decibel()
         
                case "vibref3_db":
        
                    scan_point_graph = self.scanpoints[0].create_vibref3_decibel()


            #create a half-sized graph so it will be similar size to previously displayed side-by-side graphs
            fig, ax = plt.subplots(1, 2)

            ax1 = ax[0]

            #plot the graph
            line,  = ax1.plot(scan_point_graph.x_data, scan_point_graph.y_data)
            
            #set x-axis scale to log base 2
            ax1.set_xscale("log", base = 2)

            #use FixedLocator for ticks placed at fixed locations
            ax1.xaxis.set_major_locator(tick.FixedLocator(tick_locations))

            #custom formatter to display integer labels
            #not using FixedFormatter because the tick labels become strings
            #which causes the plot to be unable to display x-coordinates of the mouse position
            #when hovering over the graph
            ax1.xaxis.set_major_formatter(tick.FuncFormatter(lambda x, _: f'{int(x)}'))
        
            #label x axis
            ax1.set_xlabel(scan_point_graph.x_label_with_unit)

            #label y-axis
            ax1.set_ylabel(scan_point_graph.y_label_with_unit)

            #label title of graph
            ax1.set_title(f"Scan Point {scan_point_graph.scan_point_no}")

            #set bottom limit of x-axis
            ax1.set_xlim([scan_point_graph.x_min, 10000])

            #display major grid
            ax1.grid(which="major", color="dimgrey", linewidth=0.5)

            #display minor grid
            ax1.minorticks_on()
            ax1.grid(which="minor", linestyle=":", color="lightgrey", linewidth=1)

            #display annotated cursor showing coordinates of the graph based on x location of mouse
            cursor = AnnotatedCursor(line=line,
            numberformat="{}\n{}",
            dataaxis='x', offset=[10, 10],
            textprops={'color': 'red'},
            ax=ax1,
            useblit=True,
            color='red',
            linewidth=1)   

            #set super title over both subplots
            fig.suptitle(f"{scan_point_graph.scan_name[:-4]}, {scan_point_graph.channel_signal}")

            #set tight layout
            plt.tight_layout()

            '''#maximise plot window
            mng = plt.get_current_fig_manager()
            mng.full_screen_toggle()'''

            #display current subplots
            plt.show(block = False)     #allow to proceed to the next line

            #get user input to see if scan point is anomalous
            print()
            print("Note that there is only one scan point in this measurement.")

            #loop until valid input
            valid0 = False

            while not valid0:

                valid0 = True

                user_anomalous = input("Is the scan point anomalous? Y or N: ")     #N or simply hitting enter key will both mean NO 

                if user_anomalous == "Y" or user_anomalous == "y":

                    anomalous_points_to_exclude = [1]
                
                elif not user_anomalous or user_anomalous == "N" or user_anomalous == "n":

                    anomalous_points_to_exclude = []
                
                else:

                    #error message
                    print("Invalid input. Please try again.")

                    valid0 = False


            #close current subplots
            plt.close()



        #if there is an even number of scan points
        elif self.number_of_scan_points % 2 == 0:

            scan_point_no = 1

            #calculate number of times to loop in order to show all graphs
            times_to_plot = self.number_of_scan_points//2

            #create a for loop to run through all the scan points in the measurement except last one
            for point in range(times_to_plot):
                
                #index to access the scan point in list of scan points for the measurement
                index = scan_point_no - 1

                #create the required channel signal graph for the current scan point
                match channel_signal_type:

                    case "disp":
            
                        scan_point_graph_1 = self.scanpoints[index].disp

                    case "vib":
            
                        scan_point_graph_1 = self.scanpoints[index].vib

                    case "acc":
            
                        scan_point_graph_1 = self.scanpoints[index].acc

                    case "ref1":

                        scan_point_graph_1 = self.scanpoints[index].ref1

                    case "ref2":
            
                        scan_point_graph_1 = self.scanpoints[index].ref2

                    case "ref3":
            
                        scan_point_graph_1 = self.scanpoints[index].ref3

                    case "h1vibref1":
            
                        scan_point_graph_1 = self.scanpoints[index].h1vibref1

                    case "h2vibref1":
            
                        scan_point_graph_1 = self.scanpoints[index].h2vibref1

                    case "vibref1":
            
                        scan_point_graph_1 = self.scanpoints[index].create_vibref1()

                    case "vibref2":
            
                        scan_point_graph_1 = self.scanpoints[index].create_vibref2()
            
                    case "vibref3":
            
                        scan_point_graph_1 = self.scanpoints[index].create_vibref3()

                    case "disp_db":
            
                        scan_point_graph_1 = self.scanpoints[index].create_disp_decibel()

                    case "vib_db":
            
                        scan_point_graph_1 = self.scanpoints[index].create_vib_decibel()

                    case "acc_db":
            
                        scan_point_graph_1 = self.scanpoints[index].create_acc_decibel()

                    case "ref1_db":

                        scan_point_graph_1 = self.scanpoints[index].create_ref1_decibel()

                    case "ref2_db":
            
                        scan_point_graph_1 = self.scanpoints[index].create_ref2_decibel()

                    case "ref3_db":
            
                        scan_point_graph_1 = self.scanpoints[index].create_ref3_decibel()

                    case "h1vibref1_db":
            
                        scan_point_graph_1 = self.scanpoints[index].create_h1vibref1_decibel()

                    case "h2vibref1_db":
            
                        scan_point_graph_1 = self.scanpoints[index].create_h2vibref1_decibel()

                    case "vibref1_db":
            
                        scan_point_graph_1 = self.scanpoints[index].create_vibref1_decibel()

                    case "vibref2_db":
            
                        scan_point_graph_1 = self.scanpoints[index].create_vibref2_decibel()
            
                    case "vibref3_db":
            
                        scan_point_graph_1 = self.scanpoints[index].create_vibref3_decibel()
                

                #plot figure using steps to connect the points
                #the y value for point 2 will be maintained from halfway between point 1 and 2
                #to halfway between point 2 and 3 for example since step setting is mid
                fig, ax = plt.subplots(1, 2)
                
                ax1 = ax[0]
                ax2 = ax[1]
                line1,  = ax1.plot(scan_point_graph_1.x_data, scan_point_graph_1.y_data)
                
                #set x-axis scale to log base 2
                ax1.set_xscale("log", base = 2)

                #use FixedLocator for ticks placed at fixed locations
                ax1.xaxis.set_major_locator(tick.FixedLocator(tick_locations))

                #custom formatter to display integer labels
                #not using FixedFormatter because the tick labels become strings
                #which causes the plot to be unable to display x-coordinates of the mouse position
                #when hovering over the graph
                ax1.xaxis.set_major_formatter(tick.FuncFormatter(lambda x, _: f'{int(x)}'))
            
                #label x axis
                ax1.set_xlabel(scan_point_graph_1.x_label_with_unit)

                #label y-axis
                ax1.set_ylabel(scan_point_graph_1.y_label_with_unit)

                #label title of graph
                ax1.set_title(f"Scan Point {scan_point_graph_1.scan_point_no}")

                #set bottom limit of x-axis
                ax1.set_xlim([scan_point_graph_1.x_min, 10000])

                #display major grid
                ax1.grid(which="major", color="dimgrey", linewidth=0.5)

                #display minor grid
                ax1.minorticks_on()
                ax1.grid(which="minor", linestyle=":", color="lightgrey", linewidth=1)

                #display annotated cursor showing coordinates of the graph based on x location of mouse
                cursor1 = AnnotatedCursor(line=line1,
                numberformat="{}\n{}",
                dataaxis='x', offset=[10, 10],
                textprops={'color': 'red'},
                ax=ax1,
                useblit=True,
                color='red',
                linewidth=1)   

                #increment index counter
                index += 1

                #increment scan point number
                scan_point_no += 1

                #create the required channel signal graph for the next scan point
                match channel_signal_type:

                    case "disp":
            
                        scan_point_graph_2 = self.scanpoints[index].disp

                    case "vib":
            
                        scan_point_graph_2 = self.scanpoints[index].vib

                    case "acc":
            
                        scan_point_graph_2 = self.scanpoints[index].acc

                    case "ref1":

                        scan_point_graph_2 = self.scanpoints[index].ref1

                    case "ref2":
            
                        scan_point_graph_2 = self.scanpoints[index].ref2

                    case "ref3":
            
                        scan_point_graph_2 = self.scanpoints[index].ref3

                    case "h1vibref1":
            
                        scan_point_graph_2 = self.scanpoints[index].h1vibref1

                    case "h2vibref1":
            
                        scan_point_graph_2 = self.scanpoints[index].h2vibref1

                    case "vibref1":
            
                        scan_point_graph_2 = self.scanpoints[index].create_vibref1()

                    case "vibref2":
            
                        scan_point_graph_2 = self.scanpoints[index].create_vibref2()
            
                    case "vibref3":
            
                        scan_point_graph_2 = self.scanpoints[index].create_vibref3()

                    case "disp_db":
            
                        scan_point_graph_2 = self.scanpoints[index].create_disp_decibel()

                    case "vib_db":
            
                        scan_point_graph_2 = self.scanpoints[index].create_vib_decibel()

                    case "acc_db":
            
                        scan_point_graph_2 = self.scanpoints[index].create_acc_decibel()

                    case "ref1_db":

                        scan_point_graph_2 = self.scanpoints[index].create_ref1_decibel()

                    case "ref2_db":
            
                        scan_point_graph_2 = self.scanpoints[index].create_ref2_decibel()

                    case "ref3_db":
            
                        scan_point_graph_2 = self.scanpoints[index].create_ref3_decibel()

                    case "h1vibref1_db":
            
                        scan_point_graph_2 = self.scanpoints[index].create_h1vibref1_decibel()

                    case "h2vibref1_db":
            
                        scan_point_graph_2 = self.scanpoints[index].create_h2vibref1_decibel()

                    case "vibref1_db":
            
                        scan_point_graph_2 = self.scanpoints[index].create_vibref1_decibel()

                    case "vibref2_db":
            
                        scan_point_graph_2 = self.scanpoints[index].create_vibref2_decibel()
            
                    case "vibref3_db":
            
                        scan_point_graph_2 = self.scanpoints[index].create_vibref3_decibel()


                #second subplot
                line2,  = ax2.plot(scan_point_graph_2.x_data, scan_point_graph_2.y_data)

                #set x-axis scale to log base 2
                ax2.set_xscale("log", base = 2)

                #use FixedLocator for ticks placed at fixed locations
                ax2.xaxis.set_major_locator(tick.FixedLocator(tick_locations))

                #custom formatter to display integer labels
                #not using FixedFormatter because the tick labels become strings
                #which causes the plot to be unable to display x-coordinates of the mouse position
                #when hovering over the graph
                ax2.xaxis.set_major_formatter(tick.FuncFormatter(lambda x, _: f'{int(x)}'))
            
                #label x axis
                ax2.set_xlabel(scan_point_graph_2.x_label_with_unit)

                #label y-axis
                ax2.set_ylabel(scan_point_graph_2.y_label_with_unit)

                #label title of graph
                ax2.set_title(f"Scan Point {scan_point_graph_2.scan_point_no}")

                #set bottom limit of x-axis
                ax2.set_xlim([scan_point_graph_2.x_min, 10000])

                #display major grid
                ax2.grid(which="major", color="dimgrey", linewidth=0.5)

                #display minor grid
                ax2.minorticks_on()
                ax2.grid(which="minor", linestyle=":", color="lightgrey", linewidth=1)

                #display annotated cursor showing coordinates of the graph based on x location of mouse
                cursor2 = AnnotatedCursor(line=line2,
                numberformat="{}\n{}",
                dataaxis='x', offset=[10, 10],
                textprops={'color': 'red'},
                ax=ax2,
                useblit=True,
                color='red',
                linewidth=1)

                #set super title over both subplots
                fig.suptitle(f"{scan_point_graph_1.scan_name[:-4]}, {scan_point_graph_1.channel_signal}")

                #set tight layout to prevent graph titles overlapping
                plt.tight_layout()

                '''#maximise plot window
                mng = plt.get_current_fig_manager()
                mng.full_screen_toggle()'''

                #display current subplots
                plt.show(block = False)     #allow to proceed to the next line

                #get user input on which scan point is anomalous
                print()
                print("If there are any scan points that are anomalous and need to be excluded, include below.")
                print("If both, type in the word both")
                print("If there is only one scan point, type in the scan point number e.g 3")
                print("If there is none, just enter")

                #loop until user gives a valid input
                valid = False

                while not valid:

                    valid = True

                    user_anomalous = input("Scan points to exclude: ")


                    #if the user input is not none
                    if user_anomalous:
                        
                        #if user input is both scan points that were displayed
                        if user_anomalous == "both":
                            
                            #append the scan point number of the left graph to the anomalous points list
                            anomalous_points_to_exclude.append(scan_point_no - 1)

                            #append the scan point number of the right graph to the anomalous points list
                            anomalous_points_to_exclude.append(scan_point_no)

                        #if user input is one scan point
                        else:
                            
                            try:
                                
                                #valid scan point number
                                if int(user_anomalous) in range(1, self.number_of_scan_points+1):

                                    #convert user input of one scan point number into an integer and append to anomalous points list
                                    anomalous_points_to_exclude.append(int(user_anomalous))

                                #scan point number does not exist in this measurement
                                else:

                                    #error message
                                    print("The scan point number does not exist in this measurement. Please try again.")

                                    valid = False

                            #input is not 'both' and is also not a number
                            except:
                                
                                #error message
                                print("Invalid input. Please try again.")

                                valid = False
                            

                #close current subplots
                plt.close()

                #increment index counter
                index += 1

                #increment scan point number
                scan_point_no += 1


        #if there is an odd number of scan points
        else:
            
            scan_point_no = 1
            times_to_plot = self.number_of_scan_points//2

            #create a for loop to run through all the scan points in the measurement except last one
            for point in range(times_to_plot):

                #index to access the scan point in list of scan points for the measurement
                index = scan_point_no - 1

                #create the required channel signal graph for the current scan point
                match channel_signal_type:

                    case "disp":
            
                        scan_point_graph_1 = self.scanpoints[index].disp

                    case "vib":
            
                        scan_point_graph_1 = self.scanpoints[index].vib

                    case "acc":
            
                        scan_point_graph_1 = self.scanpoints[index].acc

                    case "ref1":

                        scan_point_graph_1 = self.scanpoints[index].ref1

                    case "ref2":
            
                        scan_point_graph_1 = self.scanpoints[index].ref2

                    case "ref3":
            
                        scan_point_graph_1 = self.scanpoints[index].ref3

                    case "h1vibref1":
            
                        scan_point_graph_1 = self.scanpoints[index].h1vibref1

                    case "h2vibref1":
            
                        scan_point_graph_1 = self.scanpoints[index].h2vibref1

                    case "vibref1":
            
                        scan_point_graph_1 = self.scanpoints[index].create_vibref1()

                    case "vibref2":
            
                        scan_point_graph_1 = self.scanpoints[index].create_vibref2()
            
                    case "vibref3":
            
                        scan_point_graph_1 = self.scanpoints[index].create_vibref3()

                    case "disp_db":
            
                        scan_point_graph_1 = self.scanpoints[index].create_disp_decibel()

                    case "vib_db":
            
                        scan_point_graph_1 = self.scanpoints[index].create_vib_decibel()

                    case "acc_db":
            
                        scan_point_graph_1 = self.scanpoints[index].create_acc_decibel()

                    case "ref1_db":

                        scan_point_graph_1 = self.scanpoints[index].create_ref1_decibel()

                    case "ref2_db":
            
                        scan_point_graph_1 = self.scanpoints[index].create_ref2_decibel()

                    case "ref3_db":
            
                        scan_point_graph_1 = self.scanpoints[index].create_ref3_decibel()

                    case "h1vibref1_db":
            
                        scan_point_graph_1 = self.scanpoints[index].create_h1vibref1_decibel()

                    case "h2vibref1_db":
            
                        scan_point_graph_1 = self.scanpoints[index].create_h2vibref1_decibel()

                    case "vibref1_db":
            
                        scan_point_graph_1 = self.scanpoints[index].create_vibref1_decibel()

                    case "vibref2_db":
            
                        scan_point_graph_1 = self.scanpoints[index].create_vibref2_decibel()
            
                    case "vibref3_db":
            
                        scan_point_graph_1 = self.scanpoints[index].create_vibref3_decibel()


                #plot figure using steps to connect the points
                #the y value for point 2 will be maintained from halfway between point 1 and 2
                #to halfway between point 2 and 3 for example since step setting is mid
                fig, ax = plt.subplots(1, 2)
                
                ax1 = ax[0]
                ax2 = ax[1]
                line1,  = ax1.plot(scan_point_graph_1.x_data, scan_point_graph_1.y_data)
                
                #set x-axis scale to log base 2
                ax1.set_xscale("log", base = 2)

                #use FixedLocator for ticks placed at fixed locations
                ax1.xaxis.set_major_locator(tick.FixedLocator(tick_locations))

                #custom formatter to display integer labels
                #not using FixedFormatter because the tick labels become strings
                #which causes the plot to be unable to display x-coordinates of the mouse position
                #when hovering over the graph
                ax1.xaxis.set_major_formatter(tick.FuncFormatter(lambda x, _: f'{int(x)}'))
            
                #label x axis
                ax1.set_xlabel(scan_point_graph_1.x_label_with_unit)

                #label y-axis
                ax1.set_ylabel(scan_point_graph_1.y_label_with_unit)

                #label title of graph
                ax1.set_title(f"Scan Point {scan_point_graph_1.scan_point_no}")

                #set bottom limit of x-axis
                ax1.set_xlim([scan_point_graph_1.x_min, 10000])

                #display major grid
                ax1.grid(which="major", color="dimgrey", linewidth=0.5)

                #display minor grid
                ax1.minorticks_on()
                ax1.grid(which="minor", linestyle=":", color="lightgrey", linewidth=1)

                #display annotated cursor showing coordinates of the graph based on x location of mouse
                cursor1 = AnnotatedCursor(line=line1,
                numberformat="{}\n{}",
                dataaxis='x', offset=[10, 10],
                textprops={'color': 'red'},
                ax=ax1,
                useblit=True,
                color='red',
                linewidth=1)   

                #increment index counter
                index += 1

                #increment scan point number
                scan_point_no += 1

                #create the required channel signal graph for the next scan point
                match channel_signal_type:

                    case "disp":
            
                        scan_point_graph_2 = self.scanpoints[index].disp

                    case "vib":
            
                        scan_point_graph_2 = self.scanpoints[index].vib

                    case "acc":
            
                        scan_point_graph_2 = self.scanpoints[index].acc

                    case "ref1":

                        scan_point_graph_2 = self.scanpoints[index].ref1

                    case "ref2":
            
                        scan_point_graph_2 = self.scanpoints[index].ref2

                    case "ref3":
            
                        scan_point_graph_2 = self.scanpoints[index].ref3

                    case "h1vibref1":
            
                        scan_point_graph_2 = self.scanpoints[index].h1vibref1

                    case "h2vibref1":
            
                        scan_point_graph_2 = self.scanpoints[index].h2vibref1

                    case "vibref1":
            
                        scan_point_graph_2 = self.scanpoints[index].create_vibref1()

                    case "vibref2":
            
                        scan_point_graph_2 = self.scanpoints[index].create_vibref2()
            
                    case "vibref3":
            
                        scan_point_graph_2 = self.scanpoints[index].create_vibref3()

                    case "disp_db":
            
                        scan_point_graph_2 = self.scanpoints[index].create_disp_decibel()

                    case "vib_db":
            
                        scan_point_graph_2 = self.scanpoints[index].create_vib_decibel()

                    case "acc_db":
            
                        scan_point_graph_2 = self.scanpoints[index].create_acc_decibel()

                    case "ref1_db":

                        scan_point_graph_2 = self.scanpoints[index].create_ref1_decibel()

                    case "ref2_db":
            
                        scan_point_graph_2 = self.scanpoints[index].create_ref2_decibel()

                    case "ref3_db":
            
                        scan_point_graph_2 = self.scanpoints[index].create_ref3_decibel()

                    case "h1vibref1_db":
            
                        scan_point_graph_2 = self.scanpoints[index].create_h1vibref1_decibel()

                    case "h2vibref1_db":
            
                        scan_point_graph_2 = self.scanpoints[index].create_h2vibref1_decibel()

                    case "vibref1_db":
            
                        scan_point_graph_2 = self.scanpoints[index].create_vibref1_decibel()

                    case "vibref2_db":
            
                        scan_point_graph_2 = self.scanpoints[index].create_vibref2_decibel()
            
                    case "vibref3_db":
            
                        scan_point_graph_2 = self.scanpoints[index].create_vibref3_decibel()


                #second subplot
                line2,  = ax2.plot(scan_point_graph_2.x_data, scan_point_graph_2.y_data)

                #set x-axis scale to log base 2
                ax2.set_xscale("log", base = 2)

                #use FixedLocator for ticks placed at fixed locations
                ax2.xaxis.set_major_locator(tick.FixedLocator(tick_locations))

                #custom formatter to display integer labels
                #not using FixedFormatter because the tick labels become strings
                #which causes the plot to be unable to display x-coordinates of the mouse position
                #when hovering over the graph
                ax2.xaxis.set_major_formatter(tick.FuncFormatter(lambda x, _: f'{int(x)}'))
            
                #label x axis
                ax2.set_xlabel(scan_point_graph_2.x_label_with_unit)

                #label y-axis
                ax2.set_ylabel(scan_point_graph_2.y_label_with_unit)

                #label title of graph
                ax2.set_title(f"Scan Point {scan_point_graph_2.scan_point_no}")

                #set bottom limit of x-axis
                ax2.set_xlim([scan_point_graph_2.x_min, 10000])

                #display major grid
                ax2.grid(which="major", color="dimgrey", linewidth=0.5)

                #display minor grid
                ax2.minorticks_on()
                ax2.grid(which="minor", linestyle=":", color="lightgrey", linewidth=1)

                #display annotated cursor showing coordinates of the graph based on x location of mouse
                cursor2 = AnnotatedCursor(line=line2,
                numberformat="{}\n{}",
                dataaxis='x', offset=[10, 10],
                textprops={'color': 'red'},
                ax=ax2,
                useblit=True,
                color='red',
                linewidth=1)

                #set super title over both subplots
                fig.suptitle(f"{scan_point_graph_1.scan_name[:-4]}, {scan_point_graph_1.channel_signal}")

                #set tight layout to prevent graph titles overlapping
                plt.tight_layout()

                '''#maximise plot window
                mng = plt.get_current_fig_manager()
                mng.full_screen_toggle()'''

                #display current subplots
                plt.show(block = False)     #allow to proceed to the next line

                #get user input on which scan point is anomalous
                print()
                print("If there are any scan points that are anomalous and need to be excluded, include below.")
                print("If both, type in the word both")
                print("If there is only one scan point, type in the scan point number e.g 3")
                print("If there is none, just enter")

                
                #loop until user gives a valid input
                valid1 = False

                while not valid1:

                    valid1 = True

                    user_anomalous = input("Scan points to exclude: ")


                    #if the user input is not none
                    if user_anomalous:
                        
                        #if user input is both scan points that were displayed
                        if user_anomalous == "both":
                            
                            #append the scan point number of the left graph to the anomalous points list
                            anomalous_points_to_exclude.append(scan_point_no - 1)

                            #append the scan point number of the right graph to the anomalous points list
                            anomalous_points_to_exclude.append(scan_point_no)

                        #if user input is one scan point
                        else:
                            
                            try:
                                
                                #valid scan point number
                                if int(user_anomalous) in range(1, self.number_of_scan_points+1):

                                    #convert user input of one scan point number into an integer and append to anomalous points list
                                    anomalous_points_to_exclude.append(int(user_anomalous))

                                #scan point number does not exist in this measurement
                                else:

                                    #error message
                                    print("The scan point number does not exist in this measurement. Please try again.")

                                    valid1 = False

                            #input is not 'both' and is also not a number
                            except:
                                
                                #error message
                                print("Invalid input. Please try again.")

                                valid1 = False


                #close current subplots
                plt.close()

                #increment index counter
                index += 1

                #increment scan point number
                scan_point_no += 1


            #last graph

            #create the required channel signal graph for the current scan point
            match channel_signal_type:

                case "disp":
        
                    scan_point_graph_last = self.scanpoints[index].disp

                case "vib":
        
                    scan_point_graph_last = self.scanpoints[index].vib

                case "acc":
        
                    scan_point_graph_last = self.scanpoints[index].acc

                case "ref1":

                    scan_point_graph_last = self.scanpoints[index].ref1

                case "ref2":
        
                    scan_point_graph_last = self.scanpoints[index].ref2

                case "ref3":
        
                    scan_point_graph_last = self.scanpoints[index].ref3

                case "h1vibref1":
        
                    scan_point_graph_last = self.scanpoints[index].h1vibref1

                case "h2vibref1":
        
                    scan_point_graph_last = self.scanpoints[index].h2vibref1

                case "vibref1":
        
                    scan_point_graph_last = self.scanpoints[index].create_vibref1()

                case "vibref2":
        
                    scan_point_graph_last = self.scanpoints[index].create_vibref2()
        
                case "vibref3":
        
                    scan_point_graph_last = self.scanpoints[index].create_vibref3()

                case "disp_db":
        
                    scan_point_graph_last = self.scanpoints[index].create_disp_decibel()

                case "vib_db":
        
                    scan_point_graph_last = self.scanpoints[index].create_vib_decibel()

                case "acc_db":
        
                    scan_point_graph_last = self.scanpoints[index].create_acc_decibel()

                case "ref1_db":

                    scan_point_graph_last = self.scanpoints[index].create_ref1_decibel()

                case "ref2_db":
        
                    scan_point_graph_last = self.scanpoints[index].create_ref2_decibel()

                case "ref3_db":
        
                    scan_point_graph_last = self.scanpoints[index].create_ref3_decibel()

                case "h1vibref1_db":
        
                    scan_point_graph_last = self.scanpoints[index].create_h1vibref1_decibel()

                case "h2vibref1_db":
        
                    scan_point_graph_last = self.scanpoints[index].create_h2vibref1_decibel()

                case "vibref1_db":
        
                    scan_point_graph_last = self.scanpoints[index].create_vibref1_decibel()

                case "vibref2_db":
        
                    scan_point_graph_last = self.scanpoints[index].create_vibref2_decibel()
        
                case "vibref3_db":
        
                    scan_point_graph_last = self.scanpoints[index].create_vibref3_decibel()


            #create a half-sized graph so it will be similar size to previously displayed side-by-side graphs
            fig, ax = plt.subplots(1, 2)

            ax1 = ax[0]

            line,  = ax1.plot(scan_point_graph_last.x_data, scan_point_graph_last.y_data)
            
            #set x-axis scale to log base 2
            ax1.set_xscale("log", base = 2)

            #use FixedLocator for ticks placed at fixed locations
            ax1.xaxis.set_major_locator(tick.FixedLocator(tick_locations))

            #custom formatter to display integer labels
            #not using FixedFormatter because the tick labels become strings
            #which causes the plot to be unable to display x-coordinates of the mouse position
            #when hovering over the graph
            ax1.xaxis.set_major_formatter(tick.FuncFormatter(lambda x, _: f'{int(x)}'))
        
            #label x axis
            ax1.set_xlabel(scan_point_graph_last.x_label_with_unit)

            #label y-axis
            ax1.set_ylabel(scan_point_graph_last.y_label_with_unit)

            #label title of graph
            ax1.set_title(f"Scan Point {scan_point_graph_last.scan_point_no}")

            #set bottom limit of x-axis
            ax1.set_xlim([scan_point_graph_last.x_min, 10000])

            #display major grid
            ax1.grid(which="major", color="dimgrey", linewidth=0.5)

            #display minor grid
            ax1.minorticks_on()
            ax1.grid(which="minor", linestyle=":", color="lightgrey", linewidth=1)

            #display annotated cursor showing coordinates of the graph based on x location of mouse
            cursor = AnnotatedCursor(line=line,
            numberformat="{}\n{}",
            dataaxis='x', offset=[10, 10],
            textprops={'color': 'red'},
            ax=ax1,
            useblit=True,
            color='red',
            linewidth=1)   

            #set super title over both subplots
            fig.suptitle(f"{scan_point_graph_last.scan_name[:-4]}, {scan_point_graph_last.channel_signal}")

            #set tight layout to prevent graph titles overlapping
            plt.tight_layout()

            '''#maximise plot window
            mng = plt.get_current_fig_manager()
            mng.full_screen_toggle()'''

            #display current subplots
            plt.show(block = False)     #allow to proceed to the next line

            #get user input on which scan point is anomalous
            print()
            print("If the scan point is anomalous and needs to be excluded, indicate below.")
            print("If it is anomalous, type in the scan point number e.g. 3")
            print("If not, just enter")

            #loop until valid input
            valid2 = False

            while not valid2:

                valid2 = True

                user_anomalous = input("Scan points to exclude: ")

                #if the user input is not none
                if user_anomalous:
                        
                    try:
                        
                        #valid scan point number
                        if int(user_anomalous) in range(1, self.number_of_scan_points+1):

                            #convert user input of one scan point number into an integer and append to anomalous points list
                            anomalous_points_to_exclude.append(int(user_anomalous))

                        #scan point number does not exist in this measurement
                        else:

                            #error message
                            print("The scan point number does not exist in this measurement. Please try again.")

                            valid2 = False

                    #input is not 'both' and is also not a number
                    except:
                        
                        #error message
                        print("Invalid input. Please try again.")

                        valid2 = False


            #close current subplots
            plt.close()


        #if no anomalous scan points
        if len(anomalous_points_to_exclude) == 0:

            #display a message
            print()
            print(f"No anomalous scan points for {self.scan_name[:-4]}.")

        #if there are anomalous scan points
        else:

            #remove duplicates from anomalous points list if any
            anomalous_points_to_exclude = list(set(anomalous_points_to_exclude))

            #display the list of anomalous scan points
            print()
            print(f"List of anomalous scan points that will be excluded for {self.scan_name[:-4]}: {(str(anomalous_points_to_exclude))[1:-1]}")
            print()


        #update attribute for anomalous points
        self.anomalous_points = anomalous_points_to_exclude

        #create 2D lists for valid and anomalous points generated in this method
        scan_point_coordinates_anomalous = [[], [], [], []]
        scan_point_coordinates_valid = [[], [], [], []]

        #iterate through all the scanpoints in the measurement
        for index in range(len(self.scan_point_coordinates[0])):

            #if current scanpoint is anomalous
            if self.scan_point_coordinates[0][index] in self.anomalous_points:
                
                #append current scan point coordinate details to 2D list for anomalous points
                scan_point_coordinates_anomalous[0].append(self.scan_point_coordinates[0][index])
                scan_point_coordinates_anomalous[1].append(self.scan_point_coordinates[1][index])
                scan_point_coordinates_anomalous[2].append(self.scan_point_coordinates[2][index])
                scan_point_coordinates_anomalous[3].append(self.scan_point_coordinates[3][index])

            #if current scanpoint is valid
            else:

                #append current scan point coordinate details to 2D list for valid points
                scan_point_coordinates_valid[0].append(self.scan_point_coordinates[0][index])
                scan_point_coordinates_valid[1].append(self.scan_point_coordinates[1][index])
                scan_point_coordinates_valid[2].append(self.scan_point_coordinates[2][index])
                scan_point_coordinates_valid[3].append(self.scan_point_coordinates[3][index])

        
        #update attribute for 2D lists for valid and anomalous points
        self.scan_point_coordinates_valid = scan_point_coordinates_valid
        self.scan_point_coordinates_anomalous = scan_point_coordinates_anomalous

        #return list of anomalous_points_to_exclude
        return anomalous_points_to_exclude
    
    

    def get_average(self, channel_signal_type: str, anomalous_indices=None):
        """
        Return a single-point graph or a Graph_average of all non-anomalous points
        for the requested channel (raw or *_db).  If every point is anomalous
        return False.
        """

        table = {
            "disp"      : ("disp",            "create_disp_decibel"),
            "vib"       : ("vib",             "create_vib_decibel"),
            "acc"       : ("acc",             "create_acc_decibel"),
            "ref1"      : ("ref1",            "create_ref1_decibel"),
            "ref2"      : ("ref2",            "create_ref2_decibel"),
            "ref3"      : ("ref3",            "create_ref3_decibel"),
            "h1vibref1" : ("h1vibref1",       "create_h1vibref1_decibel"),
            "h2vibref1" : ("h2vibref1",       "create_h2vibref1_decibel"),
            "vibref1"   : ("create_vibref1",  "create_vibref1_decibel"),
            "vibref2"   : ("create_vibref2",  "create_vibref2_decibel"),
            "vibref3"   : ("create_vibref3",  "create_vibref3_decibel"),
        }

        # helper to fetch the correct graph from one ScanPoint ----------------
        def _get_graph(scanpoint, channel: str):
            raw_name, db_name = table[channel.replace("_db", "")]
            if channel.endswith("_db"):
                return getattr(scanpoint, db_name)()
            # raw
            return getattr(scanpoint, raw_name)

        if anomalous_indices != None:
            anomalous = anomalous_indices
        else:
            anomalous = set(self.get_anomalous(channel_signal_type))   # point numbers
        if len(anomalous) == self.number_of_scan_points:
            print(f"Error: All scan-points in {self.scan_name[:-4]} are anomalous.")
            

        if self.number_of_scan_points == 1:
            if 1 in anomalous:
                print(f"Error: The only scan-point is anomalous in {self.scan_name[:-4]}")
            return _get_graph(self.scanpoints[0], channel_signal_type)

        graphs_to_avg = [
            _get_graph(sp, channel_signal_type)
            for sp in self.scanpoints
            if sp.scan_point_no not in anomalous
        ]

        # safety: should never be empty here, but guard anyway
        if not graphs_to_avg:
            print(f"Error: No valid scan-points left in {self.scan_name[:-4]}")
            return False

        # build averaged graph 
        return Graph_average(graphs_to_avg, list(anomalous))

    def create_bands(self, channel_signal_type):

        '''Method to allow user to group scan points into bands'''

        #display scan points layout
        self.plot_scan_points_coordinates()

        #2D list to store bands
        all_bands = []

        #instructions
        print()
        print("Please do not close the scanpoint layout window until all banding has been completed.")
        print("Points that have not been added to a band are displayed in grey.")
        print("Points that have been indicated as anomalous as represented by red crosses and cannot be chosen.")
        print("You may not assign the same point to two different bands.")
        print("Key in point numbers to include in the band, using only a dash to separate each point number.")
        print("For example: 1-2-3")

        #list of scanpoints which have been assigned a band
        points_assigned = []

        #counter for the band currently being defined
        band_no = 1

        #loop until all valid points have been assigned to a band and banding is complete
        while len(points_assigned) < self.number_of_scan_points - len(self.anomalous_points):
            

            #loop until user gives valid input
            valid_band = False

            while not valid_band:

                #get user input
                print()
                str_points = input(f"Band {band_no}: ")

                #remove spaces if any
                str_points.replace(" ", "")
                    
                #convert user input into a list of strings of point numbers
                list_points = str_points.split("-")

                #try to convert input point numbers to integers
                try:

                    #create a list of integer point numbers
                    chosen_scan_points = [int(point) for point in list_points]

                    #true false flag for whether all the points chosen are valid
                    valid_points = True

                    #iterate through all the chosen scanpoints to make sure they are existing scanpoints in the measurement
                    for point in chosen_scan_points:
                        
                        #if the point is noy a valid scanpoint for the measurement
                        if point < 1 or point > self.number_of_scan_points:

                            print(f"Point {point} does not exist for this measurement.")
                            
                            #switch flag as invalid
                            valid_points = False


                    #iterate through all the chosen scanpoints to make sure they have not been previously declared anomalous
                    for point in chosen_scan_points:
                        
                        #if the point has been declared anomalous before
                        if point in self.anomalous_points:

                            print(f"Point {point} is anomalous and cannot be used. ")
                            
                            #switch flag as invalid
                            valid_points = False


                    #iterate through all the chosen scanpoints to make sure they have not been selected before for another band
                    for point in chosen_scan_points:
                        
                        #if the point has already been chosen in a previous band
                        if point in points_assigned:

                            print(f"Point {point} has already been included in a previous band and cannot be used again. ")
                            
                            #switch flag as invalid
                            valid_points = False


                    #if points are valid
                    if valid_points:

                        #append list of chosen scan points for this band to the list of all bands
                        all_bands.append(chosen_scan_points)

                        #add all the points that have been assigned to this band to the overall list of points_assigned
                        points_assigned += chosen_scan_points

                        #create a counter index to iterate through self.band_colours
                        colour_index = 0

                        #display all the scan points again with each band highlighted with different colour, overlay on the original plot
                        #iterate through all the bands that have been defined
                        for band in all_bands:
                            
                            #2D list of scanpoint coordinates included in the band
                            #structure is [[point numbers], [x-coordinates], [y-coordinates], [z-coordinates]]
                            band_point_coordinates = [[], [], [], []]

                            #iterate through each point in this band
                            for point in band:
                                
                                #calculate index to access point data
                                #e.g. point 1 will be at index 0 of each of the lists in the 2D list of self.scan_point_coordinates
                                point_index = point - 1

                                #append point data to band_point_coordinates 2D list
                                band_point_coordinates[0].append(point)
                                band_point_coordinates[1].append(self.scan_point_coordinates[1][point_index])
                                band_point_coordinates[2].append(self.scan_point_coordinates[2][point_index])
                                band_point_coordinates[3].append(self.scan_point_coordinates[3][point_index])
                            
                            #plot current band, select next colour from self.band_colours
                            plt.scatter(band_point_coordinates[1], band_point_coordinates[2], c = self.band_colours[colour_index], label = f"Band {colour_index + 1}")

                            #increment colour index
                            colour_index += 1


                        #iterate through all the scan points
                        for point_index in range(len(self.scan_point_coordinates[0])): 
                            
                            #label each point with point number
                            #annotate at a higher y-value than the point so it does not overlap
                            plt.annotate(self.scan_point_coordinates[0][point_index], (self.scan_point_coordinates[1][point_index], self.scan_point_coordinates[2][point_index]))

                        #set equal scaling for both axes so that the shape of the group of points will be correct
                        plt.axis("equal")

                        #allow program to continue executing even when figure is open
                        plt.show(block = False)

                        #increment band number
                        band_no += 1

                        #end while loop
                        valid_band = True


                    else:

                        #invalid so will repeat loop by leaving valid_band flag as False
                        
                        print("Please define this band again. ")


                #invalid input format
                except:

                    print("Input must be a list of integer point numbers separated by a comma. Do not use words e.g. one, two, three.")
                    print("Please define this band again. ")

        #close plot
        plt.close()

        #update attribute
        self.all_bands = all_bands

        #list to store bands, each band as a list of their scan point objects
        all_bands_points = []

        #iterate through list of bands
        for band in all_bands:

            #list to store the required channel signal graph for all the points in this band
            band_points = []

            #iterate through each point number in current band
            for point_number in band:

                #get index to access current point in self.scanpoints
                index = point_number - 1
                
                #append scan point object to band_points list
                band_points.append(self.scanpoints[index])

            #append list of scan point objects for this band to all_bands_points
            all_bands_points.append(band_points)

        #update attribute
        self.all_bands_points = all_bands_points

        #return all_bands
        return all_bands

    def bands_layout(self):

        '''Method to display scatter plot of scan points with each band differentiated by colour'''

        #create a counter index to iterate through self.band_colours
        colour_index = 0

        #display all the scan points again with each band highlighted with different colour, overlay on the original plot
        #iterate through all the bands that have been defined
        for band in self.all_bands:
            
            #2D list of scanpoint coordinates included in the band
            #structure is [[point numbers], [x-coordinates], [y-coordinates], [z-coordinates]]
            band_point_coordinates = [[], [], [], []]

            #iterate through each point in this band
            for point in band:
                
                #calculate index to access point data
                #e.g. point 1 will be at index 0 of each of the lists in the 2D list of self.scan_point_coordinates
                point_index = point - 1

                #append point data to band_point_coordinates 2D list
                band_point_coordinates[0].append(point)
                band_point_coordinates[1].append(self.scan_point_coordinates[1][point_index])
                band_point_coordinates[2].append(self.scan_point_coordinates[2][point_index])
                band_point_coordinates[3].append(self.scan_point_coordinates[3][point_index])
            
            #plot current band, select next colour from self.band_colours
            plt.scatter(band_point_coordinates[1], band_point_coordinates[2], c = self.band_colours[colour_index], label = f"Band {colour_index + 1}")

            #increment colour index
            colour_index += 1


        #if there are anomalous scanpoints
        if len(self.scan_point_coordinates_anomalous[0]) > 0:
            
            #plot all anomalous scanpoints as crosses
            plt.scatter(self.scan_point_coordinates_anomalous[1], self.scan_point_coordinates_anomalous[2], marker = "x", color = "red", label = "Anomalous")


        #iterate through all the scan points
        for point_index in range(len(self.scan_point_coordinates[0])): 
            
            #label each point with point number
            #annotate at a higher y-value than the point so it does not overlap
            plt.annotate(self.scan_point_coordinates[0][point_index], (self.scan_point_coordinates[1][point_index], self.scan_point_coordinates[2][point_index]))

        #set equal scaling for both axes so that the shape of the group of points will be correct
        plt.axis("equal")

        #update legend for the plot to show band numbers
        plt.legend(loc = "best")

        #show plot but allow program to continue executing even when figure is open
        plt.show(block = False)
            
        #use this to get the message box and file dialog to show as top windows later
        window = Tk()
        window.wm_attributes('-topmost', 1)

        #suppress the Tk window
        window.withdraw()

        #loop until user chooses a filename
        valid_filename = False

        while not valid_filename:

            #display a message box
            messagebox.showinfo("Save Scan Points Layout as Photo", "Choose Folder to Save Photo in", parent =window)

            #get user to choose name and folder location to save photo file in
            user_photo_filename = filedialog.asksaveasfilename(parent = window, initialdir = "C:\\", initialfile = f"{self.scan_name[:-4]} Scan Layout.png", filetypes = [(".png", "*.png")], defaultextension = ".png", confirmoverwrite = True)

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

        #save as the plot as a png image
        plt.savefig(user_photo_filename, dpi=300, bbox_inches="tight")



    def get_band_averages(self, channel_signal_type):
        
        '''Method to create average graph objects for each band, and store in a list and return the list.'''

        #define anomalous points 
        self.get_anomalous(channel_signal_type)

        #get user to define bands
        self.create_bands(channel_signal_type)

        #display and save all defined bands
        self.bands_layout()

        #list to store bands, each band as a list of their points with the required channel signal
        all_bands_channel_signal = []

        #iterate through all the bands that have been defined
        for band in self.all_bands_points:
            
            #list to store the required channel signal graph for all the points in this band
            band_channel_signal = []
            
            #iterate through each scan point object in the current band
            for point in band:

                #append the required channel signal graph for the point to the list for this band
                match channel_signal_type:

                    case "disp":
            
                        band_channel_signal.append(point.disp)

                    case "vib":
            
                        band_channel_signal.append(point.vib)

                    case "acc":
            
                        band_channel_signal.append(point.acc)

                    case "ref1":

                        band_channel_signal.append(point.ref1)

                    case "ref2":
            
                        band_channel_signal.append(point.ref2)

                    case "ref3":
            
                        band_channel_signal.append(point.ref3)

                    case "h1vibref1":
            
                        band_channel_signal.append(point.h1vibref1)

                    case "h2vibref1":
            
                        band_channel_signal.append(point.h2vibref1)

                    case "vibref1":
            
                        band_channel_signal.append(point.create_vibref1())

                    case "vibref2":
            
                        band_channel_signal.append(point.create_vibref2())
            
                    case "vibref3":
            
                        band_channel_signal.append(point.create_vibref3())

                    case "disp_db":
            
                        band_channel_signal.append(point.create_disp_decibel())

                    case "vib_db":
            
                        band_channel_signal.append(point.create_vib_decibel())

                    case "acc_db":
            
                        band_channel_signal.append(point.create_acc_decibel())

                    case "ref1_db":

                        band_channel_signal.append(point.create_ref1_decibel())

                    case "ref2_db":
            
                        band_channel_signal.append(point.create_ref2_decibel())

                    case "ref3_db":
            
                        band_channel_signal.append(point.create_ref3_decibel())

                    case "h1vibref1_db":
            
                        band_channel_signal.append(point.create_h1vibref1_decibel())

                    case "h2vibref1_db":
            
                        band_channel_signal.append(point.create_h2vibref1_decibel())

                    case "vibref1_db":
            
                        band_channel_signal.append(point.create_vibref1_decibel())

                    case "vibref2_db":
            
                        band_channel_signal.append(point.create_vibref2_decibel())
            
                    case "vibref3_db":
            
                        band_channel_signal.append(point.create_vibref3_decibel())


            #append the list of graph objects for this band into all_bands_channel_signal
            all_bands_channel_signal.append(band_channel_signal)


        #create a list of average graph objects for each band, no anomalous points in the bands, set scan name as Band (band number)
        band_averages = [Graph_average(all_bands_channel_signal[index], [], scan_name=f"Band {index+1}") for index in range(len(all_bands_channel_signal))]

        #create a list of remarks, one for for each band
        #indicate color of band as shown on scan layout, as well as the scanpoints included in the band
        remarks_list = [f"Band colour: {self.band_colours[index]}. Band points: {str(self.all_bands[index])[1:-1]}" for index in range(len(self.all_bands))]

        #update attributes
        self.band_averages = band_averages
        self.band_remarks = remarks_list

        #return band_averages
        return band_averages



    def compare_band_averages_export(self, channel_signal_type):

        '''Method to export band averages.'''

        #call band_averages method to update results to self.band_averages attribute
        self.get_band_averages(channel_signal_type)

        #create hxml file
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
            user_filename = filedialog.asksaveasfilename(parent = window, initialdir = "C:\\", initialfile = f"{self.scan_name[:-4]} Compare Band Averages.hxml", filetypes = [(".hxml", "*.hxml")], defaultextension = ".hxml", confirmoverwrite = True)

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
        hxml_object.graphs_to_hxml(self.band_averages, self.band_remarks)

        #get file name without folder directory and extension
        file_name_without_extension = os.path.splitext(os.path.basename(user_filename))[0]

        #return just file name without folder directory and extension
        return file_name_without_extension
        




    def compare_band_averages_plot(self, channel_signal_type):

        '''Method to export and then plot band averages.'''

        file_name_without_extension = self.compare_band_averages_export(channel_signal_type)


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
        
        #create list of lines using a list constructor
        #one line for each band, and using the color for that band
        #color allocation is same as when showing layout of all the bands using self.display_bands method for easy comparison
        line_list = [ax.plot(self.band_averages[index].x_data, self.band_averages[index].y_data, label = f"{(self.band_averages[index].scan_name)} Average", color = self.band_colours[index]) for index in range(len(self.band_averages))]

        plt.xscale("log", base = 2)

        ax.xaxis.set_major_locator(tick.FixedLocator(tick_locations))

        ax.xaxis.set_major_formatter(tick.FuncFormatter(lambda x, _: f'{int(x)}'))

        plt.xlabel(self.band_averages[0].x_label_with_unit)

        plt.ylabel(self.band_averages[0].y_label_with_unit)

        plt.title(f"{self.band_averages[0].channel_signal} Band Average Comparison")

        plt.xlim([self.band_averages[0].x_min, 10000])

        #display major grid
        plt.grid(which="major", color="dimgrey", linewidth=0.5)

        #display minor grid
        plt.minorticks_on()
        plt.grid(which="minor", linestyle=":", color="lightgrey", linewidth=1)

        #display a legend for the plot
        plt.legend(loc = "best")        #change loc to a fixed location eg lower right for faster speed

        #save the plot as a png image, adapted from Kuan Hsien code line for savefig
        plt.savefig(user_photo_filename, dpi=300, bbox_inches="tight")

        #display the graph
        plt.show()



#tester code for displaying scan point locations
if __name__ == "__main__":

    measurement_plane = Measurement_Plane("Measurement\\LaserVibrometerPythonAnalyser\\laser_vibrometer_scans\\RAI-DU Top.uff")

    measurement_plane.compare_band_averages_plot("vibref1_db")