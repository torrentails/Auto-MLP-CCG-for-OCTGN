#-----------------------------------------------------------------------
# Premiere keywords
#-----------------------------------------------------------------------
class KW_Caretaker(Effect_Base):
    def new_instance(self, card)
        # Create a new power modifier
        mod = card.new_modifier(modifier.power)
        # Apply it only under the right conditions
        def condition(self, card):
            found_critter = False
            if card.is_at_problem:
                for c in cards_at_location(card.location, me)
                    if cardType.friend in c.type and trait.critter in c.traits:
                        found_critter = True
                        break
            return found_critter
        mod.condition = condition
        # Increase its power by one
        def action(self, card, power): return power + 1
        mod.action = action

class KW_Inspired(Effect_Base):
    def new_instance(self, card)
        # Increment inspired effects value
        gs.writeData('inspired_effects', gs.readData('inspired_effects', 0, me)+1, me)
        # If the only inspired effect, create a new start of phase event
        if gs.readData('inspired_effects', 0, me) == 1:
            evt = new_event(event.startOfPhase)
            # set up the conditions
            def condition(self): return gs.is_phase(phase.main, me)
            evt.condition = condition
            # set up the actions
            def action(self):
                mute()
                deck = players[1].Deck
                inspired_num = gs.readData('inspired_effects', 0, me)
                card_list = deck.top(inspired_num)
                if card_list == None: return
                elif inspired_num == 1:
                    if confirm("Do you want to put {} back on top of {}'s deck?".format(card_list, players[1])):
                        notifyAll("{} used Inspired to put one card on the top of {}'s deck.".format(me, players[1]))
                    else:
                        card_list.moveToBottom(deck)
                        notifyAll("{} used Inspired to put one card on the bottom of {}'s deck.".format(me, players[1]))
                    # card_list.isFaceUp = True
                    # card_list.isFaceUp = False
                    update()
                else:
                    # cards_top = []
                    # cards_bottom = []
                    
                    # for c in card_list:
                        # c.peek()
                    # update()
                    cards_top = selectCard(card_list, min = 0, max = len(card_list), title = "Choose cards to put on top", question = "Select, in any order, the cards to put on the top of {}'s deck.".format(players[1]))
                    for c in cards_top:
                        if c in card_list: card_list.remove(c)
                    if len(card_list) <= 1:
                        cards_bottom = card_list
                    else:
                        cards_bottom = selectCard(card_list, min = 0, max = len(card_list), title = "Choose cards to put on bottom", question = "Select, in any order, the cards to put on the bottom of {}'s deck.".format(players[1]))
                    
                    # TODO: May need to take control of cards to move them.
                    cards_top.reverse()
                    for c in cards_top:
                        c.moveTo(deck,0)
                    for c in cards_bottom:
                        c.moveToBottom(deck)
                    update()
                        
                    if len(cards_top) > 0 and len(cards_bottom) == 0:
                        notifyAll("{} used Inspired to put {} cards on the top of {}'s deck.".format(me, len(cards_top), players[1]))
                    elif len(cards_top) == 0 and len(cards_bottom) > 0:
                        notifyAll("{} used Inspired to put {} cards on the bottom of {}'s deck.".format(me, len(cards_bottom), players[1]))
                    elif len(cards_top) == 1 and len(cards_bottom) == 1:
                        notifyAll("{} used Inspired to put a card on the top and a card on the bottom of {}'s deck.".format(me, players[1]))
                    elif len(cards_top) > 1 and len(cards_bottom) == 1:
                        notifyAll("{} used Inspired to put {} cards on the top and a card on the bottom of {}'s deck.".format(me, len(cards_top), players[1]))
                    elif len(cards_top) == 1 and len(cards_bottom) > 1:
                        notifyAll("{} used Inspired to put a card on the top and {} cards on the bottom of {}'s deck.".format(me, len(cards_bottom), players[1]))
                    else:
                        notifyAll("{} used Inspired to put {} cards on the top and {} cards on the bottom of {}'s deck.".format(me, len(card_top), len(cards_bottom), players[1]))
            evt.action = action
            # enable the event
            evt.enable()
            # store the event for later use
            gs.writeData('inspired_event', evt, me)
    def leaves_play(self, card):
        # Read the amount of inspired effects minus 1
        inspired_num = gs.readData('inspired_effects', 0, me)-1
        # Write that number back into inspired effects
        gs.writeData('inspired_effects', max(inspired_num, 0), me)
        # If there are no inspired effects left, remove the inspired event
        if inspired_num <= 0:
            evt = gs.readData('inspired_event', None, me)
            try: evt.destroy()
            except AttributeError: return
            else: gs.clearData('inspired_event', me)
    def face_down(self, card): self.leaves_play(card)

