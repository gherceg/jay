import logging
from typing import Dict, List, Tuple

from app.constants import *
from app.data.app_state import MessageResult
from app.data.game import Game
from app.data.network import Client
from app.gameplay import game_builder
from app.gameplay.game_controller import (update_game_for_declaration,
                                          update_game_for_question)
from app.messages import message_builder, message_validation
from app.util import util_methods

logger = logging.getLogger(__name__)


def received_message(sender: str, message: Dict, games: Dict[int, Game], clients: Dict[str, Client]) -> MessageResult:
    if MESSAGE_TYPE not in message:
        message = message_builder.error('Cannot parse message: Missing message_type field')
        return MessageResult(messages=[(sender, message)])

    if DATA not in message:
        message = message_builder.error('Cannot parse message: Missing data field')
        return MessageResult(messages=[(sender, message)])

    data = message[DATA]

    if message[MESSAGE_TYPE] == CREATE_GAME:
        return received_create_game(sender, data)

    elif message[MESSAGE_TYPE] == ENTER_PIN:
        return received_enter_pin(sender, data, games)

    elif message[MESSAGE_TYPE] == SELECT_PLAYER:
        return received_select_player(sender, data, games, clients)

    elif message[MESSAGE_TYPE] == QUESTION:
        return received_question(sender, data, games)

    elif message[MESSAGE_TYPE] == DECLARATION:
        return received_declaration(sender, data, games)


def received_create_game(sender: str, data: Dict) -> MessageResult:
    game = game_builder.create_game(data)
    logger.info('Create Game Request: created new game with pin {0}'.format(game.pin))
    message: Dict = message_builder.created_game(game)
    return MessageResult(game=game, messages=[(sender, message)])


def received_enter_pin(sender: str, data: Dict, games: Dict[int, Game]) -> MessageResult:
    if PIN in data and data[PIN] in games.keys():
        game: Game = games[data[PIN]]
        message = message_builder.joined_game(game)
        return MessageResult(messages=[(sender, message)])
    else:
        message = message_builder.error('Enter Pin Request: Missing or invalid pin field')
        return MessageResult(messages=[(sender, message)])


def received_select_player(sender: str, data: Dict, games: Dict[int, Game],
                           clients: Dict[str, Client]) -> MessageResult:
    if PIN in data and data[PIN] in games.keys():
        game: Game = games[data[PIN]]
        if NAME in data:
            registered_client: Client = register_client(sender, clients, data[NAME], data[PIN])

            player = game.players[data[NAME]]
            message = message_builder.game_update(game, player)

            return MessageResult(new_client=registered_client, messages=[(sender, message)])
        else:
            message = message_builder.error('Select Player Request: Missing name field')
            return MessageResult(messages=[(sender, message)])
    else:
        message = message_builder.error('Select Player Request: Missing or invalid pin field')
        return MessageResult(messages=[(sender, message)])


def received_question(sender: str, data: Dict, games: Dict[int, Game]) -> MessageResult:
    if PIN in data and data[PIN] in games.keys():
        game: Game = games[data[PIN]]

        error = message_validation.validate_question(game, data)
        if error:
            message = message_builder.error(error)
            return MessageResult(messages=[(sender, message)])

        updated_game: Game = update_game_for_question(game, data[QUESTIONER], data[RESPONDENT], data[CARD])

        # build game update messages for each player
        messages: List[Tuple[str, Dict]] = []
        for player in updated_game.players.values():
            message: Dict = message_builder.game_update(updated_game, player)
            client_id = util_methods.client_identifier(player.name, updated_game.pin)
            messages.append((client_id, message))

        return MessageResult(game=updated_game, messages=messages)
    else:
        message = message_builder.error('Enter Question: Missing or invalid pin field')
        return MessageResult(messages=[(sender, message)])


def received_declaration(sender: str, data: Dict, games: Dict[int, Game]) -> MessageResult:
    if PIN in data and data[PIN] in games.keys():
        game: Game = games[data[PIN]]
        card_set = util_methods.card_set_for_key(data[CARD_SET])
        if NAME in data and CARD_SET in data and DECLARED_MAP in data and card_set:
            updated_game: Game = update_game_for_declaration(game, data[NAME], card_set, data[DECLARED_MAP])

            # build game update messages for each player
            messages: List[Tuple[str, Dict]] = []
            for player in updated_game.players.values():
                message: Dict = message_builder.game_update(updated_game, player)
                client_id = util_methods.client_identifier(player.name, updated_game.pin)
                messages.append((client_id, message))

            return MessageResult(game=updated_game, messages=messages)
        else:
            message = message_builder.error('Enter Declaration: Missing or invalid name, card set or map')
            return MessageResult(messages=[(sender, message)])
    else:
        message = message_builder.error('Enter Declaration: Missing or invalid pin field')
        return MessageResult(messages=[(sender, message)])


def register_client(sender: str, clients: Dict[str, Client], player_id: str, game_id: str) -> Client:
    # check if client exists
    client_identifier = util_methods.client_identifier(player_id, game_id)
    if client_identifier in clients.keys():
        # client already exists, add connection to dictionary
        client = clients[client_identifier]
        clients[client_identifier].connections.append(sender)
        logger.info(f'Registered new connection with client\n{client}')
    else:
        # setup client
        client = Client(game_id, player_id)
        client.connections.append(sender)
        clients[client.identifier] = client
        logger.info(f'Registered new client\n{client}')

    return client
