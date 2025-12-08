from re import search, sub
from os import rename
from os.path import isfile

import pandas as pd

from Processing.base import Base


class PreprocessWhatsapp(Base):

    def preprocess(self):
        if self.force or not isfile(self.path_chat):
            self.update_chat_name()
            self.preprocess_original_chat_file()


    # Ensuring the folder name is correct

    def update_chat_name(self):
        if "WhatsApp Chat - " in self.name:
            self.set_new_name()
            self.update_folder_name()
            self.update_chat_objects()
        self.set_paths()

    def set_new_name(self):
        self.old_name = self.name
        self.name = self.old_name[16:]

    def update_folder_name(self):
        old_path = self.service.get_path_chat(self.old_name)
        new_path = self.service.get_path_chat(self.name)
        rename(old_path, new_path)

    def update_chat_objects(self):
        self.service.chat_objects[self.name] = (
            self.service.chat_objects.pop(self.old_name))


    # Parsing the original chat file and saving dataframe

    def preprocess_original_chat_file(self):
        self.extract_data_from_original_chat_file()
        self.create_chat_dict()
        self.construct_dataframe()
        self.save_dataframe()

    def create_chat_dict(self):
        self.initialise_chat_dict()
        self.populate_chat_dict()

    def construct_dataframe(self):
        self.create_dataframe()
        self.remove_messages_from_whatsapp()

    def extract_data_from_original_chat_file(self):
        pattern = r'[\u200e\u200f\u202a\u202b\u202c\u202d\u202e\n\r]'
        with open(self.path_chat_original, "r") as file:
            self.data = [sub(pattern, '', line)
                         for line in file]

    def initialise_chat_dict(self):
        self.chat_dict = {"Timestamp": [],
                          "Sender": [],
                          "Content": [],
                          "Photo": []}

    def populate_chat_dict(self):
        message = [self.data[0]]
        for line in self.data:
            if self.message_start(line):
                self.process_message(message)
                message = [line]
            else:
                message.append(line)

    def message_start(self, line):
        pattern = r"\[\d{2}/\d{2}/\d{4}, \d{2}:\d{2}:\d{2}\]"
        starts_with_timestamp = bool(search(pattern, line[:22]))
        return starts_with_timestamp

    def contains_photo(self, line):
        pattern = (r"<attached: \d{8}-(GIF|PHOTO)-\d{4}-\d{2}"
                   r"-\d{2}-\d{2}-\d{2}-\d{2}\.(mp4|jpg)>")
        photo = bool(search(pattern, line)) or (line == "image omitted")
        return photo

    def process_message(self, message):
        timestamp, name, message = self.process_first_line(message)
        photo = self.contains_photo(message[0])
        message = "\t".join(message)
        self.update_chat_dict(timestamp, name, message, photo)

    def process_first_line(self, message):
        timestamp = message[0][:22]
        colon_index = message[0][22:].index(":") + 22
        name = message[0][23:colon_index]
        message[0] = message[0][colon_index+2:]
        return timestamp, name, message

    def update_chat_dict(self, timestamp, name, message, photo):
        self.chat_dict["Timestamp"].append(timestamp)
        self.chat_dict["Sender"].append(name)
        self.chat_dict["Photo"].append(photo)
        self.chat_dict["Content"].append(message)

    def create_dataframe(self):
        data_types = {"Sender": "category", "Photo": "bool", "Content": "object"}
        self.df = pd.DataFrame(self.chat_dict).astype(data_types)
        self.df["Timestamp"] = pd.to_datetime(
            self.df["Timestamp"], format="[%d/%m/%Y, %H:%M:%S]")
        self.df = self.df.set_index("Timestamp").reindex(columns=data_types.keys())

    def remove_messages_from_whatsapp(self):
        self.df = self.df.loc[self.df["Sender"] != self.name]

    def save_dataframe(self):
        self.df.to_pickle(self.path_chat)

    def read(self):
        self.df = pd.read_pickle(self.path_chat)
