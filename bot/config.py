from decouple import config

API_ID = config("API_ID")
API_HASH = config("API_HASH")
TELEGRAM_BOT_TOKEN = config("TELEGRAM_BOT_TOKEN")
OPENAI_API_TOKEN = config("OPENAI_API_TOKEN")
ASSISTANT_PROMPT=config("ASSISTANT_PROMPT")
SHOW_USAGE=config("SHOW_USAGE")
MAX_TOKENS=config("MAX_TOKENS")
MAX_HISTORY_SIZE=config("MAX_HISTORY_SIZE")
MAX_CONVERSATION_AGE_MINUTES=config("MAX_CONVERSATION_AGE_MINUTES")
CHANNEL_ID = config("CHANNEL_ID")
ASTROLOGER_TELEGRAM_HANDLER = config("ASTROLOGER_TELEGRAM_HANDLER")
BOT_USERNAME = config("BOT_USERNAME")
ONE_SESSION_IN_MINUTES = config("ONE_SESSION_IN_MINUTES")
SCHEDULER_INTERVAL_IN_SECONDS = config("SCHEDULER_INTERVAL_IN_SECONDS")
STRIPE_PAYMENT_LINK = config("STRIPE_PAYMENT_LINK")