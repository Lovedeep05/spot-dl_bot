import os
import requests
from glob import glob

import telegram
from telegram.ext import CommandHandler, MessageHandler, filters, Application
from tinytag import TinyTag


API_TOKEN = "5928684050:AAEimzVTH6erRxFM7zbBhW5Fk2CLNlaeYhI"


def run(link):
    print(link)
    os.system(f"spotdl {link}")


async def start(update, context):
    await update.message.reply_text("send song name or spotify link")
    chat_id = update.message.chat_id
    first_name = update.message.chat.first_name
    last_name = update.message.chat.last_name
    username = update.message.chat.username
    file1 = open("/home/lovedeep/Apps/spotdl_bot/users.txt", "a")  # append mode
    file1.write("chat_id:{} firstname:{} lastname:{} username:{}\n".format(chat_id, first_name, last_name, username))
    file1.close()
    print("chat_id:{} firstname:{} lastname:{} username:{}\n".format(chat_id, first_name, last_name, username))

async def help(update, context):
    await update.message.reply_text("contact @lovedeep25")

async def handle_message(update, context):
    delete = await update.message.reply_text("please wait...")
    file2 = open("/home/lovedeep/Apps/spotdl_bot/requests.txt", "a")  # append mode
    file2.write(update.message.text)
    file2.close()
    run(update.message.text.replace(" ",""))
    audio = glob('*.mp3')
    print(audio)
    if len(audio) == 0:
        await update.message.reply_text("error, sorry this won't work, it's useless to try again")
    else:
        try:
            thumbnail = requests.get("https://open.spotify.com/oembed?url=" + update.message.text).json()
            # print(thumbnail)
            url = thumbnail["thumbnail_url"]
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open("cover.jpg", 'wb') as f:
                    f.write(response.content)
        except:
            print("Error loading thumbnail")
        await context.bot.deleteMessage(message_id=delete.message_id,chat_id=update.message.chat_id)
        delete1 = await update.message.reply_text("uploading...")

        trackN = []

        for l in audio:
            metadata = TinyTag.get(l)
            trackN.append(metadata.track)
            # print(metadata)

        print(trackN)
        audio1 = []

        n = len(trackN)

        for k in range(n):
            trackN[k] = int(trackN[k])
        for i in range(n):
            for j in range(0, n - i - 1):
                if trackN[j] > trackN[j + 1]:
                    tempN = trackN[j]
                    trackN[j] = trackN[j + 1]
                    trackN[j + 1] = tempN

                    temp = audio[j]
                    audio[j] = audio[j + 1]
                    audio[j + 1] = temp

        print(trackN)
        if metadata.disc_total != 1:
            for i in range(int(metadata.disc_total)):
                for j in range(len(audio)):
                    if int(TinyTag.get(audio[j]).disc) == i + 1:
                        audio1.append(audio[j])

        print(audio1)

        for i in range(n):
            await update.message.reply_audio(open(audio1[i], 'rb'), thumb="cover.jpg")

        await context.bot.deleteMessage(message_id=delete1.message_id,chat_id=update.message.chat_id)
        for file in audio:
            os.remove(file)
        os.remove("cover.jpg")
        print("------------------------------------------------------")


if __name__ == '__main__':
    app = Application.builder().token(API_TOKEN).get_updates_read_timeout(120).build();
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.run_polling(poll_interval=3)
