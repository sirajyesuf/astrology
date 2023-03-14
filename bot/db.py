import dataset

db = dataset.connect('sqlite:////home/siraj/Documents/projects/upwork/adam/admin/adam_astrologer')
users = db['users']
plans = db['plans']
transactions = db['transactions']
subscriptions = db['subscriptions']
conversations = db['conversations']
query = db.query