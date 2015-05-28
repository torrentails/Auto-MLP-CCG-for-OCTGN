modifiers = {}
delayedModifiers = []

#TODO: Find out why Cloudchaser's effect wasn't applied twice
def applyModifiers(modifier_type, args_dict):
    args_dict['changed'] = False
    if modifier_type in modifiers:
        args_dict['modifierType'] = modifier_type
        for m in modifiers[modifier_type]:
            args_dict['modifier'] = m
            args_dict['changed'] = m.activate(args_dict) or args_dict['changed']
    return args_dict
    
def enableDelayedModifiers():
    global delayedModifiers
    for m in delayedModifiers:
        m.enable()
    delayedModifiers = []

class Modifier():
    def __init__(self, modifier_type, activate_condition, action, removal_event=None, removal_condition=None, reversal=None, **otherData):
        self._typ = modifier_type
        self._cnd = activate_condition
        self._act = action
        self._ree = removal_event
        self._rec = removal_condition
        self._rev = reversal
        self._oth = otherData
        self._ena = True
        if type(self._typ) == list:
            for m in self._typ:
                if m not in modifiers: modifiers[m]=[]
                modifiers[m].append(self)
        else:
            if self._typ not in modifiers: modifiers[self._typ]=[]
            modifiers[self._typ].append(self)
        if self._ree:
            if type(self._ree) == list:
                for e in self._ree:
                    registerEvent(self, e, self.remove)
            else:
                registerEvent(self, self._ree, self.remove)
        return(self)
    def check(self, args):
        if not self._ena: return False
        if type(self._cnd) == bool: return self._cnd
        else: return self._cnd(args)
    def fire(self, args):
        return self._act(args)
    def activate(self, args):
        if self.check(args): return self.fire(args)
    def enable(self):
        self._ena = True
    def disable(self):
        self._ena = False
    def isEnabled(self):
        return self._ena
    def delay(self):
        self._ena = False
        delayedModifiers.append(self)
    def check_remove(self, args):
        if not self._ena: return False
        if self._rec == None: return True
        elif type(self._rec) == bool: return self._rec
        else: return self._rec(args)
    def reverse(self, args):
        if self._rev == None: return False
        else: return self._rev(args)
    def delete(self):
        try:
            modifiers[self._typ].remove(self)
            if type(self._ree) == list:
                for e in self._ree:
                    removeEvent(self, e)
            else: removeEvent(self, self._ree)
        except: return
    def remove(self, args):
        if self.check_remove(args): self.delete()
    def __getitem__(self, key):
        return self._oth[key]