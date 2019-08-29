from Classes.TPBUser import TPBParser

parser = TPBParser()
TPBParser.feed('<img src="python-logo.png" alt="The Python logo">')
print(TPBParser.get_torrents)
