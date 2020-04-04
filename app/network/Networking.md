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
        'pin': pin for game,
        'name': player name 
        }
    }
    
###Select Player
    { 'type': 'select_player',
     'data': {
        'name': player name,
        'cards': list of cards (only expected if using a physical deck) 
        }
    }

###Question
    { 'type': 'question',
      'data': {
        'identifier': identifier provided by server,
        'questioner': name of player asking question,
        'respondent': name of player being asked a question,
        'card': card in question
        }
    }
    
###Declaration
    { 'type': 'declaration',
      'data': {
        'identifier': identifier provided by server,
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
            'teams': [
                {'name':name of team, 'players':list of player names},
            ]
            'next_turn': name of player who is up
       }
    }
     
###Selected Player
      { 'type': 'selected_player',
      'data': { 
            'identifier': identifier provided by server,
            'cards': if virtual deck was specified, list of cards 
       }
    }     
     
###Game Update
    { 'message_type':'game_update'
    'data': {
        'teams': {
            'players': [
                'name': name,
                'card_count': card count,
                'status': game connection status 
            ],
            'sets': count of sets won
            },
        'last_turn': {
            'turn_type': question or declaration
            'outcome': outcome
            IF Question:
            'questioner': player name,
            'respondent': player name,
            'card': card 
            IF Declaration:
            'player': player,
            'card_set' card set
            },
        'current_turn': player name,
        'cards': [] list of cards,
        'state': data frame
        }

