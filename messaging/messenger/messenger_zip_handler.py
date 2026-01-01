"""
Takes in the path to a folder. This folder contains a collection of
subfolders, and inside each of those is a single zip file. This is
because when saving the data sent from Facebook the zip files may not be
named sensible, so a folder is needed to help keep track. Output is a
folder where each subfolder is an unzipped version of one of the folders
sent from Facebook.
"""

import os
import zipfile


input_path = r"/home/henry/Downloads/FacebookData"
output_path = r"/home/henry/Documents/Stuff/Data From Services/FacebookData/01_01_2004__03_06_2025"

if not os.path.exists(output_path):
    os.mkdir(output_path)

for folder_name in sorted(os.listdir(input_path))[59:]:
    folder_path = os.path.join(input_path, folder_name)
    zip_name = os.listdir(folder_path)
    if len(zip_name) != 1:
        print(f"Folder did not have single subfolder: {folder_path}")
        continue
    zip_name = zip_name[0]
    zip_path = os.path.join(folder_path, zip_name)
    unzipped_path = os.path.join(output_path, folder_name)
    print(folder_name)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(unzipped_path)
