import copy

modifier_list = []
modifiers_to_remove = set()
iterating_modifiers = 0

def apply_modifiers(obj, modifier_type, arg, applied_modifiers=set()):
    global iterating_modifiers
    iterating_modifiers += 1
    arg = copy.deepcopy(arg)
    changed = False
    for mod in modifier_list:
        if mod not in applied_modifiers:
            if mod.enabled and mod.type == modifier_type:
                if self in mod.apply_list:
                    if mod.condition(obj):
                        applied_modifiers.add(mod)
                        old_arg = copy.deepcopy(arg)
                        arg = mod.action(obj, arg)
                        if not changed and arg != old_arg: changed = True
    if changed:
        arg = apply_modifiers(obj, modifier_type, arg, applied_modifiers)
    iterating_modifiers -= 1
    if not iterating_modifiers:
        remove_pending_modifiers()
    return arg
    
def remove_pending_modifiers():
    for mod in modifiers_to_remove:
        mod.remove()
        
class Modifier():
    def __init__(self, card, modifier_type):
        def foo(*args): pass
        self._owner_ = card
        self._modifier_type_ = modifier_type
        self._condition_ = foo
        self._action_ = foo
        self._remove_on_new_instance_ = True
        self._applies_to_ = [card]
        self._enabled_ = True
        modifier_list.append(self)
        return(self)
    
    # Read only properties
    owner = property(lambda self: self._owner_)
    type = property(lambda self: self._modifier_type_)
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
                    l+=fetch_val(val, True)
                return l
            raise ValueError("Inappropriate value found while forming apply list: {} {}".format(str(val), str(type(val))))
        for item in self.applies_to:
            if type(item) == type(self.apply):
                lst+=[i for i in fetch_val(item()) if i not in lst]
            else:
                lst+=[i for i in fetch_val(val) if i not in lst]
        first_type = type(lst[0])
        for item in lst:
            if type(item) != first_type:
                raise ValueError("Result apply list must only contain one type of object")
        return lst
    apply_list = property(get_apply_list)
    
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
    
    def get_remove_on_new_instance(self): return self._remove_on_new_instance_
    def set_remove_on_new_instance(self, bool): self._remove_on_new_instance_ = bool
    remove_on_new_instance = parameter(get_remove_on_new_instance, set_remove_on_new_instance)
    
    def get_applies_to(self): return self._applies_to_
    def set_applies_to(self, lst):
        assert type(lst) == list, "{} must be a list".format(str(lst))
        self._applies_to_ = lst
        self.update_applied_cards()
    applies_to = parameter(get_applies_to, set_applies_to)
    
    def get_enabled(self): return self._enabled_
    def set_enabled(self, bool): self._enabled_ = bool
    enabled = property(get_enabled, set_enabled)
    
    # Methods
    def remove(self):
        self.enabled = False
        global iterating_modifiers
        if iterating_modifiers:
            modifiers_to_remove.add(self)
        else:
            modifier_list.remove(self)
            self.owner.remove_modifier(self, True)