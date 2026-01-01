import os


class MessagingService():

    def __init__(self, base_path):
        self.base_path = base_path
        self.name = os.path.split(base_path)[1]
        self.make_source_folder()
        self.make_output_folder()
        self.chats = []

    def make_source_folder(self):
        self.path = os.path.join(
            self.base_path, f"{self.name}")
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def make_output_folder(self):
        self.output_path = os.path.join(
            self.base_path, f"{self.name}__Output")
        if not os.path.exists(self.output_path):
            os.mkdir(self.output_path)
