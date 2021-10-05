import asyncio
import os
import time

import aiohttp
from telethon.events import NewMessage
from telethon.tl.custom import Button
from yadisk_async import exceptions
from yandisk import Yandex, client, humanbytes, progress, token
from yandisk.events import message


async def download_file(url, file_name, message, start_time, bot):
    async with aiohttp.ClientSession() as session:
        c_time = time.time()
        await download_coroutine(session, url, file_name, message, start_time, bot)
    return file_name


async def download_coroutine(session, url, file_name, event, start, bot):
    display_message = ""
    async with session.get(url) as response:
        total_length = int(response.headers["Content-Length"])
        content_type = response.headers["Content-Type"]
        if "text" in content_type and total_length < 500:
            return await response.release()
        await event.edit(
            """**Initiating Download**
**URL:** {}
**File Name:** {}
**File Size:** {}""".format(
                url,
                os.path.basename(file_name).replace("%20", " "),
                humanbytes(total_length),
            ),
            parse_mode="md",
        )
        CHUNK_SIZE = 1024*6  # 2341
        with open(file_name, "wb") as f_handle:
            downloaded = 0
            while True:
                chunk = await response.content.read(CHUNK_SIZE)
                if not chunk:
                    break
                f_handle.write(chunk)
                downloaded += CHUNK_SIZE
                now = time.time()
                diff = now - start
                if round(diff % 10.00) == 0:  # downloaded == total_length:
                    percentage = downloaded * 100 / total_length
                    speed = downloaded / diff
                    elapsed_time = round(diff) * 1000
                    time_to_completion = (
                        round((total_length - downloaded) / speed) * 1000)
                    estimated_total_time = elapsed_time + time_to_completion
                    try:
                        total_length = max(total_length, downloaded)
                        current_message = await progress(downloaded, total_length, event, start, f"**Downloading({file_name}) from URL**")
                        if current_message not in [display_message, "empty"]:
                            await event.edit(current_message, parse_mode="html")

                            display_message = current_message
                    except Exception as e:
                        print("Error", e)
                        # logger.info(str(e))
        return await response.release()


@client.on(NewMessage())
async def upload(event):
    if event.media is None:
        return

    mesaj = await event.reply("`Your file downloading! Please Wait...`")
    baslangic = time.time()
    filename = await event.download_media(progress_callback=lambda d, t: asyncio.get_event_loop().create_task(progress(d, t, mesaj, baslangic, "Trying to Download Your File")))
    await mesaj.edit("`Uploading to YaDisk! Please Wait...`")

    try:
        await Yandex.upload(filename, filename)
    except exceptions.PathExistsError:
        await mesaj.edit("**You have already uploaded a file with this name.**\n__Do you want remove old file?__",
                         buttons=[Button.inline('✅ Yes', f'remove-{filename}'), Button.inline('❌ No', f'nodelete-{filename}')])
    except exceptions.UnauthorizedError:
        await mesaj.edit("You are not logged to Yandex. Please use /login then try upload file.")
    except Exception as e:
        print(str(e))

    await mesaj.edit("**✅ File has been successfully uploaded to Yandex. Do you want to make it public?**",
                     buttons=[Button.inline('✅ Yes', f'publish-{filename}'), Button.inline('❌ No', f'nopublish')])


@message(pattern=r"/upload ?([\w.]*) ?(.*)")
async def upload_url(event):
    filename = event.pattern_match.group(1)
    url = event.pattern_match.group(2)

    if url is None or filename is None:
        return await event.edit("**You must provide url & filename!**\nExample: `/upload test.gif https://www.gmail.com/mail/help/images/logonew.gif`")

    event = await event.reply("`Your URL downloading! Please Wait...`")
    await download_file(url, filename, event, time.time(), event.client)
    await event.edit("`Uploading to YaDisk! Please Wait...`")

    try:
        await Yandex.upload(filename, filename)
    except exceptions.PathExistsError:
        await event.edit("**You have already uploaded a file with this name.**\n__Do you want remove old file?__", buttons=[Button.inline('✅ Yes', f'remove-{filename}'), Button.inline('❌ No', f'nodelete-{filename}')])
    except exceptions.UnauthorizedError:
        await event.edit("You are not logged to Yandex. Please use /login then try upload file.")
    except Exception as e:
        print(str(e))

    await event.edit("**✅ File has been successfully uploaded to Yandex. Do you want to make it public?**", buttons=[Button.inline('✅ Yes', f'publish-{filename}'), Button.inline('❌ No', f'nopublish')])
