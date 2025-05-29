import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from measurement_plane import Measurement_Plane
from surface_average_comparison import Compare_Surface_Average
from device import Device

graph_types = [
    "Vibration Displacement", "Vibration Velocity", "Vibration Acceleration",
    "Ref1", "Ref2", "Ref3", "H1 Vibration Ref1", "H2 Vibration Ref1",
    "Vibration Ref1", "Vibration Ref2", "Vibration Ref3"
]
short_graph_types = [
    "disp", "vib", "acc", "ref1", "ref2", "ref3", "h1vibref1", "h2vibref1",
    "vibref1", "vibref2", "vibref3"
]


class VibroGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Laser Vibrometer Analyser")

        # Make window full screen
        self.state("zoomed")

        self.task_type = tk.StringVar(value="Chooes what type of measurement to process")
        self.graph_unit = tk.StringVar(value="Chooes what type of measurement to process")
        self.graph_index = tk.IntVar(value=0)

        # Create a wrapper frame to center and limit the UI width
        outer_frame = tk.Frame(self)
        outer_frame.pack(expand=True, fill='both')

        # Center inner content using grid
        outer_frame.grid_rowconfigure(0, weight=1)
        outer_frame.grid_columnconfigure(0, weight=1)

        # Main content frame with padding and fixed width
        main_frame = tk.Frame(outer_frame, bd=2, relief='ridge', padx=40, pady=40, bg="#f0f0f0")
        main_frame.grid(row=0, column=0)
        
        # Add title label
        title_label = tk.Label(main_frame, text="Laser Vibrometer Analyser", font=("Helvetica", 20, "bold"), bg="#f0f0f0")
        title_label.pack(pady=(0, 20))

        # Task selection label and dropdown
        tk.Label(main_frame, text="Select Task:", font=("Helvetica", 14), bg="#f0f0f0").pack(pady=(0, 10))

        combobox = ttk.Combobox(main_frame, values=[
            "1: Single Measurement",
            "2: Compare Measurements",
            "3: Export all measurements for a device to a HXML file"
        ], state="readonly", textvariable=self.task_type, font=("Helvetica", 12), width=50)
        combobox.pack(pady=(0, 20))

        # Start task button
        button = tk.Button(main_frame, text="Start Task", command=self.start_task,
                           height=2, width=20, font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white")
        button.pack(pady=(0, 10))
    def start_task(self):
        match self.task_type.get()[0]:
            case "1":
                self.single_measurement()
            case "2":
                self.compare_measurements()
            case "3":
                self.export_device()
            case _:
                messagebox.showerror("Invalid", "Unknown task type.")

    def single_measurement(self):
        file = filedialog.askopenfilename(title="Select .uff Measurement File")
        if not file:
            return
        measurement = Measurement_Plane(file)

        task_win = tk.Toplevel(self)
        task_win.title("Single Measurement Options")

        tk.Label(task_win, text="Choose Output Type").pack()
        ttk.Combobox(task_win, values=["1: Display", "2: Export"],
                     textvariable=self.graph_unit).pack()

        tk.Label(task_win, text="Choose Graph Type").pack()
        graph_combo = ttk.Combobox(task_win, values=graph_types,
                                   state="readonly", width=40)
        graph_combo.pack()

        def run_action():
            idx = graph_combo.current()
            unit = self.graph_unit.get()
            if unit == "1":
                measurement.get_average(short_graph_types[idx]).plot_graph()
            else:
                measurement.get_average(f"{short_graph_types[idx]}_db").plot_graph()

        tk.Button(task_win, text="Run", command=run_action).pack(pady=10)

    def compare_measurements(self):
        files = filedialog.askopenfilenames(title="Select multiple .uff files for comparison")
        if not files:
            return

        compare_win = tk.Toplevel(self)
        compare_win.title("Compare Surface Averages")

        tk.Label(compare_win, text="Choose Graph Type").pack()
        graph_combo = ttk.Combobox(compare_win, values=graph_types, state="readonly")
        graph_combo.pack()

        tk.Label(compare_win, text="Choose Output Type").pack()
        unit_combo = ttk.Combobox(compare_win, values=["1: Display", "2: Export"], state="readonly")
        unit_combo.pack()

        def compare_action():
            idx = graph_combo.current()
            unit = unit_combo.get()
            graph_id = short_graph_types[idx]
            if unit == "1":
                Compare_Surface_Average(files, graph_id).compare_surface_average_plot()
            else:
                Compare_Surface_Average(files, f"{graph_id}_db").compare_surface_average_export()

        tk.Button(compare_win, text="Compare", command=compare_action).pack(pady=10)

    def export_device(self):
        files = filedialog.askopenfilenames(title="Select .uff files of one device")
        if not files:
            return
        device = Device(files)
        device.export()
        messagebox.showinfo("Exported", "Device measurements exported.")



app = VibroGUI()
app.mainloop()
