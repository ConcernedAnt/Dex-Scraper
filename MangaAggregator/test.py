from datetime import datetime
string = "2020-06-29 23:26:42"
publish_date = datetime.strptime(string, '%Y-%m-%d %H:%M:%S')

print(publish_date)
