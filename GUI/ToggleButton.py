import tkinter as tk

class PumpToggleButton(tk.Button):
    def __init__(self, master=None, callback=None, **kwargs):
        """
        :param master: Parent widget
        :param callback: Optional function to call when toggled. Signature: callback(state: bool)
        :param kwargs: Other Button options
        """
        self.pump_on = False  # Initial state
        self.callback = callback
        super().__init__(master, text="Pump: Vacant", command=self.toggle, **kwargs)
        self.configure(bg="green", activebackground="green", fg="white")
    
    def toggle(self):
        self.pump_on = not self.pump_on
        if self.pump_on:
            self.config(text="Pump: In use", bg="red", activebackground="red")
        else:
            self.config(text="Pump: Vacant", bg="green", activebackground="green")
        
        if self.callback:
            self.callback(self.pump_on)
