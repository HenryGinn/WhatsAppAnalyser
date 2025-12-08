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
        self.set_messages_path()

    def set_messages_path(self):
        self.messages_path = os.path.join(
            self.path, "Messages.json")

    def load_chat(self):
        with open(self.messages_path) as file:
            self.chat = json.load(file)

    def set_messages(self):
        self.init_messages_from_source()
        self.messages.rename(columns=self.rename_dict, inplace=True)
        self.messages = self.messages.astype(self.conversion_dict)
        self.set_photos()
        self.messages = self.messages.loc[self.messages["Message"] != ""]
        self.messages.drop(columns=["photos", "reactions"], inplace=True)

    def init_messages_from_source(self):
        self.messages = pd.DataFrame([
            self.get_parsed_message(ID, message)
            for ID, message in enumerate(self.chat["messages"][:10])])

    def get_parsed_message(self, ID, message):
        parsed_message = {"ID": ID} | {
            key: value
            for key, value in message.items()}
        return parsed_message

    def set_photos(self):
        self.photos = (
            self.messages
            .dropna(subset="photos")
            .drop(columns=["Message", "reactions"])
            .explode("photos"))
        self.photos["photos"] = (
            self.photos["photos"]
            .apply(lambda x: x["uri"].split("/")[-1]))
        
