"""
- Photos and stickers not associated with a chat are ignored
- Archived threads, e2ee cutover, and inbox are merged into one
"""


import os
import shutil
from unicodedata import normalize

from hgutilities.utils import json


input_path = "/home/henry/Documents/Stuff/Data From Services/FacebookData/01_01_2004__29_12_2025/01_01_2004__29_12_2025__Raw"
output_path = "/home/henry/Documents/Stuff/Data From Services/FacebookData/01_01_2004__29_12_2025/01_01_2004__29_12_2025"

if os.path.exists(output_path):
    shutil.rmtree(output_path)
os.mkdir(output_path)


# Getting a list of paths where chats could be

message_folder_paths = sorted([
    os.path.join(input_path, folder_name, "your_facebook_activity", "messages")
    for folder_name in os.listdir(input_path)])
chat_type_names = [
    "archived_threads", "e2ee_cutover", "inbox"]
chat_type_folder_paths = [
    os.path.join(message_folder_path, chat_type_name)
    for chat_type_name in chat_type_names
    for message_folder_path in message_folder_paths]
chat_type_folder_paths = [
    path for path in chat_type_folder_paths
    if os.path.isdir(path)]


# Getting a dictionary of all paths to chats
# Keys are chat names, values are lists of all paths

def get_chat_folder_short(chat_folder):
    if "_" in chat_folder:
        index = -chat_folder[::-1].index("_") - 1
        chat_folder_short = chat_folder[:index]
    else:
        chat_folder_short = chat_folder
    return chat_folder_short


# Creating a new folder with everything merged

def get_output_path_chat(content):
    chat_name = content["title"].replace("/", "").replace("\\", "").replace(".", "")
    chat_name = chat_name.encode('ascii', errors='ignore').decode("ascii").strip()
    if chat_name == "":
        chat_name = "_"
    while os.path.isdir(os.path.join(output_path, chat_name)):
        chat_name = chat_name + "_"
    output_path_chat = os.path.join(output_path, chat_name)
    os.mkdir(output_path_chat)
    return output_path_chat

def get_json_paths(paths):
    json_paths = sorted([
        os.path.join(path, item)
        for path in paths
        for item in os.listdir(path)
        if item[:8] == "message_"])
    return json_paths

def collect_json_content(paths):
    json_paths = get_json_paths(paths)
    if len(json_paths) > 0:
        with open(json_paths[0], "r") as file:
            contents = json.load(file)
        for json_path in json_paths[1:]:
            with open(json_path, "r") as file:
                extra_contents = json.load(file)
            contents["messages"] += extra_contents["messages"]
        contents.pop("thread_path", None)
    return contents

def get_collection_paths(paths, collection_name):
    collection_paths = [os.path.join(path, collection_name)
                        for path in paths]
    collection_paths = [path for path in collection_paths
                        if os.path.exists(path)]
    return collection_paths

def collect_files(output_path_chat, paths, collection_name):
    output_path_collection = os.path.join(output_path_chat,
        f"{collection_name[0].upper()}{collection_name[1:]}")
    if not os.path.exists(output_path_collection):
        os.mkdir(output_path_collection)
    collection_paths = get_collection_paths(paths, collection_name)
    for collection_path in collection_paths:
        for item in os.listdir(collection_path):
            item_path = os.path.join(collection_path, item)
            destination_path = os.path.join(output_path_collection, item)
            shutil.copy(item_path, destination_path)


chat_folder_paths = {}
for chat_type_folder_path in chat_type_folder_paths:
    for chat_folder in os.listdir(chat_type_folder_path):
        chat_folder_short = get_chat_folder_short(chat_folder)
        if chat_folder_short not in chat_folder_paths:
            chat_folder_paths.update({chat_folder_short: []})
        chat_folder_paths[chat_folder_short].append(
            os.path.join(chat_type_folder_path, chat_folder))


for chat, paths in chat_folder_paths.items():
    if len(chat) > 0 and len(paths) > 0:
        contents = collect_json_content(paths)
        output_path_chat = get_output_path_chat(contents)
        print(os.path.split(output_path_chat)[1])
        json_output_path = os.path.join(output_path_chat, "Messages.json")
        with open(json_output_path, "w+") as file:
            json.dump(contents, file)
        collect_files(output_path_chat, paths, "photos")
        collect_files(output_path_chat, paths, "videos")
        collect_files(output_path_chat, paths, "gifs")
        collect_files(output_path_chat, paths, "files")
        collect_files(output_path_chat, paths, "audio")
    else:
        print(chat, paths)
