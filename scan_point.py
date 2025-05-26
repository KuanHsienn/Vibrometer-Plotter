import matplotlib.pyplot as plt
import numpy as np
from scan_point_graph import Graph, Graph_decibel, Graph_quotient
import data_tools as dt

#class for one scan point
class Scan_Point:

    def __init__(self, scan_point_all_graphs, disp_decibel_reference = 1, vib_decibel_reference = 1, acc_decibel_reference = 1, ref1_decibel_reference = 0.00002, ref2_decibel_reference = 1, ref3_decibel_reference = 1, h1vibref1_decibel_reference = 50000, h2vibref1_decibel_reference = 50000, vibref1_decibel_reference = 50000, vibref2_decibel_reference = 1, vibref3_decibel_reference = 1):
        '''Take in a list of all graphs relating to one scan point in the order: 
        Vib Displacement (disp), Vib Velocity (vib), Vib Acceleration (acc), 
        Ref1, Ref2, Ref3, H1 Vib & Ref1, H2 Vib & Ref1. 
        Optional to specify decibel reference values. 
        Default decibel reference value is 1, except for ref1 sound pressure level which is 20 micro pascals'''


        #attribute for list of all graph data for this scan point
        self.scan_point_all_graphs = scan_point_all_graphs

        #attribute storing number of graphs for this scan point
        self.number_of_graphs = len(self.scan_point_all_graphs)

        #attributes for decibel reference values
        self.disp_decibel_reference = disp_decibel_reference
        self.vib_decibel_reference = vib_decibel_reference
        self.acc_decibel_reference = acc_decibel_reference
        self.ref1_decibel_reference = ref1_decibel_reference
        self.ref2_decibel_reference = ref2_decibel_reference
        self.ref3_decibel_reference = ref3_decibel_reference
        self.h1vibref1_decibel_reference = h1vibref1_decibel_reference
        self.h2vibref1_decibel_reference = h2vibref1_decibel_reference
        self.vibref1_decibel_reference = vibref1_decibel_reference
        self.vibref2_decibel_reference = vibref2_decibel_reference
        self.vibref3_decibel_reference = vibref3_decibel_reference

        #attribute for scan point number using scan point of disp graph
        self.scan_point_no = int(self.scan_point_all_graphs[0]["rsp_node"])

        #initialise a Graph object for each type of graph for the scan point
        self.disp = Graph(self.scan_point_all_graphs[0])
        self.vib = Graph(self.scan_point_all_graphs[1])
        self.acc = Graph(self.scan_point_all_graphs[2])
        self.ref1 = Graph(self.scan_point_all_graphs[3])
        self.ref2 = Graph(self.scan_point_all_graphs[4])
        self.ref3 = Graph(self.scan_point_all_graphs[5])
        self.h1vibref1 = Graph(self.scan_point_all_graphs[6])
        self.h2vibref1 = Graph(self.scan_point_all_graphs[7])
        
        #attributes to store transfer function graph
        #the graph division is only done when the method for transfer function is called
        #only then will the converted graph be linked to these attributes
        #this is to reduce the processing needed as graph division will be only done on request
        self.vibref1 = None
        self.vibref2 = None
        self.vibref3 = None

        #attributes to store graphs converted to decibels
        #the decibel conversion is only done when the method for conversion is called
        #only then will the converted graph be linked to these attributes
        #this is to reduce the processing needed as decibel conversion will be only done on request
        self.disp_decibel = None
        self.vib_decibel = None
        self.acc_decibel = None
        self.ref1_decibel = None
        self.ref2_decibel = None
        self.h1vibref1_decibel = None
        self.h2vibref1_decibel = None
        self.vibref1_decibel = None
        self.vibref2_decibel = None
        self.vibref3_decibel = None


    def create_vibref1(self):

        #initialise a new Graph_quotient object with vib as dividend and ref1 as divisor
        #save the new object under the respective attribute
        self.vibref1 = Graph_quotient(self.vib, self.ref1)

        #return the created object
        return self.vibref1


    def create_vibref2(self):

        #initialise a new Graph_quotient object with vib as dividend and ref2 as divisor
        #save the new object under the respective attribute
        self.vibref2 = Graph_quotient(self.vib, self.ref2)

        #return the created object
        return self.vibref2


    def create_vibref3(self):

        #initialise a new Graph_quotient object with vib as dividend and ref3 as divisor
        #save the new object under the respective attribute
        self.vibref3 = Graph_quotient(self.vib, self.ref3)

        #return the created object
        return self.vibref3


    def create_disp_decibel(self):
        
        #initialise a new Graph_decibel object with disp converted to decibel
        #save the new object under the respective attribute
        self.disp_decibel = Graph_decibel(self.disp, 1, self.disp_decibel_reference)

        #return the created object
        return self.disp_decibel
    

    def create_vib_decibel(self):
        
        #initialise a new Graph_decibel object with vib converted to decibel
        #save the new object under the respective attribute
        self.vib_decibel = Graph_decibel(self.vib, 1, self.vib_decibel_reference)

        #return the created object
        return self.vib_decibel


    def create_acc_decibel(self):
        
        #initialise a new Graph_decibel object with acc converted to decibel
        #save the new object under the respective attribute
        #for acceleration use decibel_type 2 to do decibel conversion since it has squared units
        self.acc_decibel = Graph_decibel(self.acc, 2, self.acc_decibel_reference)

        #return the created object
        return self.acc_decibel
    

    def create_ref1_decibel(self):
        
        #initialise a new Graph_decibel object with ref1 converted to decibel
        #save the new object under the respective attribute
        self.ref1_decibel = Graph_decibel(self.ref1, 1, self.ref1_decibel_reference)

        #return the created object
        return self.ref1_decibel


    def create_ref2_decibel(self):
        
        #initialise a new Graph_decibel object with ref2 converted to decibel
        #save the new object under the respective attribute
        self.ref2_decibel = Graph_decibel(self.ref2, 1, self.ref2_decibel_reference)

        #return the created object
        return self.ref2_decibel


    def create_ref3_decibel(self):
        
        #initialise a new Graph_decibel object with ref3 converted to decibel
        #save the new object under the respective attribute
        self.ref3_decibel = Graph_decibel(self.ref3, 1, self.ref3_decibel_reference)

        #return the created object
        return self.ref3_decibel


    def create_h1vibref1_decibel(self):
        
        #initialise a new Graph_decibel object with h1vibref1_decibel converted to decibel
        #save the new object under the respective attribute
        self.h1vibref1_decibel = Graph_decibel(self.h1vibref1, 1, self.h1vibref1_decibel_reference)

        #return the created object
        return self.h1vibref1_decibel


    def create_h2vibref1_decibel(self):
        
        #initialise a new Graph_decibel object with h2vibref1_decibel converted to decibel
        #save the new object under the respective attribute
        self.h2vibref1_decibel = Graph_decibel(self.h2vibref1, 1, self.h2vibref1_decibel_reference)

        #return the created object
        return self.h2vibref1_decibel


    def create_vibref1_decibel(self):
        
        #this method will create both transfer graph and transfer graph converted to decibel

        #initialise a new Graph_quotient object with vib as dividend and ref1 as divisor
        #save the new object under the respective attribute
        self.vibref1 = Graph_quotient(self.vib, self.ref1)

        #initialise a new Graph_decibel object with vibref1 converted to decibel
        #save the new object under the respective attribute
        self.vibref1_decibel = Graph_decibel(self.vibref1, 1, self.vibref1_decibel_reference)

        #return the created object
        return self.vibref1_decibel


    def create_vibref2_decibel(self):
        
        #this method will create both transfer graph and transfer graph converted to decibel

        #initialise a new Graph_quotient object with vib as dividend and ref2 as divisor
        #save the new object under the respective attribute
        self.vibref2 = Graph_quotient(self.vib, self.ref2)

        #initialise a new Graph_decibel object with vibref2 converted to decibel
        #save the new object under the respective attribute
        self.vibref2_decibel = Graph_decibel(self.vibref2, 1, self.vibref2_decibel_reference)

        #return the created object
        return self.vibref2_decibel

    
    def create_vibref3_decibel(self):
        
        #this method will create both transfer graph and transfer graph converted to decibel

        #initialise a new Graph_quotient object with vib as dividend and ref3 as divisor
        #save the new object under the respective attribute
        self.vibref3 = Graph_quotient(self.vib, self.ref3)

        #initialise a new Graph_decibel object with vibref3 converted to decibel
        #save the new object under the respective attribute
        self.vibref3_decibel = Graph_decibel(self.vibref3, 1, self.vibref3_decibel_reference)

        #return the created object
        return self.vibref3_decibel