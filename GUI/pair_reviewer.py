import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from PIL import Image, ImageTk


class GraphItem:
    """Hold a (figure, label, included?) triple."""
    def __init__(self, fig, label):
        self.fig = fig
        self.label = label
        self.included = True

class PairReviewer(tk.Frame):
    def __init__(self, master, items, on_submit):
        super().__init__(master, bg="white")
        self.items = items
        self.on_submit = on_submit
        self.page = 0  # 0, 2, 4, …
        left_arrow = Image.open("Left_Arrow.png")
        left_arrow_resized = left_arrow.resize((75, 75), Image.LANCZOS)  
        self.left_arrow_img = ImageTk.PhotoImage(left_arrow_resized)   
        right_arrow = Image.open("Right_Arrow.png")
        right_arrow_resized = right_arrow.resize((75, 75), Image.LANCZOS)  
        self.right_arrow_img = ImageTk.PhotoImage(right_arrow_resized)  

        # Container frame for checkboxes and graphs
        self.content_frame = tk.Frame(self, bg="white")
        self.content_frame.pack(pady=6, fill="both", expand=True)

        # Create two checkbox vars and widgets
        self.chk_var = [tk.BooleanVar() for _ in range(2)]
        self.chk = []
        for col in range(2):
            cb = tk.Checkbutton(self.content_frame, variable=self.chk_var[col],
                                bg="white", font=("Helvetica", 12),    
                                padx=10, pady=5, command=lambda i=col: self._toggle(i))
            cb.grid(row=0, column=col, pady=(0,10), sticky="nsew")
            self.chk.append(cb)

        # Graph canvases placeholder, grid row 1
        self.canvas = [None, None]

        # Make columns expand evenly
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=1)

        # Navigation and submit buttons frame
        nav = tk.Frame(self, bg="white")
        nav.pack(fill="x", pady=8)

        self.btn_prev = tk.Button(nav, image=self.left_arrow_img, command=self.prev,
                                  bd=0, relief="flat", highlightthickness=0, bg="white")
        self.btn_prev.grid(row=0, column=0, sticky="w", padx=10)

        self.btn_submit = tk.Button(nav, text="Submit Points", bg="#4CAF50", fg="white",
                                    font=("Helvetica", 14, "bold"), 
                                    padx=20, pady=10,       
                                    command=self._submit)
        self.btn_submit.grid(row=0, column=1)

        self.btn_next = tk.Button(nav, image=self.right_arrow_img, command=self.next,
                                  bd=0, relief="flat", highlightthickness=0, bg="white")
        self.btn_next.grid(row=0, column=2, sticky="e", padx=10)

        # Make middle column expand so buttons align left and right
        nav.grid_columnconfigure(0, weight=0)
        nav.grid_columnconfigure(1, weight=1)
        nav.grid_columnconfigure(2, weight=0)

        # Bind arrow keys to prev/next
        self.bind_all("<Left>", lambda e: self.prev())
        self.bind_all("<Right>", lambda e: self.next())
        self.bind_all("<Return>", lambda e: self._submit())  
        self.bind_all("<space>", lambda e: self._submit())   


        self._draw()

    def _toggle(self, which):
        idx = self.page + which
        if idx < len(self.items):
            self.items[idx].included = self.chk_var[which].get()

    def _draw(self):
        # Clear old canvases and hide checkboxes
        for c in self.canvas:
            if c:
                c.get_tk_widget().destroy()
        self.canvas = [None, None]

        for chk in self.chk:
            chk.grid_remove()

        num_items = min(2, len(self.items) - self.page)

        # Clear and configure columns
        for col in range(3):
            self.content_frame.grid_columnconfigure(col, weight=0)

        if num_items == 1:
            # Single graph centered in column 1
            col_indices = [1]
            self.content_frame.grid_columnconfigure(1, weight=1)
        else:
            # Two graphs at columns 0 and 2, center empty column 1
            col_indices = [0, 2]
            self.content_frame.grid_columnconfigure(0, weight=1)
            self.content_frame.grid_columnconfigure(2, weight=1)

        # Place graphs in row 0, checkboxes in row 1
        for i, col in enumerate(col_indices):
            idx = self.page + i
            if idx < len(self.items):
                item = self.items[idx]
                self.chk_var[i].set(item.included)
                self.chk[i].config(text=item.label, state="normal")
                # Graph widget in row 0
                can = FigureCanvasTkAgg(item.fig, master=self.content_frame)
                can.draw()
                can.get_tk_widget().grid(row=0, column=col, sticky="nsew")
                self.canvas[i] = can
                # Checkbox in row 1, centered under graph
                self.chk[i].grid(row=1, column=col, pady=(10,0))

        # Let row 0 (graphs) expand vertically
        self.content_frame.grid_rowconfigure(0, weight=1)


    def prev(self):
        if self.page >= 2:
            self.page -= 2
        else:
            self.page = (len(self.items) - 1) // 2 * 2
        self._draw()

    def next(self):
        if self.page + 2 < len(self.items):
            self.page += 2
        else:
            self.page = 0
        self._draw()

    def _submit(self):
        kept_idx = [i + 1 for i, item in enumerate(self.items) if item.included]
        all_idx = list(range(1, len(self.items) + 1))
        anomaly_idx = [i for i in all_idx if i not in kept_idx]

        self.on_submit([g for g in self.items if g.included], anomaly_idx)
