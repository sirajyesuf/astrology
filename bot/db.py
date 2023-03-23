import dataset

db = dataset.connect('sqlite:////home/siraj/Documents/projects/upwork/adam/astrologer/admin/database/database.db')
users = db['users']
plans = db['plans']
transactions = db['transactions']
subscriptions = db['subscriptions']
conversations = db['conversations']
messages = db['messages']
histories = db['histories']
settings = db['settings']
query = db.query


def get_setting():
    for setting in settings.all():
        return setting
