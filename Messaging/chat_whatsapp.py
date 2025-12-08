from Elements.chat import Chat
from Processing.preprocess_whatsapp import PreprocessWhatsapp


class WhatsappChat(Chat, PreprocessWhatsapp):

    def __init__(self, service, name):
        super().__init__(service, name)
