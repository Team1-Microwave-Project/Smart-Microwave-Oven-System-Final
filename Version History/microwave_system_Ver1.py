# MicrowaveGui.py
# Microwave GUI using tkinter


from tkinter import *   #Imports
import tkinter as tk

def button_press(num): # number button function - adds number to display
    current = display.get()
    display.delete(0, END)
    display.insert(0, str(current) + str(num))


def button_clear(): #Clear/Cancel button function - Clears display
    display.delete(0, END)


# Main GUI launch
HomeScreen = tk.Tk()
HomeScreen.configure(bg='gray76')
HomeScreen.title('Microwave Interface')
HomeScreen.geometry('450x430')
HomeScreen.resizable(width=False,height=False)


# Display screen for main interface

display = tk.Entry(master=HomeScreen,background='PaleTurquoise1', foreground='green2')
display.grid(row=0, column=0, columnspan=3, rowspan=2)
display.configure(font=('Times New Roman', 25, 'bold'), justify='center')
 

# label separating display from buttons
button_label = tk.Label(master=HomeScreen, text='Microwave Functions')
button_label.configure(bg='silver', font=('Times New Roman', 12, 'bold'), foreground='PaleTurquoise1', justify='center')
button_label.grid(row=2, column=0, columnspan=3)

# function buttons
buttonDefrost = tk.Button(master=HomeScreen, font=('Times New Roman', 10, 'bold'), text='\n\nDefrost\n\n', width=20,foreground='PaleTurquoise1', background='gray71')
buttonMultiStage = tk.Button(master=HomeScreen, font=('Times New Roman', 10, 'bold'), text=' \nMult-Stage\n  Cooking\n\n', width=20, foreground='PaleTurquoise1', background='gray71')
buttonPresets = tk.Button(master=HomeScreen, font=('Times New Roman', 10, 'bold'), text='\n\nPresets\n\n', width=20, foreground='PaleTurquoise1', background='gray71')
buttonStart = tk.Button(master=HomeScreen, font=('Times New Roman', 10, 'bold'), text="\n\n \nStart\n \n\n", width=20, foreground='PaleTurquoise1', background='gray71')
buttonCancel = tk.Button(master=HomeScreen, font=('Times New Roman', 10, 'bold'), text="\n\nCLEAR\n/\nCANCEL\n\n", command=button_clear, width=20, foreground='PaleTurquoise1', background='gray71')

# Function buttion orientain
buttonDefrost.grid(row=3, column=0)
buttonMultiStage.grid(row=3, column=1)
buttonPresets.grid(row=3, column=2)
buttonStart.grid(row=7, column=2)
buttonCancel.grid(row=7, column=0)

# number buttons(0-9)
button1 = tk.Button(master=HomeScreen, font=('Times New Roman', 10, 'bold'), text='\n1\n', command=lambda: button_press(1), width=20, foreground='PaleTurquoise1', background='gray71')
button2 = tk.Button(master=HomeScreen, font=('Times New Roman', 10, 'bold'), text='\n2\n', command=lambda: button_press(2), width=20, foreground='PaleTurquoise1', background='gray71')
button3 = tk.Button(master=HomeScreen, font=('Times New Roman', 10, 'bold'), text='\n3\n', command=lambda: button_press(3), width=20, foreground='PaleTurquoise1', background='gray71')
button4 = tk.Button(master=HomeScreen, font=('Times New Roman', 10, 'bold'), text='\n4\n', command=lambda: button_press(4), width=20, foreground='PaleTurquoise1', background='gray71')
button5 = tk.Button(master=HomeScreen, font=('Times New Roman', 10, 'bold'), text='\n5\n', command=lambda: button_press(5), width=20, foreground='PaleTurquoise1', background='gray71')
button6 = tk.Button(master=HomeScreen, font=('Times New Roman', 10, 'bold'), text='\n6\n', command=lambda: button_press(6), width=20, foreground='PaleTurquoise1', background='gray71')
button7 = tk.Button(master=HomeScreen, font=('Times New Roman', 10, 'bold'), text='\n7\n', command=lambda: button_press(7), width=20, foreground='PaleTurquoise1', background='gray71')
button8 = tk.Button(master=HomeScreen, font=('Times New Roman', 10, 'bold'), text='\n8\n',command=lambda: button_press(8), width=20, foreground='PaleTurquoise1', background='gray71')
button9 = tk.Button(master=HomeScreen, font=('Times New Roman', 10, 'bold'), text='\n9\n',command=lambda: button_press(9), width=20, foreground='PaleTurquoise1', background='gray71')
button0 = tk.Button(master=HomeScreen, font=('Times New Roman', 10, 'bold'), text='\n\n \n0\n \n\n', command=lambda: button_press(0), width=20, foreground='PaleTurquoise1', background='gray71')

# Number button orientation
button1.grid(row=4, column=0)
button2.grid(row=4, column=1)
button3.grid(row=4, column=2)
button4.grid(row=5, column=0)
button5.grid(row=5, column=1)
button6.grid(row=5, column=2)
button7.grid(row=6, column=0)
button8.grid(row=6, column=1)
button9.grid(row=6, column=2)
button0.grid(row=7, column=1)

##   Run application loop
HomeScreen.mainloop()



