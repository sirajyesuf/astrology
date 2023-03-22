
from enums import Status
import config
from pyrogram import Client,filters
from pyrogram.handlers import MessageHandler,CallbackQueryHandler,RawUpdateHandler
import config
from pyrogram.types import (InlineKeyboardMarkup,InlineKeyboardButton,ReplyKeyboardMarkup,)
import db
import requests
import json
from pyrogram.raw import types
from datetime import datetime,timedelta
from decorators  import only_for_subscribers,register,only_unsubscribers,has_session,timeit,typing
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import config
import logging
from openai_helper import openai_helper
from datetime import datetime
log_format = logging.Formatter(
    "%(asctime)s - [%(name)s] [%(levelname)s]  %(message)s")

logger = logging.getLogger()

logger.setLevel(logging.INFO)
file_logger = logging.FileHandler("log")
file_logger.setLevel(logging.INFO)
file_logger.setFormatter(log_format)
logger.addHandler(file_logger)
console_logger = logging.StreamHandler()
console_logger.setFormatter(log_format)
console_logger.setLevel(logging.INFO)
logger.addHandler(console_logger)

app= Client("astrologer",api_id= config.API_ID,api_hash=config.API_HASH)
bot=Client("bot",api_id=config.API_ID,api_hash=config.API_HASH,bot_token=config.BOT_USERNAME)



def job():
    for subscription in db.subscriptions.find(status = 1):
        if(subscription):
            transaction = db.transactions.find_one(id = subscription['transaction_id'])
            plan = db.plans.find_one(id = transaction['plan_id'])
            plan_num_session_in_min = plan['number_session'] * int(config.ONE_SESSION_IN_MINUTES)
            if(plan_num_session_in_min < subscription['uptime']):
                data = dict(id=subscription['id'],status = 0)
                db.subscriptions.update(data,['id'])
                


async def get_conversation():
    for conv in db.conversations.all():
        return conv
    
async def accepte_promocode_func(_, __, query):
        
        print("accepte_promocode_func")
        print(query)
        conv=await get_conversation()
        if(conv is not None):
            if(conv['que'] == "free_plan"):
                return True
        return False


accepte_promocode_func_filter = filters.create(accepte_promocode_func)

async def activate_the_subscription(app,subscription_id,user_id):
    data = dict(id=subscription_id,status = Status.ACTIVE.value)
    db.subscriptions.update(data,['id'])
    msg = "Your payment is successfully processed.thanks!\n\n you are now subscribed."
    await app.send_message(chat_id = user_id,text = msg)

async def raw_update_handler_function(app,update,users,chats):
    print(update)
    try:
        if type(update) == types.UpdateBotPrecheckoutQuery:

            #{
            # "_": "types.UpdateBotPrecheckoutQuery",
            # "query_id": 1672406644428380219,
            # "user_id": 389387515,
            # "payload": "b'17'",
            # "currency": "USD",
            # "total_amount": 300
            #}

            if(db.subscriptions.count(id=int(update.payload),status=Status.PENDING.value)):
                url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/answerPreCheckoutQuery?pre_checkout_query_id={update.query_id}&ok=true"
            else:
                url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/answerPreCheckoutQuery?pre_checkout_query_id={update.query_id}&ok=false"

            r = requests.post(url)

            print(r.text)
        
        if(type(update.message.action) == types.MessageActionPaymentSentMe):
            subscription_id = update.message.action.payload
            if(subscription_id):
                user_id = update.message.peer_id.user_id
                await activate_the_subscription(app,subscription_id,user_id)

    except AttributeError:
        pass


raw_update_handler_function_handler = RawUpdateHandler(callback=raw_update_handler_function)

async def display_plan(bot,message):
    chat = message.chat
    plans ="--- Plan ---\n\n"
    btns = []
    user = db.users.find_one(user_id=message.chat.id)
    subscription = db.subscriptions.count(user_id=user['id'],status=1)
    if(subscription):
        subscription = db.subscriptions.find_one(user_id=user['id'],status=1)
        transaction = db.transactions.find_one(id=subscription['transaction_id'])
        plan = db.plans.find_one(id=transaction['plan_id'])
        user_active_plan_detail = f"\t\t Plan Detail\t\t\n\n Name: {plan['name']}\nNumber of Session: {plan['number_session']} sessions \n\n\nNote\n one session is {config.ONE_SESSION_IN_MINUTES} min only"
        await bot.send_message(chat_id=chat.id,text=user_active_plan_detail)

    else:

        for plan in db.plans.all():
            plans = plans +f"{plan['name']}\n{plan['description']}\n✔️ {plan['number_session']} sessions only.\n✔️ {plan['price'] if plan['price'] else 0} USD\n\n"
            btns.append(InlineKeyboardButton(plan['name'],callback_data=str(plan['id'])))

        button = InlineKeyboardMarkup([btns])
        plans = plans + f"--Note--\n 1 session is {config.ONE_SESSION_IN_MINUTES} minutes only."

        await bot.send_message(chat_id=chat.id,text=plans,reply_markup=button)


