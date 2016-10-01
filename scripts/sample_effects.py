# Rainbow Dash, Flier Extraordinaire
class Effect(_Effect):
    @side.start
    def confront(self):
        lst = [card for card in self.card.location
               if CARDTYPE.TROUBLEMAKER in card.types]
        faceup = False
        for card in lst:
            if card.controller == me:
                faceup = True if card.is_faceup() else faceup
        if faceup:
            self.card.boost()

    @side.boosted
    def move(self):
        card = self.card
        if card.last_location == LOCATION.HOME and card.last_moved_by == me:
            friend_list = [c for c in LOCATION.HOME
                           if CARDTYPES.FRIEND in c.types]
            if friend_list and me.AT >= 1:
                c = choose_card("Pay one to move a friend?",
                          friend_list, min=0)
                if c:
                    me.pay_AT(1)
                    card.move_to(card.location)
