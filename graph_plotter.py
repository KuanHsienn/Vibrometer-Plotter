import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import numpy as np
import data_tools as dt
from annotated_cursor import AnnotatedCursor


def graph_plotter(graph, *args, **kwargs):
    
    '''Method to plot an individual graph or a subplot of graphs depending on input,
    but will not show plots yet'''

    
    #list containing locations to place ticks
    tick_locations = [100, 200, 500, 1000, 2000, 5000, 10000]

    number_of_graphs = len(args)

    #if no additional graphs are provided
    if number_of_graphs == 0:
        
        #plot an individual graph
        fig, ax = plt.subplots()

        #plot graph using steps to connect the points
        #the y value for point 2 will be maintained from halfway between point 1 and 2
        #to halfway between point 2 and 3 for example since step setting is mid
        line, = ax.plot(graph.x_data, graph.y_data)
    
        #set x-axis scale to log base 2
        plt.xscale("log", base = 2)

        #use FixedLocator for ticks placed at fixed locations
        ax.xaxis.set_major_locator(tick.FixedLocator(tick_locations))

        #custom formatter to display integer labels
        #not using FixedFormatter because the tick labels become strings
        #which causes the plot to be unable to display x-coordinates of the mouse position
        #when hovering over the graph
        ax.xaxis.set_major_formatter(tick.FuncFormatter(lambda x, _: f'{int(x)}'))

        #label x axis
        plt.xlabel(graph.x_label_with_unit)

        #label y-axis
        plt.ylabel(graph.y_label_with_unit)

        #label title of graph
        plt.title(graph.plot_title)

        #set bottom limit of x-axis
        plt.xlim([graph.x_min, 10000])


        #display annotated cursor showing coordinates of the graph based on x location of mouse
        cursor = AnnotatedCursor(line=line,
        numberformat="{}\n{}",
        dataaxis='x', offset=[10, 10],
        textprops={'color': 'red'},
        ax=ax,
        useblit=True,
        color='red',
        linewidth=1)


    else:

        #plot graphs as subplots
        fig, ax = plt.subplots(1, number_of_graphs)

        ax1 = ax[0]
        line1,  = ax1.plot(graph.x_data, graph.y_data)
        
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
        ax1.set_xlabel(graph.x_label_with_unit)

        #label y-axis
        ax1.set_ylabel(graph.y_label_with_unit)

        #label title of graph
        ax1.set_title(graph.plot_title)

        #set bottom limit of x-axis
        ax1.set_xlim([graph.x_min, 10000])


        #display annotated cursor showing coordinates of the graph based on x location of mouse
        cursor1 = AnnotatedCursor(line=line1,
        numberformat="{}\n{}",
        dataaxis='x', offset=[10, 10],
        textprops={'color': 'red'},
        ax=ax1,
        useblit=True,
        color='red',
        linewidth=1)


        #initialise index counter
        index = 1

        #loop through remaining graphs
        for additional_graph in args:

            #second subplot
            additional_line,  = ax[index].plot(additional_graph.x_data, additional_graph.y_data)

            #set x-axis scale to log base 2
            ax[index].set_xscale("log", base = 2)

            #use FixedLocator for ticks placed at fixed locations
            ax[index].xaxis.set_major_locator(tick.FixedLocator(tick_locations))

            #custom formatter to display integer labels
            #not using FixedFormatter because the tick labels become strings
            #which causes the plot to be unable to display x-coordinates of the mouse position
            #when hovering over the graph
            ax[index].xaxis.set_major_formatter(tick.FuncFormatter(lambda x, _: f'{int(x)}'))
        
            #label x axis
            ax[index].set_xlabel(additional_graph.x_label_with_unit)

            #label y-axis
            ax[index].set_ylabel(additional_graph.y_label_with_unit)

            #label title of graph
            ax[index].set_title(additional_graph.plot_title)

            #set bottom limit of x-axis
            ax[index].set_xlim([additional_graph.x_min, 10000])


            #display annotated cursor showing coordinates of the graph based on x location of mouse
            cursor2 = AnnotatedCursor(line=additional_line,
            numberformat="{}\n{}",
            dataaxis='x', offset=[10, 10],
            textprops={'color': 'red'},
            ax=ax[index],
            useblit=True,
            color='red',
            linewidth=1)

            #increment index counter
            index += 1


    #display major grid
    plt.grid(which="major", color="dimgrey", linewidth=0.5)

    #display minor grid
    plt.minorticks_on()
    plt.grid(which="minor", linestyle=":", color="lightgrey", linewidth=1)


    #return None
    return