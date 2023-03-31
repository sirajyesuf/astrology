from datetime import datetime

date_string1 = "2023-03-25 23:20:43"
date_string2 = "2023-03-26 00:45:43"

date_obj1 = datetime.strptime(date_string1, '%Y-%m-%d %H:%M:%S').timestamp()
date_obj2 = datetime.strptime(date_string2, '%Y-%m-%d %H:%M:%S').timestamp()

minu = (date_obj2 - date_obj1)/60
print(minu/10)