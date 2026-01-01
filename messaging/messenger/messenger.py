from collections import defaultdict
import json
import os
import re
import unicodedata

from messaging.messaging_service import MessagingService
from messaging.messenger.chat_messenger import ChatMessenger


class Messenger(MessagingService):

    def __init__(self, path):
        super().__init__(path)
        self.raw_path = os.path.join(
            self.base_path, f"{self.name}__Raw")

    def init_chats(self):
        self.chats = [
            ChatMessenger(self, chat_name)
            for chat_name in os.listdir(self.path)]


    # Facebook sends the data split across multiple zip files, and
    # within that one of these folders, a chat can be split up further
    # still. This method does the following:

    # - Collect all the photos, videos, files, and audio for a single
    # chat into one place.
    # - Collect all the json files for a single chat into a single json.
    # - Rename media to be the datetime that they were sent (in both the
    # file name and the json file).

    def preprocess(self):
        self.set_unzipped_paths()
        self.set_chat_type_paths()
        self.set_chat_raw_paths()
        self.preprocess_chat()

    def set_unzipped_paths(self):
        self.unzipped_paths = sorted([
            os.path.join(
                self.raw_path,
                folder_name,
                "your_facebook_activity",
                "messages")
            for folder_name in os.listdir(self.raw_path)])

    def set_chat_type_paths(self):
        self.init_chat_type_paths()
        self.chat_type_paths_filter_existence()

    def init_chat_type_paths(self):
        self.chat_type_paths = [
            os.path.join(message_folder_path, chat_type_name)
            for chat_type_name in chat_type_names
            for message_folder_path in self.unzipped_paths]

    def chat_type_paths_filter_existence(self):
        self.chat_type_paths = [
            path for path in self.chat_type_paths
            if os.path.isdir(path)]

    def set_chat_raw_paths(self):
        self.chat_raw_paths = defaultdict(list)
        for chat_type_path in self.chat_type_paths:
            for chat_folder in os.listdir(chat_type_path):
                self.add_chat_raw_path(chat_type_path, chat_folder)

    def add_chat_raw_path(self, chat_type_path, chat_folder):
        chat_raw_path = os.path.join(chat_type_path, chat_folder)
        self.chat_raw_paths[chat_folder].append(chat_raw_path)


    # In order to make the chat folder, we need to know what its name.
    # To find the name of a chat, we need the 'title' key from the json.
    # The json files are often split into multiple parts. To read the
    # title we first need to combine all the json files. This is why
    # combining and saving the json files is done in the same step. The
    # chat objects are not created at this stage as I only want one
    # "init_chats" method and this should work by looking at the chat
    # folder names which are not yet created at this stage.
    
    def preprocess_chat(self):
        self.previous_chat_names = [""]
        for chat_name, chat_paths in self.chat_raw_paths.items():
            self.collate_json(chat_name, chat_paths)
            chat_name = self.get_chat_name()
            chat_path = self.get_chat_path(chat_name)
            self.save_collated_json(chat_path)
            self.chat = ChatMessenger(self, chat_name)
            self.chats.append(self.chat)
            self.chat.collate_content(chat_paths)

    def collate_json(self, chat_name, chat_paths):
        json_paths = self.get_json_paths(chat_name, chat_paths)
        self.init_json(json_paths[0])
        for path in json_paths[1:]:
            self.append_to_json(path)

    def get_json_paths(self, chat_name, chat_paths):
        json_paths = sorted(
            [os.path.join(chat_path, file_name)
             for chat_path in chat_paths
             for file_name in os.listdir(chat_path)
             if os.path.splitext(file_name)[1] == ".json"],
            key=lambda x: int(x[-10:].strip("message_.json")))
        return json_paths

    def init_json(self, json_path):
        self.collated_json = self.load_json(json_path)

    def append_to_json(self, json_path):
        content = self.load_json(json_path)
        self.collated_json["messages"].append(
            content["messages"])

    # I do not know why decoding as latin-1 does not work, so I use this
    # nasty hack job instead.
    
    def load_json(self, json_path):
        with open(json_path, "r", encoding="utf-8") as file:
            raw = file.read()
        content = json.loads(raw)
        content = self.fix_unicode(content)
        return content

    def fix_unicode(self, obj):
        if isinstance(obj, str):
            return obj.encode("latin-1").decode("utf-8")
        if isinstance(obj, list):
            return [self.fix_unicode(i) for i in obj]
        if isinstance(obj, dict):
            return {key: self.fix_unicode(value)
                    for key, value in obj.items()}
        return obj

    def get_chat_path(self, chat_name):
        folder_path = os.path.join(self.path, chat_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        chat_path = os.path.join(folder_path, "Messages.json")
        return chat_path

    def get_chat_name(self):
        chat_name = self.collated_json["title"]
        chat_name = (
            unicodedata
            .normalize('NFKD', chat_name)
            .encode('ascii', 'ignore')
            .decode('ascii'))
        chat_name = re.sub(r"\?|\.|\!|\/|\;|\:", "", chat_name)
        while chat_name in self.previous_chat_names:
            chat_name = f"{chat_name}_"
        self.previous_chat_names.append(chat_name)
        return chat_name

    def save_collated_json(self, chat_path):
        with open(chat_path, "w+", encoding="utf-8") as file:
            json.dump(
                self.collated_json, file,
                indent=2, ensure_ascii=False)

    def rename_media(self):
        for chat in self.chats:
            chat.rename_media()

chat_type_names = [
    "archived_threads",
    "e2ee_cutover",
    "inbox"]
