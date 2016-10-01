# import types

# modifier types
MODIFIER = _Enum('MODIFIER',
    # Card traits
    ('NAME', 'TITLE', 'SUBTITLE', 'TYPE', 'TRAIT', 'COLOR', 'POWER','COST',
     'PLAYREQUIREMENTS', 'KEYWORD', 'BONUSPOINTS', 'YOURREQUIREMENTS',
     'OPPONENTSREQUIREMENTS', 'EFFECT',
    # Card actions
    'CANEXHAUST', 'CANREADY', 'CANCHALLENGE', 'CANCONFRONT', 'CANPLAY',
    'CANMOVE',
    # Player modifiers
    'GAINAT', 'LOSEAT', 'GAINPOINTS', 'LOSEPOINTS', 'HANDLIMIT', 'HOMELIMIT',
    'CANDRAWCARD'))

_modifier_list = []
# modifiers_to_remove = set()
# iterating_modifiers = 0

def _apply_modifiers(obj, modifier_type, arg, applied_modifiers=None):
    if applied_modifiers is None:
        applied_modifiers = set()
    # global iterating_modifiers
    # iterating_modifiers += 1
    arg = _copy(arg)
    changed = False
    # old_arg = _copy(arg)
    for mod in [mod for mod in _modifier_list if mod.enabled and
                mod not in applied_modifiers and mod.type == modifier_type and
                obj in mod.apply_list]:
        if mod.condition(obj, arg):
            applied_modifiers.add(mod)
            # old_arg = _copy(arg)
            changed = mod.action(obj, arg) or changed
            # changed = changed or arg != old_arg
    # if arg != old_arg:
    if changed:
        whisper("Need to re-apply")
        arg = _apply_modifiers(obj, modifier_type, arg, applied_modifiers)
    # iterating_modifiers -= 1
    # if not iterating_modifiers:
    #     remove_pending_modifiers()
    return arg
    
# def remove_pending_modifiers():
#     for mod in modifiers_to_remove:
#         mod.remove()

# def _build_modifier(card, modifier_type, origin, condition, action, cleanup, applies_to, remove_on_new_instance, enabled):
#     mod = Modifier(card, modifier_type, origin)
#     mod.condition = condition
#     mod.action = action
#     mod.cleanup = cleanup
#     mod.enabled = enabled

# TODO: Workout how to tell opponent to perform the same action that led to the creation of a modifier
class Modifier(object):
    def __init__(self, modifier_type, origin):
        self.type = modifier_type
        self.origin = origin
        self.__condition = None
        self.__action = None
        # depreciated
        self.__cleanup = None
        self.__applies_to = [origin]
        self.remove_on_new_instance = True
        self.enabled = True
        _modifier_list.append(self)
        
    def __del__(self):
        self.cleanup(self)

    def __null_func(*args, **kwargs):
        return True

    def function(self, func):
        if func.__name__ == 'condition':
            self.condition = func
        elif func.__name__ == 'action':
            self.action = func
        elif func.__name__ == 'cleanup':
            self.cleanup = func
        else:
            raise ValueError("Incorectly named function: {}. Must be one of"
                " 'condition', 'action' or 'cleanup'".format(func.__name__))
        return func
    
    @property
    def apply_list(self):
        lst = []
        def fetch_val(val, is_recursing = False):
            if val in LOCATION:
                return [c for c in get_cards_at_location(val)
                        if c != self.origin]
            elif type(val) == Card or type(val) == Player:
                return [val]
            elif type(val) == list:
                assert (not is_recursing), ("Must not contain a list in a"
                                            " list: {}".format(str(val)))
                l = []
                for i in val:
                    l+=fetch_val(val, True)
                return l
            raise ValueError("Inappropriate value found while forming apply"
                             " list: {} {}".format(str(val), str(type(val))))
        for item in self.__applies_to:
            if type(item) == _FuncionType:
                lst+=[i for i in fetch_val(item()) if i not in lst]
            else:
                lst+=[i for i in fetch_val(item) if i not in lst]
        first_type = type(lst[0])
        for item in lst:
            if type(item) != first_type:
                raise ValueError("Result apply list must only contain one type"
                                 " of object")
        return lst
    @apply_list.setter
    def apply_list(self, lst):
        # Valid list contents:
        #   card object(s)
        #   player object(s)
        #   location(s)
        #   function(s) that return a list containing any of the above
        # NOTE: Functions and locations are dynamically evaluated at the time
        #   the modifier is applied. After the dynamic evaluation is performed,
        #   the resulting list may only contain objects of one type.
        assert type(lst) == list, ("{} must be a list, even if it would only"
                                   " contain one value".format(str(lst)))
        self.__applies_to = lst
        # self.update_applied_cards()

    @property
    def condition(self): return self.__condition or self.__null_func
    @condition.setter
    def condition(self, func):
        assert type(func) == _FuncionType, "{} must be a function".format(
            str(func))
        self.__condition = _MethodType(func, self)
    
    @property
    def action(self):
        if self.__action:
            return self.__action
        else:
            log("No action function is defined on {}".format(repr(self)),
                LOGLEVEL.ERROR)
            raise NoActionDeffined("No action function is defined"
                                   " on {}".format(repr(self)))
    @action.setter
    def action(self, func):
        assert type(func) == _FuncionType, "{} must be a function".format(
            str(func))
        self.__action = _MethodType(func, self)
    
    @property
    def cleanup(self): return self.__cleanup or self.__null_func
    @cleanup.setter
    def cleanup(self, func):
        assert type(func) == _FuncionType, "{} must be a function".format(
            str(func))
        self.__cleanup = _MethodType(func, self)
    
    # @property
    # def value(self):
    #     try: return self.__value
    #     except AttributeError:
    #         raise AttributeError("No value has been assigned to this modifier.")
    # @value.setter
    # def value(self, val):
    #     self.__value = val
    
    def remove(self):
        self.enabled = False
        _modifier_list.remove(self)