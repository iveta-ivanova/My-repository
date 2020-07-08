# -*- coding: utf-8 -*-
"""
Created on Thu May 28 14:58:19 2020

@author: iveta

"""
import os 
import sys 

import tkinter as tk 
from tkinter import filedialog
from tkinter import messagebox

import sqlite3
from tkinter import ttk 

root = tk.Tk()       ##entire window - everything will go there 
root.title('IBS Archiver')
##root.iconbitmap('image.ico')

HEIGHT = 500 
WIDTH = 1200

canvas = tk.Canvas(root, height= HEIGHT, width = WIDTH)
canvas.pack()


## find resource path for the .exe file
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

### create a database or connect to one
conn = sqlite3.connect('FilesToArchive.db')
##create coursor instance
c = conn.cursor()

def initialize(): 
    conn = sqlite3.connect('FilesToArchive.db')
    #create table that will go inside the database 
    c = conn.cursor()
    createFiles = "CREATE TABLE IF NOT EXISTS Files (FileName text, Time_Interval integer, Destination text)"
    c.execute(createFiles)
    c.execute('SELECT Filename, Time_Interval, Destination FROM Files')
    initials = c.fetchall()
    for i in initials: 
        tree.insert("", "end", text ="", values=(i[0],i[1],i[2]))
    conn.commit()
    conn.close()


"""
Extract variables from GUI inputs

"""
def browse_dirs(): 
    global filedir      ##global to survive outside this function
    filedir.set(filedialog.askopenfilename())

## extract output dir 
def output_dirs(): 
    global outputdir
    outputdir.set(filedialog.askdirectory())

## extract time and delete intervals
def Intervals(): 
    global time_int
    time_int.set(Interval.get())

## set string variables
filedir = tk.StringVar()
outputdir = tk.StringVar()
time_int = tk.IntVar()


"""
Support Functions 
"""

## adds (creates) entries to database
def Add(): 
    ##check if everything is there 
    if not str(filedir.get()): 
        messagebox.showerror('Грешка', 'Моля, изберете файл за архивиране')
        return
    else: 
        pass 
    if not str(outputdir.get()): 
        messagebox.showerror('Грешка', 'Моля, изберете дестинация за Вашия архив')
        return
    else: 
        pass 
    if not Interval.get(): 
        messagebox.showerror('Грешка', 'Моля, изберете времеви интервал за архивиране')
        return
    conn = sqlite3.connect('FilesToArchive.db')
    c = conn.cursor()
    ## check if Filename already exists?? 
    c.execute("SELECT Filename, COUNT(*) FROM Files WHERE Filename = ? GROUP BY Filename", (str(filedir.get()),))
    exists = c.fetchone()
    if not exists:
        time_unit = OptVar.get()
        if time_unit == 'days': 
            time_int = int(Interval.get())*1440         ## how many minutes in a day? 
        else: 
            time_int = int(Interval.get())
        c.execute("INSERT INTO Files VALUES (:Filename, :Time_Interval, :Destination)",
                  {
                      'Filename': str(filedir.get()),
                      'Time_Interval': time_int,
                      'Destination': str(outputdir.get())
                      }
                  )
        conn.commit()       
        treeUpdate()
        conn.close()
        ## clear all variables used in this function
        filedir.set('')
        outputdir.set('')
        Interval.delete(first = 0,last = tk.END)
    else: 
        messagebox.showerror('Грешка','Този файл вече е избран за архивиране. Моля, избере друг файл.')
        return
    #c.close()

#### update table after every modification
def treeUpdate(): 
    tree.delete(*tree.get_children())
    c.execute('SELECT Filename, Time_Interval, Destination FROM Files')  ## table holds everything ever done? 
    records = c.fetchall()
    for i in records: 
        tree.insert("", "end", text ="", values=(i[0],i[1],i[2]))
    conn.commit()

### extract the item currently selected in the GUI tree
def selected(event):
        info = tree.item(tree.identify_row(event.y))
        global SelectedFile
        SelectedFile = info['values'][0]
        print(SelectedFile)
        global SelectedOutput
        SelectedOutput = info['values'][2]
        pass

