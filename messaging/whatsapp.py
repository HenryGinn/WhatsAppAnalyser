from os.path import join

from Services.chat_service import ChatService
from Elements.whatsapp_chat import WhatsappChat


class WhatsApp(ChatService):

    def initialise_chat(self, name):
        chat_obj = WhatsappChat(self, name)
        self.chat_objects.append(chat_obj)

    def get_path_chat(self, name):
        path = join(self.path_base, name)
        return path


