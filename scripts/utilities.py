import time
import re

#-----------------------------------------------------------------------
# Globals
#-----------------------------------------------------------------------

devMode = eval(getGlobalVariable('devMode'))

#setup 256 white space characters for usage with notifyBar
longSpace="                                                                "
longSpace=longSpace+longSpace+longSpace+longSpace

#Setup useful colors
highlight = {'faceoff':'#00C000', 'faceoffIgnored':'#006000', 'selection':'#C000FF'}
infoColor = '#000000'       #Used to inform of an action taken
errorColor = '#7F0000'      #Used for errors, player trying to do something illegal, etc.
warnColor = '#7F7F00'       #Used for warnings, unable to take an action, etc.
queryColor = '#00007F'      #Used to indicate action needs to be taken, select a card, etc.

#-----------------------------------------------------------------------
# Enumeration class
# Licensed under the GNU LGPL V3. See for more info:
# https://github.com/torrentails/Python-2.x-Enumeration-Class
#-----------------------------------------------------------------------
#Define the enum item class
class Enum_Item(object):
    _name = ''
    _type = ''
    _initiated = False
    def __init__(self, name, type):
        self._name = name
        self._type = type
    def __getattr__(self, name):
        if name == 'name':
            return self._name
        if name == 'type':
            return self._type
        else: raise AttributeError("No such attribute on 'Enum_Item' object.", name)
    def __setattr__(self, name, value):
        if self._initiated:
            raise NotImplementedError("'Enum_Item' object does not support attribute assignment", name, value)
        else: super(Enum_Item, self).__setattr__(name, value)

#Define the enum class
class Enum(object):
    _d = {}
    _name = ''
    _initiated = False
    def __init__(self, name, *enums):
        if type(name) != str: raise ValueError("Invalid name for object 'Enum'", name)
        if type(enums[0]) == list: enums = enums[0]
        for i in enums:
            if type(i) != str: raise TypeError("Enum values must be a string.", i)
            if enums.count(i) > 1: raise ValueError("Duplicate values not allowed.", i)
            self._d[i.upper().replace(' ','')] = Enum_Item(i, name)
        self._name = name
        self._initiated = True
    def __getattr__(self, a):
        try:
            return self._d[a.upper()]
        except KeyError:
            raise AttributeError("No enum value defined.", a)
        else:
            raise
    def __setattr__(self, a, v):
        if self._initiated:
            raise NotImplementedError("'Enum' object does not support attribute assignment")
        else: super(Enum, self).__setattr__(a, v)
    def __getitem__(self, k):
        return self._d[k.upper().replace(' ','')]
    def __name__(self):
        return self._name

#-----------------------------------------------------------------------
# Script loading and dispatcher functions
#-----------------------------------------------------------------------
    
def excecute(card, effectType, a={}, retVal=True):
    if   effectType == dispatch.onGameLoad:    e = OnGameLoad(card)
    elif effectType == dispatch.activatedList: e = ActivatedList(card)
    elif effectType == dispatch.activated:     e = Activated(card)
    elif effectType == dispatch.checkPlay:     e = CheckPlay(card)
    #TODO: PrePlayCard may be unnecessary; re-examine this when the core is more fleshed out.
    elif effectType == dispatch.prePlayCard:   e = PrePlayCard(card)
    elif effectType == dispatch.entersPlay:    e = EntersPlay(card)
    #TODO: Should we remove LeavesPlay as it can be set via events through EntersPlay?
    elif effectType == dispatch.leavesPlay:    e = LeavesPlay(card)
    elif effectType == dispatch.flipped:       e = Flipped(card)
    #TODO: Should we remove Moved as it can be set via events through EntersPlay?
    elif effectType == dispatch.moved:         e = Moved(card)
    elif effectType == dispatch.uncovered:     e = Uncovered(card)
    elif effectType == dispatch.confronted:    e = Confronted(card)
    elif effectType == dispatch.replaced:      e = Replaced(card)
    
    if e == "": return retVal
    whiteSpace = -1
    while e[0] == ' ':
        whiteSpace += 1
        e = e[1:]
    e = parseString(e, whiteSpace)
    
    a['card'] = card
    #whisper("{}".format(e))
    exec(e)
    return retVal
    
