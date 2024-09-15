from tkinter import Frame, Scrollbar, Listbox
from tkinter import X, Y, END, RIGHT, BOTTOM

import sys
import threading
import queue
from time import sleep

class ShellFrame(Frame):
    
    def __init__(self, app):
        
        super().__init__(app)
        
        self.yscrollbar = Scrollbar(self)
        self.yscrollbar.pack(side = RIGHT, fill = Y)
        
        self.xscrollbar = Scrollbar(self)
        self.xscrollbar.pack(side = BOTTOM, fill = X)
        
        self.listbox = Listbox(self, yscrollcommand=self.yscrollbar.set, xscrollcommand=self.xscrollbar.set)
        self.listbox.pack()
        
        self.printredirector = PrintRedirector(self.listbox)
        self.printredirector.daemon = True
        self.printredirector.start()
        
        sys.stdout = self.printredirector
        
        
        
class PrintRedirector(threading.Thread):
    def __init__(self, listbox):
        super(PrintRedirector, self).__init__()
        self.queue = queue.Queue()
        self.listbox = listbox
        
        self.live = True

    def write(self, message):
        self.queue.put(message)
        
    def flush(self):
        while not self.queue.empty():
            message = self.queue.get()
            
            message = message.replace("\n", "")
            message = message.replace("\r", "")
            message = message.replace("\t", "")
            
            if message != "":
                self.listbox.insert(END, message)
                self.listbox.see(END)

    def run(self):
        while self.live:
            print("flush", file = sys.stderr)
            self.flush()
            sleep(0.1)
            
    def kill(self):
        self.live = False