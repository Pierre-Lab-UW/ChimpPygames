import tkinter as tk
from tkinter import filedialog, messagebox
from FileEditor import FileEditor  # Import your FileEditor class
import subprocess
import os



class ParameterEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Parameter Editor")
        self.file_editor = None
        self.global_params = ["subject_1_name", "subject_2_name", "subject_1_id", "subject_2_id", "subject_1_task_order", "subject_2_task_order"]
        self.tasks_params = {
            "SHAPE0": [],
            "SHAPE1": ["SHAPE1_to_decrement", "SHAPE1trials", "SHAPE1criterion"],
            "SHAPE2": ["SHAPE2size", "SHAPE2_zones", "SHAPE2trials", "SHAPE2criterion"],
            "Two_Choice_Discrimination": ["2choicesize","2choicereset","2choiceproblems","2choicetrials","2choicecorrect"],
            "Match_To_Sample": [],
            "Delayed_Match_To_Sample": ["dMTSsize","dMTStrials","dMTScriterion"],
            "Oddity_Testing": [],
            "Delayed_Response_Task": [],
            "SocialStimuli": []
        }
        
        # UI Elements
        self.setup_ui()

    def setup_ui(self):
        # Load CSV file button
        tk.Button(self.root, text="Load Parameter File", command=self.load_file).pack(pady=10)

        # Global Parameters Section
        self.global_frame = tk.LabelFrame(self.root, text="Global Parameters")
        self.global_frame.pack(fill="x", padx=10, pady=5)
        tk.Button(self.global_frame, text="Edit Global Parameters", command=self.edit_global_parameters).pack()

        # Task Buttons
        self.tasks_frame = tk.LabelFrame(self.root, text="Task Parameters")
        self.tasks_frame.pack(fill="x", padx=10, pady=5)

        self.task_buttons = {}
        for task in self.tasks_params:
            button = tk.Button(self.tasks_frame, text=f"Edit {task} Parameters", 
                               command=lambda t=task: self.edit_task_parameters(t))
            button.pack(fill="x", padx=5, pady=2)
            self.task_buttons[task] = button
        
        # Start Program Button
        tk.Button(self.root, text="Start Program", command=self.start_program).pack(pady=10)
    
    def start_program(self):
        try:
            # Define the relative path to the program
            program_path = os.path.join(os.path.dirname(__file__), "../ACTS_frontend.py")
            
            # Check if the file exists
            if not os.path.exists(program_path):
                messagebox.showerror("Error", "Program file not found!")
                return
            
            # Start the program
            subprocess.Popen(["python", program_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            messagebox.showinfo("Success", "Program started successfully!")
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

        frame = tk.Frame(window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Inputs for global parameters
        subject_1_name = tk.StringVar(value=self.file_editor.df.iloc[0]["Subject"])
        subject_2_name = tk.StringVar(value=self.file_editor.df.iloc[1]["Subject"])
        subject_1_id = tk.StringVar(value=self.file_editor.df.iloc[0]["Left Wrist"])
        subject_2_id = tk.StringVar(value=self.file_editor.df.iloc[1]["Left Wrist"])

        tk.Label(frame, text="Subject 1 Name").grid(row=0, column=0, pady=2)
        tk.Entry(frame, textvariable=subject_1_name).grid(row=0, column=1, pady=2)
        tk.Label(frame, text="Subject 2 Name").grid(row=1, column=0, pady=2)
        tk.Entry(frame, textvariable=subject_2_name).grid(row=1, column=1, pady=2)

        tk.Label(frame, text="Subject 1 ID").grid(row=2, column=0, pady=2)
        tk.Entry(frame, textvariable=subject_1_id).grid(row=2, column=1, pady=2)
        tk.Label(frame, text="Subject 2 ID").grid(row=3, column=0, pady=2)
        tk.Entry(frame, textvariable=subject_2_id).grid(row=3, column=1, pady=2)

        # Task order section
        tk.Label(frame, text="Subject 1 Task Order").grid(row=4, column=0, pady=5, sticky="w")
        subject_1_task_list = tk.Listbox(frame, height=10, selectmode=tk.SINGLE, exportselection=False)
        subject_1_tasks = self.file_editor.df.iloc[0]["task-order"].split("-") if "task-order" in self.file_editor.df.columns else list(self.tasks_params.keys())
        for task in subject_1_tasks:
            subject_1_task_list.insert(tk.END, task)
        subject_1_task_list.grid(row=5, column=0, pady=2, sticky="w")

        # Dropdown menu for available tasks
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

        tk.OptionMenu(frame, subject_1_selected_task, *available_tasks).grid(row=6, column=0, pady=2, sticky="w")
        tk.Button(frame, text="Add Task", command=add_subject_1_task).grid(row=7, column=0, pady=2)
        tk.Button(frame, text="Delete Task", command=delete_subject_1_task).grid(row=8, column=0, pady=2)
        tk.Button(frame, text="Move Up", command=move_subject_1_task_up).grid(row=9, column=0, pady=2)
        tk.Button(frame, text="Move Down", command=move_subject_1_task_down).grid(row=10, column=0, pady=2)

        # Similar controls for Subject 2
        tk.Label(frame, text="Subject 2 Task Order").grid(row=4, column=1, pady=5, sticky="w")
        subject_2_task_list = tk.Listbox(frame, height=10, selectmode=tk.SINGLE, exportselection=False)
        subject_2_tasks = self.file_editor.df.iloc[1]["task-order"].split("-") if "task-order" in self.file_editor.df.columns else list(self.tasks_params.keys())
        for task in subject_2_tasks:
            subject_2_task_list.insert(tk.END, task)
        subject_2_task_list.grid(row=5, column=1, pady=2, sticky="w")

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

        tk.OptionMenu(frame, subject_2_selected_task, *available_tasks).grid(row=6, column=1, pady=2, sticky="w")
        tk.Button(frame, text="Add Task", command=add_subject_2_task).grid(row=7, column=1, pady=2)
        tk.Button(frame, text="Delete Task", command=delete_subject_2_task).grid(row=8, column=1, pady=2)
        tk.Button(frame, text="Move Up", command=move_subject_2_task_up).grid(row=9, column=1, pady=2)
        tk.Button(frame, text="Move Down", command=move_subject_2_task_down).grid(row=10, column=1, pady=2)

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

        tk.Button(frame, text="Save", command=save_changes).grid(columnspan=2, pady=10)



    def edit_task_parameters(self, task_name):
        if self.file_editor is None:
            messagebox.showwarning("Warning", "Load a parameter file first!")
            return

        window = tk.Toplevel(self.root)
        window.title(f"Edit {task_name} Parameters")

        frame = tk.Frame(window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Inputs for task parameters for Subject 1 and 2
        subject_1_params = {}
        subject_2_params = {}
        for i, param in enumerate(self.tasks_params[task_name]):
            if True:
                tk.Label(frame, text=f"{param} (Subject 1)").grid(row=i, column=0, sticky="w", padx=5, pady=2)
                value_1 = tk.StringVar(value=self.file_editor.df.iloc[0][param])
                entry_1 = tk.Entry(frame, textvariable=value_1)
                entry_1.grid(row=i, column=1, padx=5, pady=2)
                subject_1_params[param] = value_1

                tk.Label(frame, text=f"{param} (Subject 2)").grid(row=i, column=2, sticky="w", padx=5, pady=2)
                value_2 = tk.StringVar(value=self.file_editor.df.iloc[1][param] if len(self.file_editor.df) > 1 else "")
                entry_2 = tk.Entry(frame, textvariable=value_2)
                entry_2.grid(row=i, column=3, padx=5, pady=2)
                subject_2_params[param] = value_2

        def save_changes():
            for param, var in subject_1_params.items():
                self.file_editor.set_task_param(0, param, var.get())
            for param, var in subject_2_params.items():
                self.file_editor.set_task_param(1, param, var.get())
            messagebox.showinfo("Success", f"{task_name} Parameters updated successfully!")
            window.destroy()

        tk.Button(frame, text="Save", command=save_changes).grid(columnspan=4, pady=10)

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = ParameterEditorApp(root)
    root.mainloop()
