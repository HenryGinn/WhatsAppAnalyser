from Messaging.messenger import Messenger

path = r"/home/henry/Documents/Stuff/Data From Services/FacebookData/01_01_2004__03_06_2025"

messenger = Messenger(path)
messenger.init_chats()

for chat in messenger.chats:
    print(chat.name)
    chat.load_chat()
    chat.set_posts()
    chat.set_summary()
    chat.output_summary_text()
    chat.output_summary_plot()
    chat.set_activity_day()
    chat.plot_activity_day()
