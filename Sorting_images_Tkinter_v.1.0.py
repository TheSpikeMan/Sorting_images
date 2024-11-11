# -*- coding: utf-8 -*-
"""
Created on Sat Jul  2 14:50:45 2022

@author: grzeg
"""

import os
from pathlib import Path
import re
import shutil
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import scrolledtext



def find_image_video_files(path, pathLOGS):
    """
    
    Function searches for .jpg and .mp4 files in specific path folder.
    For now it considers only files, not subdirectories.

    Parameters
    ----------
    path : type STRING, path to look for image and video files
    pathLOGS: type STRING, path to save logs files

    Returns
    -------
    files_list: type LIST, list of .jpg and .mp4 files in 'path' folder
    date_part: type LIST, list of all year-months combinations
    
    """
    files_list = []
    non_matches_list = []
    date_part = []
    path = Path(path)
    for index, file in enumerate(path.iterdir()):
        pattern = r'.*(?P<year>20[12]\d)(?P<month>[01]\d)(?P<day>[0123]\d).*'
        if file.suffix == '.jpg' or file.suffix == '.mp4' or \
                                    file.suffix == '.jpeg':
            matchObj = re.match(pattern= pattern, string = file.stem)
            if matchObj:
                date_part.append(matchObj.group('year') + '-' + \
                                 matchObj.group('month'))   
                files_list.append(file.name)
            else:
                non_matches_list.append(file.name)
                continue
    date_part = list(set(date_part))
    return files_list, date_part


def creating_folders_for_pictures(path, date_part):
    """
    Function creates folders in specific location and gives them names 
    according to dates of pictures found
    
    Parameters
    ----------
    path : type STRING, path to save pictures
    date_part : type LIST, list of dates of pictures

    Returns
    -------
    Information about folder creating
    
    """
    folder_counter = [0, 0]
    for date in date_part:
        try:
            path_to_folder = os.path.join(path, date.split("-")[0])
            os.mkdir(path_to_folder)
            folder_counter[0] += 1
        except FileExistsError:
            continue
    for date in date_part:
        try:
            path_to_folder = os.path.join(path, date.split("-")[0], 
                                          date.split("-")[1])
            os.mkdir(path_to_folder)
            folder_counter[1] += 1
        except FileExistsError:
            continue

    if folder_counter[0] & folder_counter[1] == 0:
        return "5 of 7: No folders need to be created.\n"
    else:
        return f"5 of 7: Created {folder_counter[0]} folders and {folder_counter[1]} subfolders.\n"
    
    
def search_for_copies(path, files_list):
    
    """
    
    This function takes as a parameter 
    
    Parameters
    ----------
    path : type STRING, absolute path to search location and 
    files_list : type LIST, list of files to check from, with suffixes'.

    Returns
    -------
    list_of_copies: type LIST
    copy_flag: indicator 
    info1, info2: information file

    """
    
    copy_flag = 1
    list_of_copies = []
    for picture in files_list:
        for roots, dirs, files in os.walk(path):
            for file in files:
                if file == picture:
                    list_of_copies.append(file)
            
    info1 = f'Total number of checked files checked is {len(files_list)}.'
    f' Among pictures from location "{path}" number of repetition is '
    f'{len(list_of_copies)}. '
    info2 = "\n"
    
    if len(list_of_copies) == len(files_list):
        info2 = "Copying is not recommended. All the files in destination folder.\n"
        copy_flag = 0
        
    return list_of_copies, copy_flag, info1, info2


def copying_files(pathFROM, pathTO, list_of_copies, files_list):
    """
    Copying files to new locations

    Parameters
    ----------
    pathFROM : type STRING, path to files
    pathTO: type STRING, destination for copying
    list_of_copies: type LIST, list of copies in destination fodler
    files_list : type LIST, list of files to copy

    Returns
    -------
    info3, info4: information files.

    """
    info3 = "6.5 of 7: Starting to copy files. Please wait (...)\n"
    copy_counter = 0
    for file in files_list:
        if file not in list_of_copies:
            pattern = r'.*(?P<year>20[12]\d)(?P<month>[01]\d)(?P<day>[0123]\d).*'
            matchObj = re.match(pattern= pattern, string = file.split(".")[0])
            try:
                destination = pathTO + "\\" + matchObj.group("year") + \
                                        "\\"+ matchObj.group("month") 
                source = pathFROM + "\\" + file
                shutil.copy2(source , destination)
                copy_counter += 1
            except FileExistsError:
                continue
    info4 = f'Copying completed. {copy_counter} files have been copied\n'
    return info3, info4


def Browse1():
    textBoxPath1.delete(0, "end")
    pathFROM = filedialog.askdirectory()
    textBoxPath1.insert(0, pathFROM)


def Browse2():
    textBoxPath2.delete(0, "end")
    pathTO = filedialog.askdirectory()
    textBoxPath2.insert(0, pathTO)


def Browse3():
    textBoxPath3.delete(0, "end")
    pathLOGS = filedialog.askdirectory()
    textBoxPath3.insert(0, pathLOGS)
    
    
