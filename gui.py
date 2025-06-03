import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Tk
from measurement_plane import Measurement_Plane
from surface_average_comparison import Compare_Surface_Average
from scan_point_graph import Graph_average
from device import Device
from graph_plotter import graph_plotter
from PIL import Image, ImageTk
from GUI.pair_reviewer import PairReviewer, GraphItem
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt

graph_types = [
    "Vibration Displacement", "Vibration Velocity", "Vibration Acceleration",
    "Ref1", "Ref2", "Ref3", "H1 Vibration Ref1", "H2 Vibration Ref1",
    "Vibration Ref1", "Vibration Ref2", "Vibration Ref3"
]
short_graph_types = [
    "disp", "vib", "acc", "ref1", "ref2", "ref3", "h1vibref1", "h2vibref1",
    "vibref1", "vibref2", "vibref3"
]



class VibroGUI(Tk):
    def __init__(self):
        super().__init__()
        self.title("Laser Vibrometer Analyser")

        # Make window full screen
        self.state("zoomed")
        self.container = tk.Frame(self)
        self.container.pack(expand=True, fill="both")
        img = Image.open("house.png")
        img_resized = img.resize((75, 75), Image.LANCZOS)  
        self.home_img = ImageTk.PhotoImage(img_resized)   

        # Graph figs
        self.current_figs = []

        # Initialise variables for UFF files
        self.single_file_path = ""

        self.build_menu_page()

    def show_page(self, frame: tk.Frame):
        # remove every child of the container, then show the requested one
        for w in self.container.winfo_children():
            w.pack_forget()
        frame.pack(expand=True, fill="both")

    def build_menu_page(self):
        self.task_type = tk.StringVar(value="Choose what type of measurement to process")
        self.graph_unit = tk.StringVar(value="Choose what type of measurement to process")
        self.graph_index = tk.IntVar(value=0)

        # Main content frame with padding and fixed width
        main_frame = tk.Frame(self.container, bd=2, relief='ridge', bg="white")
        self.menu_frame = main_frame
        self.add_home_button(main_frame)
        self.show_page(main_frame)

        content_frame = tk.Frame(main_frame, bd=10, relief="groove", padx=40, pady=40, bg="#f0f0f0")
        content_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Add title label
        title_label = tk.Label(content_frame, text="Laser Vibrometer Analyser", font=("Times New Roman", 20, "bold"), bg="#f0f0f0")
        title_label.pack(pady=(0, 20))

        # Task selection label and dropdown
        tk.Label(content_frame, text="Select Task:", font=("Times New Roman", 14), bg="#f0f0f0").pack(pady=(0, 10))

        combobox = ttk.Combobox(content_frame, values=[
            "1: Single Measurement",
            "2: Compare Measurements",
            "3: Export all measurements for a device to a HXML file"
        ], state="readonly", textvariable=self.task_type, font=("Times New Roman", 12), width=50)
        combobox.pack(pady=(0, 20))

        # Start task button
        button = tk.Button(content_frame, text="Start Task", command=self.start_task,
                           height=2, width=20, font=("Times New Roman", 12, "bold"), bg="#4CAF50", fg="white")
        button.pack(pady=(0, 10))

    def add_home_button(self, parent):
        button = tk.Button(parent, image=self.home_img, command=lambda: self.show_page(self.menu_frame),
                        height=75, width=75, bd="0", bg="#f0f0f0", fg="#f0f0f0")
        button.pack(pady=(30, 0))
        button.place(relx=1, rely=0, anchor="ne", x=-10, y=10)

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

    def add_nav_buttons(self, container, export_callback=None, back_callback=None):
        """Add back/export buttons to the given container frame."""
        back_frame = tk.Frame(container, bg="white")
        back_frame.pack(fill=tk.X, padx=10, pady=10)

        def back():
            for figure in self.current_figs:
                plt.close(figure)
            self.current_figs = []
            if back_callback:
                back_callback()

        tk.Button(back_frame, text="Back to Measurement Options", command=back,
                bg="#4CAF50", fg="white", font=("Times New Roman", 11, "bold")).pack(side=tk.LEFT)

        if export_callback is not None:
            tk.Button(back_frame, text="Export", command=export_callback,
                    bg="#4CAF50", fg="white", font=("Times New Roman", 11, "bold")).pack(side=tk.RIGHT)

    def single_measurement(self, is_new_instance=True):
        if is_new_instance:
            window = Tk()
            window.withdraw()

            # ---- UFF file verification ----
            messagebox.showinfo("Choose Scan Data Measurement File", "Please select the measurement file with extension .uff", parent=window)

            self.single_file_path = filedialog.askopenfilename(
                title="Select a *.uff measurement file",
                filetypes=[("UFF files", "*.uff"), ("All files", "*.*")]
            )
            if not self.single_file_path:
                return
            if not self.single_file_path.lower().endswith(".uff"):
                messagebox.showerror("Invalid File", "Selected file is not a .uff file.")
                return
        try:
            measurement = Measurement_Plane(self.single_file_path)
        except Exception as e:
            messagebox.showerror("Load Error", str(e))
            return

        # ---- Menu Box For Selection ----
        # Create a new page frame
        page = tk.Frame(self.container, bg="white")
        self.page_frame = page
        self.add_home_button(page)

        content = tk.Frame(page, bg="#f0f0f0", bd="10", relief="groove", padx=40, pady=30)
        content.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        tk.Label(content, text="Measurement Options", font=("Times New Roman", 16, "bold"), relief="groove", bg="#f0f0f0").pack(pady=(0, 12))

        # Task
        unit_var = tk.StringVar(value="raw")
        tgt_var  = tk.StringVar(value="average")
        graph_var = tk.StringVar(value=graph_types[0])
        point_var = tk.StringVar(value="Point 1")

        # Units
        tk.Label(content, text="Units:", font=("Times New Roman", 11, "bold"), bg="#f0f0f0").pack(anchor="w", pady=(8, 0))
        for t, v in (("Raw", "raw"), ("Decibel", "db")):
            ttk.Radiobutton(content, text=t, variable=unit_var, value=v).pack(anchor="w")

        # Target
        tk.Label(content, text="Target:", font=("Times New Roman", 11, "bold"), bg="#f0f0f0").pack(anchor="w", pady=(8, 0))
        for t, v in (("Surface average", "average"), ("Single scan point", "scan")):
            ttk.Radiobutton(content, text=t, variable=tgt_var, value=v).pack(anchor="w")

        # Point selection combobox
        point_frame = tk.Frame(content, bg="#f0f0f0")
        point_cb = ttk.Combobox(point_frame, state="readonly",
            values=[f"Point {i}" for i in range(1, measurement.number_of_scan_points + 1)],
            textvariable=point_var, width=12)
        point_cb.pack()

        # Graph type combobox
        graph_type_label = tk.Label(content, text="Graph type:", font=("Times New Roman", 11, "bold"), bg="#f0f0f0")
        graph_type_label.pack(anchor="w", pady=(8, 0))
        ttk.Combobox(content, state="readonly", values=graph_types, textvariable=graph_var, width=35).pack()
        
        def _toggle_point(*_):
            if tgt_var.get() == "scan":
                point_frame.pack(before=graph_type_label, pady=(6,0))
            else:
                point_frame.pack_forget()
        tgt_var.trace_add("write", _toggle_point)
        _toggle_point()

        # ---- Graph processing onto Tkinter window ----
        def run():

            units = unit_var.get()                # "raw" | "db"
            target = tgt_var.get()                # "average" | "scan"
            graph_id = short_graph_types[graph_types.index(graph_var.get())]

            # Create a new frame for the graph page
            graph_page = tk.Frame(self.container, bg="white")
            graph_frame = tk.Frame(graph_page)
            graph_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            if target == "average":
                channel_signal_type = graph_id if units == "raw" else f"{graph_id}_db"

                graph_items = []
                key_raw = graph_id
                key_db = f"{graph_id}_db"
                key = key_raw if units == "raw" else key_db

                for i, sp in enumerate(measurement.scanpoints, start=1):
                    try:
                        if units == "raw":
                            g_obj = getattr(sp, key_raw)
                        else:
                            g_obj = getattr(sp, f"create_{key_raw}_decibel")()
                    except AttributeError:
                        g_obj = getattr(sp, key) if hasattr(sp, key) else None
                    if g_obj is None:
                        continue
                    fig = graph_plotter(g_obj)
                    graph_items.append(GraphItem(fig, f"Point {i}"))
                    self.current_figs.append(fig)

                def build_final_average(kept_items, anomalous_indices):
                    if not kept_items:
                        messagebox.showwarning("No points selected", "You excluded every scan point.")
                        return


                    try:
                        # Step 3: Call CLI-style averaging method
                        avg_graph = measurement.get_average(key, anomalous_indices=anomalous_indices)
                    except Exception as e:
                        messagebox.showerror("Averaging Failed", f"An error occurred while averaging:\n{str(e)}")
                        return

                    avg_fig = graph_plotter(avg_graph)
                    self.current_figs.append(avg_fig)

                    # Step 4: Create new page to show the average
                    avg_page = tk.Frame(self.container, bg="white")
                    avg_frame = tk.Frame(avg_page, bg="white")
                    avg_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

                    tk.Label(avg_frame, text="Final Average", bg="white",
                            font=("Times New Roman", 16, "bold")).pack(pady=(12, 6))

                    canvas = FigureCanvasTkAgg(avg_fig, master=avg_frame)
                    canvas.draw()
                    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

                    def export_average():
                        avg_graph.gui_export()

                    tk.Button(avg_frame, text="Back to reviewer",
                            command=lambda: self.show_page(graph_page),
                            bg="#4CAF50", fg="white",
                            font=("Times New Roman", 11, "bold")).pack(pady=10)

                    self.add_nav_buttons(avg_page, export_callback=export_average,
                                    back_callback=lambda: self.single_measurement(False))

                    self.show_page(avg_page)

                viewer = PairReviewer(graph_frame, graph_items, build_final_average)
                viewer.pack(fill="both", expand=True)

                # Add back/export buttons to main graph_page (reviewer)
                self.add_nav_buttons(graph_page, back_callback=lambda: self.single_measurement(False))

            else:
                # Single scan-point graph
                raw, decibel = {
                    "disp": ("disp", "create_disp_decibel"),
                    "vib": ("vib", "create_vib_decibel"),
                    "acc": ("acc", "create_acc_decibel"),
                    "ref1": ("ref1", "create_ref1_decibel"),
                    "ref2": ("ref2", "create_ref2_decibel"),
                    "ref3": ("ref3", "create_ref3_decibel"),
                    "h1vibref1": ("h1vibref1", "create_h1vibref1_decibel"),
                    "h2vibref1": ("h2vibref1", "create_h2vibref1_decibel"),
                    "vibref1": ("create_vibref1", "create_vibref1_decibel"),
                    "vibref2": ("create_vibref2", "create_vibref2_decibel"),
                    "vibref3": ("create_vibref3", "create_vibref3_decibel")
                }[graph_id]

                idx = int(point_var.get().split()[1]) - 1
                sp = measurement.scanpoints[idx]
                graph_obj = getattr(sp, raw) if units == "raw" else getattr(sp, decibel)()
                fig = graph_plotter(graph_obj)
                self.current_figs.append(fig)

                canvas = FigureCanvasTkAgg(fig, master=graph_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

                toolbar = NavigationToolbar2Tk(canvas, graph_frame)
                toolbar.update()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

                def export_single():
                    exported_name = graph_obj.gui_export()

                # Add back/export buttons to graph_page
                self.add_nav_buttons(graph_page, export_callback=export_single, back_callback=lambda: self.single_measurement(False))

            self.show_page(graph_page)


        # Run button
        tk.Button(content, text="Run", bg="#4CAF50", fg="white",
                font=("Times New Roman", 11, "bold"),
                command=run).pack(side="bottom", pady=(12, 4))

        # Show the page
        self.show_page(page)

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
        device.export(isGUI=True)
        messagebox.showinfo("Exported", "Device measurements exported.")

app = VibroGUI()
app.mainloop()
