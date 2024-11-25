import tkinter as tk
from tkinter import filedialog, messagebox
from GUI import FileEditor  # Import your FileEditor class



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
            "Delayed_Response_Task": []
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

        def save_changes():
            self.file_editor.set_subject_name(0, subject_1_name.get())
            self.file_editor.set_subject_name(1, subject_2_name.get())
            self.file_editor.set_subject_id(0, subject_1_id.get())
            self.file_editor.set_subject_id(1, subject_2_id.get())
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