display_plan_handler = MessageHandler(callback=display_plan,filters=filters.regex('Plan'))


async def send_invoice(message):
    # create the subscription
    db_user = db.users.find_one(telegram_user_id=message.chat.id)
    plan =  db.plans.find_one(is_primary = 1)
    subscription = db.subscriptions.count(status = Status.PENDING.value,plan_id = plan['id'])
    if(subscription == 0):
        subscription = {
        'user_id':db_user['id'],
        'plan_id':plan['id'],
        'status': Status.PENDING.value,
        'uptime': 0,
        'welcome_message_sent':False,
        'created_at': datetime.now(),
        'updated_at' :datetime.now()
        }
        subscription_id = db.subscriptions.insert(subscription)
    else:
        subscription = db.subscriptions.find_one(status = Status.PENDING.value,plan_id = plan['id'])

        subscription_id = subscription['id']



    prices = [{"label": plan['name'], "amount": int(plan['price'])*100}]
    prices_json = json.dumps(prices)
    invoice = {
        'chat_id' : message.chat.id,
        'title':plan['name'],
        'description':plan['description'],
        'payload':str(subscription_id),
        'provider_token':config.PAYMENT_PROVIDER_TOKEN,
        'currency':'USD',
        'prices':prices_json,
        'start_parameter': str(subscription_id)
    }

    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendInvoice"

    r = requests.post(url,data=invoice)
    # message_id = r.json()['result']['message_id']

    


async def accepte_promo_code(bot,message):
    user = db.users.find_one()
    promo_code = message.text
    plan = db.plans.find_one(is_free=True)
    conv  = await get_conversation()
    if(promo_code == plan['promo_code']):    
        user = db.users.find_one(user_id=message.chat.id)
        db.transactions.update(dict(id=int(conv['txt_id']),status="success"),['id'])
        data = dict(
            user_id =  int(user['id']),
            transaction_id = int(conv['txt_id']),
            start_date=datetime.now(),
            due_date=datetime.now() + timedelta(days=30),
            uptime = 0
        )
        db.subscriptions.insert(data)
        await bot.send_message(chat_id = message.chat.id,text="you are successfully subscribed.enjoy it.")


    else:
        await bot.send_message(chat_id = message.chat.id,text="Invalid Promo code")
    
    db.conversations.delete()


accepte_promo_code_handler = MessageHandler(callback=accepte_promo_code,filters=filters.text & accepte_promocode_func_filter)


async def user_plan_preference(bot,callback_query):

    await callback_query.answer()
    plan =  db.plans.find_one(id=callback_query.data)

    if(plan['is_free']):
        # create transaction
        db_user = db.users.find_one(user_id=callback_query.message.chat.id)

        txt = {
            'user_id':db_user['id'],
            'plan_id':plan['id'],
            'status':'pending'
        }
        txt_id = db.transactions.insert(txt)

        # ask for promo code
        conv = {'que': "free_plan", 'txt_id': txt_id }
        db.conversations.insert(conv)
        await bot.send_message(chat_id = callback_query.message.chat.id,text="please enter the promo code")
    else:
        await send_invoice(bot,callback_query)


user_plan_preference_handler = CallbackQueryHandler(user_plan_preference,filters=filters.regex("1|2|3"))







