# Data Module

- Turn Representation 
    - There are two actions a player can take at any given time
         - ask a question
         - declare a set
    - From a representation perspective, a declaration is really a series of questions
        - Example - Peter has the 2 of hearts, Mikaela has the 3 of hearts, Peter has the 4 of hearts
        - "Peter has the 2 of hearts" is the player declaring asking Peter for the 2 of hearts
    - Does the idea of a declaration being a list of turns help us in any way with design?
    - Looking at a question
        - There are two types of questions
            - Determined outcome
            - Pending outcome
        - All pending questions become completed questions, and we don't gain anything by updating the game state prior to the question being complete, since no decision making takes place then
        - Is there a reason to design a representation for a partial/pending question?
        
        
 - Game Settings
        