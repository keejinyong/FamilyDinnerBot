from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import JobQueue
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import logging
import datetime

from dbhelper import DBHelper

#daily tasks time
#utc time for pythonanywhere (-8)
resettime = datetime.time(16,0,0)
remindertime = datetime.time(8,0,0)
statustime = datetime.time(9,0,0)


token = '600148561:AAFHMlyD-by4AdrxTanUFanFjdqchz6syj4'
#slight change to commit
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)


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
        reply_keyboard = [[InlineKeyboardButton('Yes', callback_data='Yes')], 
            [InlineKeyboardButton('No I want to join a family', callback_data='No I want to join a family')]]
        update.message.reply_text(
            'Hi! You are not in a family yet \n'
            'Do you want to create a new family?',
            reply_markup=InlineKeyboardMarkup(reply_keyboard))
    #if in a family
    #ask to set if eating dinner
    else:
        my_name = db.find_myname(update.message.chat_id)
        waitaction.append(update.message.chat_id)
        reply_keyboard = [[InlineKeyboardButton('Dinner?', callback_data='Dinner?')], 
            [InlineKeyboardButton('Check family status', callback_data='Check family status')], 
            [InlineKeyboardButton('Add member', callback_data='Add member')], 
            [InlineKeyboardButton('Remove member', callback_data='Remove member')], 
            [InlineKeyboardButton('Chg Name', callback_data='Chg Name')]]
        update.message.reply_text(
            'Hi ' + my_name + '! You are in ' + family_name + " family! \n"
            'What do you want to do?',
            reply_markup=InlineKeyboardMarkup(reply_keyboard))
        
        
#        reply_keyboard = [['Having Dinner', 'No Dinner', 'Unconfirmed']]
#        update.message.reply_text(
#            'Hi! I am Family Dinner bot! \n'
#            'Tell me, are you having dinner today?',
#            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    
    db.close()
    
def create_family(familyname, myname, id):
    db = DBHelper()
    res = db.add_family(familyname)
    if not res:
        db.add_family_member(id, familyname, myname)
    db.close()
    return res
    
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
    res = db.add_family_member(newid, familyname, name)
    db.close()
    return res
    
def updatename(id, name):
    db = DBHelper()
    db.set_name(id,name)
    db.close()
    
def removefromfamily(rmvname, id):
    db = DBHelper()
    res = db.removefromfamily(id, rmvname)
    db.close()
    return res

def dostuff(bot, update):
            
    #waiting for name reply
    if update.message.chat_id in waitfamilyname:
        #sets up family in sql
        waitfamilyname.remove(update.message.chat_id)
        familyname = update.message.text
        id = update.message.chat_id
        if not create_family(familyname, "", id):
            bot.send_message(chat_id=update.message.chat_id, text="Congratulations your family has been created\nPlease enter your name")
            waitmyname.append(update.message.chat_id)
        else:
            bot.send_message(chat_id=update.message.chat_id, text="Name taken try another 1")
            waitfamilyname.append(update.message.chat_id)
        
    elif update.message.chat_id in waitmyname:
        waitmyname.remove(update.message.chat_id)
        updatename(update.message.chat_id, update.message.text)
        bot.send_message(chat_id=update.message.chat_id, text="Done")
        
    #waiting for id to add
    elif update.message.chat_id in waitadd:
        waitadd.remove(update.message.chat_id)
        id = update.message.text
        if addmember(update.message.chat_id, id, ""):
            bot.send_message(chat_id=update.message.chat_id, text="Added")
        else:
            bot.send_message(chat_id=update.message.chat_id, text="Already in a family")
        
    #waiting for name to rmv
    elif update.message.chat_id in waitrmv:
        waitrmv.remove(update.message.chat_id)
        if removefromfamily(update.message.text, update.message.chat_id):
            bot.send_message(chat_id=update.message.chat_id, text="Removed from family")
        else:
            bot.send_message(chat_id=update.message.chat_id, text="Name not found")
    #no action done jus echo
    else:
        bot.send_message(chat_id=update.message.chat_id, text=update.message.text)
        
