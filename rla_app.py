import os
from tkinter import *
from tkinter import ttk
from tkinter import font
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import dronekit_scripts.path_generation as backend


class MainApp(Tk):
    def __init__(self) -> None:
        # Set up main window
        Tk.__init__(self)
        self.wm_title("Robotic Lawn Aerator - Path Planner")
        # default geometry 915x522
        self.geometry("950x550")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Create main frame container to store other widgets
        self.mainframe = ttk.Frame(self, padding=3)
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        # All rows scale equally
        self.mainframe.rowconfigure(0, weight=1)
        self.mainframe.rowconfigure(1, weight=1)
        self.mainframe.rowconfigure(2, weight=1)
        self.mainframe.rowconfigure(3, weight=1)
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
        # Action widget: connect to vehicle
        self.connect_to_vehicle_widget = ConnectToVehicle(
            self.mainframe, padding=(10, 3))
        self.connect_to_vehicle_widget.grid(column=0, row=2, sticky='n')
        # Action widget: upload mission (need to connect to vehicle first)
        self.upload_mission_widget = UploadMission(
            self.mainframe, self, padding=(10, 3))
        self.upload_mission_widget.grid(column=0, row=3, sticky='ne')

        # Plot widgets (right hand side)
        # Initialise plot page first
        self.plot_page = PlotPage(
            self.mainframe, self, borderwidth=1, relief='solid')
        self.plot_page.grid(column=1, row=0, rowspan=4, sticky='nwse')
        # Draw start info page on top
        self.info_page = InfoPage(
            self.mainframe,
            """Welcome to RLA-Path Planner\n\nThis application is used to generate "lawnmower" path for Mission Planner.\nPlease import a .poly file to generate a path which will be displayed in a plot. Then you can write the generated path to a text file to be used in Mission Planner.""",
            borderwidth=1, relief='solid')
        self.info_page.grid(column=1, row=0, rowspan=4, sticky='nwse')

    def update_plot_page(self):
        # Can move this to ImportPolygon method
        # Clear old axes and redraw
        self.plot_page.ax.clear()
        temp = backend.draw_highlighted_node(
            self.polygon_file_path, self.plot_page.ax
        )
        # temp solution before OOP implemented for backend
        self.polygon, self.grid = temp
        self.plot_page.canvas.draw()
        self.plot_page.tkraise()

    def show_end_page(self):
        self.info_page.info_msg.set("This is the end page")
        self.info_page.tkraise()


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
        label = ttk.Label(self, text="Import polygon:")
        label.grid(column=0, row=0, sticky='w')
        # Entry to take in connection string
        self.polygon_file = StringVar(value="lawn-polygon.poly")
        polygon_file_entry = ttk.Entry(
            self, textvariable=self.polygon_file
        )
        polygon_file_entry.grid(column=0, row=1)
        # Button to initiate connect to vehicle callback
        connect_button = ttk.Button(
            self, text="Import", command=self.import_polygon)
        connect_button.grid(column=1, row=1, sticky='e')

    def import_polygon(self):
        # Get absolute path and plot the path
        self.controller.polygon_file_path = os.path.join(
            os.getcwd(),
            "rla_app_files",
            self.polygon_file.get()
        )
        self.controller.update_plot_page()
        # Enable writing to file
        self.controller.export_mission_widget.export_button.state([
                                                                  '!disabled'])


class ExportMission(ttk.Frame):
    def __init__(self, master, controller, *args, **kwargs):
        ttk.Frame.__init__(self, master, *args, **kwargs)
        self.controller = controller
        # Label to explain the widget
        label = ttk.Label(self, text="Export mission:")
        label.grid(column=0, row=0, sticky='w')
        # Entry to take in connection string
        self.mission_file = StringVar(value="polygon-path.txt")
        mission_file_entry = ttk.Entry(
            self, textvariable=self.mission_file
        )
        mission_file_entry.grid(column=0, row=1)
        # Button to initiate connect to vehicle callback
        self.export_button = ttk.Button(
            self, text="Write", command=self.export_mission)
        # Disable if haven't imported polygon
        self.export_button.state(['disabled'])
        self.export_button.grid(column=1, row=1, sticky='e')
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
        self.plot_toggle.grid(column=0, row=2, sticky='e')

    def export_mission(self):
        # Get absolute path and write to file
        mission_file_name = os.path.join(
            os.getcwd(),
            "rla_app_files",
            self.mission_file.get()
        )
        backend.save_mission_to_file(
            mission_file_name,
            self.controller.grid,
            self.controller.polygon
        )
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


# class PlotFrame(ttk.Frame):
#     def __init__(self, master, *args, **kwargs):
#         ttk.Frame.__init__(self, master, *args, **kwargs)
#         self.info_msg = "Start"
#         self.info_page = InfoPage(self, self.info_msg)
#         self.info_page.grid(row=0, column=0, sticky='nwse')
#         self.columnconfigure(0, weight=1)
#         self.rowconfigure(0, weight=1)

#     def show_plot_page(self):
#         self.plot_page = PlotPage(self)
#         self.plot_page.grid(row=0, column=0, sticky='nwse')


class InfoPage(ttk.Frame):
    def __init__(self, master, info_msg, *args, **kwargs):
        ttk.Frame.__init__(self, master, *args, **kwargs)
        description_font = font.Font(family='Helvetica', size=16)
        self.info_msg = StringVar(value=info_msg)
        display_text = ttk.Label(
            self, textvariable=self.info_msg, font=description_font)
        display_text.grid(row=0, column=0)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)


class PlotPage(ttk.Frame):
    def __init__(self, master, controller, * args, **kwargs):
        ttk.Frame.__init__(self, master, *args, **kwargs)
        self.controller = controller
        # Plot
        # Initialise matplotlib.figure.Figure rather than pyplot.Figure
        # to avoid tk not closing
        fig = Figure(tight_layout=True, facecolor="#d9d9d9")
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
