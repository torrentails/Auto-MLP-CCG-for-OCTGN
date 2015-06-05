import collections
#-----------------------------------------------------------------------
# Event bus management
#-----------------------------------------------------------------------

#Event bus
eventBus = {}
delayedEvents = []
eventsToRemove = []
isIteratingEvents = False

def registerEvent(evt, func, delayed=False, runOnce=False, id=None, **kwargs):
    if id == None: id = uuid4()
    if delayed: delayedEvents.append([evt, func, runOnce, id, kwargs])
    else:
        if evt not in eventBus: eventBus[evt] = {}
        eventBus[evt][id] = [func, runOnce, kwargs]
    return id
        
def enableDelayedEvents():
    global delayedEvents
    for e in delayedEvents:
        registerEvent(e[0], e[1], runOnce=e[2], id=e[3])
    delayedEvents = []

def removeEvent(id):
    eventsToRemove.append(id)
    cleanupEvents()
    
def cleanupEvents():
    global isIteratingEvents
    if isIteratingEvents: return
    rmLst = []
    global eventsToRemove
    for e in eventBus.iterkeys():
        for id in eventsToRemove:
            if id in eventBus[e]:
                rmLst.append([e,eventsToRemove.pop(eventsToRemove.index(id))])
    for v in rmLst:
        del eventBus[v[0]][v[1]]
    eventsToRemove = []
    
def fireEvent(evt, **args):
    if evt not in eventBus: return False
    args['event'] = evt
    args['canceled'] = False
    global isIteratingEvents
    isIteratingEvents = True
    for id in eventBus[evt].iterkeys():
        args.update(eventBus[evt][id][2])
        ret = eventBus[evt][id][0](args)
        if ret == None or ret == True:
            if eventBus[evt][id][1]: removeEvent(id)
    isIteratingEvents = False
    cleanupEvents()
    return args['canceled']
    
#-----------------------------------------------------------------------
# Pre-Priority Processing Queue
#-----------------------------------------------------------------------

#TODO: add PPP management