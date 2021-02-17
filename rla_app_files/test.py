from tkinter import *

# pip install pillow
from PIL import Image, ImageTk


class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.pack(fill=BOTH, expand=1)

        load = Image.open("rla_app_files/rla-logo.png")
        render = ImageTk.PhotoImage(Image.open("rla_app_files/rla-logo.png"))
        imgobj = PhotoImage(file="rla_app_files/rla-logo.png")
        img = Label(self, image=imgobj)
        img.image = imgobj
        img.grid(row=0, column=0, sticky='nwse')


root = Tk()
app = Window(root)
root.wm_title("Tkinter window")
root.mainloop()
