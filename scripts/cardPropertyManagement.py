import re

#-----------------------------------------------------------------------
# Card defaults
#-----------------------------------------------------------------------

#TODO: Rewrite as a class extension of Card

#Dictionary of cards with overwritten properties
cardDefaults = {}

def initializeCardDefaults(cardList):
    for card in cardList: writeDefaults(card)

def writeDefaults(card):
    cardDefaults[card._id] = [{},{}]
    d = cardDefaults[card._id][0]
    d["Title"] = card.name#.replace(' ','')
    d["Subtitle"] = card.Subtitle#.replace(' ','')
    d["Name"] = d["Title"]
    if d["Subtitle"] != '': d["Name"] = d["Name"] + ', ' + d["Subtitle"]
    d["Number"] = card.Number.replace(' ','')
    d["Type"] = cardType[card.Type.replace(' ','')]
    d["Traits"] = parseDefaultTraits(card.Traits)
    d["Colors"] = parseDefaultColors(card.Colors)
    if card.Power == '': d["Power"] = -1
    else: d["Power"] = int(card.Power)
    if card.Cost == '': d["Cost"] = -1
    else: d["Cost"] = int(card.Cost)
    d["PlayRequirements"] = parseDefaultPlayRequirements(card.PlayRequirements)
    d["Keywords"] = parseDefaultKeywords(card.Keywords)
    d["Text"] = card.Text
    if card.BonusPoints == '': d["BonusPoints"] = -1
    else: d["BonusPoints"] = int(card.BonusPoints)
    d["YourRequirements"] = parseDefaultYourRequirements(card.YourRequirements)
    d["OpponentsRequirements"] = parseDefaultOpponentsRequirements(card.OpponentsRequirements)
    d["Rarity"] = card.Rarity.replace(' ','')
    d["OnGameLoad"] = card.OnGameLoad
    d["ActivatedList"] = card.ActivatedList
    d["Activated"] = card.Activated
    d["CheckPlay"] = card.CheckPlay
    d["PrePlayCard"] = card.PrePlayCard
    d["EntersPlay"] = card.EntersPlay
    d["LeavesPlay"] = card.LeavesPlay
    d["Flipped"] = card.Flipped
    d["Moved"] = card.Moved
    d["Uncovered"] = card.Uncovered
    d["Confront"] = card.Confront
    d["Replaced"] = card.Replaced
    if card.Type == "Mane Character":
        alt = "Mane Character Boosted"
        a = cardDefaults[card._id][1]
        a["Title"] = card.alternateProperty(alt,'Name')#.replace(' ','')
        a["Subtitle"] = card.alternateProperty(alt,'Subtitle')#.replace(' ','')
        a["Name"] = a["Title"]
        if a["Subtitle"] != '': a["Name"] = a["Name"] + ', ' + a["Subtitle"]
        a["Number"] = card.alternateProperty(alt,'Number').replace(' ','')
        a["Type"] = cardType[card.Type.replace(' ','')]
        a["Traits"] = parseDefaultTraits(card.alternateProperty(alt,'Traits'))
        a["Colors"] = parseDefaultColors(card.alternateProperty(alt,'Colors'))
        if card.alternateProperty(alt,'Power') == '': a["Power"] = -1
        else: a["Power"] = int(card.alternateProperty(alt,'Power'))
        if card.alternateProperty(alt,'Cost') == '': a["Cost"] = -1
        else: a["Cost"] = int(card.alternateProperty(alt,'Cost'))
        a["PlayRequirements"] = parseDefaultPlayRequirements(card.alternateProperty(alt,'PlayRequirements'))
        a["Keywords"] = parseDefaultKeywords(card.alternateProperty(alt,'Keywords'))
        a["Text"] = card.alternateProperty(alt,'Text')
        if card.alternateProperty(alt,'BonusPoints') == '': a["BonusPoints"] = -1
        else: a["BonusPoints"] = int(card.alternateProperty(alt,'BonusPoints'))
        a["YourRequirements"] = parseDefaultYourRequirements(card.alternateProperty(alt,'YourRequirements'))
        a["OpponentsRequirements"] = parseDefaultOpponentsRequirements(card.alternateProperty(alt,'OpponentsRequirements'))
        a["Rarity"] = card.alternateProperty(alt,'Rarity').replace(' ','')
        a["OnGameLoad"] = card.alternateProperty(alt,'OnGameLoad')
        a["ActivatedList"] = card.alternateProperty(alt,'ActivatedList')
        a["Activated"] = card.alternateProperty(alt,'Activated')
        a["CheckPlay"] = card.alternateProperty(alt,'CheckPlay')
        a["PrePlayCard"] = card.alternateProperty(alt,'PrePlayCard')
        a["EntersPlay"] = card.alternateProperty(alt,'EntersPlay')
        a["LeavesPlay"] = card.alternateProperty(alt,'LeavesPlay')
        a["Flipped"] = card.alternateProperty(alt,'Flipped')
        a["Moved"] = card.alternateProperty(alt,'Moved')
        a["Uncovered"] = card.alternateProperty(alt,'Uncovered')
        a["Confront"] = card.alternateProperty(alt,'Confront')
        a["Replaced"] = card.alternateProperty(alt,'Replaced')
        

