import dataset

db = dataset.connect('sqlite:////home/siraj/Documents/projects/upwork/adam/astrologer/admin/database/database.db')
users = db['users']
plans = db['plans']
transactions = db['transactions']
subscriptions = db['subscriptions']
conversations = db['conversations']
messages = db['messages']
histories = db['histories']
query = db.query