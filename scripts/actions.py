import re
import time

#-----------------------------------------------------------------------
# Table actions
#-----------------------------------------------------------------------

def cancelPlayingCard(group, x = 0, y = 0):
    """This action is called when the user presses the Esc key on their keyboard and is used to cancel playing a card."""
    if eval(getGlobalVariable('playingCard_player')) == me._id:
        setGlobalVariable('playingCard_player', 'None')
        card = Card(eval(getGlobalVariable('playingCard_card')))
        whisperBar(warnColor, "Cancelled playing {}".format(card))
        return

def tableActivate(group, x = 0, y = 0):
    """The primary action of the game, called by pressing the Space bar. The function will first check if a card being played is awaiting selection and, if so, will play the card to home; else function checks for priority and checks for and activates the card's effect."""
    if eval(getGlobalVariable('playingCard_player')) == me._id:
        playCard(location.home)
        return

def activate(card, x = 0, y = 0):
    """Called when a card is clicked once. It will check if an action or a card being played is awaiting selection and, if so, will select the card/play the card being played to the clicked card's location. If not, then event.preClickCard and event.clickCard are fired."""
    if eval(getGlobalVariable('playingCard_player')) == me._id:
        playCard(location.home)
        return
    lst = excecute(card, dispatch.activatedList, retVal=False)
    if lst != False and lst != None:
        if lst == True or len(lst) == 1:
            msg = excecute(card, dispatch.activated, {'effect':1}, retVal='')
            notifyAll(infoColor, "{} activates the effect of {}".format(me, card)+msg)
        elif len(lst) > 1:
            colorsList = []
            for i in range(len(lst)):
                if type(lst[i]) == list:
                    colorsList.append(lst[i][1])
                    lst[i] = lst[i][0]
                else: colorsList.append('#000000')
            choice = askChoice("Activate an effect of {}".format(card), lst, colorsList, customButtons = ["Cancel"])
            if choice == -1: return
            msg = excecute(card, dispatch.activated, {'effect':choice}, retVal='')
            notifyAll(infoColor, "{} activates the {} effect of {}".format(me, lst[choice], card)+msg)
    
def onClickCard(card, x = 0, y = 0):
    """Called when a card is clicked once. It will check if an action or a card being played is awaiting selection and, if so, will select the card/play the card being played to the clicked card's location. If not, then event.preClickCard and event.clickCard are fired. Finally, if it is not cancelled by event.preClickCard, the function will make a call to activate."""
    if eval(getGlobalVariable('playingCard_player')) == me._id:
        if inPlay(card):
            playCard(getLocation(card))
        return
    if fireEvent(event.preClickCard, card=card, doubleClick=False) == True: return
    fireEvent(event.clickCard, card=card, doubleClick=False)

def onDoubleClick(card, x = 0, y = 0):
    """Called when a card is clicked once. It will check if an action or a card being played is awaiting selection and, if so, will select the card/play the card being played to the clicked card's location. If not, then event.preClickCard and event.clickCard are fired. Finally, if it is not cancelled by event.preClickCard, the function will make a call to activate."""
    if eval(getGlobalVariable('playingCard_player')) == me._id:
        if inPlay(card):
            playCard(getLocation(card))
        return
    if fireEvent(event.preClickCard, card=card, doubleClick=True) == True: return
    fireEvent(event.clickCard, card=card, doubleClick=True)
    activate(card, x, y)
    if getLocation(card) == location.hand:
        tryPlayCard(card)

#Called when multiple cards are moved at once
#Possible bug: both this and onMoveCard event are fired when multiple cards are moved.
def onMoveCards(player, cards, fromGroups, toGroups, oldZs, z, oldXs, oldYs, x, y, highlights, markers=[], scriptedMove=None):
    if type(highlights) == bool:
        scriptedMove = highlights
        highlights = []
        markers = []
        
    for i in range(len(cards)):
        onMoveCard(player, cards[i], fromGroups[i], toGroups[i], oldZs[i], z[i], oldXs[i], oldYs[i], x[i], y[i], highlights[i], markers[i], scriptedMove)

#Called whenever a card is moved.
def onMoveCard(player, card, fromGroup, toGroup, oldZ, z, oldX, oldY, x, y, manualMove, highlight, markers=None):
    """Not called by a user input but by the OnMoveCard event when a user manually moves a card. The function will warn all players if the movement was between groups. Assuming the movement was on the table, it check to see if it was moved to a different zone; if not, then the zone it is in is rearranged, otherwise it performs validation to see if the movement is allowed and removes the appropriate AT while notifying all players of the move."""
    mute()
    if not devMode:
        whisper("x:{} y:{}".format(x,y))
        return
    if manualMove == True:
        if fromGroup != toGroup:
            notifyAll(errorColor, "WARNING: {} manually moved {} from {} to {}. The script handles most everything, so please be sure that's what you wanted to do.".format(me, card, fromGroup.name, toGroup.name))
            return
        if fromGroup == table and toGroup == table:
            newLoc = getLocationFromCords(card)
            oldLoc = getLocation(card)
            if oldLoc == newLoc:
                repositionCard(card, newLoc)
                return
            if isCharacter(card):
                cost = 2
                #cost = applyModifiers(modifier.movementCost, {'card':card, 'oldLoc':oldLoc, 'newLoc':newLoc, 'cost': cost})
                if me.counters['AT'].value >= cost:
                    #fireEvent(preEvent.moveCard, card=card, oldLoc=oldLoc, newLoc=newLoc, cost=cost)
                    me.counters['AT'].value -= cost
                    setLocation(card, newLoc)
                    notifyAll(infoColor, "{} moves {} to {} for {} AT.".format(me,card,newLoc.name,cost))
                    #fireEvent(event.moveCard, card=card, oldLoc=oldLoc, newLoc=newLoc, cost=cost)
                else:
                    whisperBar(warnColor, "Not enough AT to move {}.".format(card))
                    organizeZone(getLocation(card))
            else:
                whisperBar(errorColor, "Can't move non-characters.")
                organizeZone(getLocation(card))

