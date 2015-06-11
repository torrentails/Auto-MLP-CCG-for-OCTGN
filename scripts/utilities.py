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
    if   effectType == dispatch.onGameLoad:    e,p = OnGameLoad(card),True
    elif effectType == dispatch.activatedList: e,p = ActivatedList(card),True
    elif effectType == dispatch.activated:     e,p = Activated(card),False
    elif effectType == dispatch.checkPlay:     e,p = CheckPlay(card),True
    #TODO: PrePlayCard may be unnecessary; re-examine this when the core is more fleshed out.
    elif effectType == dispatch.prePlayCard:   e,p = PrePlayCard(card),True
    elif effectType == dispatch.entersPlay:    e,p = EntersPlay(card),False
    #TODO: Should we remove LeavesPlay as it can be set via events through EntersPlay?
    elif effectType == dispatch.leavesPlay:    e,p = LeavesPlay(card),False
    elif effectType == dispatch.flipped:       e,p = Flipped(card),False
    #TODO: Should we remove Moved as it can be set via events through EntersPlay?
    elif effectType == dispatch.moved:         e,p = Moved(card),False
    elif effectType == dispatch.uncovered:     e,p = Uncovered(card),False
    elif effectType == dispatch.confronted:    e,p = Confronted(card),False
    elif effectType == dispatch.replaced:      e,p = Replaced(card),False
    
    if e == "": return retVal
    if p or isPPPEnabled():
        whiteSpace = -1
        while e[0] == ' ':
            whiteSpace += 1
            e = e[1:]
        e = parseString(e, whiteSpace)
        a['card'] = card
        exec(e)
    else: addPPP(excecute, card, effectType, a, retVal)
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

def readData(name, default=None):
    if name not in dataDict: return default
    return dataDict[name]

def popData(name, default=None):
    if name not in dataDict: return default
    return dataDict.pop(name)
    
def writeData(name, data):
    dataDict[name] = data
    
def reason(msg):
    writeData('reason', msg)

#-----------------------------------------------------------------------
# Context manager
#-----------------------------------------------------------------------

context = {}

def setContext(**kargs):
    global context
    context = kargs
    remoteCall(players[1], setContext, [**kargs])
    
def clearContext():
    global context
    context = {}
    remoteCall(players[1], flushContext, [])

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
        if isInPlay(card):
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
    if isReady(card, True) == True:
        return applyModifiers(modifier.canExhaust, {'card':card, 'isReady':True})['isReady']
    return False
    
def canReady(card):
    if isExhausted(card, True) == True:
        return applyModifiers(modifier.canReady, {'card':card, 'isExhausted':True})['isExhausted']
    return False
    
def exhaust(card):
    mute()
    if card.controler != me:
        remoteCall(card.controler, 'exhaust', [card])
        return
    if canExhaust(card):
        if not fireEvent(preEvent.exhaust, card=card):
            card.orientation = Rot90
            fireEvent(event.exhaust, card=card)
    
def ready(card):
    mute()
    if card.controler != me:
        remoteCall(card.controler, 'ready', [card])
        return
    if canReady(card):
        if not fireEvent(preEvent.ready, card=card):
            card.orientation = Rot0
            fireEvent(event.ready, card=card)
    
def isCharacter(card):
    if cardType.friend in TypeList(card) or cardType.maneCharacter in TypeList(card):
        return cardType.character
    else: return False
    
def getTurnPlayer():
    return Player(eval(setGlobalVariable('turnPlayer')))
    
def draw(amount=1, player=me note=True):
    mute()
    if player != me:
        remoteCall(player, 'draw', [amount, player, note])
        return
    deck = me.deck
    if len(deck) == 0:
        whisperBar(warnColor, "You don't have any cards in your {} to draw.".format(deck.name))
        return
    dict={'amount':amount}
    applyModifiers(modifier.drawCard, dict)
    if dict['amount'] > 0:
        if not fireEvent(preEvent.draw, **dict):
            if len(deck) < dict['amount']:
                whisperBar(errorColor, "Ran out of cards in your {} to draw.".format(deck.name))
                dict['amount'] = len(deck)
            disablePPP()
            for card in deck.top(dict['amount']):
                moveToLocation(card, location.hand)
                update()
                fireEvent(event.draw, **dict)
            enablePPP()
            if note:
                if dict['amount'] == 1: notifyAll(infoColor, "{} draws a card.".format(me))
                else: notifyAll(infoColor, "{} draws {} cards.".format(me,dict['amount']))

def gainAT(amount):
    dict = {'amount':amount}
    applyModifiers(modifier.gainAT, dict)
    if dict['amount'] > 0:
        if not fireEvent(preEvent.gainAT, **dict):
            me.counters['AT'].value += dict['amount']
            if dict['amount'] == 1: notifyAll("{} gains an Actions Token.".format(me)
            else: notifyAll("{} gains {} Actions Tokens.".format(me, dict['amount'])
            fireEvent(event.gainAT, **dict)
            
def loseAT(amount, spent=False):
    dict = {'amount':amount, 'spent':spent}
    applyModifiers(modifier.loseAT, dict)
    if dict['amount'] > 0:
        if not fireEvent(preEvent.loseAT, **dict):
            me.counters['AT'].value -= dict['amount']
            fireEvent(event.loseAT, **dict)

def spendAT(amount):
    loseAT(amount, True)

def gainPoints(amount):
    dict = {'amount':amount}
    applyModifiers(modifier.gainPoints, dict)
    if dict['amount'] > 0:
        if not fireEvent(preEvent.gainPoints, **dict):
            me.counters['Points'].value += dict['amount']
            if dict['amount'] == 1: notifyAll("{} gains a Point.".format(me)
            else: notifyAll("{} gains {} Points.".format(me, dict['amount'])
            fireEvent(event.gainPoints, **dict).

def losePoints(amount):
    dict = {'amount':amount}
    applyModifiers(modifier.losePoints, dict)
    if dict['amount'] > 0:
        if not fireEvent(preEvent.losePoints, **dict):
            me.counters['Points'].value += dict['amount']
            if dict['amount'] == 1: notifyAll("{} loses a Point.".format(me)
            else: notifyAll("{} loses {} Points.".format(me, dict['amount'])
            fireEvent(event.losePoints, **dict)