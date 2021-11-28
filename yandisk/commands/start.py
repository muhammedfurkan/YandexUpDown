from yandisk.events import message


@message(pattern="/start")
async def start(event):
    msg = "**Welcome to Yandisk!**\n\n" + \
        "**This bot is made by @By_Azade.**\n" + \
        "**You can use this bot to upload files to Yandisk.**\n" + \
        "**You can use this bot to download files from Yandisk.**\n" + \
        "**You can use this bot to get info about files on Yandisk.**\n" + \
        "**You can use this bot to delete files on Yandisk.**\n" + \
        "**You can use this bot to make files public.**\n" + \
        "**You can use this bot to make files private.**\n" + \
        "**You can use this bot to get public link of files.**\n" + \
        "**You can use this bot to get private link of files.**\n" + \
        "**ALL COMMANDS:**\n\n" + \
        "`/info` get information disk usage\n"

    await event.reply(msg)
