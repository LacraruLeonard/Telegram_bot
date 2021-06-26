
import asyncio
import random
import secrets
import logging
from tinydb import TinyDB, Query
from captcha.image import ImageCaptcha
from pyrogram.errors import MessageNotModified
from typing import Tuple, Optional
from telegram import Update, Chat, ChatMember, ParseMode, ChatMemberUpdated
from telegram.ext import Updater, CommandHandler, CallbackContext, ChatMemberHandler
from pyrogram import Client, idle, filters, emoji
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ChatPermissions
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logging.getLogger(__name__)

API_KEY = os.environ.get('API_KEY')
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')

WrappedWebdollar_bot= Client(
    session_name="WrappedWebdollar_bot",
    api_id=,
    api_hash="",
    bot_token="",
    workers=200
)

image = ImageCaptcha(fonts=['font1.ttf'])


@WrappedWebdollar_bot.on_callback_query(filters.regex('^wrong.*'))
async def wrong_captcha_cb_handler(c: Client, cb: CallbackQuery):
    cb_data = cb.data.split("_")
    if len(cb_data) > 1:
        f_user_id = int(cb_data[1])
        if f_user_id == cb.from_user.id:
            await cb.answer(
                "You have failed to verify the captcha",
                show_alert=True
            )
        else:
            await cb.answer(
                "This captcha is not for you",
                show_alert=True
            )

@WrappedWebdollar_bot.on_callback_query(filters.regex('^correct.*'))
async def correct_captcha_cb_handler(c: Client, cb: CallbackQuery):
    cb_data = cb.data.split("_")
    if len(cb_data) > 1:
        f_user_id = int(cb_data[1])
        if f_user_id == cb.from_user.id:
            await cb.answer()

            await c.restrict_chat_member(
                cb.message.chat.id,
                f_user_id,
                ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_stickers=True,
                    can_send_animations=True,
                    can_use_inline_bots= True,
                    can_send_games=False,
                    can_add_web_page_previews=True,
                    can_send_polls=True,
                )
            )
            await cb.edit_message_reply_markup()
            user = await c.get_users(f_user_id)
            mention = f"<a href='tg://user_id={user.id}'>{user.frist_name}</a"
            await cb.edit_message_text(
                f"{mention} has successfully solved the Captcha"
            )


        else:
            await cb.answer(
                "This captcha is not for you",
                show_alert=True
            )


@WrappedWebdollar_bot.on_message(filters.new_chat_members)
async def on_new_chat_members(c: Client, ms: Message):
    await c.restrict_chat_member(
        chat_id=ms.chat.id,
        user_id=ms.from_user.id,
        permission=ChatPermissions()
    )
    secret = secrets.token_hex(2)
    buttons = []
    for x in range(2):
        buttons.append(
            InlineKeyboardButton(
                text=f'{secrets.token_hex(2)}',
                callback_data=f'wrong{ms.from_user.id}'
        )
    )

    buttons.append(
        InlineKeyboardButton(
            text=f"{secret}",
            callback_data=f"correct{ms.from_user.id}"
        )
    )

    random.shuffle(buttons)
    data = image.generate(secret)
    image.write(secret, f"{secret}.png")
    mention = f"<a href='tg://user_id={ms.from_user.id}'>{ms.from_user.frist_name}</a"
    await ms.reply_photo(
        photo=f"{secret}.png",
        caption=f"{emoji.SHIELD} {mention}, To complete your captcha select the correct text",
        reply_markup=InlineKeyboardMarkup(
            [buttons]
        )
    )
    if os.path.isfile(f"{secret}.png"):
        os.remove(f"{secret}.png")



async def main():
    await WrappedWebdollar_bot.start()
    await idle()



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
