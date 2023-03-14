from functools import wraps
import db
import config
import time
import db
import math

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
    async def wrapper(bot,message):
            user = db.users.find_one(user_id=message.chat.id)
            subscription = db.subscriptions.find_one(user_id=user['id'],status=1)
            transaction = db.transactions.find_one(id=subscription['transaction_id'])
            plan = db.plans.find_one(id=transaction['plan_id'])
            number_session_in_minute = plan['number_session'] * int(config.ONE_SESSION_IN_MINUTES)
            uptime = subscription['uptime']
            if(number_session_in_minute - uptime > 0):
                return  await func(bot,message)
            else:
                msg = f"you finished your subscription plan go and buy plan using the bot\n\n@{bot.get_me().username}"
                await bot.send_message(chat_id = message.chat.id,text=msg)
    return wrapper






def timeit(func):
    @wraps(func)
    async def timeit_wrapper(app,message):
        start_time = time.perf_counter()
        result = await func(app,message)
        end_time = time.perf_counter()
        total_time = (end_time - start_time) / 60

        user = db.users.find_one(user_id = message.chat.id)
        user_id = user['id']
        db.query(f'UPDATE subscriptions SET uptime = uptime + {total_time} WHERE user_id = {user_id} AND  status = 1')
        return result
    return timeit_wrapper