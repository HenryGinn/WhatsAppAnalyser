import os

from Messaging.messaging_service import MessagingService
from Messaging.chat_messenger import ChatMessenger


class Messenger(MessagingService):

    def __init__(self, path):
        super().__init__(path)

    def init_chats(self):
        self.chats = [
            ChatMessenger(self, chat_name)
            for chat_name in os.listdir(self.path)]

