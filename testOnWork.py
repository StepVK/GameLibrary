from Classes.TPBUser import TPBUser

user = TPBUser()
with open('text.html', 'r') as f:
    text = ''.join([line.strip() for line in f.readlines()])
    text = text.replace('\n', '')

print(*user.get_torrents_from_string(text))
