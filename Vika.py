n = int(input())
addonemorestepcounter = 0
actualLines = 0


def addOneMoreStep(openedBrackets, closedBrackets, n, currentString, open=True):
    global addonemorestepcounter
    if open:
        currentString += '('
        openedBrackets += 1
    else:
        currentString += ')'
        closedBrackets += 1
    if openedBrackets == n:
        currentString += ')' * (n - closedBrackets)
        global actualLines
        actualLines += 1
        # print(currentString)
    else:
        addonemorestepcounter += 1
        addOneMoreStep(openedBrackets, closedBrackets, n, currentString)
        if openedBrackets > closedBrackets:
            addonemorestepcounter += 1
            addOneMoreStep(openedBrackets, closedBrackets,
                           n, currentString, False)


openedBrackets = 0
closedBrackets = 0
currentString = ''
addonemorestepcounter += 1
addOneMoreStep(openedBrackets, closedBrackets, n, currentString)
print(addonemorestepcounter)
print(actualLines)
