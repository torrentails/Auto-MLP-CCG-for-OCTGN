#-----------------------------------------------------------------------
# Turn control
#-----------------------------------------------------------------------

def _startTurn():
    mute()
    enablePPP()
    fireEvent(event.startTurn)

def _readyPhase():
    mute()
    setGlobalVariable("Phase", phase.ready.name)
    disablePPP()
    fireEvent(event.startOfPhase, phase=phase.ready)
    fireEvent(event.readyPhase)
    # Ready Step
    for card in getCardsInPlay(me): ready(card)
    # Action Step
    higestPoints = max(me.counters['Points'].value, players[1].counters['Points'].value)
    if highestPoints >= 11: AtToGain = 5
    elif highestPoints >= 6: AtToGain = 4
    elif highestPoints >= 3: AtToGain = 3
    else: AtToGain = 2
    gainAT(AtToGain)
    enablePPP()
    # Draw Step
    if not eval(getGlobalVariable('firstTurn')): draw()
    fireEvent(event.endPhase, phase=phase.ready)

def _troublemakerPhase():
    mute()
    setGlobalVariable("Phase", phase.troublemaker.name)
    fireEvent(event.startOfPhase, phase=phase.troublemaker)
    fireEvent(event.troublemakerPhase)
    # Uncover step
    for card in getCardsInPlay():
        if cardType.troublemaker in TypeList(card) and card.controler = me:
            uncover(card)
    # Challenge Step
    foundTMToChalange = False
    for card in getCardsInPlay():
        if cardType.troublemaker in TypeList(card):
            if canChallange(card, me): foundTMToChalange = True
    if not foundTMToChalange:
        _troublemakerPhaseEnd()
    
def _troublemakerPhaseEnd():
    fireEvent(event.endOfPhase, phase=phase.troublemaker)

def _mainPhase():
    mute()
    setGlobalVariable("Phase", phase.main.name)
    firEvent(event.startOfPhase, phase=phase.main)
    fireEvent(event.mainPhase)
    # Main phase actions (in any order):
        # Play a card
        # Move a character
        # Draw a card for 1 AT
        # Rally a frightened friend
        # Activate an ability
        
def _mainPhaseEnd():
    firEvent(event.endOfPhase, phase=phase.main)

def _scorePhase():
    mute()
    setGlobalVariable("Phase", phase.score.name)
    fireEvent(event.startOfPhase, pahse=phase.score)
    fireEvent(event.scorePhase)
    # Confront step
    problemsConfronted = []
    for card in getCardsInPlay():
        if cardType.problem in Typelist(card):
            if canConfront(card, me):
                #TODO: Maybe ask which problem to confront first?
                problemsConfronted.append(confront(card))
    # Faceoff Step
    problemsToSolve = []
    if len(problemsConfronted) >= 2:
        problemsToSolve.append(beginFaceoff(faceoff.double))
    else:
        for card in problemsConfronted:
            if canConfront(card, players[1]):
                problemsToSolve.append(beginFaceoff(faceoff.problem, problem=card))
    # Solve Step
    for card in problemsToSolve:
        solveProblem(card)
    fireEvent(event.endOfPhase, pahse=phase.score)

def _endPhase():
    mute()
    setGlobalVariable("Phase", phase.end.name)
    fireEvent(event.startOfPhase, pahse=phase.end)
    # End of Turn Step
    fireEvent(event.endPhase)
    disablePPP()
    # Wrap up Step
    # Apply hand limit
    cardsInHand = getCardsAtLocation(location.hand, me)
    dicardList = []
    handLimit = applyModifiers(modifier.handLimit, {'player':me, 'limit':8})['limit']
    if len(cardsInHand) > handLimit
        boxTitle = "Too many cards in hand."
        while len(cardsInHand) > handLimit:
            if len(cardsInHand)-handLimit == 1: question = "Choose a card to discard."
            else: question = "Choose {} cards to discard.".format(len(cardsInHand)-handLimit)
            card = askCard(cardsInHand, boxTitle, question)
            dicardList.append(cardsInHand.pop(card))
        discard(dicardList)
    # Apply home limit
    cardsAtHome = [c for c in getCardsAtLocation(location.home, me) if cardType.friend in TypeList(c)]
    homeLimit = getHomeLimit(me)
    if len(cardsAtHome) > homeLimit:
        boxTitle = "Too many Friends at home."
        while len(cardsAtHome) > homeLimit:
            if len(cardsAtHome)-homeLimit == 1: question = "Choose a Friend to retire."
            else: question = "Choose {} Friends to retire.".format(len(cardsAtHome)-homeLimit)
            card = askCard(cardsAtHome, boxTitle, question)
            dicardList.append(cardsAtHome.pop(card))
        retire(dicardList)
    fireEvent(event.endTurn)
    fireEvent(event.endOfPhase, pahse=phase.end)
    setGlobalVariable('firstTurn', 'False')