class KW_Random(Effect_Base):
    def faceoff(self, card):
        # Crate a new event to before each card is flipped
        preevt = new_event(preEvent.flipCard)
        # Make sure the car being flipped is ours
        def condition(self, card): return card.controller == me
        preevt.condition = condition
        # Reset if random has been used in a previous flip
        def action(self, card): gs.writeData('random_used', False, me)
        preevt.action = action
        # Remove this event at the end of the faceoff
        preevt.remove_on_event = event.faceoffCleanup
        
        # Create another event to fire after a card is flipped
        evt = new_event(event.flipCard)
        # Check that the card is ours, has 1 power and that we haven't used random for this card yet
        def condition(self, card): return card.controller == me and card.power == 1 and not gs.readData('random_used', False, me)
        evt.condition = condition
        # Time for action!
        def action(self, card):
            # let the game know that random has triggered for this card
            gs.writeData('random_used', True, me)
            # Ask if the player would like to re-flip
            if confirm("Would you like to activate Random to ignore the power of {} and flip a new card?".format(card)):
                # Ignore the flipped card's power
                card.ignoreFlippedPower()
                # Flip a new card
                flipFaceoffCard(me)
                # Remove this event
                self.destroy()
        evt.action = action

class KW_Stubborn(Effect_Base):
    def new_instance(self, card):
        # TODO: Write once we know how exhaustion code affects the card
        pass

class KW_Studious(Effect_Base):
    def faceoff(self, card):
        # Create a new resolve faceoff event
        evt = new_event(event.resolveFaceoff)
        # Check that the player is the winner of the faceoff
        def condition(self): return cm['faceoff_winner'] == me
        evt.condition = condition
        # Give the player an action token
        def action(self): gainAT(me)
        evt.action = action
        # Remove the event at the end of the faceoff
        evt.remove_on_event = event.faceoffCleanup

class KW_Swift(Effect_Base):
    def new_instance(self, card):
        # Create a new movement modifier
        mod = card.new_modifier(modifier.movement)
        # Check that it was a standard, main phase move
        def condition(self, card): return cm.is_main_pahse_move
        mod.condition = condition
        # Reduce its main phase movement by one
        def action(self, card, cost): return max(cost-1, 0)
        mod.action = action

class KW_Villain(Effect_Base):
    def face_up(self, card):
        # When turned face up, frighten each friend at it's problem
        for c in card.location:
            if cardType.friend in c.type:
                c.frighten()

#-----------------------------------------------------------------------
# Canterlot Nights keywords
#-----------------------------------------------------------------------
class KW_Pumped(Effect_Base):
    def faceoff(self, card):
        # Create a new event to trigger at the end of the faceoff
        evt = new_event(event.endFaceoff)
        # We need to store what card created the event for later use
        evt.card = card
        def condition(self):
            # Get a list of flipped cards we control
            lst = [c for c in cm.flippedCards if c.controller == me]
            # Check that we did actually flip cards and that the Pumped card was actually involved in the faceoff
            return len(lst) >= 1 and self.card.involved_in_faceoff() and confirm("Would you like to banish a card beneath {} for Pumped?".format(self.card))
        evt.condition = condition
        def action(self):
            # We need to build the list again
            lst = [c for c in cm.flippedCards if c.controller == me]
            # If there was more than one card flipped during the faceoff, we need to ask which one the player wants to banish
            if len(lst) > 1:
                lst = selectCard(lst, title="Chose a card for pumped.", question="Choose a card to banish beneath {}".format(self.card))
            # Banish the chosen card beneath the Pumped card
            self.card.banish_cards_beneath(lst)
        evt.action = action
        # Remove the event during the faceoffs clean up
        evt.remove_on_event(event.faceoffCleanup)
        
