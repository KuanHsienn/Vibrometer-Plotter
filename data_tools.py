import numpy as np


def array_to_decibel_1(input_array, reference = 1):
    '''
    Function for converting values in an array to dB, assuming no squares in units
    takes in an array of values and the reference value for dB conversion
    by default the reference value is 1
    perform conversion element wise and create a new output array
    using dB conversion 20log10(ratio)
    Commented print statements are for debugging purposes
    '''

    #print(input_array)

    #do element wise division of input array by refence to get ratio
    ratio_array = np.divide(input_array, reference)
    
    #print(ratio_array)

    #perform log10 element wise on the array of ratios
    log_array = np.log10(ratio_array)
    
    #print(log_array)

    #perform element wise multiplication by 20 on the array of the logarithmic values
    #use 20 instead of 10 because the values being converted do not have squares in their units 
    #e.g. veloctiy, spl and voltage, instead of acceleration and power
    dB_array = np.multiply(log_array, 20)
    
    #print(dB_array)

    return dB_array
 

def array_to_decibel_2(input_array, reference = 1):
    '''
    Function for converting values in an array to dB, if there are squared units
    takes in an array of values and the reference value for dB conversion
    by default the reference value is 1
    perform conversion element wise and create a new output array
    using dB conversion 10log10(ratio)
    Commented print statements are for debugging purposes
    '''

    #print(input_array)

    #do element wise division of input array by refence to get ratio
    ratio_array = np.divide(input_array, reference)
    
    #print(ratio_array)

    #perform log10 element wise on the array of ratios
    log_array = np.log10(ratio_array)
    
    #print(log_array)

    #perform element wise multiplication by 10 on the array of the logarithmic values
    #use 20 instead of 10 because the values being converted do not have squares in their units 
    #e.g. veloctiy, spl and voltage, instead of acceleration and power
    dB_array = np.multiply(log_array, 10)
    
    #print(dB_array)

    return dB_array


#function for returning a shortened scan name
def get_short_names(graph_names):

    #initialise a list to store shortened forms of the graph names
    #to prevent file name becoming too long
    short_names = ""

    #iterate through the list of graph names
    for index in range(len(graph_names)):

        if "Concept B Sample 1" in graph_names[index]:

            #replace shortened name
            graph_names[index] = graph_names[index].replace("Concept B Sample 1", "CBS1")

        elif "Concept B Sample 2" in graph_names[index]:

            #replace shortened name
            graph_names[index] = graph_names[index].replace("Concept B Sample 2", "CBS2")

        elif "RAI Diaphragm-Up" in graph_names[index]:

            #replace shortened name
            graph_names[index] = graph_names[index].replace("RAI Diaphragm-Up", "RAI-DU")
        
        elif "RAI Diaphragm-Side" in graph_names[index]:

            #replace shortened name
            graph_names[index] = graph_names[index].replace("RAI Diaphragm-Side", "RAI-DS")

        elif "D11 Box" in graph_names[index]:

            #replace shortened name
            graph_names[index] = graph_names[index].replace("D11 Box", "D11")

        else:

            #keep current name since it does not need shortening
            pass

    #iterate through the list of graph names except last name
    for index in range(len(graph_names)-1):

        short_names += graph_names[index]
        short_names += " "

    #add the last name
    short_names += graph_names[-1]

    #return shortened names
    return short_names


#function for returning the 
def get_short_chan_signal(channel_signal):

    #create a shortened channel signal name
    short_chan_sig = channel_signal

    #replace each channel signal with the shortened version
    if "Vib  Velocity" in short_chan_sig:
        short_chan_sig = short_chan_sig.replace("Vib  Velocity", "Vib")

    if "Ref1  Sound Pressure" in short_chan_sig:
        short_chan_sig = short_chan_sig.replace("Ref1  Sound Pressure", "Ref1")

    if "Ref2  Voltage" in short_chan_sig:
        short_chan_sig = short_chan_sig.replace("Ref2  Voltage", "Ref2")

    if "Ref3  Voltage" in short_chan_sig:
        short_chan_sig = short_chan_sig.replace("Ref3  Voltage", "Ref3")

    if "Vib  Ref1  H1 Velocity / Sound Pressure" in short_chan_sig:
        short_chan_sig = short_chan_sig.replace("Vib  Ref1  H1 Velocity / Sound Pressure", "H1 Vib Ref1")

    if "Vib  Ref1  H2 Velocity / Sound Pressure" in short_chan_sig:
        short_chan_sig = short_chan_sig.replace("Vib  Ref1  H2 Velocity / Sound Pressure", "H2 Vib Ref1")

    #return shortened channel signal
    return short_chan_sig