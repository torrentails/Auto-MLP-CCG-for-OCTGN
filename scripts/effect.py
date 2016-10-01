class ZONECHANGEMETHOD():
    PUT = 0
    BANISHED = 1
    RETURNED = 2
    DISMISSED = 3
    RETIRED = 4
    DISCARDED = 5
    OVERLIMIT = 6

class side(object):
    def __init__(self, fstart=None, fboosted=None):
        self.fstart = fstart
        self.fboosted = fboosted
        self.start = self.__start
        self.boosted = self.__boosted

    @classmethod
    def start(cls, fstart):
        return cls(fstart)

    @classmethod
    def boosted(cls, fboosted):
        return cls(None, fboosted)

    def __start(self, fstart):
        return type(self)(fstart, self.fboosted)

    def __boosted(self, fboosted):
        return type(self)(self.fstart, fboosted)

    def __get__(self, obj, objtype=None):
        if obj.card.is_boosted():
            func = self.fboosted
        else:
            func = self.fstart
        def _func(*args, **kwargs):
            if func is None:
                return None
            return func(obj, *args, **kwargs)
        if func is not None:
            _func.__name__ = func.__name__
            _func.__doc__ = func.__doc__
        return _func
        
    def __set__(self, obj, value):
        raise AttributeError("Can't set function after initilization")

class _Effect(object):
    def __init__(self, card):
        self.id = uuid4()
        self.card = card
        self.printed = False
        self.is_keyword = False

    def gameload(self):
        """ Called when the card is first loaded """
        pass

    def activate_list(self):
        """ Called to check if there are any effects on the card that can be
            activated. Also called before a card is played the see if the card
            has an alternate action that is activated from hand.

            Returns:
                a list of strings, one for each action that the card can
                currently perform, for the user to choose from.
        """
        return []

    def activate(self, index = 0): 
        """ Activtes an effect on the card as sellected by :func:activate_list

            Args:
                index: the index of the effect to activate in this class, Can
                be ignored if the class only has the one effect
        """
        pass

    def can_play(self):
        """ Used to check for additional costs of playing the card, such as
            having to discard a card.

            Returns:
                True if the card meets any additional costs, False otherwise.
        """
        return True

    # def new_instance(self):
    #     """ Called everytime a the card becomes a new instance.

    #         Probably not usefull anymore, as most of what creates a new
    #         instance of a card are also handled below. :func:new_instance is
    #         called before any others though, so use that as you will.
    #     """
    #     pass

    def enter_discard(self, old_location, method):
        """ Called when a card enters the discard pile.

            Args:
                old_location: The previous location the card existed.

                method: One of :class:ZONECHANGEMETHOD
        """

    def as_enters_play(self, was_played):
        """ Called at the point where "as enters play" effects trigger.

            This is called after all costs are played, but before the card is
            actually put into play.

            Args:
                was_played: True if the card was played from hand, False
                otherwise.
        """
        pass

    def enters_play(self, was_played):
        """ Called when a card enters play.

            Args:
                was_played: True if the card was played from hand, False
                otherwise.
        """
        pass

    def leaves_play(self, method):
        """ When a card is removed from gameplay.

            Args:
                method: One of :class:ZONECHANGEMETHOD
        """
        pass

    def moved(self, old_location):
        """ When a card in play is moved.

            Args:
                old_location: the previous location the card was before moving.
        """ 
        pass

    def turned_over(self, face_up=False, uncovered=False):
        """ Called when a card is turned over

        Args:
            face_up: True if the card is flipped to face_up, False otherwise.
            for Mane Characters, True indicates if the card is being flipped to
            its Start side, False for Boosted.

            uncovered: True if the Troublemaker was uncovered propperly. If this
            is False, then Troublemakers shouldn't activate their
            "when uncovered" effect.
        """
        pass

    def faceoff(self):
        """ Called when the card first becomes involved in a faceoff.

            Note that this can mean that the method is called in the middle of
            a faceoff if the card becomes involved in the faceoff and so should
            not be used as a reliable "When a faceoff begins" effect, use an
            event for that.
        """
        pass

    def flipped(self):
        """ Called when a card is flipped during a faceoff. """
        pass

    def confront(self):
        """ Called when a card is involved in a problem being confronted.

            This is called even if a card is at the problem but wasn't directly
            involved in confronting the problem. Also called for the problem
            itself when it is confronted.
        """
        pass

    def solved(self):
        """ Called for all cards at a problem when that problem is solved,
            including the problem itself.
        """
        pass

    def replaced(self):
        """ Called when a problem is replaced, either by being solved of through
            an effect.
        """
        pass

    def __eq__(self, other):
        if other is self: return True
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        if other is self: return False
        if isinstance(other, self.__class__):
            return not self == other
        return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))