class KW_Supportive(Effect_Base):
    def __init__(self, card, value):
        # Supportive has and X value associated with it, so we need to capture that and store it for later retrieval
        self.supportive_value = value
        # Since we're overwriting __init__ we need to call the base class' __init__ manually
        super(Effect_Base, self).__init__(self, card)
    def new_instance(self, card):
        # Create a new modifier for power
        mod = card.new_modifier(modifier.power)
        # We need to store the creating effect so that we car retrieve the Supportive value
        mod.effect = self
        def condition(self, card):
            # Check that the card is at a problem
            if card.is_at_problem:
                for c in card.location:
                    # For each card at this location, check if it is ours and that it's a Mane Character
                    if c.controller == me and cardType.maneCharacter in c.type:
                        for col in card.colors:
                            # Cross reference the colors of the two cards and return True if there is a match
                            if col in c.colors:
                                return True
            # Otherwise, no match is found, so we return False
            return False
        mod.condition = condition
        # Add power equal to the Supportive value
        def action(self, card, power): return power + self.effect.supportive_value
        mod.action = action

#-----------------------------------------------------------------------
# Crystal Games keywords
#-----------------------------------------------------------------------
class KW_Prismatic(Effect_Base):
    def new_instance(self, card):
        # Create a new color modifier
        mod = card.new_modifier(modifier.color)
        def action(self, card, colorList):
            # Get a list of our cards in play that also have the crystal trait
            lst = [c for c in gs.cards_in_play(me) if trait.crystal in c.traits]
            for c in lst:
                for col in c.colors:
                    # If the card doesn't have the color, add it to the list
                    if col not in colorList: colorList.append(col)
            return colorList
        mod.action = action

class KW_Teamwork(Effect_Base):
    def new_instance(self, card):
        # Created two new modifiers, one for the keywords and one for the effects
        mod_effect = card.new_modifier(modifier.effect)
        mod_kword = card.new_modifier(modifier.keyword)
        # Store the printed effects set for use later
        mod_effect.set = card.get_effects(printed=True)
        # Likewise for the keywords
        mod_kword.lst = [kw for kw in card.get_keywords(printed=True).items() if kw[0] != keyword.teamwork]
        # Check that the card is a friend and shares a trait with the Teamwork card
        def condition(self, card):
            if card.controller == me and cardType.friend in card.type:
                for t in self.card.traits:
                    if t in card.traits: return True
            return False
        mod_effect.condition = condition
        mod_kword.condition = condition
        # Add the effect to the set
        def effect_action(self, card, effect_set):
            return effect_set |= self.set
        mod_effect.action = effect_action
        # Add the keywords to the dict
        def kword_action(self, card, kw_dict):
            for kw in self.lst:
                if kw[0] not in kw_dict: kw_dict[kw[0]]=kw[1])
            return kw_dict
        mod_kword.action = kword_action
        # Apply only to cards at it's location
        mod_effect.applies_to = [card.get_location]
        mod_kword.applies_to = [card.get_location]

#-----------------------------------------------------------------------
# Absolute Discord keywords
#-----------------------------------------------------------------------
# class Chaos(Effect_Base):

#-----------------------------------------------------------------------
# Equestrian Odysseys keywords
#-----------------------------------------------------------------------
class KW_Calming(Effect_Base):

class KW_Competitive(Effect_Base):

class KW_Diligent(Effect_Base):

class KW_Eccentric(Effect_Base):

class KW_Meticulous(Effect_Base):

class KW_Showy(Effect_Base):

class KW_Vexing(Effect_Base):