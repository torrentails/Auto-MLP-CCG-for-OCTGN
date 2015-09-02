import copy
import types

modifier_list = []
modifiers_to_remove = set()
iterating_modifiers = 0

def apply_modifiers(obj, modifier_type, arg, applied_modifiers=set()):
    global iterating_modifiers
    iterating_modifiers += 1
    arg = copy.deepcopy(arg)
    changed = False
    for mod in [mod for mod in modifier_list if mod.enabled and mod not in applied_modifiers and mod.type == modifier_type and obj in mod.apply_list]:
        if mod.condition(obj):
            applied_modifiers.add(mod)
            old_arg = copy.deepcopy(arg)
            arg = mod.action(obj, arg)
            changed = changed or arg != old_arg
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
    def __init__(self, card, modifier_type, effect=None):
        def foo(*args, **kwargs): pass
        self._card_owner_ = card
        self._owner_ = effect
        self._modifier_type_ = modifier_type
        self._condition_ = foo
        self._action_ = foo
        self._cleanup_ = foo
        self._remove_on_new_instance_ = True
        self._applies_to_ = [card]
        self._enabled_ = True
        modifier_list.append(self)
        return(self)
    
    # Read only properties
    card_owner = property(lambda self: self._card_owner_)
    owner = property(lambda self: self._owner_)
    type = property(lambda self: self._modifier_type_)
    def get_apply_list(self):
        lst = []
        def fetch_val(val, is_recursing = False):
            if val in location:
                return [c for c in get_cards_at_location(val) if c != self.card_owner]
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
        self._condition_ = types.MethodType(func, self)
    condition = parameter(get_condition, set_condition)
    
    def get_action(self): return self._action_
    def set_action(self, func):
        assert type(func) == type(self.apply), "{} must be a function".format(str(func))
        self._action_ = types.MethodType(func, self)
    action = parameter(get_action, set_action)
    
    def get_cleanup(self): return self._cleanup_
    def set_cleanup(self, func):
        assert type(func) == type(self.apply), "{} must be a function".format(str(func))
        self._action_ = types.MethodType(func, self)
    cleanup = parameter(get_action, set_action)
    
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
    
    def get_value(self):
        try: return self._value_
        except AttributeError:
            try:
                return self.owner.value
            except AttributeError:
                raise AttributeError("No value or owner has been assigned to this modifier.")
    def set_value(self, val):
        self._value_ = val
    value = (get_value, set_value)
    
    # Methods
    def remove(self):
        self.enabled = False
        global iterating_modifiers
        if iterating_modifiers:
            modifiers_to_remove.add(self)
        else:
            modifier_list.remove(self)
            self.card_owner.remove_modifier(self, True)