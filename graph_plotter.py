import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import numpy as np
import data_tools as dt
from annotated_cursor import AnnotatedCursor
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def graph_plotter(graph, *args, **kwargs):
    
    '''Method to plot an individual graph or a subplot of graphs depending on input,
    but will not show plots yet'''
    
    tick_locations = [100, 200, 500, 1000, 2000, 5000, 10000]
    number_of_graphs = len(args)

    if number_of_graphs == 0:
        # Single graph
        fig, ax = plt.subplots()
        line, = ax.plot(graph.x_data, graph.y_data)
        
        plt.xscale("log", base=2)
        ax.xaxis.set_major_locator(tick.FixedLocator(tick_locations))
        ax.xaxis.set_major_formatter(tick.FuncFormatter(lambda x, _: f'{int(x)}'))
        
        ax.set_xlabel(graph.x_label_with_unit)
        ax.set_ylabel(graph.y_label_with_unit)
        ax.set_title(graph.plot_title)
        ax.set_xlim([graph.x_min, 10000])

        # Annotated cursor (optional, remove if not needed)
        cursor = AnnotatedCursor(
            line=line,
            numberformat="{}\n{}",
            dataaxis='x',
            offset=[10, 10],
            textprops={'color': 'red'},
            ax=ax,
            useblit=True,
            color='red',
            linewidth=1
        )

    else:
        # Multiple subplots
        fig, ax = plt.subplots(1, number_of_graphs)
        
        # First subplot
        line1, = ax[0].plot(graph.x_data, graph.y_data)
        ax[0].set_xscale("log", base=2)
        ax[0].xaxis.set_major_locator(tick.FixedLocator(tick_locations))
        ax[0].xaxis.set_major_formatter(tick.FuncFormatter(lambda x, _: f'{int(x)}'))
        ax[0].set_xlabel(graph.x_label_with_unit)
        ax[0].set_ylabel(graph.y_label_with_unit)
        ax[0].set_title(graph.plot_title)
        ax[0].set_xlim([graph.x_min, 10000])

        cursor1 = AnnotatedCursor(
            line=line1,
            numberformat="{}\n{}",
            dataaxis='x',
            offset=[10, 10],
            textprops={'color': 'red'},
            ax=ax[0],
            useblit=True,
            color='red',
            linewidth=1
        )

        # Remaining subplots
        for i, additional_graph in enumerate(args, start=1):
            line, = ax[i].plot(additional_graph.x_data, additional_graph.y_data)
            ax[i].set_xscale("log", base=2)
            ax[i].xaxis.set_major_locator(tick.FixedLocator(tick_locations))
            ax[i].xaxis.set_major_formatter(tick.FuncFormatter(lambda x, _: f'{int(x)}'))
            ax[i].set_xlabel(additional_graph.x_label_with_unit)
            ax[i].set_ylabel(additional_graph.y_label_with_unit)
            ax[i].set_title(additional_graph.plot_title)
            ax[i].set_xlim([additional_graph.x_min, 10000])

            cursor = AnnotatedCursor(
                line=line,
                numberformat="{}\n{}",
                dataaxis='x',
                offset=[10, 10],
                textprops={'color': 'red'},
                ax=ax[i],
                useblit=True,
                color='red',
                linewidth=1
            )

    # Apply grids (for all subplots)
    for axis in (ax if number_of_graphs > 0 else [ax]):
        axis.grid(which="major", color="dimgrey", linewidth=0.5)
        axis.minorticks_on()
        axis.grid(which="minor", linestyle=":", color="lightgrey", linewidth=1)

    return fig