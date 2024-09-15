from fc.Project import create_home_directory
    

from .ProjectFrame import ProjectFrame
from .ProjectToolBar import ProjectToolBar
from .ShellFrame import ShellFrame

from tkinter import Tk, Frame


# The main frame of my windows
class Babel(Frame):
    
    def __init__(self, app, title = "Babel project"):
        
        super().__init__(app)
        
        self.master.title(title)
        
        # The home directory is where the projects are inside the file system
        self.create_home_directory()
        
        # The project frame is the frame where are print the files of the project
        self.init_projectframe()
        
        # The tool bar for create / open a project + file commands
        self.init_toolbar()
        
        # The shell frame where are show up the 'print(sys.sdtout)'
        self.init_shellframe()
        #self.toolbar.open("test")
        
        # When I quit the processus I want to save the cache and end the tread using updating the shell frame
        self.master.bind('<Destroy>', self.exit) #I suppose it works ...
        
    # I save the cache and stop the thread using the shell frame then wait for it
    def exit(self, evt):
        print("write cache")
        from fc.Cache import Cache
        cache = Cache()
        cache.write()
        
    # The home directory is where the projects are inside the file system
    def create_home_directory(self):
        self.home = create_home_directory()
        
    def init_toolbar(self):
        self.toolbar = ProjectToolBar(self)
        
    def init_projectframe(self):
        self.projectframe = ProjectFrame(self)
        self.projectframe.pack()
        
    def init_shellframe(self):
        self.shellframe = ShellFrame(self)
        self.shellframe.pack()
        
   
        
        
# Create a Tk windows with a Babel inside
def mainui():
    root = Tk()
    
    root.geometry("500x500")
    
    window = Babel(root)
    window.pack()
    
    root.mainloop()