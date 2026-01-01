"""
Goes through every photo send across every chat and puts it in one
folder, labelled by timestamp and date. Used to find images
chronologically.
"""


import os
import json
import datetime
import shutil


input_path = "/home/henry/Documents/Stuff/Data From Services/FacebookData/01_01_2004__03_06_2025"
output_path = "/home/henry/Documents/Stuff/Data From Services/FacebookData/01_01_2004__03_06_2025__Photos"

if not os.path.exists(output_path):
    os.mkdir(output_path)

for year in range(2012, 2026):
    path = os.path.join(output_path, str(year))
    if not os.path.exists(path):
        os.mkdir(path)

for folder_name in sorted(os.listdir(input_path)):
    print(folder_name)
    folder_path = os.path.join(input_path, folder_name)
    json_path = os.path.join(folder_path, "Messages.json")
    photos_path = os.path.join(folder_path, "Photos")
    with open(json_path, "r") as file:
        content = json.load(file)
    content = content["messages"]
    content = [message for message in content if "photos" in message]
    photos = [{"Timestamp": message["timestamp_ms"],
               "Name": photo["uri"].split("/")[-1]}
              for message in content for photo in message["photos"]
              if photo["uri"] != "" and not photo["uri"].startswith("http")]
    for photo in photos:
        timestamp = photo["Timestamp"]
        date = datetime.datetime.fromtimestamp(round(timestamp/1000))
        year = date.strftime("%Y")
        time_label = date.strftime("%Y_%m_%d__%H_%M_%S")
        extension = os.path.splitext(photo["Name"])[1]
        name = f"{timestamp} {time_label}.{extension}"
        source_path = os.path.join(photos_path, photo["Name"])
        save_path = os.path.join(output_path, year, name)
        if os.path.exists(source_path):
            shutil.copy(source_path, save_path)
