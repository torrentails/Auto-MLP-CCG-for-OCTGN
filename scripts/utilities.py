import time, re, math

#-----------------------------------------------------------------------
# Globals
#-----------------------------------------------------------------------

# The types module is not available so we need to set thes up
_MethodType = type(g._get_diff_patch)
_FuncionType = type(sync)

_long_space=' '*256

prnt = whisper

class HIGHLIGHT:
    FACEOFF = '#C00000'
    FACEOFFIGNORED = '#600000'
    SELECTION = '#00C060'

class COLOR:
    INFO = '#3A3A3A' # Used to inform of an action taken
    ERROR = '#801111' # Used for errors, trying to do something illegal, etc.
    WARN = '#AB6808' # Used for warnings, unable to take an action, etc.
    QUERY = '#5C4584' # Used to indicate action needs to be taken.

class LOGLEVEL:
    ERROR = 4
    WARN = 3
    INFO = 2
    DEBUG = 1
    VERBOSE = 0

    def __getitem__(self, i):
        return ('VERBOSE', 'DEBUG', 'INFO', 'WARNING', 'ERROR')[i]

LOGLEVEL = LOGLEVEL()

#-----------------------------------------------------------------------
# Logger
#-----------------------------------------------------------------------

class _Logger(object):

    def __init__(self, tmp_log):
        if setting.debug:
            self.log_save_level = LOGLEVEL.DEBUG
        else:
            self.log_save_level = LOGLEVEL.INFO
        if setting.debug:
            self.log_display_level = LOGLEVEL.INFO
        else:
            self.log_display_level = LOGLEVEL.WARN
        self.__log = _copy(tmp_log)

        self.card_re = re.compile("\{#(\d{5})\}")

        # previous_log = getSetting('log', [])
        # update()
        # whisper("{} {}".format(type(previous_log), previous_log))
        # setSetting('previous_log', previous_log)
        # update()

        _log = []
        for val in tmp_log:
            if val['level'] >= self.log_save_level:
                log_string = ("<{0[3]:0>2n}:{0[4]:0>2n}:{0[5]:0>2n}>"
                    " [{1}] {2}".format(time.localtime(val['time']),
                    LOGLEVEL[val['level']], val['message']))

                log_string = self.card_re.sub(
                    lambda m: _card_base(int(m.group(1))).Name, log_string)
                _log.append(log_string)

            if val['level'] >= self.log_display_level:
                prnt("[{}] {}".format(LOGLEVEL[val['level']],
                    val['message']))

            if val['level'] >= LOGLEVEL.ERROR:
                alert("[{}] {}".format(LOGLEVEL[val['level']],
                    val['message']))

        setSetting('log', _log)

    def __call__(self, msg, level=LOGLEVEL.INFO):
        cur_time = time.time()
        msg = str(msg)
        self.__log.append({'time':cur_time, 'level':level, 'message':msg})

        if level >= self.log_save_level:
            _log = []
            for l in self.__log:
                # whisper("{}".format(l['level']))
                if l['level'] >= self.log_save_level:
                    # whisper("yep {}".format(l))
                    log_string = ("<{0[3]:0>2n}:{0[4]:0>2n}:{0[5]:0>2n}>"
                        " [{1}] {2}".format(time.localtime(l['time']),
                        LOGLEVEL[l['level']], l['message']))

                    log_string = self.card_re.sub(
                        lambda m: _card_base(int(m.group(1))).Name, log_string)
                    _log.append(log_string)

            # whisper("{}".format(_log))
            setSetting('log', _log)

        if level >= self.log_display_level:
            prnt("[{}] {}".format(LOGLEVEL[level], msg))

        if level >= LOGLEVEL.ERROR:
            alert("[{}] {}".format(LOGLEVEL[level], msg))

    @property
    def log(self):
        return self.__log

    def pretty_print(self):
        for l in self.log:
            prnt(LOGLEVEL[l['level']], self.card_re.sub(
                lambda m: _card_base(int(m.group(1))).Name, l['message']))
    
    def save_log(self, level=LOGLEVEL.DEBUG):
        log("Manually saving log at level {}".format(LOGLEVEL[level]),
            LOGLEVEL.VERBOSE)

        _log = []
        for l in self.__log:
            # whisper("{}".format(l['level']))
            if l['level'] >= level:
                # whisper("yep {}".format(l))
                log_string = ("<{0[3]:0>2n}:{0[4]:0>2n}:{0[5]:0>2n}>"
                    " [{1}] {2}".format(time.localtime(l['time']),
                    LOGLEVEL[l['level']], l['message']))

                log_string = self.card_re.sub(
                    lambda m: _card_base(int(m.group(1))).Name, log_string)
                
                _log.append(log_string)

        setSetting('log', _log)

# Temporarry logger because of the 'Empty Queue' issue
_tmp_log = []
def log(msg, level=LOGLEVEL.INFO):
    _tmp_log.append({'time':time.time(), 'level':level, 'message':msg})

#-----------------------------------------------------------------------
# Custom Exceptions
#-----------------------------------------------------------------------

class StaticAttributeError(TypeError):
    def __init__(self, *args):
        TypeError.__init__(self, *args)
        
class IncorrectCommandType(TypeError):
    def __init__(self, *args):
        TypeError.__init__(self, *args)
        
# class Timeout(Exception):
#     def __init__(self, *args):
#         Exception.__init__(self, *args)
        
class NoEffectDeffined(NotImplementedError):
    def __init__(self, *args):
        NotImplementedError.__init__(self, *args)

class NoActionDeffined(NotImplementedError):
    def __init__(self, *args):
        NotImplementedError.__init__(self, *args)

