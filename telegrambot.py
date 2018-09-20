from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import InlineQueryHandler
import logging
import json

token = '600148561:AAFHMlyD-by4AdrxTanUFanFjdqchz6syj4'
#slight change to commit
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

DINNERSTATUS = range(1)

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Hi, I am family dinner bot")

    reply_keyboard = [['Having Dinner', 'No Dinner', 'Unconfirmed']]
    update.message.reply_text(
        'Hi! I am Family Dinner bot! \n'
        'Tell me, are you having dinner today?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

def help(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='no help')


def end(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Family dinner bot never ends")


def echo(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=update.message.text)


def caps(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=text_caps)


def inline_caps(bot, update):
    query = update.inline_query.query
    if not query:
        return
    results = list()
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    bot.answer_inline_query(update.inline_query.id, results)

def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")


def main():
	updater = Updater(token)

	#get dispatcher to register handlers
	dispatcher = updater.dispatcher

	#handle commands
	start_handler = CommandHandler('start', start)
	echo_handler = MessageHandler(Filters.text, echo)
	caps_handler = CommandHandler('caps', caps, pass_args=True)
	inline_caps_handler = InlineQueryHandler(inline_caps)
	unknown_handler = MessageHandler(Filters.command, unknown)
	help_handler = CommandHandler('help', help)
	end_handler = CommandHandler('end', end)

	dispatcher.add_handler(start_handler)
	dispatcher.add_handler(echo_handler)
	dispatcher.add_handler(caps_handler)
	dispatcher.add_handler(inline_caps_handler)
	dispatcher.add_handler(help_handler)
	dispatcher.add_handler(end_handler)


	dispatcher.add_handler(unknown_handler)

	updater.start_polling()

	updater.idle()

if __name__ == '__main__':
    main()
