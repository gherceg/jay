#Networking

##Defined Keys
Card Sets are defined as follows:
- low_spades
- high_spades
- low_diamonds
- high_diamonds
- low_clubs
- high_clubs
- low_hearts
- high_hearts

##Client Messages

###Create Game
    { 'type': 'create_game',
      'data': {
        'players': [
            'name': player name 
            'type': player type ]
        'virtual_deck': Defaults to False
        'teams': [
            'name': team name
            'players': player names ]
        }
    }
    
###Enter Pin
    { 'type': 'enter_pin',
     'data': {
        'pin': pin for game
        }
    }
    
###Select Player
    { 'type': 'select_player',
     'data': {
        'pin': pin for game, 
        'name': player name,
        'cards': list of cards (only expected if using a physical deck) 
        }
    }

###Question
    { 'type': 'question',
      'data': {
        'pin': game pin
        'questioner': name of player asking question,
        'respondent': name of player being asked a question,
        'card': card in question
        }
    }
    
###Declaration
    { 'type': 'declaration',
      'data': {
        'pin': game pin
        'name': name of player,
        'card_set': set being declared
        'declared_map': [
            { 'card': card, 'player': player name }
        ]
      } 

##Server Messages 

###Game Created
    { 'type': 'created_game',
      'data': {
            'pin': pin to connect to game
            }
    }
     
###Joined Game
    { 'type': 'joined_game',
      'data': { 
            'pin': game pin
            'teams': [
                {'name':name of team, 
                'players': [{
                    'name': name of player,
                    'type': player type
                    'card_count': number of cards,
                }],
                'set_count': number of sets
                }
            ]
       }
    }
          
###Game Update
    { 'message_type':'game_update',
      'data': {
        'pin': game pin,
        'teams': [
                {'name':name of team, 
                'players': [{
                    'name': name of player,
                    'type': player type
                    'card_count': number of cards,
                }],
                'set_count': number of sets
                }
            ]
        'last_turn': {
            'type': question,
            'data': {
               'outcome': outcome,
               'questioner': player name,
               'respondent': player name,
               'card': card 
            }
            OR
            'type': declaration,
            'data': {
                'outcome': outcome,
                'player': player,
                'card_set' card set,
            }
        },
        'next_turn': player name,
        'player': {
                'name': name of player,
                'cards': list of cards,
            }
        }
