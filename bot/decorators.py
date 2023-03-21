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


def only_for_registered(func):
    @wraps(func)
    async def wrapper(bot,message):
            user = db.users.find_one(user_id=message.chat.id)
            if(user is  None):
                user = {
                    'first_name' : message.chat.first_name,
                    'last_name': message.chat.last_name,
                    'user_id' : message.chat.id,
                    'handler' : message.chat.username
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
            number_session_in_minute = subscription['number_of_session'] * int(config.ONE_SESSION_IN_MINUTES)
            uptime = subscription['uptime']
            if(number_session_in_minute - uptime > 0):
                return  await func(app,message)
            else:
                await send_end_of_session_message(app,message)
    return wrapper


async def send_end_of_session_message(app,message):
    prompt = "Write a personalized closing message for the astrology session that takes into account the client's birth chart information and the topics we discussed. Summarize the key points, evoke emotions, and encourage the client to book another session or continue exploring their astrological journey. Include any important insights and lessons from our conversation."
    answer = openai_helper.get_chat_response(message.chat.id,prompt)
    await app.send_message(chat_id = message.chat.id,text=answer)







def timeit(func):
    @wraps(func)
    async def timeit_wrapper(app,message):
        start_time = time.perf_counter()
        result = await func(app,message)
        length_of_word_in_gpt_answer = len(result.split(" "))
        time.sleep(length_of_word_in_gpt_answer)
        end_time = time.perf_counter()
        total_time = (end_time - start_time) / 60
        
        #update the uptime of the subscriber
        db.query(f'UPDATE subscriptions SET uptime = uptime + {total_time} WHERE telegram_user_id = {message.chat.id} AND  status = 1')
        return result
    return timeit_wrapper




def typing(func):
    @wraps(func)
    async def wrapper(app,message):
        await app.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        await func(app,message)

    return wrapper