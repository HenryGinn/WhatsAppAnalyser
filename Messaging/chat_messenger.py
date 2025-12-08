import os
import json

import numpy as np
import pandas as pd

from Messaging.chat import Chat


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
        self.set_posts_path()

    def set_posts_path(self):
        self.posts_path = os.path.join(
            self.path, "Messages.json")

    def load_chat(self):
        with open(self.posts_path) as file:
            self.chat = json.load(file)

    def set_posts(self):
        self.init_posts_from_source()
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
        self.photos["photos"] = (
            self.photos["photos"]
            .apply(lambda x: x["uri"].split("/")[-1]))
    
    def set_photos_empty(self):
        columns = list(self.rename_dict.values()) + ["photos"]
        self.photos = pd.DataFrame(columns=columns)
