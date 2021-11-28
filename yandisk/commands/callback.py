from os import remove
from re import compile

from telethon.events import CallbackQuery
from telethon.tl.custom import Button
from yandisk import Yandex, client


@client.on(CallbackQuery())
async def callquery(event):
    data = event.data.decode("utf-8")

    if data.startswith("ndlt"):
        filename = data.split("ndlt-")[1]
        await Yandex.publish(filename)
        file = await Yandex.get_meta(filename)
        await event.edit(f"**Here is the link of the old file: ** [Link]({file.public_url})", buttons=Button.url('🔗 Public Link', file.public_url))
    elif data.startswith("rm"):
        filename = data.split("rm-")[1]
        await event.edit(f"**Are you sure for delete `{filename}` permanently?**", buttons=[Button.inline('✅ Yes', f"yes-{filename}"), Button.inline('❌ No', "no")])
    elif data.startswith("yes"):
        msg = await event.client.get_messages(entity=event.query.peer, ids=event.query.msg_id)
        print(msg)
        filename = data.split("yes-")[1]
        await Yandex.remove(filename, permanently=True)
        return await event.edit('✅ **Deleted successfully!**')
    elif data == "no":
        return await event.edit("__OK! File will not be deleted.__")
    elif data.startswith("ph"):
        filename = data.split("ph-")[1]
        await Yandex.publish(filename)
        file = await Yandex.get_meta(filename)
        await event.edit(f"__✅ I made the file public.__ **Here is public link: ** [Link]({file.public_url})", buttons=Button.url('🔗 Public Link', file.public_url))
        remove(filename)
        return "file removed"
    elif data == "npb":
        return await event.edit("__OK! Only you will access the file.__")