def updateDefaults(overideList):
    for card_id, value in overideList:
        cardDefaults[card_id] = value

def syncDefaults():
    for p in players:
        if p != me:
            remoteCall(p, updateDefaults, [cardDefaults])
            
def parseDefaultTraits(string):
    l = parseDefaultList(string)
    for i in range(len(l)):
        l[i] = trait[l[i]]
    return l
        
def parseDefaultColors(string):
    l = parseDefaultList(string)
    for i in range(len(l)):
        l[i] = color[l[i]]
    return l
        
def parseDefaultPlayRequirements(string):
    l = parseDefaultDict(string)
    d = {}
    for i in l:
        d[color[i[0]]] = int(i[1])
    return d
        
def parseDefaultKeywords(string):
    d = {}
    if string == '': return d
    s = []
    l = re.split("(,|, )",string)
    for i in range(len(l)):
        if l[i] != r', ' and l[i] != r',': s.append(l[i])
    
    for v in s:
        n = ''
        if v.endswith(('0','1','2','3','4','5','6','7','8','9')):
            n = int(v[-1])
            v = v[:-2]
        d[keyword[v.replace(' ','')]] = n
    return d

def parseDefaultYourRequirements(string):
    l = parseDefaultDict(string)
    d = {}
    for i in l:
        d[colorRequirement[i[0]]] = int(i[1])
    return d

def parseDefaultOpponentsRequirements(string):
    l = parseDefaultDict(string)
    d = {}
    for i in l:
        d[colorRequirement[i[0]]] = int(i[1])
    return d
            
def parseDefaultList(string):
    lst = []
    if string == '': return lst
    l = re.split("(,|, )",string)
    for i in range(len(l)):
        if l[i] != r', ' and l[i] != r',': lst.append(l[i].replace(' ',''))
    return lst
    
def parseDefaultDict(string):
    lst = []
    if string == '': return lst
    s = []
    l = [x for x in re.split(",|, | ",string) if x != '']
    for i in range(len(l)):
        if i < len(l):
            if l[i] != r', ' and l[i] != r',' and l[i] != r' ': s.append(l[i])
    for n in range(len(l)):
        if n%2 != 0:
            lst.append([l[n].replace(' ',''),l[n-1]])
    return lst

def default_name(card):
    return cardDefaults[card._id][int(isBoosted(card))]['Name']
    
def default_title(card):
    return cardDefaults[card._id][int(isBoosted(card))]['Title']
        
def default_subtitle(card):
    return cardDefaults[card._id][int(isBoosted(card))]['Subtitle']
        
def default_number(card):
    return cardDefaults[card._id][int(isBoosted(card))]['Number']
        
def default_type(card):
    return cardDefaults[card._id][int(isBoosted(card))]['Type']
        
def default_traits(card):
    return cardDefaults[card._id][int(isBoosted(card))]['Traits']
        
def default_colors(card):
    return cardDefaults[card._id][int(isBoosted(card))]['Colors']
        
def default_power(card):
    return cardDefaults[card._id][int(isBoosted(card))]['Power']
        
def default_cost(card):
    return cardDefaults[card._id][int(isBoosted(card))]['Cost']
        
def default_play_requirements(card):
    return cardDefaults[card._id][int(isBoosted(card))]['PlayRequirements']
        
def default_keywords(card):
    return cardDefaults[card._id][int(isBoosted(card))]['Keywords']
        
def default_text(card):
    return cardDefaults[card._id][int(isBoosted(card))]['Text']
        
def default_bonus_points(card):
    return cardDefaults[card._id][int(isBoosted(card))]['BonusPoints']
        
def default_your_requirements(card):
    return cardDefaults[card._id][int(isBoosted(card))]['YourRequirements']
        
def default_opponents_requirements(card):
    return cardDefaults[card._id][int(isBoosted(card))]['OpponentsRequirements']
        
def default_rarity(card):
    return cardDefaults[card._id][int(isBoosted(card))]['Rarity']
        
def default_on_game_load(card):
    return cardDefaults[card._id][int(isBoosted(card))]['OnGameLoad']
        
def default_activated_list(card):
    return cardDefaults[card._id][int(isBoosted(card))]['ActivatedList']
        
def default_activated(card):
    return cardDefaults[card._id][int(isBoosted(card))]['Activated']
        