def button(bot, update):
    query = update.callback_query
    #/start without family
    if query.message.chat_id in waitcreatefamily:
        waitcreatefamily.remove(query.message.chat_id)
        #if yes send to waitfamilyname queue
        if query.data == "Yes":
            bot.send_message(chat_id=query.message.chat_id, text="Type a name for your family")
            waitfamilyname.append(query.message.chat_id)
        elif query.data == "No I want to join a family":
            bot.send_message(chat_id=query.message.chat_id, text="Get your family to invite you with your id: " + str(query.message.chat_id))
            
    #when /start when in family 
    elif query.message.chat_id in waitaction:
        waitaction.remove(query.message.chat_id)
        if query.data == "Dinner?":
            #shift to waitdinner queue set key options
            waitdinner.append(query.message.chat_id)
            reply_keyboard = [[InlineKeyboardButton('Having Dinner', callback_data='Having Dinner')], 
                [InlineKeyboardButton('No Dinner', callback_data='No Dinner')]]
            bot.send_message(chat_id=query.message.chat_id,
                text='Tell me, are you having dinner today?',
                reply_markup=InlineKeyboardMarkup(reply_keyboard))
        elif query.data == "Add member":
            #shift to waitadd queue
            waitadd.append(query.message.chat_id)
            bot.send_message(chat_id=query.message.chat_id, text="Enter the id of your new member")
        elif query.data == "Remove member":
            #shift to waitrmv queue
            waitrmv.append(query.message.chat_id)
            bot.send_message(chat_id=query.message.chat_id, text="Enter the name of the member")
        elif query.data == "Check family status":
            bot.send_message(chat_id=query.message.chat_id, text=familystatus(query.message.chat_id))
        elif query.data == "Chg Name":
            waitmyname.append(query.message.chat_id)
            bot.send_message(chat_id=query.message.chat_id, text="Enter your name")
            
    #get response for eating dinner?
    elif query.message.chat_id in waitdinner:
        waitdinner.remove(query.message.chat_id)
        if query.data == "Having Dinner":
            #eating, update sql
            set_eating(query.message.chat_id, "Eating")
            bot.send_message(chat_id=query.message.chat_id, text="Status updated")
        elif query.data == "No Dinner":
            #not eatin, update sql
            set_eating(query.message.chat_id, "Not Eating")
            bot.send_message(chat_id=query.message.chat_id, text="Status updated")
            
    else:
        bot.send_message(chat_id=query.message.chat_id, text="Use /start to start")
    

def help(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='no help')


def end(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Family dinner bot never ends")

def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Your id is: " + str(update.message.chat_id))
    
def getid(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Your id is: " + str(update.message.chat_id))
    
def resetdinner(bot, job):
    print("reset at: " + str(datetime.datetime.now()))
    db = DBHelper()
    db.resetdinner()
    db.close()
    
def remind(bot, job):
    print("reminder send at: " + str(datetime.datetime.now()))
    db = DBHelper()
    nums = db.listofnum()
    for num in nums:
        if db.geteat(num) == "0":
            #send reminder
            waitdinner.append(int(num))
            reply_keyboard = [[InlineKeyboardButton('Having Dinner', callback_data='Having Dinner')], 
                [InlineKeyboardButton('No Dinner', callback_data='No Dinner')]]
            bot.send_message(chat_id=num, text='You have not tell me yet, are you having dinner today?',
                reply_markup=InlineKeyboardMarkup(reply_keyboard))
    
def sendstatus(bot,job):
    print("status send at: " + str(datetime.datetime.now()))
    db = DBHelper()
    nums = db.listofnum()
    reply_keyboard = [['/start']]
    for num in nums:
        bot.send_message(chat_id=num, text=familystatus(num),
            reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    
    


def main():
    db = DBHelper()
    db.setup()
    db.close()
    updater = Updater(token)
    jobqueue = updater.job_queue

    #get dispatcher to register handlers
    dispatcher = updater.dispatcher

    #handle commands
    start_handler = CommandHandler('start', start)
    button_handler = CallbackQueryHandler(button)
    reply_handler = MessageHandler(Filters.text, dostuff)
    unknown_handler = MessageHandler(Filters.command, getid)
    help_handler = CommandHandler('help', help)
    end_handler = CommandHandler('end', end)

    dispatcher.add_handler(button_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(reply_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(end_handler)
    dispatcher.add_handler(unknown_handler)

    updater.start_polling()
    
    jobqueue.run_daily(resetdinner, resettime)
    jobqueue.run_daily(sendstatus, statustime)
    jobqueue.run_daily(remind, remindertime)
    #jobqueue.run_once(resetdinner, 0)
    #jobqueue.run_once(remind, 0)
    #jobqueue.run_once(sendstatus, 0)

    updater.idle()

if __name__ == '__main__':
    main()
