from .gif2canvas import MyLabel
import tkinter as tk
import os

class Loading:
    def __init__(self, master):
        self.lframe = tk.Toplevel(master, bg="white")
        self.master = master
        # Gets both half the screen width/height and window width/height
        self.positionRight = int(master.winfo_rootx())
        self.positionDown = int(master.winfo_rooty())
        self.anim = MyLabel(self.lframe, os.path.dirname(os.path.abspath(__file__))+"/loading.gif")

    def show(self):
        self.lframe.geometry("{}x{}+{}+{}".format(self.master.winfo_width(), self.master.winfo_height(), self.positionRight, self.positionDown))
        self.lframe.grab_set()
        self.lframe.focus_force()
        self.lframe.overrideredirect(True)
        self.lframe.attributes("-alpha", 0.8)
        self.anim.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        tlabel = tk.Label(self.lframe, text="Loading...", bg="white")
        tlabel.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

    def stop(self):
        self.anim.after_cancel(self.anim.cancel)
        self.lframe.destroy()