def deleteItem():
        confirmAdd = messagebox.askquestion("Потвърждение", 
                                            "Сигурни ли сте, че искате да изтриете този файл?", icon='warning')
        if confirmAdd == 'yes': 
            global SelectedFile
            #print('pre-SelectedFile:', SelectedFile)
            conn = sqlite3.connect('FilesToArchive.db')
            c = conn.cursor()
            FileDel = SelectedFile        
            c.execute("DELETE from Files WHERE Filename = ?", (FileDel,))
            print('deleting:', FileDel)
            conn.commit()       
            treeUpdate()            
            SelectedFile = None
            #print('post-SelectedFile:', SelectedFile)
            conn.close()          
        else: 
            pass 
        
def OpenArchiveDirectory(): 
    os.startfile(SelectedOutput)

"""
Build GUI
"""
    
##does not work for now 
#background_image = ImageTk.PhotoImage(file = Image.open('image2.jpg'))
#background_label = tk.Label(root, image= background_image)
#background_label.place(relwidth=1, relheight =1)


## create a frames
TopFrame = tk.Frame(root, bg = '#1A5276', bd=5)      ##frame inside window
TopFrame.place(relx = 0.05, rely = 0.05, relwidth=0.9, relheight=0.50)

BottomFrame = tk.Frame(root, bg = '#1A5276', bd=5)      ##frame inside window
BottomFrame.place(relx = 0.05, rely = 0.60, relwidth=0.9, relheight=0.30)

### create tree to hold data
tree = ttk.Treeview(BottomFrame)
tree['columns'] = ('column1','column2', 'column3')

tree.heading("#0", text = '', anchor = "w")
tree.column("#0", width = 5, anchor = 'center', stretch = tk.NO)

tree.heading("#1", text = 'File for Archiving', anchor = "w")
#tree.column("#1", width = 80, anchor = 'w')

tree.heading("#2", text = 'Archive Interval',anchor = "w")
#tree.column("#2", width = 20, anchor = 'w')

tree.heading("#3", text = 'Archive Location',anchor = "w")
#tree.column("#4", width = 80, anchor = 'w')

tree.bind("<Button-1>", selected)

tree.pack(fill = "x")

initialize()

## Buttons for input and output 
InputBtn = tk.Button(TopFrame, text = 'File name', bg = 'white', command = browse_dirs, state = 'disabled')
InputBtn.place(relx = 0.05, rely = 0.25, relwidth = 0.1, relheight=0.35)

OutputBtn = tk.Button(TopFrame, text = 'Destination', bg = 'white', command = output_dirs, state = 'disabled')
OutputBtn.place(relx = 0.17, rely = 0.25, relwidth = 0.1, relheight=0.35)

## Archive and delete intervals - labels and entries
IntervalLbl1 = tk.Label(TopFrame, text = 'Archive Interval', bg = 'white', fg = 'black')
IntervalLbl1.place(relx = 0.05, rely = 0.65, relwidth = 0.15, relheight = 0.1 )

Options = ['minutes', 'days']

OptVar = tk.StringVar(root)
OptVar.set(Options[0]) # default value

IntervalOpt = tk.OptionMenu(TopFrame, OptVar, *Options)
IntervalOpt.place(relx = 0.30, rely = 0.65, relwidth = 0.1, relheight = 0.1 )

Interval = tk.Entry(TopFrame, bg='white')
Interval.place(relx = 0.20, rely = 0.65, relwidth = 0.1, relheight=0.1)

## Add Data
AddBtn = tk.Button(TopFrame, text = 'Add', bg = 'white', command = Add, state = 'disabled')
AddBtn.place(relx = 0.45, rely = 0.65, relwidth = 0.1, relheight=0.3)

## Delete Data
DelBtn = tk.Button(TopFrame, text = 'Delete', bg = 'white', command = deleteItem, state = 'disabled')
DelBtn.place(relx = 0.57, rely = 0.65, relwidth = 0.1, relheight=0.3)

