from Classes.TPBUser import TPBUser

user = TPBUser()
with open('text.html', 'r') as f:
    text = f.read()

print(user.get_torrents_from_string(text))
