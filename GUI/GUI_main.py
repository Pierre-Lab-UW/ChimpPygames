import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from FileEditor import FileEditor  # Import your FileEditor class
import subprocess
import os
import shlex
import serial
import serial.tools.list_ports
from threading import Thread
try:
    # checks if you have access to RPi.GPIO, which is available inside RPi
    import RPi.GPIO as GPIO
except:
    # In case of exception, you are executing your script outside of RPi, so import Mock.GPIO
    import Mock.GPIO as GPIO


class ParameterEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ACTS Parameter Editor")
        self.file_editor = None
        self.global_params = ["subject_1_name", "subject_2_name", "subject_1_id", "subject_2_id",
                              "subject_1_task_order", "subject_2_task_order"]
        # add all tasks parameters present in primate_params.csv here
        self.tasks_params = {
            "SHAPE0": [],
            "SHAPE1": ["SHAPE1_to_decrement", "SHAPE1trials", "SHAPE1criterion"],
            "SHAPE2": ["SHAPE2size", "SHAPE2_zones", "SHAPE2trials", "SHAPE2criterion"],
            "TwoChoice": ["2choicesize", "2choicereset", "2choiceproblems", "2choicetrials",
                                          "2choicecorrect"],
           # "Match_To_Sample": [],
           # "Delayed_Match_To_Sample": ["dMTSsize", "dMTStrials", "dMTScriterion"],
           # "Oddity_Testing": [],
           # "Delayed_Response_Task": [],
           # "GO_NO_GO": ["subj_name", "GNG_Ratio", "NG_delay", "abort_trial_time", "treats_dispensed"]
        }

        self.pump_status = False
        self.status_bar = None

        # Configure root window to expand properly
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Set minimum window size
        self.root.minsize(600, 700)
        
        # Style configuration
        self.setup_styles()
        
        # UI Elements
        self.create_main_interface()

    def setup_styles(self):
        """Configure ttk styles for a modern look"""
        style = ttk.Style()
        
        # Configure the theme
        style.theme_use('clam')
        
        # Main colors
        style.configure('.', background='#f0f0f0', foreground='black')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Helvetica', 10))
        style.configure('TButton', font=('Helvetica', 10), padding=5)
        style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'))
        style.configure('Section.TLabel', font=('Helvetica', 12, 'bold'), foreground='#2c3e50')
        style.configure('Primary.TButton', background='#3498db', foreground='white')
        style.configure('Secondary.TButton', background='#95a5a6', foreground='white')
        style.configure('Success.TButton', background='#2ecc71', foreground='white')
        style.configure('Warning.TButton', background='#e74c3c', foreground='white')
        
        # Configure labelframe styles
        style.configure('TLabelframe', background='#f0f0f0', relief=tk.GROOVE, borderwidth=2)
        style.configure('TLabelframe.Label', background='#f0f0f0', font=('Helvetica', 10, 'bold'))
        
        # Configure entry styles
        style.configure('TEntry', fieldbackground='white', padding=5)
        
        # Configure scrollbar
        style.configure('Vertical.TScrollbar', background='#bdc3c7')

    def create_main_interface(self):
        """Create the main application interface with modern styling"""
        # Main container frame with padding
        main_frame = ttk.Frame(self.root, padding="10 10 10 10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Create a canvas and scrollbar for the main content
        canvas = tk.Canvas(main_frame, highlightthickness=0, background='#f0f0f0')
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configure the scrollable area
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configure weights for resizing
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Store the scrollable frame
        self.scrollable_frame = scrollable_frame
        
        # Add content to the scrollable frame
        self.setup_main_content()

    def setup_main_content(self):
        """Create the main content widgets"""
        # Configure the scrollable frame to center its contents
        self.scrollable_frame.grid_columnconfigure(0, weight=1)  # Keep
        self.scrollable_frame.grid_columnconfigure(1, weight=0)  # Add center column
        self.scrollable_frame.grid_columnconfigure(2, weight=1)  # Add center column

        # Create a container frame for centered content with padding
        content_frame = ttk.Frame(self.scrollable_frame, padding="20 20 20 20")
        content_frame.grid(row=0, column=1, sticky="n")  # Place in center column

        content_frame.grid_columnconfigure(0, weight=1)  # Allow inner content to stretch slightly

        # Application title
        title_label = ttk.Label(content_frame, text="ACTS Parameter Editor", style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 20), sticky="n")

        # File operations section
        file_frame = ttk.LabelFrame(content_frame, text="File Operations", padding="10 10 10 10")
        file_frame.grid(row=1, column=0, pady=10, sticky="n")  # Changed from "ew"

        # Load CSV file button
        load_btn = ttk.Button(file_frame, text="Load Parameter File", 
                            command=self.load_file, style='Primary.TButton')
        load_btn.grid(row=0, column=0, pady=5, sticky="ew")  # Keep "ew" inside buttons

        # Global Parameters Section
        self.global_frame = ttk.LabelFrame(content_frame, text="Global Parameters", padding="10 10 10 10")
        self.global_frame.grid(row=2, column=0, pady=10, sticky="n")  # Changed from "ew"

        global_btn = ttk.Button(self.global_frame, text="Edit Global Parameters", 
                            command=self.edit_global_parameters, style='Primary.TButton')
        global_btn.grid(row=0, column=0, pady=5, sticky="ew")

        # Task Parameters Section
        self.tasks_frame = ttk.LabelFrame(content_frame, text="Task Parameters", padding="10 10 10 10")
        self.tasks_frame.grid(row=3, column=0, pady=10, sticky="n")  # Changed from "ew"

        task_buttons_frame = ttk.Frame(self.tasks_frame)
        task_buttons_frame.grid(row=0, column=0, sticky="ew")

        self.task_buttons = {}
        for i, task in enumerate(self.tasks_params):
            row = i // 2
            col = i % 2
            button = ttk.Button(task_buttons_frame, text=f"Edit {task}",
                            command=lambda t=task: self.edit_task_parameters(t),
                            style='Secondary.TButton')
            button.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            self.task_buttons[task] = button
            task_buttons_frame.grid_columnconfigure(col, weight=1)

        # System Operations Section
        system_frame = ttk.LabelFrame(content_frame, text="System Operations", padding="10 10 10 10")
        system_frame.grid(row=4, column=0, pady=10, sticky="n")  # Changed from "ew"

        start_btn = ttk.Button(system_frame, text="Start ACTS Program", 
                            command=self.start_program, style='Success.TButton')
        start_btn.grid(row=0, column=0, pady=5, sticky="ew")

        reset_btn = ttk.Button(system_frame, text="Reset Progress", 
                            command=self.reset_progress, style='Warning.TButton')
        reset_btn.grid(row=1, column=0, pady=5, sticky="ew")

        rfid_btn = ttk.Button(system_frame, text="RFID Test", 
                            command=self.rfid_test, style='Secondary.TButton')
        rfid_btn.grid(row=2, column=0, pady=5, sticky="ew")

        pump_btn = ttk.Button(system_frame, text="Toggle Pump", 
                            command=self.toggle_pump, style='Secondary.TButton')
        pump_btn.grid(row=3, column=0, pady=5, sticky="ew")

        # Status bar at the bottom
        self.status_var = tk.StringVar()
        self.status_var.set(self.pad_to_warning_length_centered("Ready"))
        self.status_bar = ttk.Label(content_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=5, column=0, pady=(20, 0), sticky="ew")

    def toggle_pump(self, channel = 17):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(channel, GPIO.OUT)
        
        if not self.pump_status:
            self.pump_status = True
            GPIO.output(channel, GPIO.LOW)
            self.status_var.set("Warning: Primate Pump is on. Please do not stop the program at this time!")
        else:
            self.pump_status = False
            GPIO.output(channel, GPIO.HIGH)
            self.status_var.set(self.pad_to_warning_length_centered("Ready"))

    def pad_to_warning_length_centered(self, text: str) -> str:
        TARGET_LENGTH = 128
        current_length = len(text)
        
        if current_length >= TARGET_LENGTH:
            return text[:TARGET_LENGTH]  # Truncate if too long
        
        total_padding = TARGET_LENGTH - current_length
        left_padding = total_padding // 2
        right_padding = total_padding - left_padding
        
        return " " * left_padding + text + " " * right_padding





    def rfid_test(self):
        """Open a window to display RFID data from serial port"""
        rfid_window = tk.Toplevel(self.root)
        rfid_window.title("RFID Test")
        rfid_window.geometry("500x400")
        
        # Configure window style
        rfid_window.configure(bg='#f0f0f0')
        
        # Main frame
        main_frame = ttk.Frame(rfid_window, padding="10 10 10 10")
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Title
        ttk.Label(main_frame, text="RFID Reader Test", style='Title.TLabel').pack(pady=(0, 10))
        
        # Text widget with scrollbar for displaying serial data
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(expand=True, fill=tk.BOTH, pady=5)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Courier', 10), 
                             bg='white', padx=10, pady=10)
        scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Stop button
        stop_button = ttk.Button(button_frame, text="Stop", 
                              command=lambda: self.stop_serial_reading.set(),
                              style='Warning.TButton')
        stop_button.pack(side=tk.RIGHT, padx=5)
        
        # Flag to control the serial reading thread
        self.stop_serial_reading = threading.Event()
        
        def read_from_serial():
            """Thread function to read from serial port"""
            try:
                # Try to find the RFID reader (adjust as needed for your hardware)
                rfid_port = "/dev/serial0"
                    
                ser = serial.Serial(rfid_port, baudrate=9600, timeout=1)
                text_widget.insert(tk.END, f"Connected to {rfid_port}\n")
                
                while not self.stop_serial_reading.is_set():
                    if ser.in_waiting:
                        data = ser.readline().decode('utf-8').strip()
                        if data:
                            text_widget.insert(tk.END, f"RFID: {data}\n")
                            text_widget.see(tk.END)
                
                ser.close()
                text_widget.insert(tk.END, "Disconnected\n")
                
            except Exception as e:
                text_widget.insert(tk.END, f"Error: {str(e)}\n")
        
        # Start the serial reading thread
        serial_thread = Thread(target=read_from_serial, daemon=True)
        serial_thread.start()
        
        # Clean up when window closes
        def on_closing():
            self.stop_serial_reading.set()
            rfid_window.destroy()
        
        rfid_window.protocol("WM_DELETE_WINDOW", on_closing)

    def start_program(self):
        try:
            if self.pump_status == True:
                messagebox.showerror(self.pad_to_warning_length_centered("Error", "Can't start program with Primate Pump on!"))
                return

            self.status_var.set(self.pad_to_warning_length_centered("Starting ACTS program..."))
            self.root.update()
            
            # Define the relative path to the program
            current_directory = os.getcwd()
            program_path = os.path.join(current_directory, "ACTS_frontend.py")
            
            # Check if the file exists
            if not os.path.exists(program_path):
                messagebox.showerror("Error", "ACTS program file not found!")
                self.status_var.set(self.pad_to_warning_length_centered("Error: Program file not found!"))
                return

            # Start the program
            subprocess.run(["python3", program_path])
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start program: {e}")
            self.status_var.set(self.pad_to_warning_length_centered(f"Error: {str(e)}"))

    def load_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv")],
            title="Select Parameter File"
        )
        
        if not file_path:
            return
            
        try:
            self.file_editor = FileEditor(file_path)
            messagebox.showinfo("Success", "Parameter file loaded successfully!")
            self.status_var.set(self.pad_to_warning_length_centered(f"Loaded: {os.path.basename(file_path)}"))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")
            self.status_var.set(self.pad_to_warning_length_centered(f"Error loading file: {str(e)}"))

    def edit_global_parameters(self):
        if self.file_editor is None:
            messagebox.showwarning("Warning", "Load a parameter file first!")
            return

        window = tk.Toplevel(self.root)
        window.title("Edit Global Parameters")
        window.grid_columnconfigure(0, weight=1)
        window.minsize(500, 400)

        main_frame = tk.Frame(window)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        canvas = tk.Canvas(main_frame, highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        content_frame = tk.Frame(scrollable_frame, padx=20, pady=20)
        content_frame.grid(row=0, column=0, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)

        tk.Label(content_frame, text="Edit Global Parameters", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Load values from CSV
        def get_val(row, col):
            return self.file_editor.df.iloc[row][col] if col in self.file_editor.df.columns else ""

        # Subject 1
        subject_1_name = tk.StringVar(value=get_val(0, "Subject"))
        subject_1_id = tk.StringVar(value=get_val(0, "Left Wrist"))
        subject_1_sex = tk.StringVar(value=get_val(0, "Sex"))
        subject_1_internal_name = tk.StringVar(value=get_val(0, "subj_name"))
        subject_1_dob = tk.StringVar(value=get_val(0, "DOB"))
        subject_1_room = tk.StringVar(value=get_val(0, "Room"))

        # Subject 2
        subject_2_name = tk.StringVar(value=get_val(1, "Subject"))
        subject_2_id = tk.StringVar(value=get_val(1, "Left Wrist"))
        subject_2_sex = tk.StringVar(value=get_val(1, "Sex"))
        subject_2_internal_name = tk.StringVar(value=get_val(1, "subj_name"))
        subject_2_dob = tk.StringVar(value=get_val(1, "DOB"))
        subject_2_room = tk.StringVar(value=get_val(1, "Room"))

        def add_entry(label, var, row, label_text):
            tk.Label(content_frame, text=label_text, font=("Arial", 10)).grid(row=row, column=0, pady=5, sticky="w")
            tk.Entry(content_frame, textvariable=var, font=("Arial", 10)).grid(row=row, column=1, pady=5, sticky="ew")

        row = 1
        for label, var in [
            ("Subject 1 Name", subject_1_name),
            ("Subject 2 Name", subject_2_name),
            ("Subject 1 ID", subject_1_id),
            ("Subject 2 ID", subject_2_id),
            ("Subject 1 Sex", subject_1_sex),
            ("Subject 2 Sex", subject_2_sex),
            ("Subject 1 Internal Name", subject_1_internal_name),
            ("Subject 2 Internal Name", subject_2_internal_name),
            ("Subject 1 DOB", subject_1_dob),
            ("Subject 2 DOB", subject_2_dob),
            ("Subject 1 Room", subject_1_room),
            ("Subject 2 Room", subject_2_room),
        ]:
            add_entry(label, var, row, label)
            row += 1

        # Task management
        tk.Label(content_frame, text="Subject 1 Task Order", font=("Arial", 10, "bold")).grid(row=row, column=0, pady=10, sticky="w", columnspan=2)
        subject_1_task_list = tk.Listbox(content_frame, height=5, selectmode=tk.SINGLE, exportselection=False, font=("Arial", 10))
        subject_1_tasks = get_val(0, "task-order").split("-") if "task-order" in self.file_editor.df.columns else list(self.tasks_params.keys())
        for task in subject_1_tasks:
            subject_1_task_list.insert(tk.END, task)
        row += 1
        subject_1_task_list.grid(row=row, column=0, columnspan=2, sticky="ew")
        row += 1

        available_tasks = list(self.tasks_params.keys())
        subject_1_selected_task = tk.StringVar(value=available_tasks[0])

        def update_task_list(listbox, tasks):
            listbox.delete(0, tk.END)
            for t in tasks:
                listbox.insert(tk.END, t)

        def move_up(listbox, tasks):
            selected = listbox.curselection()
            if selected and selected[0] > 0:
                idx = selected[0]
                tasks[idx], tasks[idx - 1] = tasks[idx - 1], tasks[idx]
                update_task_list(listbox, tasks)
                listbox.selection_set(idx - 1)

        def move_down(listbox, tasks):
            selected = listbox.curselection()
            if selected and selected[0] < len(tasks) - 1:
                idx = selected[0]
                tasks[idx], tasks[idx + 1] = tasks[idx + 1], tasks[idx]
                update_task_list(listbox, tasks)
                listbox.selection_set(idx + 1)

        def add_task(listbox, tasks, selected_var):
            new_task = selected_var.get()
            if new_task not in tasks:
                tasks.append(new_task)
                update_task_list(listbox, tasks)

        def delete_task(listbox, tasks):
            selected = listbox.curselection()
            if selected:
                tasks.pop(selected[0])
                update_task_list(listbox, tasks)

        tk.OptionMenu(content_frame, subject_1_selected_task, *available_tasks).grid(row=row, column=0, columnspan=2, sticky="ew")
        row += 1

        btn_frame = tk.Frame(content_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=5, sticky="ew")
        for i in range(4): btn_frame.grid_columnconfigure(i, weight=1)
        tk.Button(btn_frame, text="Add Task", command=lambda: add_task(subject_1_task_list, subject_1_tasks, subject_1_selected_task)).grid(row=0, column=0, sticky="ew")
        tk.Button(btn_frame, text="Delete Task", command=lambda: delete_task(subject_1_task_list, subject_1_tasks)).grid(row=0, column=1, sticky="ew")
        tk.Button(btn_frame, text="Move Up", command=lambda: move_up(subject_1_task_list, subject_1_tasks)).grid(row=0, column=2, sticky="ew")
        tk.Button(btn_frame, text="Move Down", command=lambda: move_down(subject_1_task_list, subject_1_tasks)).grid(row=0, column=3, sticky="ew")
        row += 1

        # Subject 2 task section
        tk.Label(content_frame, text="Subject 2 Task Order", font=("Arial", 10, "bold")).grid(row=row, column=0, pady=10, sticky="w", columnspan=2)
        subject_2_task_list = tk.Listbox(content_frame, height=5, selectmode=tk.SINGLE, exportselection=False, font=("Arial", 10))
        subject_2_tasks = get_val(1, "task-order").split("-") if "task-order" in self.file_editor.df.columns else list(self.tasks_params.keys())
        for task in subject_2_tasks:
            subject_2_task_list.insert(tk.END, task)
        row += 1
        subject_2_task_list.grid(row=row, column=0, columnspan=2, sticky="ew")
        row += 1

        subject_2_selected_task = tk.StringVar(value=available_tasks[0])
        tk.OptionMenu(content_frame, subject_2_selected_task, *available_tasks).grid(row=row, column=0, columnspan=2, sticky="ew")
        row += 1

        btn_frame2 = tk.Frame(content_frame)
        btn_frame2.grid(row=row, column=0, columnspan=2, pady=5, sticky="ew")
        for i in range(4): btn_frame2.grid_columnconfigure(i, weight=1)
        tk.Button(btn_frame2, text="Add Task", command=lambda: add_task(subject_2_task_list, subject_2_tasks, subject_2_selected_task)).grid(row=0, column=0, sticky="ew")
        tk.Button(btn_frame2, text="Delete Task", command=lambda: delete_task(subject_2_task_list, subject_2_tasks)).grid(row=0, column=1, sticky="ew")
        tk.Button(btn_frame2, text="Move Up", command=lambda: move_up(subject_2_task_list, subject_2_tasks)).grid(row=0, column=2, sticky="ew")
        tk.Button(btn_frame2, text="Move Down", command=lambda: move_down(subject_2_task_list, subject_2_tasks)).grid(row=0, column=3, sticky="ew")
        row += 1

        def save_changes():
            try:
                # Subject 1
                self.file_editor.set_subject_name(0, subject_1_name.get())
                self.file_editor.set_subject_id(0, subject_1_id.get())
                self.file_editor.set_subject_sex(0, subject_1_sex.get())
                self.file_editor.set_subject_internal_name(0, subject_1_internal_name.get())
                self.file_editor.set_task_param(0, "DOB", subject_1_dob.get())
                self.file_editor.set_task_param(0, "Room", subject_1_room.get())
                self.file_editor.set_tasks_order(0, subject_1_tasks)

                # Subject 2
                self.file_editor.set_subject_name(1, subject_2_name.get())
                self.file_editor.set_subject_id(1, subject_2_id.get())
                self.file_editor.set_subject_sex(1, subject_2_sex.get())
                self.file_editor.set_subject_internal_name(1, subject_2_internal_name.get())
                self.file_editor.set_task_param(1, "DOB", subject_2_dob.get())
                self.file_editor.set_task_param(1, "Room", subject_2_room.get())
                self.file_editor.set_tasks_order(1, subject_2_tasks)

                messagebox.showinfo("Success", "Global Parameters updated successfully!")
                window.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(content_frame, text="Save Changes", command=save_changes,
                padx=10, pady=5, font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, pady=20, sticky="ew")
        
    def edit_task_parameters(self, task_name):
        if self.file_editor is None:
            messagebox.showwarning("Warning", "Please load a parameter file first!")
            self.status_var.set(self.pad_to_warning_length_centered("Warning: No parameter file loaded"))
            return

        window = tk.Toplevel(self.root)
        window.title(f"Edit {task_name} Parameters")
        window.geometry("800x600")
        window.grid_columnconfigure(0, weight=1)
        window.grid_rowconfigure(0, weight=1)

        # Main container frame
        main_frame = ttk.Frame(window, padding="10 10 10 10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Create a canvas and scrollbar
        canvas = tk.Canvas(main_frame, highlightthickness=0, bg='#f0f0f0')
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        # Configure the scrollable area
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Content frame with padding
        content_frame = ttk.Frame(scrollable_frame, padding="20 20 20 20")
        content_frame.grid(row=0, column=0, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)

        # Title
        ttk.Label(content_frame, text=f"Edit {task_name} Parameters", style='Title.TLabel').grid(
            row=0, column=0, columnspan=4, pady=(0, 20))

        # Inputs for task parameters for Subject 1 and 2
        subject_1_params = {}
        subject_2_params = {}
        
        # Subject 1 frame
        subject_1_frame = ttk.LabelFrame(content_frame, text="Subject 1 Parameters", padding="10 10 10 10")
        subject_1_frame.grid(row=1, column=0, pady=10, sticky="nsew", padx=5)
        subject_1_frame.grid_columnconfigure(1, weight=1)

        # Subject 2 frame (only if not GO_NO_GO task)
        if task_name != 'GO_NO_GO':
            subject_2_frame = ttk.LabelFrame(content_frame, text="Subject 2 Parameters", padding="10 10 10 10")
            subject_2_frame.grid(row=1, column=1, pady=10, sticky="nsew", padx=5)
            subject_2_frame.grid_columnconfigure(1, weight=1)

        for i, param in enumerate(self.tasks_params[task_name]):
            # Subject 1 parameters
            ttk.Label(subject_1_frame, text=f"{param}:").grid(row=i, column=0, sticky="w", padx=5, pady=5)
            value_1 = tk.StringVar(value=self.file_editor.df.iloc[0][param])
            entry_1 = ttk.Entry(subject_1_frame, textvariable=value_1)
            entry_1.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            subject_1_params[param] = value_1

            # Subject 2 parameters (if applicable)
            if task_name != 'GO_NO_GO':
                ttk.Label(subject_2_frame, text=f"{param}:").grid(row=i, column=0, sticky="w", padx=5, pady=5)
                value_2 = tk.StringVar(
                    value=self.file_editor.df.iloc[1][param] if len(self.file_editor.df) > 1 else "")
                entry_2 = ttk.Entry(subject_2_frame, textvariable=value_2)
                entry_2.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                subject_2_params[param] = value_2

        # Save button
        button_frame = ttk.Frame(content_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        def save_changes():
            try:
                for param, var in subject_1_params.items():
                    self.file_editor.set_task_param(0, param, var.get())
                for param, var in subject_2_params.items():
                    self.file_editor.set_task_param(1, param, var.get())
                    
                messagebox.showinfo("Success", f"{task_name} Parameters updated successfully!")
                window.destroy()
                self.status_var.set(self.pad_to_warning_length_centered(f"Updated {task_name} parameters"))
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.status_var.set(self.pad_to_warning_length_centered(f"Error updating {task_name} parameters"))

        ttk.Button(button_frame, text="Save Changes", command=save_changes,
                 style='Success.TButton').pack(pady=10, ipadx=20)

    def reset_progress(self):
        try:
            # Ask for confirmation
            if not messagebox.askyesno("Confirm Reset", 
                                    "Are you sure you want to reset all progress?\nThis action cannot be undone."):
                return
                
            self.status_var.set(self.pad_to_warning_length_centered("Resetting progress..."))
            self.root.update()
            
            # Define the path to the reset script
            current_directory = os.getcwd()
            script_path = os.path.join(current_directory, "reset_progress.py")

            # Check if the file exists
            if not os.path.exists(script_path):
                messagebox.showerror("Error", "reset_progress.py not found in current directory!")
                self.status_var.set(self.pad_to_warning_length_centered("Error: Reset script not found"))
                return

            # Run the reset script
            result = subprocess.run(["python", script_path], capture_output=True, text=True)
            
            if result.returncode == 0:
                messagebox.showinfo("Success", "Progress reset successfully!")
                self.status_var.set(self.pad_to_warning_length_centered("Progress reset complete"))
            else:
                messagebox.showerror("Error", f"Failed to reset progress:\n{result.stderr}")
                self.status_var.set(self.pad_to_warning_length_centered("Error resetting progress"))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run reset script: {e}")
            self.status_var.set(self.pad_to_warning_length_centered(f"Error: {str(e)}"))


# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = ParameterEditorApp(root)
    root.mainloop()