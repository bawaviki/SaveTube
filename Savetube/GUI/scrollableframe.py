import tkinter as tk


class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, height=600)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        # canvas.place(relheight=1, relwidth=0.9)
        # scrollbar.pack(fill="y", side="right")
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


# root = tk.Tk()
#
# frame = ScrollableFrame(root)
#
# for i in range(50):
#     ttk.Label(frame.scrollable_frame, text="Sample scrolling label").pack()
#
# frame.pack()
# root.mainloop()
