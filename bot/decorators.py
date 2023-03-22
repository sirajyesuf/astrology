from functools import wraps
import db
import config
import time
import db
import math
import time
from pyrogram.types import (InlineKeyboardMarkup,InlineKeyboardButton,ReplyKeyboardMarkup,)
from pyrogram import enums
from openai_helper import openai_helper
from datetime import datetime
from enums import Status
from pyrogram import errors
def only_for_subscribers(func):
    
    @wraps(func)
    async def wrapper(bot,message):
            user = db.users.find_one(user_id=message.chat.id)
            print(user)
            subscription = db.subscriptions.count(user_id=user['id'],status=1)
            if(subscription):
                return  await func(bot,message)
            else:
                msg = f"you dont have active subscription.use this bot to buy a subscription.\n\n {config.BOT_USERNAME}"
                await bot.send_message(chat_id = message.chat.id,text=msg)
    return wrapper


def register(func):
    @wraps(func)
    async def wrapper(bot,message):
            user = db.users.find_one(telegram_user_id=message.chat.id)
            if(user is  None):
                user = {
                
                    'first_name' : message.chat.first_name,
                    'last_name': message.chat.last_name,
                    'telegram_user_id' : message.chat.id,
                    'telegram_handler' : message.chat.username,
                    'created_at' : datetime.now(),
                    'updated_at' : datetime.now()
                }
                db.users.insert(user)
            await func(bot,message)
    return wrapper


def only_unsubscribers(func):
    @wraps(func)
    async def wrapper(bot,message):
            user = db.users.find_one(user_id=message.chat.id)
            subscription = db.subscriptions.count(user_id=user['id'],status=1)
            if(subscription == 0):
                return  await func(bot,message)
            else:
                msg = "you are already subscribed"
                await bot.send_message(chat_id = message.chat.id,text=msg)
    return wrapper



def has_session(func):
    @wraps(func)
    async def wrapper(app,message):
            subscription = db.subscriptions.find_one(telegram_user_id=message.chat.id,status=1)
            number_session_in_minute = subscription['number_of_session'] * config.ONE_SESSION_IN_MINUTES
            uptime = subscription['uptime']
            if((number_session_in_minute - uptime) > 0):
                return  await func(app,message)
            else:
                await send_end_of_session_message(app,message)
    return wrapper


async def send_end_of_session_message(app,message):
    prompt = "Write a personalized closing message for the astrology session that takes into account the client's birth chart information and the topics we discussed. Summarize the key points, evoke emotions, and encourage the client to book another session or continue exploring their astrological journey. Include any important insights and lessons from our conversation."
    answer = openai_helper.get_chat_response(message.chat.id,prompt)
    await app.send_message(chat_id = message.chat.id,text=answer)






async def add_client_chat_history(user_id,prompt,answer):
    return db.histories.insert({
        'user_id': user_id,
        'prompt' : prompt,
        'answer' : answer      
    })

def timeit(bot):
    def wrapper(func):
        @wraps(func)
        async def inner_wrapper(*args,**kwrags):
            start_time = time.perf_counter()
            app = args[0]
            message = args[1]
            user = db.users.find_one(telegram_user_id = message.chat.id)
            subscription = db.subscriptions.find_one(user_id = user['id'],status = Status.ACTIVE.value)
            plan = db.plans.find_one(id=subscription['plan_id'])

            chat_gpt_answer = await func(*args,**kwrags)
            await add_client_chat_history(user['id'],message.text,chat_gpt_answer)
            length_of_words_in_gpt_answer = len(chat_gpt_answer.split(" "))
            # time.sleep(length_of_words_in_gpt_answer)
            await app.send_message(chat_id = message.chat.id,text=chat_gpt_answer)
            end_time = time.perf_counter()
            # minutes
            total_time = (end_time - start_time ) / 60
            
            #update the uptime and  number of prompt  of the subscriber
            db.query(f'UPDATE subscriptions SET uptime = uptime + {total_time} WHERE user_id = {user["id"]} AND  status = 2')
            if(subscription['number_of_propmt'] >= 5):
                db.subscriptions.update(dict(id=subscription['id'],number_of_propmt = 0),['id'])
                remaning_sessions_in_minutes = math.ceil(int(plan ['number_of_session'] * config.ONE_SESSION_IN_MINUTES)  - subscription['uptime'])
                await  countdown(bot,message,remaning_sessions_in_minutes)
            else:
                db.query(f'UPDATE subscriptions SET number_of_propmt = number_of_propmt + 1 WHERE user_id = {user["id"]} AND  status = 2')

        return inner_wrapper
    return wrapper




def typing(func):
    @wraps(func)
    async def wrapper(app,message):
        await app.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        await func(app,message)

    return wrapper



async def countdown(bot,message,remaning_sessions_in_minutes):

        messages = db.messages.count(telegram_user_id = message.chat.id)
        if(messages):
            messages = db.messages.find_one(telegram_user_id = message.chat.id)
            try:
                await bot.edit_message_text(chat_id=message.chat.id,message_id=messages['message_id'] ,text=f"#Remaing Sessions in Minutes\n\n ⏳ {remaning_sessions_in_minutes} minutes only.")
            except errors.exceptions.bad_request_400.MessageNotModified:
                print(remaning_sessions_in_minutes)
        else:
            response = await bot.send_message(chat_id = message.chat.id,text=f"#Remaing Sessions in Minutes\n\n ⏳ {remaning_sessions_in_minutes} minutes only.")
            db.messages.insert({
            'telegram_user_id':message.chat.id,
            'message_id':response.id,
            'start_session_message_id': response.id,
            'is_close_session_button_sent' :False
            })
    




