# Project Setup

### Using venv

The venv module is used to create a virtual environment, and comes prepackaged with Python versions >=3.3

### Activate the virtual environment

You can activate the python environment by running the following command:
Mac OS / Linux
`source jay-env/bin/activate`

Windows
`jay-env\Scripts\activate`

You should see the name of your virtual environment in parenthesis on your terminal line e.g. (jay-env).

### Deactivate the virtual environment

To decativate the virtual environment and use your original Python environment, simply type ‘deactivate’.
`deactivate`

# Classes

-   Server API

    -   Responsible for setting up connections
    -   Assigns a game id to a newly created or potential game (lobby)
    -   Needs to properly format data to pass on to the game interface

-   Lobby (only necessary for online games)

    -   Holds onto clients
    -   Can receive request to start a game

-   Game Factory

    -   Could be handled in the server api, but something should hold onto references for each existing game via the game id

-   Game Interface

    -   Only concerned with logic pertaining to ONE game
    -   The implementation of the Game Interface should have the following knowledge upon setup:
        -   (REQUIRED) list of player names
        -   (OPTIONAL) desired algorithm type for AI, which shall have a default if not specified, aka Optional parameter
        -   (???)
    -   How to handle async operations?
        -   Contains a direct or indirect reference to the server in order to callback when necessary
        -   Callbacks are defined in the method declarations
        -   Wrap calls to game interface with async (TODO: need to look into async)
    -   How should we handle partial/incomplete turns?
        -   A turn contains an outcome, make the outcome optional so the game knows whether it is a completed turn or not
        -   A turn is subclassed into two types, one that contains an outcome and one that does not

-   Data Classes
    -   Turn
        -   holds information pertaining to the turn
    -   Player Info
        -   game id -> used to correctly identify which game the client is a part of
        -   team id
        -   list of cards
-   Enums
    -   SetType
        -   Unknown, Low Hearts, Low Diamonds, Low Spades, Low Clubs, High Hearts, High Diamonds, High Spades, High Clubs
    -   CardStatus
        -   Unknown, Does Not Have, Might Have, Does Have, Declared
        -   Comments
            -   We've toyed with the idea of having Asked For, but I remember coming to the conclusion it was unnecessary becuase the ledger should contain that information
                -   Small idea for ledger, small helper method when given a player and card, returns how many times the player has asked for it
    -   TurnType (TBD)
        -   Unknonw, Question, Declaration