#TODO: rewrite for priority.
def declareResponse(group, x = 0, y = 0):
    """Called by pressing CTRL+SPACE, this will eventually freeze the game state to allow the calling player to take action; for now it only notifies all players."""
    notifyAll(queryColor, "{} wishes to respond.".format(me))
    
def surrender(group, x=0, y=0):
    """Called by pressing CTRL+SHIFT+S; it will put up a dialogue box, confirming that the player wishes to surrender. If the press 'yes' it will end the game in their opponents victory and clean up the board."""
    mute()
    if not confirm("Are you sure you want to concede the game?"): return
    for loc in locations:
        for card in loc:
            if card.owner == me:
                if card.controller != me:
                    remoteCall(card.controller, 'giveControl', [card, me])
                    update()
                card.delete()
    update()
    notifyAll(infoColor, "{} concedes the game.".format(me))

#-----------------------------------------------------------------------
# Hand actions
#-----------------------------------------------------------------------

#Called when a card is played.
def tryPlayCard(card, x = 0, y = 0):
    """Called by pressing space on or double clicking a card in hand; this will run through various validations before finally enabling the player to play the card.
    NOTE: Eventually double clicking a card will prioritize activating the effect of a card in hand before trying to play it, such as if a card can discard itself to activate an effect or something similar. Players should be encouraged to press Space bar to play cards."""
    mute()
    if eval(getGlobalVariable('playingCard_player')) == me._id:
        playCard(location.home)
        return
    typ, cost = Type(card), Cost(card)
    if typ == cardType.Problem or typ == cardType.ManeCharacter: return
    cost = max(applyModifiers(modifier.cost, {'card':card, 'cost':cost, 'played':True})['cost'], 0)
    if typ == cardType.troublemaker:
        if me.counters['AT'].value < cost:
            whisperBar(warnColor,"You don't have the required {} AT to play {}".format(cost, card)+longSpace)
            return      
    else:
        for preq in iter(PlayRequirements(card)):
            power = countTotalPower(me, preq)
            if power < PlayRequirements(card)[preq]:
                whisperBar(warnColor,"You don't meet the requirements to play {}".format(card)+longSpace)
                return
        if me.counters['AT'].value < cost:
            whisperBar(warnColor,"You don't have the required {} AT to play {}".format(cost, card)+longSpace)
            return
    retVal = excecute(card, dispatch.checkPlay)
    if retVal == False:
        whisperBar(errorColor,"You can't play {}: {}".format(card, popData('reason', 'Unknown reason.')))
        return False
    
    #Passed the test to play the card, time to play it!        
    if typ == cardType.troublemaker:
        me.counters['AT'].value -= cost
        card.moveToTable(x, y, True)
        notifyAll(infoColor, "{} plays a facedown troublemaker.".format(me))
    
    else:
        setGlobalVariable('playingCard_player', str(me._id))
        setGlobalVariable('playingCard_card', str(card._id))
        setGlobalVariable('playingCard_cost', str(cost))
        if typ == cardType.event:
            playCard()
        elif typ == cardType.resource:
            playCard(retVal)
        else:
            whisperBar(infoColor, "Playing {}: Click the problem you want to play it to, or press 'Space' to play to home. 'Esc' to cancel.".format(card))

def playCard(loc=location.home):
    """Called to actually play the card; for events this means straight away, for other card types, it is called when the selection of location has been made."""
    mute()
    card = Card(eval(getGlobalVariable('playingCard_card')))
    tpy = Type(card)
    cost = eval(getGlobalVariable('playingCard_cost'))
    fireEvent(event.prePlayCard, card=card, cost=cost, loc=loc, played=True)
    me.counters['AT'].value -= cost
    #card.moveToTable(-95,60)
    moveToLocation(card, loc, trigger=False)
    setGlobalVariable('playingCard_player', 'None')
    dict = {'played':True, 'cleanup':True}
    msg = excecute(card, dispatch.entersPlay, dict, retVal='')
    if dict['cleanup']: playCardCleanup(card, cost, loc, True, message=msg)

def playCardCleanup(card=None, cost=None, loc=location.home, played=True, message=''):
    """Called when a card is finished playing. This can be delayed by card scripting if necessary, as is often the case with events that need to target another card."""
    if card == None: card = Card(eval(getGlobalVariable('playingCard_card')))
    if cost == None: cost = eval(getGlobalVariable('playingCard_cost'))
    if Type(card) == cardType.Event: notifyAll('#333333', "{} plays {} for {} AT".format(me,card,cost)+message)
    else: notifyAll('#333333', "{} plays {} to {} for {} AT".format(me,card,loc.name,cost)+message)
    fireEvent(event.playCard, card=card, cost=cost, loc=loc, played=played)
    if Type(card) == cardType.Event: moveToLocation(card, location.discardPile)
    enableDelayedModifiers()
    enableDelayedEvents()

#-----------------------------------------------------------------------
# Deck Actions
#-----------------------------------------------------------------------
    
def payToDraw(group, x=0, y=0):
    """Called by pressing CTRL+D or by double clicking the deck. This will check for and deduct an action token to draw a card."""
    mute()
    whisper("group {}".format(group.name))
    if len(me.deck) == 0: whisperBar(warnColor, "You don't have any cards in your {} to draw.".format(group.name))
    elif me.counters['AT'].value == 0: whisperBar(warnColor, "You don't have enough action tokens to draw a card.")
    else:
        me.counters['AT'].value -= 1
        draw()