async def account_detail(bot,message):
    account_detail = "\tPlan Detail\t\t\n\n"
    user = db.users.find_one(telegram_user_id=message.chat.id)

    subscription = db.subscriptions.count(user_id=int(user['id']),status = Status.ACTIVE.value)
    if(subscription):
        subscription = db.subscriptions.find_one(user_id=int(user['id']),status = Status.ACTIVE.value)
        plan = db.plans.find_one(id=int(subscription['plan_id']))
        plan_name = plan['name']
        plan_num_session = plan ['number_of_session']
        uptime = subscription['uptime']
        button= InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                "Start Session",
                url=f"t.me/{config.ASTROLOGER_TELEGRAM_HANDLER}"
                )
            ]
        ]
        )

        account_detail = account_detail + f"Plan: {plan_name}\nNumber of Session:{plan_num_session}\nRemaining Number of Session: {plan_num_session-(uptime//60)} sessions only"

        response = await bot.send_message(chat_id = message.chat.id,text = account_detail,reply_markup = button)

        # db.messages.insert({
        # 'telegram_user_id':message.chat.id,
        # 'message_id':None,
        # 'start_session_message_id': response.message_id,
        # 'is_close_session_button_sent' :False
        # })

    else:
        await bot.send_message(chat_id = message.chat.id,text = "sorry! you dont have active subscription.please buy a new one.")
        await send_invoice(message)






account_detail_handler = MessageHandler(callback=account_detail,filters=filters.regex("Account"))


@register
async def start(bot,message):
    query =  message.text.split(" ")[1] if len(message.text.split(" ")) == 2 else None
    await bot.send_message(chat_id = message.chat.id,text = f"wellcome {message.chat.first_name}")

    if(query == "buy_session"):
        await send_invoice(message)
    if(query == "start_session"):
        await account_detail(bot,message)








start_handler = MessageHandler(start,filters=filters.command('start'))

async def send_welcome_message_to_the_client_job():
    for subscription in db.subscriptions.find(welcome_message_sent = False):
        # send welcome message
        print("welcome message for new subscription")
        print(subscription)
        text = """
        Hi there,

        I'm an experienced astrologer, and I'm excited to connect with you on Telegram! I understand that astrology can be a powerful tool for gaining insight and guidance in life, and I'm here to help you navigate the stars.

        My approach is empathetic and focused on helping you find the answers you're seeking. Whether you want to gain insight into your current situation or need guidance about the future, I'm here to help.

        To start a session, simply click "START," and we can begin whenever you're ready. And don't hesitate to reach out whenever you need guidance - I'm available 24/7 to accommodate your schedule.

        I'm looking forward to helping you discover the power of astrology and guiding you on your journey. Let's get started! 🔮✨
        """

        button= InlineKeyboardMarkup(
        [
        [
        InlineKeyboardButton(
        "Start Session",
        callback_data="start_session"
        )
        ]
        ]
        )
        response = await app.send_message(
        chat_id= subscription['telegram_user_id'],
        text =  text,
        reply_markup= button
        )

        if(response):
            db.subscriptions.update(dict(id=int(subscription['id']),welcome_message_sent=True),['id'])



async def attach_button_for_pinned_post(bot,message):
        _bot = await bot.get_me()

        message_id = message.pinned_message.id

        button= InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Start Session",
                                url = f"t.me/{_bot.username}?start=start_session"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "Buy Session",
                                url = f"t.me/{_bot.username}?start=buy_session"
                            )
                        ]
                    ]
        )

        await bot.edit_message_reply_markup(
            chat_id = int(config.CHANNEL_ID),
            message_id = message_id,
            reply_markup = button
        )

attach_button_for_pinned_post_handler = MessageHandler(callback=attach_button_for_pinned_post,filters=filters.pinned_message)


# @only_for_registered
# @only_for_subscribers
# @has_session

@typing
@timeit(bot)
async def  prompt(app,message):
    return openai_helper.get_chat_response(message.chat.id,message.text)
    

prompt_handler = MessageHandler(prompt,filters=filters.text & filters.private & ~filters.bot & filters.incoming & ~filters.group & ~ filters.channel)



scheduler = AsyncIOScheduler()
# scheduler.add_job(job, "interval", seconds=int(config.SCHEDULER_INTERVAL_IN_SECONDS))
# scheduler.add_job(send_welcome_message_to_the_client_job,'interval',seconds=int(config.SCHEDULER_INTERVAL_IN_SECONDS))
# scheduler.start()
app.add_handler(prompt_handler)
bot.add_handler(start_handler)
bot.add_handler(attach_button_for_pinned_post_handler)
# bot.add_handler(display_plan_handler)
# bot.add_handler(user_plan_preference_handler)
# bot.add_handler(account_detail_handler)
# bot.add_handler(accepte_promo_code_handler)
# bot.add_handler(raw_update_handler_function_handler)
app.start()
bot.run()




