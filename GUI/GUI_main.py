import tkinter as tk
from tkinter import filedialog, messagebox
from FileEditor import FileEditor  # Import your FileEditor class
import subprocess
import os
import shlex


class ParameterEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Parameter Editor")
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

        # Configure root window to expand properly
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Set minimum window size
        self.root.minsize(400, 500)
        
        # UI Elements
        self.create_scrollable_frame()

    def create_scrollable_frame(self):
        # Create main container frame
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Create a canvas and scrollbar
        canvas = tk.Canvas(main_frame, highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        # Configure the scrollable area
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Center the scrollable frame
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
        self.setup_ui()

    def setup_ui(self):
        # Configure the scrollable frame to center its contents
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Create a container frame for centered content
        content_frame = tk.Frame(self.scrollable_frame, padx=20, pady=20)
        content_frame.grid(row=0, column=0, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Title label
        title_label = tk.Label(content_frame, text="Parameter Editor", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 20), sticky="n")
        
        # Load CSV file button - centered with padding
        load_btn = tk.Button(content_frame, text="Load Parameter File", 
                           command=self.load_file, width=20, padx=10, pady=5)
        load_btn.grid(row=1, column=0, pady=10, sticky="ew")
        
        # Global Parameters Section - centered with styling
        self.global_frame = tk.LabelFrame(content_frame, text="Global Parameters", 
                                         padx=10, pady=10, font=("Arial", 10, "bold"))
        self.global_frame.grid(row=2, column=0, pady=10, sticky="ew")
        self.global_frame.grid_columnconfigure(0, weight=1)
        
        global_btn = tk.Button(self.global_frame, text="Edit Global Parameters", 
                              command=self.edit_global_parameters, width=20, pady=5)
        global_btn.grid(row=0, column=0, pady=5, padx=10, sticky="ew")

        # Task Buttons - centered with consistent styling
        self.tasks_frame = tk.LabelFrame(content_frame, text="Task Parameters", 
                                       padx=10, pady=10, font=("Arial", 10, "bold"))
        self.tasks_frame.grid(row=3, column=0, pady=10, sticky="ew")
        self.tasks_frame.grid_columnconfigure(0, weight=1)

        self.task_buttons = {}
        for i, task in enumerate(self.tasks_params):
            button = tk.Button(self.tasks_frame, text=f"Edit {task} Parameters",
                             command=lambda t=task: self.edit_task_parameters(t),
                             width=20, pady=3)
            button.grid(row=i, column=0, pady=3, padx=10, sticky="ew")
            self.task_buttons[task] = button

        # Start Program Button - centered with padding
        start_btn = tk.Button(content_frame, text="Start Program", 
                             command=self.start_program, width=20, pady=5)
        start_btn.grid(row=6, column=0, pady=20, sticky="ew")

        # Reset Progress Button
        reset_btn = tk.Button(content_frame, text="Reset Progress", 
                     command=self.reset_progress, width=20, pady=5)
        reset_btn.grid(row=4, column=0, padx=5, sticky="ew")


    def start_program(self):
        try:
            # Define the relative path to the program
            current_directory = os.getcwd()
            program_path = os.path.join(current_directory, "ACTS_frontend.py")
            print(program_path)
            # Check if the file exists
            if not os.path.exists(program_path):
                messagebox.showerror("Error", "Program file not found!")
                return

            # Start the program
            #subprocess.Popen([program_path], shell = True)
            #messagebox.showinfo("Success", "Program started successfully!")
            subprocess.run(["python3", program_path])
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start program: {e}")

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return
        try:
            self.file_editor = FileEditor(file_path)
            messagebox.showinfo("Success", "File loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def edit_global_parameters(self):
        if self.file_editor is None:
            messagebox.showwarning("Warning", "Load a parameter file first!")
            return

        window = tk.Toplevel(self.root)
        window.title("Edit Global Parameters")
        window.grid_columnconfigure(0, weight=1)
        window.minsize(500, 400)

        # Create main container frame with scrollbar
        main_frame = tk.Frame(window)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Create canvas and scrollbar
        canvas = tk.Canvas(main_frame, highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        # Configure the scrollable area
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Configure weights for resizing
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Add padding to the scrollable frame
        content_frame = tk.Frame(scrollable_frame, padx=20, pady=20)
        content_frame.grid(row=0, column=0, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)

        # Title label
        title_label = tk.Label(content_frame, text="Edit Global Parameters", font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Inputs for global parameters
        subject_1_name = tk.StringVar(value=self.file_editor.df.iloc[0]["Subject"])
        subject_2_name = tk.StringVar(value=self.file_editor.df.iloc[1]["Subject"])
        subject_1_id = tk.StringVar(value=self.file_editor.df.iloc[0]["Left Wrist"])
        subject_2_id = tk.StringVar(value=self.file_editor.df.iloc[1]["Left Wrist"])

        # Labels and entries for names and IDs
        tk.Label(content_frame, text="Subject 1 Name", font=("Arial", 10)).grid(row=1, column=0, pady=5, sticky="w")
        tk.Entry(content_frame, textvariable=subject_1_name, font=("Arial", 10)).grid(row=1, column=1, pady=5, sticky="ew")
        tk.Label(content_frame, text="Subject 2 Name", font=("Arial", 10)).grid(row=2, column=0, pady=5, sticky="w")
        tk.Entry(content_frame, textvariable=subject_2_name, font=("Arial", 10)).grid(row=2, column=1, pady=5, sticky="ew")

        tk.Label(content_frame, text="Subject 1 ID", font=("Arial", 10)).grid(row=3, column=0, pady=5, sticky="w")
        tk.Entry(content_frame, textvariable=subject_1_id, font=("Arial", 10)).grid(row=3, column=1, pady=5, sticky="ew")
        tk.Label(content_frame, text="Subject 2 ID", font=("Arial", 10)).grid(row=4, column=0, pady=5, sticky="w")
        tk.Entry(content_frame, textvariable=subject_2_id, font=("Arial", 10)).grid(row=4, column=1, pady=5, sticky="ew")

        # Task order section for Subject 1
        tk.Label(content_frame, text="Subject 1 Task Order", font=("Arial", 10, "bold")).grid(row=5, column=0, pady=10, sticky="w", columnspan=2)
        subject_1_task_list = tk.Listbox(content_frame, height=5, selectmode=tk.SINGLE, exportselection=False, font=("Arial", 10))
        subject_1_tasks = self.file_editor.df.iloc[0]["task-order"].split(
            "-") if "task-order" in self.file_editor.df.columns else list(self.tasks_params.keys())
        for task in subject_1_tasks:
            subject_1_task_list.insert(tk.END, task)
        subject_1_task_list.grid(row=6, column=0, pady=5, sticky="ew", columnspan=2)

        # Dropdown menu for available tasks for Subject 1
        available_tasks = list(self.tasks_params.keys())
        subject_1_selected_task = tk.StringVar(value=available_tasks[0])

        def move_subject_1_task_up():
            selected = subject_1_task_list.curselection()
            if selected and selected[0] > 0:
                index = selected[0]
                subject_1_tasks[index], subject_1_tasks[index - 1] = subject_1_tasks[index - 1], subject_1_tasks[index]
                update_task_list(subject_1_task_list, subject_1_tasks)
                subject_1_task_list.selection_set(index - 1)

        def move_subject_1_task_down():
            selected = subject_1_task_list.curselection()
            if selected and selected[0] < len(subject_1_tasks) - 1:
                index = selected[0]
                subject_1_tasks[index], subject_1_tasks[index + 1] = subject_1_tasks[index + 1], subject_1_tasks[index]
                update_task_list(subject_1_task_list, subject_1_tasks)
                subject_1_task_list.selection_set(index + 1)

        def add_subject_1_task():
            new_task = subject_1_selected_task.get()
            if new_task not in subject_1_tasks:
                subject_1_tasks.append(new_task)
                update_task_list(subject_1_task_list, subject_1_tasks)

        def delete_subject_1_task():
            selected = subject_1_task_list.curselection()
            if selected:
                index = selected[0]
                subject_1_tasks.pop(index)
                update_task_list(subject_1_task_list, subject_1_tasks)

        task_menu = tk.OptionMenu(content_frame, subject_1_selected_task, *available_tasks)
        task_menu.config(font=("Arial", 10))
        task_menu.grid(row=7, column=0, pady=5, sticky="ew", columnspan=2)

        # Button frame for Subject 1 tasks
        btn_frame = tk.Frame(content_frame)
        btn_frame.grid(row=8, column=0, columnspan=2, pady=5, sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        btn_frame.grid_columnconfigure(2, weight=1)
        btn_frame.grid_columnconfigure(3, weight=1)

        tk.Button(btn_frame, text="Add Task", command=add_subject_1_task, padx=5).grid(row=0, column=0, padx=2, sticky="ew")
        tk.Button(btn_frame, text="Delete Task", command=delete_subject_1_task, padx=5).grid(row=0, column=1, padx=2, sticky="ew")
        tk.Button(btn_frame, text="Move Up", command=move_subject_1_task_up, padx=5).grid(row=0, column=2, padx=2, sticky="ew")
        tk.Button(btn_frame, text="Move Down", command=move_subject_1_task_down, padx=5).grid(row=0, column=3, padx=2, sticky="ew")

        # Task order section for Subject 2
        tk.Label(content_frame, text="Subject 2 Task Order", font=("Arial", 10, "bold")).grid(row=9, column=0, pady=10, sticky="w", columnspan=2)
        subject_2_task_list = tk.Listbox(content_frame, height=5, selectmode=tk.SINGLE, exportselection=False, font=("Arial", 10))
        subject_2_tasks = self.file_editor.df.iloc[1]["task-order"].split(
            "-") if "task-order" in self.file_editor.df.columns else list(self.tasks_params.keys())
        for task in subject_2_tasks:
            subject_2_task_list.insert(tk.END, task)
        subject_2_task_list.grid(row=10, column=0, pady=5, sticky="ew", columnspan=2)

        subject_2_selected_task = tk.StringVar(value=available_tasks[0])

        def move_subject_2_task_up():
            selected = subject_2_task_list.curselection()
            if selected and selected[0] > 0:
                index = selected[0]
                subject_2_tasks[index], subject_2_tasks[index - 1] = subject_2_tasks[index - 1], subject_2_tasks[index]
                update_task_list(subject_2_task_list, subject_2_tasks)
                subject_2_task_list.selection_set(index - 1)

        def move_subject_2_task_down():
            selected = subject_2_task_list.curselection()
            if selected and selected[0] < len(subject_2_tasks) - 1:
                index = selected[0]
                subject_2_tasks[index], subject_2_tasks[index + 1] = subject_2_tasks[index + 1], subject_2_tasks[index]
                update_task_list(subject_2_task_list, subject_2_tasks)
                subject_2_task_list.selection_set(index + 1)

        def add_subject_2_task():
            new_task = subject_2_selected_task.get()
            if new_task not in subject_2_tasks:
                subject_2_tasks.append(new_task)
                update_task_list(subject_2_task_list, subject_2_tasks)

        def delete_subject_2_task():
            selected = subject_2_task_list.curselection()
            if selected:
                index = selected[0]
                subject_2_tasks.pop(index)
                update_task_list(subject_2_task_list, subject_2_tasks)

        task_menu2 = tk.OptionMenu(content_frame, subject_2_selected_task, *available_tasks)
        task_menu2.config(font=("Arial", 10))
        task_menu2.grid(row=11, column=0, pady=5, sticky="ew", columnspan=2)

        # Button frame for Subject 2 tasks
        btn_frame2 = tk.Frame(content_frame)
        btn_frame2.grid(row=12, column=0, columnspan=2, pady=5, sticky="ew")
        btn_frame2.grid_columnconfigure(0, weight=1)
        btn_frame2.grid_columnconfigure(1, weight=1)
        btn_frame2.grid_columnconfigure(2, weight=1)
        btn_frame2.grid_columnconfigure(3, weight=1)

        tk.Button(btn_frame2, text="Add Task", command=add_subject_2_task, padx=5).grid(row=0, column=0, padx=2, sticky="ew")
        tk.Button(btn_frame2, text="Delete Task", command=delete_subject_2_task, padx=5).grid(row=0, column=1, padx=2, sticky="ew")
        tk.Button(btn_frame2, text="Move Up", command=move_subject_2_task_up, padx=5).grid(row=0, column=2, padx=2, sticky="ew")
        tk.Button(btn_frame2, text="Move Down", command=move_subject_2_task_down, padx=5).grid(row=0, column=3, padx=2, sticky="ew")

        def update_task_list(listbox, tasks):
            listbox.delete(0, tk.END)
            for task in tasks:
                listbox.insert(tk.END, task)

        def save_changes():
            self.file_editor.set_subject_name(0, subject_1_name.get())
            self.file_editor.set_subject_name(1, subject_2_name.get())
            self.file_editor.set_subject_id(0, subject_1_id.get())
            self.file_editor.set_subject_id(1, subject_2_id.get())
            self.file_editor.set_tasks_order(0, subject_1_tasks)
            self.file_editor.set_tasks_order(1, subject_2_tasks)
            messagebox.showinfo("Success", "Global Parameters updated successfully!")
            window.destroy()

        # Save button centered below both columns
        save_btn = tk.Button(content_frame, text="Save Changes", command=save_changes, 
                           padx=10, pady=5, font=("Arial", 10, "bold"))
        save_btn.grid(row=13, column=0, columnspan=2, pady=20, sticky="ew")

    def edit_task_parameters(self, task_name):
        if self.file_editor is None:
            messagebox.showwarning("Warning", "Load a parameter file first!")
            return

        window = tk.Toplevel(self.root)
        window.title(f"Edit {task_name} Parameters")
        window.grid_columnconfigure(0, weight=1)
        window.minsize(500, 400)

        # Create main frame for centering
        main_frame = tk.Frame(window, padx=20, pady=20)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)

        # Create content frame
        frame = tk.Frame(main_frame)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)
        frame.grid_columnconfigure(3, weight=1)

        # Title label
        title_label = tk.Label(frame, text=f"Edit {task_name} Parameters", font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))

        # Inputs for task parameters for Subject 1 and 2
        subject_1_params = {}
        subject_2_params = {}
        for i, param in enumerate(self.tasks_params[task_name]):
            tk.Label(frame, text=f"{param} (Subject 1)", font=("Arial", 10)).grid(row=i+1, column=0, sticky="w", padx=5, pady=5)

            value_1 = tk.StringVar(value=self.file_editor.df.iloc[0][param])
            entry_1 = tk.Entry(frame, textvariable=value_1, font=("Arial", 10))
            entry_1.grid(row=i+1, column=1, padx=5, pady=5, sticky="ew")
            subject_1_params[param] = value_1

            if task_name != 'GO_NO_GO':
                tk.Label(frame, text=f"{param} (Subject 2)", font=("Arial", 10)).grid(row=i+1, column=2, sticky="w", padx=5, pady=5)
                value_2 = tk.StringVar(
                    value=self.file_editor.df.iloc[1][param] if len(self.file_editor.df) > 1 else "")
                entry_2 = tk.Entry(frame, textvariable=value_2, font=("Arial", 10))
                entry_2.grid(row=i+1, column=3, padx=5, pady=5, sticky="ew")
                subject_2_params[param] = value_2

        def save_changes():
            for param, var in subject_1_params.items():
                self.file_editor.set_task_param(0, param, var.get())
            for param, var in subject_2_params.items():
                self.file_editor.set_task_param(1, param, var.get())
            messagebox.showinfo("Success", f"{task_name} Parameters updated successfully!")
            window.destroy()

        # Save button centered below all columns
        save_btn = tk.Button(frame, text="Save Changes", command=save_changes, 
                           padx=10, pady=5, font=("Arial", 10, "bold"))
        save_btn.grid(row=len(self.tasks_params[task_name])+2, column=0, columnspan=4, pady=20, sticky="ew")

    def reset_progress(self):
        try:
            # Define the path to the reset script
            current_directory = os.getcwd()
            script_path = os.path.join(current_directory, "reset_progress.py")

            # Check if the file exists
            if not os.path.exists(script_path):
                messagebox.showerror("Error", "reset_progress.py not found in current directory!")
                return

            # Run the reset script
            result = subprocess.run(["python", script_path], capture_output=True, text=True)
            
            if result.returncode == 0:
                messagebox.showinfo("Success", "Progress reset successfully!")
            else:
                messagebox.showerror("Error", f"Failed to reset progress:\n{result.stderr}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run reset script: {e}")


# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = ParameterEditorApp(root)
    root.mainloop()