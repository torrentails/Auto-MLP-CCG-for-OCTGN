##Dispatcher
dispatch = Enum('dispatch', ['onGameLoad', 'activatedList', 'activated', 'checkPlay', 'prePlayCard', 'entersPlay', 'leavesPlay', 'flipped', 'moved', 'uncovered', 'confronted', 'replaced'])

##Event types
event = Enum('event', ['Start of Phase', 'End of Phase', 'Start Turn', 'End Turn', 'Ready Phase', 'Troublemaker Phase', 'Main Phase', 'Score Phase', 'End Phase', 'Play Card', 'Click Card', 'Activate Effect', 'Leave Play'])
preEvent = Enum('preEvent', ['Play Card', 'Click Card', 'Activate Effect', 'Leave Play'])

##Phases
pahse = Enum('phase', ['Ready', 'Troublemaker', 'Main', 'Score', 'End'])

##Modifier types
modifier = Enum('modifier', ['cost', 'power', 'color', 'gainAT'])

##Card Properties
property = Enum('property', ['Name', 'Title', 'Subtitle', 'Number', 'Type', 'Traits', 'Colors', 'Power', 'Cost', 'Play Requirements', 'Keywords', 'Text', 'Bonus Points', 'Your Requirements', 'Opponents Requirements', 'Rarity', 'On Game Load', 'Activated List', 'Activated', 'Check Play', 'Pre Play Card', 'Enters Play', 'Leaves Play', 'Flipped', 'Moved', 'Uncovered', 'Confront', 'Replaced'])

##Card types
cardType = Enum('cardType', ['Character', 'Mane Character', 'Friend', 'Event', 'Resource', 'Troublemaker', 'Problem', 'Strife', 'Quest'])

##Card traits
trait = Enum('trait', ['Earth Pony', 'Unicorn', 'Pegasus', 'Alicorn', 'Ally', 'Breezie', 'Buffalo', 'Changeling', 'Critter', 'Crystal', 'Donkey', 'Draconequus', 'Dragon', 'Griffon', 'Zebra', 'Ahuizotl', 'Cow', 'Chaotic', 'Elder', 'Foal', 'Minotaur', 'Performer', 'Rock', 'Royalty', 'Sea Serpent', 'Tree', 'Accessory', 'Armor', 'Artifact', 'Asset', 'Condition', 'Location', 'Report', 'Mailbox', 'Unique', 'Gotcha', 'Showdown', 'Epic'])

##Card keywords
keyword = Enum('keyword', ['Home Limit', 'Caretaker', 'Inspired', 'Prismatic', 'Pumped', 'Random', 'Starting Problem', 'Stubborn', 'Studious', 'Supportive', 'Swift', 'Teamwork', 'Villain'])

##Card colours
color = Enum('color', ['Blue', 'Orange', 'Pink', 'Purple', 'White', 'Yellow', 'Colorless'])

#TODO: Should we merge color and colorRequirement?
##Problem Requirements
colorRequirement = Enum('colorRequirement', ['Blue', 'Orange', 'Pink', 'Purple', 'White', 'Yellow', 'Wild', 'Harmony', 'Non-Blue', 'Non-Orange', 'Non-Pink', 'Non-Purple', 'Non-White', 'Non-Yellow'])

##Zone locations
location = Enum('location', ['Home', 'My Problem', 'Opp Problem', 'Deck', 'Problem Deck', 'Hand', 'Discard Pile', 'Banished Pile', 'Queue'])