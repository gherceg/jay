#Networking

- Game Setup JSON
    - "type":"setup" 
    - "data": {
        - "players": []
            - "name": player name 
            - "type": player type
        - "virtual_deck": bool
        - (OPTIONAL) "teams": []
            - "name": team name
            - "players": player names 
        - }

- Connecting To Existing Game JSON
    - "type":"connect"
    - "data": {
        - "pin": pin for game
        - "name": player name
    - }
    
- Update Cards JSON
    - "type":"set_cards"
    - "data": {
        - "name": player name
        - "cards": list of cards
    - }

- Question JSON
    - "type":"question"
    - "data": {
        - "questioner": player name
        - "respondent": player name
        - "card": card
    - }
        
- Game update JSON
    - "message_type":"new_turn"
    - "data"
        - "game_id": pin
        - "teams": []
            - "players": []
                - "name": name
                - "card_count": card count
                - "status": game connection status
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