def parseString(str, ws):
    if ws == -1: ws = 0
    l = re.split("(/;|/`|;;|`|;,|;\.|; )",str)
    for i in range(len(l)):
        if l[i] == r'/;':    l[i] = ';'
        elif l[i] == r'/`':  l[i] = '`'
        elif l[i] == r';;':  l[i] = '"'
        elif l[i] == r'`':   l[i] = "'"
        elif l[i] == r';,':  l[i] = '<'
        elif l[i] == r';.':  l[i] = '>'
        elif l[i] == r'; ':
            l[i] = "\n"
            try:
                l[i+1] = l[i+1][ws:]
            except: pass
    return "".join(l)

#-----------------------------------------------------------------------
# Arbitrary data system
#-----------------------------------------------------------------------

dataDict = {}

def readData(name, default=''):
    if name not in dataDict: dataDict[name] = default
    return dataDict[name]

def popData(name, default=''):
    if name not in dataDict: return default
    return dataDict.pop(name)
    
def writeData(name, data):
    dataDict[name] = data
    
def reason(msg):
    writeData('reason', msg)

#-----------------------------------------------------------------------
# Internal helper functions
#-----------------------------------------------------------------------
        
def countTotalPower(player, col = "all"):
    power = 0
    for c in table:
        if isCharacter(c):
            if c.controller == player:
                cols = col in applyModifiers(modifier.color, {'card':c, 'colors':Colors(c)})['colors']
                if col == "all" or cols:
                    power += max(applyModifiers(modifier.power, {'card':c, 'power':Power(c)})['power'], 0)
    return power
    
def giveControl(lst):
    lst[0].setController(lst[1])

#-----------------------------------------------------------------------
# Misc Helper functions
#-----------------------------------------------------------------------

def notifyAll(col, message, alsoLog=True):
    mute()
    if alsoLog: notify(message)
    for p in players:
        remoteCall(p, 'notifyBar', [col,message+longSpace])
        
def whisperBar(col, message):
    mute()
    notifyBar(col, message+longSpace)
    whisper(message)
    
def isBoosted(card):
    return card.alternate == "Mane Character Boosted"

def shuffle(group=None):
    if group: group.shuffle()
    else: me.deck.shuffle()

def isPhase(p):
    return phase[getGlobalVariable("Phase")] == p

def isMyPhase(p):
    return isPhase(p) and me.isActivePlayer()
    
def isExhausted(card, truefalse):
    typList = TypeList(card)
    if cardType.resource in typList or cardType.troublemaker in typList or isCharacter(card):
        if inPlay(card):
            return card.orientation & Rot90 == Rot90
    if truefalse: return False
    return None
    
def isReady(card, truefalse=False):
    ex = isExhausted(card, truefalse)
    if ex == None:
        if trueFalse: return False
        else: return ex
    return not ex
    
def canExhaust(card):
    return isReady(card, True)
    
def canReady(card):
    return isExhausted(card, True)
    
def exhaust(card):
    mute()
    if canExhaust(card):
        card.orientation = Rot90
    
def ready(card):
    mute()
    if canExhaust(card):
        card.orientation = Rot0
    
def isCharacter(card):
    if cardType.friend in TypeList(card) or cardType.maneCharacter in TypeList(card):
        return cardType.character
    else: return False
    
def draw(ammount=1, note=True):
    mute()
    group = me.deck
    if type(ammount) != int:
        group = ammount
        ammount = 1
    if len(group) == 0:
        whisperBar(warnColor, "You don't have any cards in your {} to draw.".format(group.name))
        return
    if len(group) < ammount:
        whisperBar(errorColor, "Ran out of cards in your {} to draw.".format(group.name))
        ammount = len(group)
    for card in group.top(ammount):
        card.moveTo(me.hand)
    if note:
        if ammount == 1: notifyAll(infoColor, "{} draws a card.".format(me))
        else: notifyAll(infoColor, "{} draws {} cards.".format(me,ammount))