def default_pre_play_card(card):
    return cardDefaults[card._id][int(isBoosted(card))]['PrePlayCard']
    
def default_check_play(card):
    return cardDefaults[card._id][int(isBoosted(card))]['CheckPlay']
        
def default_enters_play(card):
    return cardDefaults[card._id][int(isBoosted(card))]['EntersPlay']
        
def default_leaves_play(card):
    return cardDefaults[card._id][int(isBoosted(card))]['LeavesPlay']
        
def default_flipped(card):
    return cardDefaults[card._id][int(isBoosted(card))]['Flipped']
        
def default_moved(card):
    return cardDefaults[card._id][int(isBoosted(card))]['Moved']
        
def default_uncovered(card):
    return cardDefaults[card._id][int(isBoosted(card))]['Unconvered']
        
def default_confront(card):
    return cardDefaults[card._id][int(isBoosted(card))]['Confronted']
        
def default_replaced(card):
    return cardDefaults[card._id][int(isBoosted(card))]['Replaced']
        
#-----------------------------------------------------------------------
# Card property override system
#-----------------------------------------------------------------------

#TODO: mostly depreciated by the modifiers system. May remove in the near future

#Dictionary of cards with overwritten properties
cardOverideDict = {}

def updateOverides(overideList):
    for card_id, value in overideList:
        cardOverideDict[card_id] = value

def syncOverides():
    for p in players:
        if p != me:
            remoteCall(p, updateOverides, [cardOverideDict])
            
def override(card, prop, val=None):
    i = int(isBoosted(card))
    if val:
        if not card._id in cardOverideDict: cardOverideDict[card._id] = [{},{}]
        cardOverideDict[card._id][i][prop] = val
        syncOverides()
    if card._id in cardOverideDict and prop in cardOverideDict[card._id][i]:
        return cardOverideDict[card._id][i][prop]
    else:
        return None

def Name(card, val=None):
    return override(card, 'Name', val) or default_name(card)

def Title(card, val=None):
    return override(card, 'Title', val) or default_title(card)
        
def Subtitle(card, val=None):
    return override(card, 'Subtitle', val) or default_subtitle(card)
        
def Number(card, val=None):
    return override(card, 'Number', val) or default_number(card)
        
def Type(card, val=None):
    return override(card, 'Type', val) or default_type(card)
        
def Traits(card, val=None):
    return override(card, 'Traits', val) or default_traits(card)
        
def Colors(card, val=None):
    return override(card, 'Colors', val) or default_colors(card)
        
def Power(card, val=None):
    return override(card, 'Power', val) or default_power(card)
        
def Cost(card, val=None):
    return override(card, 'Cost', val) or default_cost(card)
        
def PlayRequirements(card, val=None):
    return override(card, 'PlayRequirements', val) or default_play_requirements(card)
        
def Keywords(card, val=None):
    return override(card, 'Keywords', val) or default_keywords(card)
        
def Text(card, val=None):
    return override(card, 'Text', val) or default_text(card)
        
def BonusPoints(card, val=None):
    return override(card, 'BonusPoints', val) or default_bonus_points(card)
        
def YourRequirements(card, val=None):
    return override(card, 'YourRequirements', val) or default_your_requirements(card)
        
def OpponentsRequirements(card, val=None):
    return override(card, 'OpponentsRequirements', val) or default_opponents_requirements(card)
        
def Rarity(card, val=None):
    return override(card, 'Rarity', val) or default_rarity(card)
        
def OnGameLoad(card, val=None):
    return override(card, 'OnGameLoad', val) or default_on_game_load(card)
        
def ActivatedList(card, val=None):
    return override(card, 'ActivatedList', val) or default_activated_list(card)
    
def Activated(card, val=None):
    return override(card, 'Activated', val) or default_activated(card)
        
def PrePlayCard(card, val=None):
    return override(card, 'PrePlayCard', val) or default_pre_play_card(card)
        
def CheckPlay(card, val=None):
    return override(card, 'CheckPlay', val) or default_check_play(card)
        
def EntersPlay(card, val=None):
    return override(card, 'EntersPlay', val) or default_enters_play(card)
        
def LeavesPlay(card, val=None):
    return override(card, 'LeavesPlay', val) or default_leaves_play(card)
        
def Flipped(card, val=None):
    return override(card, 'Flipped', val) or default_flipped(card)
        
def Moved(card, val=None):
    return override(card, 'Moved', val) or default_moved(card)
        
def Uncovered(card, val=None):
    return override(card, 'Uncovered', val) or default_uncovered(card)
        
def Confront(card, val=None):
    return override(card, 'Confronted', val) or default_confront(card)
        
def Replaced(card, val=None):
    return override(card, 'Replaced', val) or default_solved(card)