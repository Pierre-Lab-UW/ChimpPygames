import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd


class FileEditor:
    def __init__(self, path_to_csv: str):
        self.path_to_csv = path_to_csv
        self.df = pd.read_csv(self.path_to_csv, dtype=str)
        print(self.df)
        print(self.path_to_csv)

    def set_subject_name(self, subject_number:int, subject_name:str):
        if subject_number > 2 or subject_number < 0:
            raise Exception("Subject number not valid!")
        self.df.iloc[subject_number, self.df.columns.get_loc("Subject")] = subject_name
        self.save_csv()

    def set_subject_id(self, subject_number:int, subject_id: any):
        if subject_number > 2 or subject_number < 0:
            raise Exception("Subject number not valid!")
        self.df.iloc[subject_number, self.df.columns.get_loc("Left Wrist")] = subject_id
        self.save_csv()

    def set_tasks_order(self, subject_number:int, task_list:list[str]):
        if subject_number > 2 or subject_number < 0:
            raise Exception("Subject number not valid!")
        string = ""
        for i in range(len(task_list)):
            string += task_list[i]
            if i != len(task_list) - 1:
                string += "-"
        self.set_task_param(subject_number, "task-order", string)
        self.save_csv()

    def set_task_param(self, subject_number:int, task_param: str, task_param_value: any):
        if subject_number > 2 or subject_number < 0:
            raise Exception("Subject number not valid!")
        #all task params are integers except one
        self.df.iloc[subject_number, self.df.columns.get_loc(task_param)] = task_param_value
        self.save_csv()

    def save_csv(self):
        self.df.to_csv(self.path_to_csv, index=False, na_rep="NA")

