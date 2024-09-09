from fc.Project import list_projects, create_project, get_project

from fc.archiver import extract

from tkinter import Menu, Toplevel, Label, StringVar
#https://docs.python.org/3/library/tkinter.messagebox.html
#https://docs.python.org/3/library/dialog.html
from tkinter import messagebox, simpledialog, filedialog
from tkinter import ttk

from os import path
from threading import Thread

class ProjectToolBar(Menu):
    
    ACCEPTED_FILES = [("Accepted file", ".afs .iso .xp3"),
                      ("AFS file", ".afs"),
                      ("ISO file", ".iso"),
                      ("XP3 file", ".xp3")]
    
    def __init__(self, app):
        
        # I initialise my tool bar with app (BabelFrame)
        super().__init__(app)
        app.master.config(menu = self)
        
        # I save the project frame for the reload command and for open a project
        self.projectframe = app.projectframe
        
        project = Menu(self, tearoff = False)
        project.add_command(label = "New", command = self.new)
        project.add_command(label = "New from file", command = self.newfromfile)
        project.add_command(label = "Open", command = self.open)
        project.add_separator()
        project.add_command(label = "Reload", command = self.projectframe.print_project)
        self.add_cascade(label = "Project", menu = project)
        
        file = Menu(self, tearoff = False)
        file.add_command(label = "Import file", command = self.projectframe.importfile)
        file.add_command(label = "Import directory", command = self.projectframe.importdir)
        self.add_cascade(label = "File", menu = file)
        
        self.add_command(label = "Help")
        
    # Disable the tool bar and save the old states inside a list
    def disable(self):
        end = self.index("end")
        self.old_state = []
        for i in range(end):
            self.old_state.append(self.entrycget(i+1, 'state'))
            self.entryconfigure(i+1, state = 'disabled')
            
    # Re-enable the too bar
    def reenable(self):
        end = self.index("end")
        if end != len(self.old_state):
            return -1 # Just stop but no raise an Exception, maybe?
        
        for i in range(end):
            self.entryconfigure(i+1, state = self.old_state.pop(0))
        
    # I ask a name for the project then try to create it and finaly open it
    def new(self):
        name = simpledialog.askstring(title = "Name your project", prompt = "name")
         
        if name is None:
            return
         
        try:
            create_project(name)
            messagebox.showinfo("Create", f"Projects '{name}' created")
            self.open(name)
        except Exception as e:
            messagebox.showerror("Already exists", f"{e}")
    
    # I ask the file use to create the project, ask the name and start the creation of the project
    # I extract the project inside another thread because otherwise it will freeze the main window
    def newfromfile(self):
        selected_file = filedialog.askopenfilename(filetypes=self.ACCEPTED_FILES)
         
        if selected_file == "":
            return
         
        basename = path.basename(selected_file)
        name = ".".join(basename.split(".")[:-1])
        
        name = simpledialog.askstring(title = "Name your project", prompt = "name", initialvalue=name)
        
        if name is None:
            return
        
        try:
            create_project(name)
        except Exception as e:
            messagebox.showerror("Already exists", f"{e}")
            return
        
        project = get_project(name)
        project_path = project.path
                
        t = Thread(target = self.newfromfileThread, args = [selected_file, project_path, name])
        t.start()
    
    # I disable the tool bar, extract the project the re-enable the tool bar with the same state, and I open the new project
    def newfromfileThread(self, selected_file, project_path, name):
        
        self.disable()
               
        try:
            extract(selected_file, project_path)
        except Exception as e:
            messagebox.showerror("Creation failed", f"{e}")
            self.reenable()
            return
    
        self.reenable()
            
        messagebox.showinfo("Create", f"Projects '{name}' created")
        self.open(name)
    
    # I ask the name of the project if None, then try to find it and show it inside the project frame
    def open(self, name = None):
        if not name:
            name = self.select_project()
           
        if not name:
            return
         
        project = get_project(name)
        
        if not project:
            messagebox.showerror("Can't open project", f"Can't found project '{name}'")
            return
        
        self.projectframe.load_project(project)
    
    # I open a window with a combobox asking which project open
    def select_project(self):
        top = Toplevel()
        Label(top, text = "Which project open?").pack()
        value = StringVar()
        combo = ttk.Combobox(top, textvariable=value, values = [p.name for p in list_projects()])
        combo.pack()
        combo.bind("<<ComboboxSelected>>", lambda _:top.destroy())
        top.grab_set()
        top.wait_window(top)
        return value.get()