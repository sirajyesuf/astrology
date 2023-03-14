import config
# Setup configurations
openai_config = {

    'api_key': config.OPENAI_API_TOKEN,
    'show_usage': bool(config.SHOW_USAGE),
    'max_history_size':int(config.MAX_HISTORY_SIZE),
    'max_conversation_age_minutes': int(config.MAX_CONVERSATION_AGE_MINUTES),
    'assistant_prompt': config.ASSISTANT_PROMPT,
    'max_tokens': int(config.MAX_TOKENS),

    # 'gpt-3.5-turbo' or 'gpt-3.5-turbo-0301'
    'model': 'gpt-3.5-turbo',

    # Number between 0 and 2. Higher values like 0.8 will make the output more random,
    # while lower values like 0.2 will make it more focused and deterministic.
    'temperature': 1,

    # How many chat completion choices to generate for each input message.
    'n_choices': 1,

    # Number between -2.0 and 2.0. Positive values penalize new tokens based on whether
    # they appear in the text so far, increasing the model's likelihood to talk about new topics.
    'presence_penalty': 0,

    # Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing
    # frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.
    'frequency_penalty': 0,

    # The DALL·E generated image size
    'image_size': '512x512'
}
from openai_helper import OpenAIHelper
openai_helper = OpenAIHelper(config=openai_config)
import config
from pyrogram import Client,filters
from pyrogram.handlers import MessageHandler,CallbackQueryHandler,RawUpdateHandler
import config
from openai_helper import OpenAIHelper
from pyrogram.types import (InlineKeyboardMarkup,InlineKeyboardButton,ReplyKeyboardMarkup,)
import db
import requests
import json
from pyrogram.raw import types
from datetime import datetime,timedelta
from decorators  import only_for_subscribers,only_for_registered,only_unsubscribers,has_session,timeit
from apscheduler.schedulers.asyncio import AsyncIOScheduler

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
async def add_subscription(app,txt_id,user_id):
    # update the transaction
    db.transactions.update(dict(id=txt_id,status="success"),['id'])
    data = dict(
        transaction_id = txt_id,
        start_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=30),
        uptime = 0
    )
    db.subscriptions.insert(data)

    msg = "Your payment is successfully processed.thanks!\n\n you are now subscribed."
    await app.send_message(chat_id = user_id,text = msg)

async def raw_update_handler_function(app,update,users,chats):
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
            if(db.transactions.count(id=update.payload,status='pending')):
                url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/answerPreCheckoutQuery?pre_checkout_query_id={update.query_id}&ok=true"
            else:
                url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/answerPreCheckoutQuery?pre_checkout_query_id={update.query_id}&ok=false"

            requests.post(url)
        
        if(type(update.message.action) == types.MessageActionPaymentSentMe):
            txt_id = update.message.action.payload
            if(txt_id):
                user_id = update.message.peer_id.user_id
                await add_subscription(app,txt_id,user_id)

    except AttributeError:
        pass


raw_update_handler_function_handler = RawUpdateHandler(callback=raw_update_handler_function)

@only_for_registered
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


async def send_invoice(app,callback_query):
    # create the transaction
    db_user = db.users.find_one(user_id=callback_query.message.chat.id)
    plan =  db.plans.find_one(id=callback_query.data)

    txt = {
        'user_id':db_user['id'],
        'plan_id':plan['id'],
        'status':'pending'
    }
    txt_id = db.transactions.insert(txt)
    pt = "284685063:TEST:NmMzNTI3NTdkNWJm"
    prices = [{"label": plan['name'], "amount": plan['price']*100}]
    prices_json = json.dumps(prices)
    invoice = {
        'chat_id' : callback_query.message.chat.id,
        'title':plan['name'],
        'description':plan['description'],
        'payload':str(txt_id),
        'provider_token':pt,
        'currency':'USD',
        'prices':prices_json,
        'start_parameter': str(txt_id)
    }

    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendInvoice"

    r = requests.post(url,data=invoice)


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
    account_detail = "\t\tAccount Detail\t\t\n\n"
    user = db.users.find_one(user_id=message.chat.id)
    plan_name = "No Active Plan"
    subscription = db.subscriptions.count(user_id=int(user['id']),status = True)
    if(subscription):
        subscription = db.subscriptions.find_one(user_id=int(user['id']),status = True)
        transaction = db.transactions.find_one(id=int(subscription['transaction_id']))
        plan = db.plans.find_one(id=int(transaction['plan_id']))
        plan_name = plan['name']

    
    fn = user['first_name']
    ln = user.get('last_name',None)
    account_detail = account_detail + f"First Name: {fn}\n" + f"Last Name: {ln}\n" + f"Plan: {plan_name}"

    await bot.send_message(chat_id = message.chat.id,text = account_detail)

account_detail_handler = MessageHandler(callback=account_detail,filters=filters.regex("Account"))

async def start(bot,message):
    # send the main menu
    main_menu = ReplyKeyboardMarkup(
                [
                    ["Account", "Plan"],
                    ["Help","About Us"],
               
                ],
                resize_keyboard=True
            )
    await bot.send_message(chat_id = message.chat.id,text = "hello wellcome back!",reply_markup = main_menu)








start_handler = MessageHandler(start,filters=filters.command('start'))

async def post(bot,message):
        _bot =  await bot.get_me()
        text="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum"
        button= InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Start Session",
                                url = f"http://t.me/{config.ASTROLOGER_TELEGRAM_HANDLER}"
                            ),
                            InlineKeyboardButton(
                                "Add Account",
                                url = f"http://t.me/{_bot.username}?start=add_acount"
                            ),
                        ]
                    ]
        )

        await bot.send_message(chat_id=int(config.CHANNEL_ID),text=text,reply_markup=button)

post_handler = MessageHandler(post,filters=filters.command('post'))


@only_for_registered
@only_for_subscribers
@has_session
@timeit
async def  prompt(app,message):
    result = openai_helper.get_chat_response(message.chat.id,message.text)
    response = await app.send_message(chat_id = message.chat.id,text=result)
    return response

prompt_handler = MessageHandler(prompt,filters=filters.text & filters.private & ~filters.bot & filters.incoming & ~filters.group & ~ filters.channel)

class Astrologer:


    def __init__(self,config:dict) -> None:
        self.config = config
    
    def run(self):
        app= Client("astrologer",api_id= self.config['api_id'],api_hash=self.config['api_hash'])
        bot=Client("bot",api_id=self.config['api_id'],api_hash=self.config['api_hash'],bot_token=self.config['bot_token'])

        scheduler = AsyncIOScheduler()
        scheduler.add_job(job, "interval", seconds=int(config.SCHEDULER_INTERVAL_IN_SECONDS))
        scheduler.start()
        app.add_handler(prompt_handler)
        bot.add_handler(start_handler)
        bot.add_handler(post_handler)
        bot.add_handler(display_plan_handler)
        bot.add_handler(user_plan_preference_handler)
        bot.add_handler(account_detail_handler)
        bot.add_handler(accepte_promo_code_handler)
        bot.add_handler(raw_update_handler_function_handler)
        app.start()
        bot.run()




