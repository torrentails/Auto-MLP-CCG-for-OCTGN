modifiers = []
delayedModifiers = []

def applyModifiers(modifier_type, args_dict):
    args_dict['changed'] = False
    if modifier_type in modifiers:
        args_dict['modifierType'] = modifier_type
        for m in modifiers[modifier_type]:
            args_dict['modifier'] = m
            try:
                args_dict['changed'] = m.activate(args_dict) or args_dict['changed']
            except:
                if devMode: whisper("Keyerror in modifiers.")
    return args_dict
    
def enableDelayedModifiers():
    global delayedModifiers
    for m in delayedModifiers:
        m.enable()
    delayedModifiers = []

class Modifier():
    def __init__(self, card, modifier_type):
        def foo(*args): pass
        self._owner_ = card
        self._modifier_type_ = modifier_type
        self._condition_ = foo
        self._action_ = foo
        self._remove_on_event_ = None
        self._apply_once_ = False
        self._applies_to_ = [card]
        self._enabled_ = True
        modifiers.append(self)
        return(self)
    
    # Read only properties
    owner = property(lambda self: self._owner_)
    type = property(lambda self: self._modifier_type_)
    
    # Writeable properties
    def get_condition(self): return self._condition_
    def set_condition(self, func):
        assert type(func) == type(self.apply), "{} must be a function".format(str(func))
        self._condition_ = func
    condition = parameter(get_condition, set_condition)
    
    def get_action(self): return self._action_
    def set_action(self, func):
        assert type(func) == type(self.apply), "{} must be a function".format(str(func))
        self._action_ = func
    action = parameter(get_action, set_action)
    
    def get_remove_on_event(self): return self._remove_on_event_
    def set_remove_on_event(self, evt): self._remove_on_event_ = evt
    remove_on_event = parameter(get_remove_on_event, set_remove_on_event)
    
    def get_apply_once(self): return self._apply_once_
    def set_apply_once(self, bool): self._apply_once_ = bool
    apply_once = parameter(get_apply_once, set_apply_once)
    
    def get_applies_to(self): return self._applies_to_
    def set_applies_to(self, lst):
        assert type(lst) == list, "{} must be a list".format(str(lst))
        self._applies_to_ = lst
    applies_to = parameter(get_applies_to, set_applies_to)
    
    def get_enabled(self): return self._enabled_
    def set_enabled(self, bool): self._enabled_ = bool
    enabled = property(get_enabled, set_enabled)
    
    # Internal methods
    def get_apply_list(self):
        lst = []
        def fetch_val(val, is_recursing = False):
            if val in location:
                return [c for c in get_cards_at_location(val) if c != self.owner]
            elif type(val) == Card or type(val) == Player:
                return [val]
            elif type(val) == list and:
                assert (not is_recursing), "Must not contain a list in a list: {}".format(str(val))
                l = []
                for i in val:
                    l+fetch_val(val, True)
                return l
            raise ValueError("Inappropriate value found while forming apply list: {} {}".format(str(val), str(type(val))))
        for item in self.applies_to:
            if type(item) == type(self.apply):
                lst+[i for i in fetch_val(item()) if i not in lst]
            else:
                lst+[i for i in fetch_val(val) if i not in lst]
        first_type = type(lst[0])
        for item in lst:
            if type(item) != first_type:
                raise ValueError("Modifier apply lists must only contain one object type")
        return lst
    
    def apply(self):
        pass
        
    # def check(self, args):
        # if not self._ena: return False
        # if type(self._cnd) == bool: return self._cnd
        # else: return self._cnd(args)
    # def fire(self, args):
        # return self._act(args)
    # def activate(self, args):
        # if self.check(args): return self.fire(args)
    # def enable(self):
        # self._ena = True
    # def disable(self):
        # self._ena = False
    # def isEnabled(self):
        # return self._ena
    # def delay(self):
        # self._ena = False
        # delayedModifiers.append(self)
    # def check_remove(self, args):
        # if not self._ena: return False
        # if self._rec == None: return True
        # elif type(self._rec) == bool: return self._rec
        # else: return self._rec(args)
    # def reverse(self, args):
        # if self._rev == None: return False
        # else: return self._rev(args)
    # def delete(self):
        # try:
            # modifiers[self._typ].remove(self)
            # for id in self._rei:
                # removeEvent(id)
        # except: return
    # def remove(self, args):
        # if self.check_remove(args): self.delete()
    # def __getitem__(self, key):
        # return self._oth[key]