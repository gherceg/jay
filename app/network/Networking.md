#Networking

##Client Messages

###Create Game
    { 'type': 'create_game' 
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
    
###Connect To Game
    { 'type': 'connect_to_game'
     'data': {
        'pin': pin for game,
        'name': player name 
        }
    }
    
###Set Cards
    { 'type': 'set_cards'
      'data': {
        'identifier': identifier provided by server,
        'cards': list of cards
        }
     }

###Question
    { 'type': 'question'
      'data': {
        'identifier': identifier provided by server,
        'questioner': name of player asking question,
        'respondent': name of player being asked a question,
        'card': card in question
        }
    }

##Server Messages 

###Game Created
    { 'type': 'created_game',
      'data': {
            'identifier': identifier provided by server,
            'pin': pin to connect to game,
            'players': list of all players in game,
            'teams': list of list of players for each team,
            }
    }
     

###Connected To Game
    { 'type': 'connected_to_game',
      'data': { 
            'identifier': identifier provided by server,
            'cards': if virtual deck was specified, list of cards 
       }
    }
     
        
###Game Update (still needs work)
    { 'message_type':'game_update'
    'data': {
        'teams':
            - "players": [
                - "name": name
                - "card_count": card count
                - "status": game connection status ]
            - "sets": count of sets won
        - "last_turn": {}
            - "questioner": player name
            - "respondent: player name
            - "card": card 
            - "outcome": outcome
        - (client could figure this out for every turn except who is up first, so let's just provide it
        "current_turn": player name
        - "cards": [] list of cards
        - "state": how to pass back state?

