import os


class MessagingService():

    def __init__(self, path):
        self.path = path
        self.make_output_folder()

    def make_output_folder(self):
        self.output_path = f"{self.path}_Analysis"
        if not os.path.exists(self.output_path):
            os.makedir(self.output_path)
