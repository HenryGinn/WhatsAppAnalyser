from datetime import datetime
import json
import os
import shutil

import numpy as np
import pandas as pd

from messaging.chat import Chat


class ChatMessenger(Chat):

    rename_dict = {
        "ID": "ID",
        "sender_name": "Sender",
        "timestamp_ms": "Timestamp",
        "content": "Message",
        "is_geoblocked_for_viewer": "Geoblocked",
        "is_unsent_image_by_messenger_kid_parent": "Unsent"}

    def __init__(self, service, name):
        super().__init__(service, name)
        self.set_paths()

    def set_paths(self):
        self.posts_path = os.path.join(self.path, "Messages.json")
        self.media_paths = {
            media_type: os.path.join(self.path, media_name)
            for media_type, media_name in media_names.items()}

    def collate_content(self, chat_paths_raw):
        self.chat_paths_raw = chat_paths_raw
        self.make_subfolders()
        for media_type, media_path in self.media_paths.items():
            self.collate_content_type(media_type, media_path)
        print(self.name)

    def collate_content_type(self, content_type, output_path):
        folder_paths = self.get_content_type_paths(content_type)
        for folder_path in folder_paths:
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                target_path = os.path.join(output_path, file_name)
                if not os.path.exists(target_path):
                    shutil.copy(file_path, target_path)

    def get_content_type_paths(self, content_type):
        paths = [
            os.path.join(chat_path, folder_name)
            for chat_path in self.chat_paths_raw
            for folder_name in os.listdir(chat_path)
            if folder_name == content_type]
        return paths

    def make_subfolders(self):
        for path in self.media_paths.values():
            if not os.path.exists(path):
                os.makedirs(path)

    def rename_media(self):
        self.load_chat()
        for message in self.chat["messages"]:
            for media_type, media_path in self.media_paths.items():
                if media_type in message:
                    message[media_type] = [
                        self.rename_media_item(media, media_path, message["timestamp_ms"])
                        for media in message[media_type]]
                    message[media_type] = [
                        item for item in message[media_type]
                        if item is not None]
        self.save_posts()

    def save_posts(self):
        with open(self.posts_path, "w") as file:
            json.dump(self.chat, file, indent=2)

    def rename_media_item(self, media, media_path, timestamp):
        new_name = media
        if isinstance(media, dict):
            if media["uri"] != "":
                uri = os.path.split(media["uri"])[-1]
                if len(uri) < 21:
                    timestamp = datetime.utcfromtimestamp(timestamp/1000).strftime("%Y_%m_%d__%H_%M_%S")
                    new_name = f"{timestamp} {uri}"
                    old_path = os.path.join(media_path, uri)
                    new_path = os.path.join(media_path, new_name)
                    if os.path.exists(old_path):
                        os.rename(old_path, new_path)
                    else:
                        self.copy_media(uri, media_path, new_path)
                else:
                    return None
            else:
                return None
        return new_name

    # If an image has been sent twice then it will have only been saved
    # one time. It will already have been renamed and marked with a
    # timestamp so we need to find it and copy it with the new name.
    
    def copy_media(self, uri, media_path, new_path):
        for item in os.listdir(media_path):
            if uri in item:
                old_path = os.path.join(media_path, item)
                while os.path.exists(new_path):
                    new_path = f"{os.path.splitext(new_path)[0]}_{os.path.splitext(new_path)[1]}"
                shutil.copy(old_path, new_path)

    def load_chat(self):
        with open(self.posts_path, "r") as file:
            self.chat = json.load(file)

    def set_posts(self):
        self.init_posts_from_source()
        self.add_missing_columns()
        self.posts.rename(columns=self.rename_dict, inplace=True)
        self.posts = self.posts.astype(self.conversion_dict)
        self.set_photos()
        self.messages = self.posts.loc[self.posts["Message"] != ""]
        self.messages = self.messages.drop(
            columns=["photos", "reactions"], errors="ignore")

    def init_posts_from_source(self):
        self.posts = pd.DataFrame([
            self.get_parsed_posts(ID, post)
            for ID, post in enumerate(self.chat["messages"])])

    def get_parsed_posts(self, ID, post):
        parsed_posts = {"ID": ID} | {
            key: value
            for key, value in post.items()}
        return parsed_posts

    def add_missing_columns(self):
        for column in self.rename_dict:
            if column not in self.posts:
                self.posts[column] = pd.Series()

    def set_photos(self):
        if "photos" in self.posts.columns:
            self.set_photos_non_empty()
        else:
            self.set_photos_empty()

    def set_photos_non_empty(self):
        self.photos = (
            self.posts
            .dropna(subset="photos")
            .drop(columns=["Message", "reactions"], errors="ignore")
            .explode("photos"))
        #self.photos["photos"] = (
        #    self.photos["photos"]
        #    .apply(lambda x: x["uri"].split("/")[-1]))
    
    def set_photos_empty(self):
        columns = list(self.rename_dict.values()) + ["photos"]
        self.photos = pd.DataFrame(columns=columns)

media_names = {
    "photos": "Photos",
    "videos": "Videos",
    "files": "Files",
    "gifs": "Gifs",
    "audio_files": "Audio"}
