EVENT = _Enum('EVENT',
    # Timing events
    ('STARTOFPHASE','ENDOFPHASE','AFTERSTARTOFPHASE','STARTTURN','ENDTURN',
    # Player based events
    'GAINAT','LOOSEAT','SPENDAT','GAINPOINTS','LOOSEPOINTS','DRAWCARD',
    # Card state
    'ENTERSPLAY','LEAVESPLAY','EXHAUSTED','READIED','FRIGHTENED','RALLIED',
    # Card interaction
    'CLICKCARD','ACTIVATEEFFECT'))
PREEVENT = _Enum('PREEVENT',
    # Player based events
    ('GAINAT','LOOSEAT','SPENDAT','GAINPOINTS','LOOSEPOINTS','DRAWCARD',
    # Card state
    'ENTERSPLAY','LEAVESPLAY','EXHAUSTED','READIED','FRIGHTENED','RALLIED',
    # Card interaction
    'CLICKCARD','ACTIVATEEFFECT'))

_evt_list = [e for e in EVENT]+[pe for pe in PREEVENT]
_event_bus = dict(zip(_evt_list,[[]]*len(_evt_list)))
_delayed_events = []

def _trigger_event(event_type):
    for evt in _copy(_event_bus[event_type]):
        if g.doing_PPP() or evt.ignore_PPP:
            evt.action()

def _enable_delayed_events():
    global _delayed_events
    for evt in _delayed_events:
        for et in evt.event_type:
            _event_bus[et].append(evt)
        evt.enabled = True
    _delayed_events = []

class Event(object):
    def __init__(self, event_type, card, origin=None, delayed=False,
                 enabled=True, run_once=False, ignore_PPP=False):
        if hasattr(event_type, '__iter__'):
            self.event_type = list(event_type)
        else:
            self.event_type = [event_type]
        self.card = card
        self.origin = origin
        self.enabled = enabled
        self.run_once = run_once
        self.ignore_PPP = ignore_PPP
        self.__action = None
        if delayed:
            self.enabled = False
            _delayed_events.append(self)
        else:
            for et in self.event_type:
                _event_bus[et].append(self)

    def function(self, func):
        self.action = func
        return func

    @property
    def action(self):
        if self.__action:
            return self.__action
        else:
            raise NoActionDeffined("No action function is defined on {}".format(
                repr(self)))
    @action.setter
    def action(self, func):
        assert type(func) == _FuncionType, "{} must be a function".format(
            str(func))
        self.__action = _MethodType(func, self)

    def remove(self):
        self.enabled = False
        for et in self.event_type:
            lst = _event_bus[et]
            del lst[lst.index(self)]