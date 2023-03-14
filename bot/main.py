import config
from bot import Astrologer
import logging
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


bot_config = {
    'bot_token' : config.TELEGRAM_BOT_TOKEN,
    'api_hash': config.API_HASH,
    'api_id' : config.API_ID
}

def main():
    Astrologer(config=bot_config).run()




if __name__ == '__main__':
    main()