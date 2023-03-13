import json
import logging
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, MessageEntity, Update
from telegram.ext import Updater, CommandHandler, ContextTypes, CallbackQueryHandler, CallbackContext

from article_recs.target.target import Handler, Target


class TelegramTarget(Target):

    def __init__(self, token: str, chat_id: str, handler: Handler) -> None:
        #self.token = token
        self.chat_id = chat_id
        self.bot = Bot(token)
        self.updater = Updater(token)
        self.handler = handler
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.InlineKeyboardHandler))

    def InlineKeyboardHandler(self, update: Update, cb: CallbackContext) -> None:
        query = update.callback_query
        query.answer()
        data = json.loads(query.data)
        self.handler.handle(data)
        return 1

    def start(self):
        self.updater.start_polling()
        self.updater.idle()

    def _get_markups(self, content_id: str):
        markup = []
        markup.append(InlineKeyboardButton(text="🔥", callback_data=json.dumps(
            {"content_id": content_id, "vote": "fire"})))
        markup.append(InlineKeyboardButton(text="👍", callback_data=json.dumps(
            {"content_id": content_id, "vote": "up"})))
        markup.append(InlineKeyboardButton(text="👎", callback_data=json.dumps(
            {"content_id": content_id, "vote": "down"})))
        markup.append(InlineKeyboardButton(text="❌", callback_data=json.dumps(
            {"content_id": content_id, "vote": "block"})))
        markup.append(InlineKeyboardButton(text="Paywall", callback_data=json.dumps(
            {"content_id": content_id, "vote": "paywall"})))
        return markup

    def send(self, content_id: str, text: str, image_url: str = None):
        try:
            inline_markup = InlineKeyboardMarkup([self._get_markups(content_id)])

            if image_url == None:
                self.bot.send_message(
                    self.chat_id,
                    text,
                    reply_markup=inline_markup
                )
            else:
                self.bot.send_photo(
                    self.chat_id,
                    image_url,
                    caption=text,
                    reply_markup=inline_markup
                )
        except Exception as e:
            logging.error(f"Error while sending message {str(e)}")
