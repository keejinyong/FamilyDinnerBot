from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import InlineQueryHandler

import logging
import json

from dbhelper import DBHelper

token = '600148561:AAFHMlyD-by4AdrxTanUFanFjdqchz6syj4'
#slight change to commit
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

db = DBHelper()
db.setup()
db.close()

waitcreatefamily = []
waitfamilyname = []
waitmyname = []
waitaction = []
waitdinner = []
waitadd = []
waitaddname = []
waitrmv = []

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Hi, I am family dinner bot")

    #check if in family
    db = DBHelper()
    family_name = db.find_family(update.message.chat_id)
    #if no family name = not in family
    #ask if want to create family
    if not family_name:
        waitcreatefamily.append(update.message.chat_id)
        reply_keyboard = [['Yes', 'No']]
        update.message.reply_text(
            'Hi! You are not in a family yet \n'
            'Do you want to create a new family?',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    #if in a family
    #ask to set if eating dinner
    else:
        my_name = db.find_myname(update.message.chat_id)
        waitaction.append(update.message.chat_id)
        reply_keyboard = [['Dinner?', 'Check family status', 'Add member', 'Remove member', 'Chg Name']]
        update.message.reply_text(
            'Hi ' + my_name + '! You are in ' + family_name + " family! \n"
            'What do you want to do?',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        
        
#        reply_keyboard = [['Having Dinner', 'No Dinner', 'Unconfirmed']]
#        update.message.reply_text(
#            'Hi! I am Family Dinner bot! \n'
#            'Tell me, are you having dinner today?',
#            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    
    db.close()
    
def create_family(familyname, myname, id):
    db = DBHelper()
    db.add_family(familyname)
    db.add_family_member(id, familyname, myname)
    db.close()
    
def set_eating(id, eating):
    db = DBHelper()
    db.set_eating(id, eating)
    db.close()
    
def familystatus(id):
    db = DBHelper()
    res = db.check_status(id)
    db.close()
    return res 
    
def addmember(myid, newid, name):
    db = DBHelper()
    familyname = db.find_family(myid)
    db.add_family_member(newid, familyname, name)
    db.close()
    
def updatename(id, name):
    db = DBHelper()
    db.set_name(id,name)
    db.close()

def dostuff(bot, update):
    #when /start when not in family
    if update.message.chat_id in waitcreatefamily:
        waitcreatefamily.remove(update.message.chat_id)
        #if yes send to waitfamilyname queue
        if update.message.text == "Yes":
            bot.send_message(chat_id=update.message.chat_id, text="Type a name for your family")
            waitfamilyname.append(update.message.chat_id)
            
    #waiting for name reply
    elif update.message.chat_id in waitfamilyname:
        #sets up family in sql
        waitfamilyname.remove(update.message.chat_id)
        familyname = update.message.text
        id = update.message.chat_id
        create_family(familyname, "", id)
        bot.send_message(chat_id=update.message.chat_id, text="Congratulations your family has been created\nPlease enter your name")
        waitmyname.append(update.message,chat_id)
        
    elif update.message.chat_id in waitmyname:
        waitmyname.remove(update.message.chat_id)
        updatename(update.message.chat_id, update.message.text)
        bot.send_message(chat_id=update.message.chat_id, text="Done")
        
    #when /start when in family 
    elif update.message.chat_id in waitaction:
        waitaction.remove(update.message.chat_id)
        if update.message.text == "Dinner?":
            #shift to waitdinner queue set key options
            waitdinner.append(update.message.chat_id)
            reply_keyboard = [['Having Dinner', 'No Dinner']]
            update.message.reply_text(
                'Tell me, are you having dinner today?',
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        elif update.message.text == "Add member":
            #shift to waitadd queue
            waitadd.append(update.message.chat_id)
            bot.send_message(chat_id=update.message.chat_id, text="Enter the id of your new member")
        elif update.message.text == "Remove member":
            #shift to waitrmv queue
            waitrmv.append(update.message.chat_id)
            bot.send_message(chat_id=update.message.chat_id, text="Enter the name of the member")
        elif update.message.text == "Check family status":
            bot.send_message(chat_id=update.message.chat_id, text=familystatus(update.message.chat_id))
        elif update.message.text == "Chg Name":
            waitmyname.append(update.message.chat_id)
            bot.send_message(chat_id=update.message.chat_id, text="Enter your name")
            
            
    #get response for eating dinner?
    elif update.message.chat_id in waitdinner:
        waitdinner.remove(update.message.chat_id)
        if update.message.text == "Having Dinner":
            #eating, update sql
            set_eating(update.message.chat_id, 1)
            bot.send_message(chat_id=update.message.chat_id, text="Status updated")
        elif update.message.text == "No Dinner":
            #not eatin, update sql
            set_eating(update.message.chat_id, 1)
            bot.send_message(chat_id=update.message.chat_id, text="Status updated")
    
    #waiting for id to add
    elif update.message.chat_id in waitadd:
        waitadd.remove(update.message.chat_id)
        id = update.message.text
        addmember(update.message.chat_id, id, "")
        bot.send_message(chat_id=update.message.chat_id, text="Added")
        
    #waiting for name to rmv
    elif update.message.chat_id in waitrmv:
        waitrmv.remove(update.message.chat_id)
        print("nothin")
    #no action done jus echo
    else:
        bot.send_message(chat_id=update.message.chat_id, text=update.message.text)

def help(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='no help')


def end(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Family dinner bot never ends")

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
    bot.send_message(chat_id=update.message.chat_id, text=str(update.message.chat_id))
    
def getid(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=str(update.message.chat_id))


def main():
    updater = Updater(token)


    #get dispatcher to register handlers
    dispatcher = updater.dispatcher

    updater = Updater(token)

    #get dispatcher to register handlers
    dispatcher = updater.dispatcher

    #handle commands
    getid_handler = CommandHandler('id', getid)
    start_handler = CommandHandler('start', start)
    reply_handler = MessageHandler(Filters.text, dostuff)
    caps_handler = CommandHandler('caps', caps, pass_args=True)
    inline_caps_handler = InlineQueryHandler(inline_caps)
    unknown_handler = MessageHandler(Filters.command, unknown)
    help_handler = CommandHandler('help', help)
    end_handler = CommandHandler('end', end)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(reply_handler)
    dispatcher.add_handler(caps_handler)
    dispatcher.add_handler(inline_caps_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(end_handler)


    dispatcher.add_handler(unknown_handler)

    updater.start_polling()
    
    print("rdy")

    updater.idle()

if __name__ == '__main__':
    main()
