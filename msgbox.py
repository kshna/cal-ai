import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.withdraw()

def getConfirmation():
    
    response = messagebox.askyesno("Confirmation","Do you want to proceed?")

    return response
