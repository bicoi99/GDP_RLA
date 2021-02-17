import os
import json
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from rla_app_files.path_planner import PathPlanner


class MainApp(Tk):
    def __init__(self) -> None:
        # Set up main window
        Tk.__init__(self)
        self.wm_title("Robotic Lawn Aerator - Path Planner")
        # default geometry 915x522
        self.geometry("950x550")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Get background colour to display on plot
        bg_colour16 = self.winfo_rgb(self['bg'])
        # Divide 16 bit R G B by 256 and convert to hex using format function,
        # then join them as well as slap a # at the front
        self.bg_colour = "#" + \
            "".join(map(lambda x: format(x//256, 'x'), bg_colour16))

        # Utils
        self.files_folder = os.path.join(os.getcwd(), "rla_app_files")

        # Menu bar
        self.option_add('*tearOff', FALSE)
        self.menubar = Menu(self)
        self['menu'] = self.menubar
        # File menu
        self.menu_file = Menu(self.menubar)
        self.menubar.add_cascade(menu=self.menu_file, label="File")
        self.menu_file.add_command(label="Not supported yet")
        # Help menu
        self.menu_help = Menu(self.menubar)
        self.menubar.add_cascade(menu=self.menu_help, label="Help")
        self.help_show = BooleanVar()
        self.menu_help.add_checkbutton(
            label="Show help page",
            command=self.show_help_page,
            variable=self.help_show,
            onvalue=True,
            offvalue=False
        )

        # Create main frame container to store other widgets
        self.mainframe = ttk.Frame(self, padding=3)
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        # All rows scale equally
        self.mainframe.rowconfigure(0, weight=1)
        self.mainframe.rowconfigure(1, weight=1)
        self.mainframe.rowconfigure(2, weight=1)
        # Plot column scales while action column stays the same
        self.mainframe.columnconfigure(1, weight=1)

        # Action widgets (left hand side)
        self.import_polygon_widget = ImportPolygon(
            self.mainframe, self, padding=(10, 3))
        self.import_polygon_widget.grid(column=0, row=0, sticky='n')
        # Action widget: export mission
        self.export_mission_widget = ExportMission(
            self.mainframe, self, padding=(10, 3))
        self.export_mission_widget.grid(column=0, row=1, sticky='n')
        # Logo
        self.logo = Logo(self.mainframe, self)
        self.logo.grid(column=0, row=2, sticky='s')

        # Plot widgets (right hand side)
        # Initialise plot page first
        self.plot_page = PlotPage(
            self.mainframe, self, borderwidth=1, relief='solid')
        self.plot_page.grid(column=1, row=0, rowspan=3, sticky='nwse')
        # Draw start info page on top
        # Get start page text
        with open(os.path.join(self.files_folder, "info_text.json")) as f:
            self.info_text = json.load(f)
        self.info_page = InfoPage(
            self.mainframe,
            self.info_text['start_page']['title'],
            self.info_text['start_page']['body'].format(
                self.files_folder,
                self.files_folder
            ),
            borderwidth=1,
            relief='solid'
        )
        self.info_page.grid(column=1, row=0, rowspan=3, sticky='nwse')

    def show_end_page(self):
        self.info_page.title_msg.set(self.info_text['end_page']['title'])
        self.info_page.info_msg.set(
            self.info_text['end_page']['body'].format(
                os.path.join(
                    self.files_folder,
                    self.export_mission_widget.mission_file.get()
                )
            )
        )
        self.info_page.tkraise()

    def show_help_page(self):
        pass
        # Need to split start and end page
        # start page is the help page


class Logo(ttk.Frame):
    def __init__(self, master, controller, *args, **kwargs):
        ttk.Frame.__init__(self, master, *args, **kwargs)
        img = PhotoImage(file=os.path.join(
            controller.files_folder, "rla-logo.png"
        ))
        label = ttk.Label(self, text="test", image=img)
        label.image = img
        label.grid(column=0, row=0, sticky='nwse')


class ConnectToVehicle(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        ttk.Frame.__init__(self, master, *args, **kwargs)

        # Label to explain the widget
        label = ttk.Label(self, text="Connect to vehicle:")
        label.grid(column=0, row=0, sticky='w')
        # Entry to take in connection string
        self.connection_string = StringVar(value="127.0.0.1:14550")
        connection_string_entry = ttk.Entry(
            self, textvariable=self.connection_string
        )
        connection_string_entry.grid(column=0, row=1)
        # Button to initiate connect to vehicle callback
        connect_button = ttk.Button(
            self, text="Connect", command=self.connect_to_vehicle)
        connect_button.state(['disabled'])
        connect_button.grid(column=1, row=1, sticky='e')

    def connect_to_vehicle(self):
        print(self.connection_string.get())


class ImportPolygon(ttk.Frame):
    def __init__(self, master, controller, *args, **kwargs):
        ttk.Frame.__init__(self, master, *args, **kwargs)
        self.controller = controller

        # Label to explain the widget
        label = ttk.Label(self, text="Choose polygon file to import:")
        label.grid(column=0, row=0, sticky='w')
        # Entry to import file path
        self.polygon_file = StringVar(value=os.path.join(
            os.getcwd(),
            self.controller.files_folder,
            "lawn-polygon.poly"))
        polygon_file_entry = ttk.Entry(
            self, textvariable=self.polygon_file, width=30
        )
        polygon_file_entry.xview_moveto(1)
        polygon_file_entry.grid(column=0, row=1, sticky='we')
        # Browse button to browse file path
        browse_icon = PhotoImage(file=os.path.join(
            controller.files_folder, "search-folder-icon.png"
        ))
        browse_button = Button(
            self, image=browse_icon, height=18, width=18,
            command=self.browse_file
        )
        browse_button.image = browse_icon
        browse_button.grid(column=1, row=1)
        # Import button
        import_button = ttk.Button(
            self, text="Import", command=self.import_polygon)
        import_button.grid(column=0, row=2, columnspan=2)

    def browse_file(self):
        file_name = filedialog.askopenfilename(
            initialdir=self.controller.files_folder,
            initialfile="lawn-polygon.poly",
            filetypes=[
                ("Polygon files", "*.poly"),
                ("All files", "*.*")
            ]
        )
        self.polygon_file.set(file_name)

    def import_polygon(self):
        # Clear old axis
        self.controller.plot_page.ax.clear()
        # Make backend using fetched polygon file path
        self.controller.backend = PathPlanner(
            self.polygon_file.get(),
            self.controller.plot_page.ax,
            self.controller.bg_colour
        )
        # Draw on new axis
        self.controller.backend.plot_path()
        # Update and rase the widget
        self.controller.plot_page.canvas.draw()
        self.controller.plot_page.tkraise()

        # Enable writing to file
        self.controller.export_mission_widget.export_button.state([
                                                                  '!disabled'])
        # Ensure that Hide/Show button is disabled and it is not on True
        self.controller.export_mission_widget.plot_toggle.state(['disabled'])
        self.controller.export_mission_widget.plot_show.set(False)


class ExportMission(ttk.Frame):
    def __init__(self, master, controller, *args, **kwargs):
        ttk.Frame.__init__(self, master, *args, **kwargs)
        self.controller = controller
        # Label to explain the widget
        label = ttk.Label(self, text="Choose location of export file:")
        label.grid(column=0, row=0, sticky='w')
        # Entry to get location export file
        self.mission_file = StringVar(value=os.path.join(
            os.getcwd(),
            self.controller.files_folder,
            "polygon-path.txt"))
        mission_file_entry = ttk.Entry(
            self, textvariable=self.mission_file, width=30
        )
        # Display the right of the text
        mission_file_entry.xview_moveto(1)
        mission_file_entry.grid(column=0, row=1, sticky='we')
        # Browse button to browse file path
        browse_icon = PhotoImage(file=os.path.join(
            controller.files_folder, "search-folder-icon.png"
        ))
        browse_button = Button(
            self, image=browse_icon, height=18, width=18,
            command=self.browse_file
        )
        browse_button.image = browse_icon
        browse_button.grid(column=1, row=1)
        # Button to export mission to file
        self.export_button = ttk.Button(
            self, text="Export", command=self.export_mission)
        # Disable if haven't imported polygon
        self.export_button.state(['disabled'])
        self.export_button.grid(column=0, row=2, columnspan=2)
        # Toggle box to turn plot
        self.plot_show = BooleanVar()
        self.plot_toggle = ttk.Checkbutton(
            self, text="Hide/Show Plot",
            command=self.show_hide_plot,
            variable=self.plot_show,
            onvalue=True,
            offvalue=False
        )
        # Disable if haven't exported
        self.plot_toggle.state(['disabled'])
        self.plot_toggle.grid(column=0, row=3, columnspan=2)

    def browse_file(self):
        file_name = filedialog.asksaveasfilename(
            initialdir=self.controller.files_folder,
            initialfile="polygon-path.txt",
            filetypes=[
                ("Supported files", "*.txt *.mission"),
                ("All files", "*.*")
            ]
        )
        self.mission_file.set(file_name)

    def export_mission(self):
        self.controller.backend.export_path(
            self.mission_file.get())
        # Display end page
        self.controller.show_end_page()
        # Enable graph toggle
        self.plot_toggle.state(['!disabled'])

    def show_hide_plot(self):
        if self.plot_show.get():
            self.controller.plot_page.tkraise()
        else:
            self.controller.info_page.tkraise()


class UploadMission(ttk.Frame):
    def __init__(self, master, controller, *args, **kwargs):
        ttk.Frame.__init__(self, master, *args, **kwargs)
        self.controller = controller
        # Label to explain the widget
        label = ttk.Label(self, text="Upload mission:")
        label.grid(column=0, row=0, sticky='w')
        # Button to upload mission to SITL or Cube
        upload_button = ttk.Button(
            self, text="Upload", command=self.upload_mission)
        # Disable this feature for now since differences found between
        # upload to vehicle and export to MP
        upload_button.state(['disabled'])
        upload_button.grid(column=1, row=0, sticky='e')

    def upload_mission(self):
        pass


class InfoPage(ttk.Frame):
    def __init__(self, master, title_msg, info_msg, *args, **kwargs):
        ttk.Frame.__init__(self, master, *args, **kwargs)
        self.title_msg = StringVar(value=title_msg)
        self.info_msg = StringVar(value=info_msg)
        text_title = ttk.Label(
            self, textvariable=self.title_msg,
            font="TkDefaultFont 16 bold"
        )
        text_title.grid(row=0, column=0, sticky='s')
        text_body = ttk.Label(
            self, textvariable=self.info_msg,
            font="TkTextFont", wraplength=650)
        text_body.grid(row=1, column=0, sticky='n', pady=10)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)


class PlotPage(ttk.Frame):
    def __init__(self, master, controller, * args, **kwargs):
        ttk.Frame.__init__(self, master, *args, **kwargs)
        self.controller = controller
        # Plot
        # Initialise matplotlib.figure.Figure rather than pyplot.Figure
        # to avoid tk not closing
        fig = Figure(tight_layout=True, facecolor=self.controller.bg_colour)
        # Generate axes to be drawn on later
        self.ax = fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.draw()
        # Toolbar
        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()
        # Pack the two elements
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)


if __name__ == "__main__":
    root = MainApp()
    root.mainloop()
