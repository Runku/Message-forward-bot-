import os
import random
from time import sleep
from pyrogram import filters
from bot import LOG, app, advance_config, chats_data, from_chats, to_chats, \
                remove_strings, replace_string, sudo_users
from bot.helper.utils import get_formatted_chat

def copy_with_media(client, message, chat, caption):
  if message.media and (message.audio or message.photo or message.document or message.video or message.voice):
    if caption is None:
      caption = message.caption
    if caption is None:
      caption = ''

    file = message.download('/tmp/tgfiles/')
    
    if message.photo:
      client.send_photo(chat_id=chat, photo=file, caption=caption)
    else:
      client.send_document(chat_id=chat, document=file, caption=caption)
      
    os.remove(file)

  else:
    message.copy(chat)

@app.on_message(filters.chat(from_chats) & filters.incoming)
def work(client, message):
    caption = None
    msg = None
    if remove_strings:
      for string in remove_strings:
        if message.media and not message.poll:
          caption = message.caption.html.replace(string, replace_string)
        elif message.text:
          msg = message.text.html.replace(string, replace_string)
    if advance_config:
      try:
        for chat in chats_data[message.chat.id]:
          if msg:
            app.send_message(chat, msg)
          else:
            copy_with_media(client, message, chat, caption)
      except Exception as e:
        LOG.error(e)
    else:
      try:
        for chat in to_chats:
          if msg:
            app.send_message(chat, msg)
          else:
            copy_with_media(client, message, chat, caption)
      except Exception as e:
        LOG.error(e)

@app.on_message(filters.user(sudo_users) & filters.command(["fwd", "forward"]), group=1)
def forward(app, message):
    if len(message.command) > 1:
      chat_id = get_formatted_chat(message.command[1], app)
      if chat_id:
        try:
          offset_id = 0
          limit = 0
          if len(message.command) > 2:
            limit = int(message.command[2])
          if len(message.command) > 3:
            offset_id = int(message.command[3])
          for msg in app.iter_history(chat_id, limit=limit, offset_id=offset_id):
            msg.copy(message.chat.id)
            sleep(random.randint(1, 10))
        except Exception as e:
          message.reply_text(f"```{e}```")
      else:
        reply = message.reply_text("```Invalid Chat Identifier. Give me a chat id, username or message link.```")
        sleep(5)
        reply.delete()
    else:
      reply = message.reply_text("```Invalid Command ! Use /fwd {ChatID} {limit} {FirstMessageID}```")
      sleep(20)
      reply.delete()

app.run()