def BlockBrowse():
    [buttonPath.configure(state='disabled') for buttonPath in buttonPaths]
    [textBoxPath.configure(state='disabled') for textBoxPath in textBoxPaths]
    
    
def EditBrowse():
    [buttonPath.configure(state='enabled') for buttonPath in buttonPaths]
    [textBoxPath.configure(state='enabled') for textBoxPath in textBoxPaths]
    
    
def ClearFields():
    [buttonPath.configure(state='enabled') for buttonPath in buttonPaths]
    [textBoxPath.configure(state='enabled') for textBoxPath in textBoxPaths]
    textBoxPath1.delete(0, "end")
    textBoxPath2.delete(0, "end")
    textBoxPath3.delete(0, "end")
    
    
def Sort():
    files_list, date_part =  find_image_video_files(pathFROM.get(), 
                                                    pathLOGS.get())
    scrolledBoxResults.insert(tk.INSERT, 
            """1 of 7: Starting the app!
2 of 7: Exploring the data for .jpg/.jpeg/.mp4 files.
3 of 7: Exporting the logs to excel files.
4 of 7: Creating folders.\n""")
    resultText = creating_folders_for_pictures(pathTO.get(), date_part)
    scrolledBoxResults.insert(tk.INSERT, resultText)
    scrolledBoxResults.insert(tk.INSERT, 
            '6 of 7: Checking the copies in destination folder.\n')
    
    list_of_copies, copy_flag, info1, info2 = search_for_copies(pathTO.get(), 
                                                            files_list)
    scrolledBoxResults.insert(tk.INSERT, info1)
    scrolledBoxResults.insert(tk.INSERT, info2)
    
    if copy_flag:
        # copying files
        info3, info4 = copying_files(pathFROM.get(), pathTO.get(), \
                                         list_of_copies, files_list)
        scrolledBoxResults.insert(tk.INSERT, info3)
        scrolledBoxResults.insert(tk.INSERT, info4)
    scrolledBoxResults.insert(tk.INSERT, "7 of 7: Closing the app.")
       
# END of functions  
    
win = tk.Tk()
win.title("Sort your pictures and videos!")
win.geometry("1200x400")

pathFROM = tk.StringVar()
pathTO = tk.StringVar()
pathLOGS = tk.StringVar()
checkVar1 = tk.IntVar()
checkVar2 = tk.IntVar()

scrolW = 100
scrolH = 7

pathLabel1 = ttk.Label(win, text="1. Select input path to images and "
                       "videos to sort.")
pathLabel2 = ttk.Label(win, text="2. Select output path for pictures and "
                       "images.")
pathLabel3 = ttk.Label(win, text="3. Select output path for logs to generate.")
buttonPath1 = ttk.Button(win, text="Browse...", command = Browse1)
buttonPath2 = ttk.Button(win, text="Browse...", command = Browse2)
buttonPath3 = ttk.Button(win, text="Browse...", command = Browse3)
textBoxPath1 = ttk.Entry(win, width=70, textvariable = pathFROM)
textBoxPath2 = ttk.Entry(win, width=70, textvariable = pathTO)
textBoxPath3 = ttk.Entry(win, width=70, textvariable = pathLOGS)
scrolledBoxResults = scrolledtext.ScrolledText(win, width=scrolW, 
                    height=scrolH, wrap= tk.WORD) 
buttonSet = ttk.Button(win, text="Confirm all paths.", command = BlockBrowse)
buttonEdit = ttk.Button(win, text="Edit paths", command = EditBrowse)
buttonClear = ttk.Button(win, text="Clear all fields.", command= ClearFields)
buttonSort = ttk.Button(win, text="Sort", command = Sort)
checkBoxLogs1 = ttk.Checkbutton(win, text="Generate logs to .xlsx",
                                variable=checkVar1)
checkBoxLogs2 = ttk.Checkbutton(win, text="Generate logs to .txt",
                                variable=checkVar2)

buttonPaths = [buttonPath1, buttonPath2, buttonPath3]
textBoxPaths = [textBoxPath1, textBoxPath2, textBoxPath3]

pathLabel1.grid(row=0, column=0, sticky=tk.W, pady=5, padx=10)
pathLabel2.grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)
pathLabel3.grid(row=2, column=0, sticky=tk.W, pady=5, padx=10)
buttonPath1.grid(row=0, column=1)
buttonPath2.grid(row=1, column=1)
buttonPath3.grid(row=2, column=1)
textBoxPath1.grid(row=0, column=2, sticky = tk.W)
textBoxPath2.grid(row=1, column=2, sticky = tk.W)
textBoxPath3.grid(row=2, column=2, sticky = tk.W)
scrolledBoxResults.grid(row=5, column=0, columnspan=3, sticky= tk.W, padx=10)

buttonSet.grid(row=3, column=0, pady=10)
buttonEdit.grid(row=3, column=1)
buttonClear.grid(row=3, column=2)
buttonSort.grid(row=5, column=3)
checkBoxLogs1.grid(row=4, column=0, pady=15)
checkBoxLogs2.grid(row=4, column=1, pady=15)

win.mainloop()