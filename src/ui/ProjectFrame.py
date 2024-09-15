from fc.translate.magic_translate import translate, patch
from fc.archiver import extract, pack_from_list

from tkinter import Frame, Scrollbar, Listbox, Menu
from tkinter import Y, END, RIGHT
from tkinter import messagebox, filedialog

from os import path
from shutil import copy, copytree
from concurrent.futures import ThreadPoolExecutor

class ProjectFrame(Frame):
    
    EXECUTABLE_EXT = ["bat", "sh", "exe", "ps1", "bash"]
    
    PACK_EXT = [("ISO file", "*.iso"),
                ("AFS file", "*.afs"),
                ("XP3 file", "*.xp3")]
    
    def __init__(self, app):
        
        super().__init__(app)
        
        #self.toolbar = self.master.toolbar
        
        self.init_menu_right_click()
        
        self.scrollbar = Scrollbar(self)
        self.scrollbar.pack(side = RIGHT, fill = Y)
        
        self.listbox = Listbox(self, yscrollcommand=self.scrollbar.set)
        self.listbox.bind("<Double-1>", self.double_click)
        self.listbox.bind("<Button-3>", self.right_click)
        self.listbox.bind("<Button-2>", self.middle_click)
        self.listbox.pack()
        
        self.executor = ThreadPoolExecutor()
        
        self.project = None
        
    def init_menu_right_click(self):
        self.menu = Menu(self, tearoff = False)
        
        self.menu_pack = Menu(self.menu, tearoff= False)
        self.menu.add_command(label = "Pack", command = lambda: self.executor.submit(self.repack))
        
        self.menu.add_command(label = "Extract", command = lambda: self.executor.submit(self.extract))
        
        self.menu.add_separator()
        
        self.menu.add_command(label = "Translate", command = lambda: self.executor.submit(self.translate))
        self.menu.add_command(label = "Patch", command = lambda: self.executor.submit(self.patch))
        
        self.menu.add_separator()
        
        self.menu.add_command(label = "Delete", command = lambda: self.executor.submit(self.deletefile))
        
    def double_click(self, evt):
        clicked = self.listbox.selection_get()
        if len(clicked) == 0:
            return
        clicked = clicked.split("\n")[0]
        if clicked[-1] == "/":
            self.project.update_path(clicked[1:-1])
            self.print_project()
        else:
            ext = clicked.split(".")[-1]
            if ext in self.EXECUTABLE_EXT:
                sure = messagebox.askyesno("Open?", "This file may be malicious, do you want to open it?")
                if not sure:
                    return
            self.project.open(clicked)
            
    def right_click(self, evt):
        element = None
        for i in range(self.listbox.size()):
            bbox = self.listbox.bbox(i)
            if (bbox[0] <= evt.x <= bbox[0] + bbox[2]) & (bbox[1] <= evt.y <= bbox[1] + bbox[3]):
                element = i
                break
        if element is None:
            return 
        
        if not self.listbox.select_includes(element):
            self.listbox.selection_clear(0, END)
            self.listbox.select_set(element)
            
        self.menu_right_click_config(self.listbox.winfo_rootx()+bbox[0]+bbox[2],
            self.listbox.winfo_rooty()+bbox[1]+bbox[3])
        
    def middle_click(self, evt):
        element = None
        for i in range(self.listbox.size()):
            bbox = self.listbox.bbox(i)
            if (bbox[0] <= evt.x <= bbox[0] + bbox[2]) & (bbox[1] <= evt.y <= bbox[1] + bbox[3]):
                element = i
                break
        if element is None:
            return
        
        if self.listbox.select_includes(element):
            self.listbox.selection_clear(element)
        else:
            self.listbox.select_set(element)
        
    def load_project(self, project):
        self.project = project
        self.print_project()
        
    def print_project(self):
        self.listbox.delete(0, END)
        
        if not self.project:
            return
        
        for dir in self.project.get_dirs():
            self.listbox.insert(0, "📁" + dir + "/")
            
        for file in self.project.get_files():
            self.listbox.insert(END, file)
        self.listbox.pack()
        
    ####################################################
    ############# Functions menu right click ###########
    ####################################################
        
    def menu_right_click_config(self, x, y):
        
        files = self.listbox.selection_get().split("\n")
        
        hasdir = False
        for file in files:
            if file[-1] == "/":
                hasdir = True
                break
        
        if len(files) == 1 and not hasdir:
            self.menu.entryconfig("Extract", state = "normal")
        else:
            self.menu.entryconfig("Extract", state = "disabled")
            
        if not hasdir:
            self.menu.entryconfig("Translate", state = "normal")
            self.menu.entryconfig("Patch", state = "normal")
        else:
            self.menu.entryconfig("Translate", state = "disabled")
            self.menu.entryconfig("Patch", state = "disabled")
        
        self.menu.tk_popup(x, y)
        
    ### Pack / Extract ###
    
    def repack(self):
        files = self.listbox.selection_get().split("\n")
        dirname = self.project.get_actual_path()
        files = [path.join(dirname, file) for file in files]
        if len(files) == 0:
            return
        
        savefile = filedialog.asksaveasfile(filetypes = self.PACK_EXT, defaultextension  = self.PACK_EXT)
        
        if not savefile:
            return
        
        pack_from_list(*files, outfile = savefile.name)
    
    def extract(self):
        for file in self.listbox.selection_get().split("\n"):
            file = path.join(self.project.get_actual_path(), file)
            self.extractSingle(file)
            
    def extractSingle(self, file):
        try:
            extract(file)
        except Exception as e:
            messagebox.showerror("Cannot extract", f"{e}")
            
        self.print_project()
    
    ### Translate / Patch ###
        
    def translate(self):
        dirpath = self.project.get_actual_path()
        files = self.listbox.selection_get().split("\n")
        absfile = [path.join(dirpath, file) for file in files]
        fail, failed = translate(*absfile)
        if fail != 0:
            messagebox.showerror("Can't translate", f"Can't translate {failed}, check extension")
        self.print_project()
        
    def patch(self):
        dirpath = self.project.get_actual_path()
        files = self.listbox.selection_get().split("\n")
        absfile = [path.join(dirpath, file) for file in files]
        res = patch(*absfile, actual_dir = dirpath)
        
        if res < 0:
            messagebox.showerror("Can't patch", f"Can't translate {files}, check extension")
        self.print_project()
        
    ### File command ###
    
    def importfile(self, filepath = None):
        if not filepath:
            filepath = filedialog.askopenfilename()
        if not filepath:
            return
        
        filename = path.basename(filepath)
        newpath = path.join(self.project.get_actual_path(), filename)
        
        try:
            copy(filepath, newpath)
        except Exception as e:
            messagebox.showerror("Can't copy file", f"Can't copy file {filename}\n{e}")
            
        self.print_project()
            
    def importdir(self, dirpath = None):
        if not dirpath:
            dirpath = filedialog.askdirectory()
        if not dirpath:
            return
         
        dirname = path.basename(dirpath)
        newpath = path.join(self.project.get_actual_path(), dirname)
        
        try:
            copytree(dirpath, newpath)
        except Exception as e:
            messagebox.showerror("Can't copy file", f"Can't copy file {dirname}\n{e}")
            
        self.print_project()
    
    def deletefile(self):
        files = self.listbox.selection_get().split("\n")
        
        for file in files:
            if file[-1] == "/":
                self.project.delete(file[1:-1], True)
            else:
                self.project.delete(file)
                
        self.print_project()