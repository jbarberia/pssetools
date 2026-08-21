# Parche para entornos embebidos de PSSE donde sys.argv no existe
import sys
if not hasattr(sys, 'argv'):
    sys.argv = ['']

try:
    import tkinter as tk    
except ImportError:
    import Tkinter as tk

import programs
from main import PSSEAutomationApp

def gui():
    root = tk.Tk()
    app = PSSEAutomationApp(root)
    root.mainloop()

if __name__ == "__main__":
    gui()
