#-----------------------------------------------------------------------
# Event bus management
#-----------------------------------------------------------------------

#Event bus
eventBus = {}
delayedEvents = []

def registerEvent(obj, evt, func, delayed=False):
    if delayed: delayedEvents.append([obj, evt, func])
    else:
        if evt not in eventBus: eventBus[evt] = {}
        eventBus[evt][obj] = func
        
def enableDelayedEvents():
    global delayedEvents
    for e in delayedEvents:
        registerEvent(e[0], e[1], e[2])
    delayedEvents = []

def removeEvent(obj, evt):
    if evt not in eventBus: return
    try:
        eventBus[evt].remove(obj)
    except: return
    
def fireEvent(evt, **args):
    if evt not in eventBus: return False
    args['event'] = evt
    args['canceled'] = False
    for obj in iter(eventBus[evt]):
        args['self'] = obj
        eventBus[evt][obj](args)
    return args['canceled']
    
#-----------------------------------------------------------------------
# Pre-Priority Processing Queue
#-----------------------------------------------------------------------

#TODO: add PPP management