## Open archive
OpenDirBtn = tk.Button(TopFrame, text = 'Open Archive Folder', bg = 'white', 
                       command = OpenArchiveDirectory, state = 'normal')
OpenDirBtn.place(relx = 0.70, rely = 0.65, relwidth = 0.15, relheight=0.3)

"""
Threading and Archiving 
"""
import patoolib 
import threading
from threading import Thread
import time
import shutil


### set ON/OFF buttons to turn the Archiving loop on/off, using global variable sched_var 

sched_var = True

def ArchiveOnOff():
    global sched_var
    if OnOffBtn.config('relief')[-1] == 'sunken':    ### OFF button
        OnOffBtn.config(relief = 'raised')
        sched_var = False
        AddBtn['state'] = 'normal'
        InputBtn['state'] = 'normal'
        OutputBtn['state'] = 'normal'
        DelBtn['state'] = 'normal'
    else: 
        OnOffBtn.config(relief = 'sunken')           ### ON button
        sched_var = True 
        Scheduler()
        AddBtn['state'] = 'disabled'
        InputBtn['state'] = 'disabled'
        OutputBtn['state'] = 'disabled'
        DelBtn['state'] = 'disabled'
        conn = sqlite3.connect('FilesToArchive.db')
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM Files")
        print('number of rows after ON:', c.fetchone())
        
OnOffBtn = tk.Button(text='Archive ON/OFF',relief = 'sunken', bg = 'white',command = ArchiveOnOff)
OnOffBtn.place(relx = 0.51, rely = 0.18, relwidth = 0.11, relheight=0.15)


"""
Scheduler() always ON by default, with the start of the GUI 

PROBLEM: 
    click OFF -> Delete file -> ON      ----- deleted file still being archived (forever!)
    click OFF -> wait for current thread cycle to finish (i.e. for archive to happen) -> Delete file -> ON     --- deleted file no longer archived 
    
"""


def Archiver(input_file, output_dir, archive_int):
    while True:
        global sched_var
        print('Archiver: now looking at file:', input_file)
        time.sleep(archive_int*60)                       ## time sleep is in seconds 
        input_name = os.path.basename(input_file)        ## extract name of file
        main_dir = os.path.dirname(input_file)           ## extract directory of file 
        if not os.path.exists(main_dir + '/temp'): 
                os.mkdir(main_dir + '/temp')          
        shutil.copy(input_file, os.path.join(main_dir, 'temp'))  
        tempfiledir = os.path.join(main_dir + '/temp/' + input_name)         
        archName = input_name + "_" + time.strftime("%H%M_%d%m%Y")+'.rar'     ##input name in correct format    
        outputarch = os.path.join(output_dir + '/' + archName)   ## archived file in output dir 
        patoolib._create_archive(resource_path(archName),(tempfiledir,),)
        shutil.move(resource_path(archName), outputarch)
        if sched_var == False:
            print('Archiving off, sched_var is:', sched_var)
            break 

## this function has the thread, and the thread executes the function above
            
def Scheduler():
    print('Scheduler: connecting to database...')
    filedir.set('')
    outputdir.set('')
    Interval.delete(first = 0,last = tk.END)
    conn = sqlite3.connect('FilesToArchive.db')
    c = conn.cursor()
    c.execute('SELECT Filename, Time_Interval, Destination FROM Files')  ## table holds everything ever done? 
    Files = c.fetchall()
    desc = c.description
    Columns = [col[0] for col in desc]        ##get column names 
    data = [dict(zip(Columns,row))            ##make a list of dictionaries for each row 
            for row in Files]
    for row in data:                        ##iterate through rows by accessing column(key in each row) 
        print('Scheduler: how many rows:', len(data))
        input_file = row['FileName']          
        output_dir = row['Destination']
        archive_int = row['Time_Interval']
        t = threading.Thread(target = Archiver, args = (input_file, output_dir,archive_int,)).start()
        #next_int = datetime.now() + dt.timedelta(minutes=archive_int) ##calculates next archive time for given 
            
Scheduler()

root.mainloop()











    