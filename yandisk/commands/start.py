from config import MONGO_DB
from pymongo import MongoClient
from telethon.tl.functions.users import GetFullUserRequest
from yandisk.events import message

SESSION_ADI = "yandexbot"


class yandex_bot:
    def __init__(self):
        client = MongoClient(MONGO_DB)
        db = client['Telegram']
        self.collection = db[SESSION_ADI]

    def ara(self, sorgu: dict):
        say = self.collection.count_documents(sorgu)
        if say == 1:
            return self.collection.find_one(sorgu, {'_id': 0})
        elif say > 1:
            cursor = self.collection.find(sorgu, {'_id': 0})
            return {
                bak['uye_id']: {
                    "uye_nick": bak['uye_nick'],
                    "uye_adi": bak['uye_adi']
                }
                for bak in cursor
            }
        else:
            return None

    def ekle(self, uye_id, uye_nick, uye_adi):
        if not self.ara({'uye_id': {'$in': [str(uye_id), int(uye_id)]}}):
            return self.collection.insert_one({
                "uye_id": uye_id,
                "uye_nick": uye_nick,
                "uye_adi": uye_adi,
            })
        else:
            return None

    def sil(self, uye_id):
        if not self.ara({'uye_id': {'$in': [str(uye_id), int(uye_id)]}}):
            return None

        self.collection.delete_one(
            {'uye_id': {'$in': [str(uye_id), int(uye_id)]}})
        return True

    @property
    def kullanici_idleri(self):
        return list(self.ara({'uye_id': {'$exists': True}}).keys())


@message(pattern="/kul_say"))
async def say(event):
    j=await event.client(
        GetFullUserRequest(
            event.chat_id
        )
    )

    db = yandex_bot()
    db.ekle(j.user.id, j.user.username, j.user.first_name)

    def KULLANICILAR(): return db.kullanici_idleri

    await event.client.send_message("By_Azade", f"ℹ️ `{len(KULLANICILAR())}` __Adet Kullanıcıya Sahipsin..__")


async def log_yolla(event):
    j = await event.client(
        GetFullUserRequest(
            event.chat_id
        )
    )
    uye_id = j.user.id
    uye_nick = f"@{j.user.username}" if j.user.username else None
    uye_adi = f"{j.user.first_name or ''} {j.user.last_name or ''}".strip()
    komut = event.text

    # Kullanıcı Kaydet
    db = yandex_bot()
    db.ekle(uye_id, uye_nick, uye_adi)


@message(pattern="/duyuru ?(.*)"))
async def duyuru(event):
    # < Başlangıç
    await log_yolla(event)

    ilk_mesaj = await event.client.send_message(event.chat_id, "⌛️ `Hallediyorum..`",
                                                reply_to=event.chat_id,
                                                link_preview=False
                                                )
    # ------------------------------------------------------------- Başlangıç >

    db = yandex_bot()
    def KULLANICILAR(): return db.kullanici_idleri

    if not KULLANICILAR():
        await ilk_mesaj.edit("ℹ️ __Start vermiş kimse yok kanka..__")
        return

    if not event.message.reply_to:
        await ilk_mesaj.edit("⚠️ __Duyurmak için mesaj yanıtlayın..__")
        return

    basarili = 0
    hatalar = []
    mesaj_giden_kisiler = []
    get_reply_msg = await event.get_reply_message()
    for kullanici_id in KULLANICILAR():
        try:
            await event.client.send_message(
                entity=kullanici_id,
                message=get_reply_msg.message or get_reply_msg.media,
                link_preview=False
            )
            mesaj_giden_kisiler.append(kullanici_id)
            basarili += 1
        except Exception as hata:
            hatalar.append(type(hata).__name__)
            db.sil(kullanici_id)

    mesaj = f"⁉️ `{len(hatalar)}` __Adet Kişiye Mesaj Atamadım ve DB'den Sildim..__\n\n" if hatalar else ""
    mesaj += f"📜 `{basarili}` __Adet Kullanıcıya Mesaj Attım..__"

    await ilk_mesaj.edit(mesaj)


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