#-----------------------------------------------------------------------
# Enumeration class
# Licensed under the GNU LGPL V3. See for more info:
# https://github.com/torrentails/Python-2.x-Enumeration-Class
#-----------------------------------------------------------------------

class _Enum_Item(object):

    _name = ''
    _type = ''
    _initiated = False

    def __init__(self, name, type):
        self._name = name
        self._type = type
        self._initiated = True

    def __getattr__(self, name):
        if name == 'name':
            return self._name
        if name == 'type':
            return self._type
        else: raise AttributeError("No such attribute on 'Enum_Item' object.",
                                    name)

    def __setattr__(self, name, value):
        if self._initiated:
            raise TypeError("'Enum_Item' object does not support"
                            "attribute assignment", name, value)
        else: super(_Enum_Item, self).__setattr__(name, value)

    def __str__(self):
        return self.type+'.'+self.name

class _Enum(object):

    _initiated = False

    def __init__(self, name, enums):
        if type(name) != str: raise ValueError(
            "Invalid name for object 'Enum'", name)
        self._d = {}
        for i in enums:
            if type(i) != str: raise TypeError(
                "Enum values must be a string.", i)
            if enums.count(i) > 1: raise ValueError(
                "Duplicate values not allowed.", i)
            self._d[i.upper().replace(' ','')] = _Enum_Item(i, name)
        self._name = name
        self._initiated = True

    def __getattr__(self, a):
        try:
            return self._d[a.upper()]
        except KeyError:
            raise AttributeError("No enum value defined.", a)

    def __setattr__(self, a, v):
        if self._initiated:
            raise TypeError("'Enum' object does not support"
                            "attribute assignment")
        else: super(_Enum, self).__setattr__(a, v)

    def __getitem__(self, k):
        return self._d[k.upper().replace(' ','')]

    def __name__(self):
        return self._name

    def __iter__(self):
        i = 0 
        l = self._d.values()
        while i < len(l):
            yield l[i]
            i+=1

#-----------------------------------------------------------------------
# Action Helper functions
#-----------------------------------------------------------------------

# TODO: move to player class when done
def shuffle(group=None):
    if group: group.shuffle()
    else: me.deck.shuffle()

#-----------------------------------------------------------------------
# Misc Helper functions
#-----------------------------------------------------------------------

def notify_all(message, col=COLOR.INFO, alsoLog=True):
    mute()
    if alsoLog: notify(message)
    for p in getPlayers():
        remoteCall(p, 'notifyBar', [col,message+_long_space])
        
def whisper_bar(message, col=COLOR.INFO):
    mute()
    whisper(message)
    notify_bar(col, message+_long_space)

def alert(message, button='ok', col=COLOR.WARN):
    return askChoice(message, [button], [col])

def get_opponent():
    players = getPlayers()
    try:
        return players[1]
    except IndexError:
        if setting.debug:
            return me
        else:
            raise

#-----------------------------------------------------------------------
# Internal helper functions
#-----------------------------------------------------------------------

def _copy(obj):
    if type(obj) not in (tuple,list,dict,set):
        log("Only tuples, lists, dicts and sets can be coppied", LOGLEVEL.ERROR)
        raise TypeError("Invalid type for _copy: {}".format(obj))
    if type(obj) in (tuple,list,set):
        copy = []
        for i in obj:
            copy.append(i)
        if type(obj) in (tuple,set):
            copy = type(obj)(copy)
    else:
        copy = {}
        for k,v in obj.items():
            copy[k] = v
    return copy

def _tween(start, end=None, dtime=500, interval=10, tween_func=easeOutSine):
    if end is None:
        end = start
        start = 0
    diff = end - start
    inc = 1/(dtime/(interval*1.0))
    dtime *= 0.001
    interval *= 0.001
    cur = 0
    while cur <= 1.0:
        val = tween_func(cur)*diff+start
        yield val
        time.sleep(interval)
        cur += inc
    if val < end:
        yield end

def _tween_list(start, end=None, dtime=500, interval=10, tween_func=easeOutSine):
    if end is None:
        end = start
        start = (0,)*len(end)
    for ratio in _tween(0, 1, dtime, interval, linear):
        lst = []
        for i in range(len(end)):
            diff = end[i] - start[i]
            if type(tween_func) == _FuncionType:
                lst.append(tween_func(ratio)*diff+start[i])
            else:
                lst.append(tween_func[i](ratio)*diff+start[i])
        yield lst

#-----------------------------------------------------------------------
# OCTGN Events / Anti-Cheating measures
#-----------------------------------------------------------------------

def _on_table_load():
    pass

def _on_game_load():
    global prnt, setting, log, _tmp_log
    log("Loading new game", LOGLEVEL.DEBUG)

    log("Initializing settings", LOGLEVEL.DEBUG)
    setting = _Setting_Manager()

    if setting.develop:
        prnt = print

    log("Initializing logger", LOGLEVEL.DEBUG)
    previous_log = getSetting('log', [])
    setSetting('previous_log', previous_log)
    try:
        log = _Logger(_tmp_log)
        del _tmp_log
    except NameError:
        log = _Logger([])

def _adjust_counter(event):
    if not event.scripted and not setting.debug:
        counter, value = event.counter, event.value
        log("Manually addjusted counter {}: from:{:n} to:{:n}".format(
            counter.name, counter.value, value), LOGLEVEL.WARN)
        mute()
        counter.value = value
        alert("You shouldn't cheat!")
        notify_all("{}'s {} set back to {}".format(event.player,
            counter.name, value))