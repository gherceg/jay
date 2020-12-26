import logging
import random
from typing import Dict, List

from pandas import DataFrame

from app.constants import *
from app.data.game import Game, Player
from app.data.game_enums import CardSet
from app.data.turn import Declaration, Question
from app.gameplay import game_data_methods, game_state_methods
from app.util import Optional

logger = logging.getLogger(__name__)


def update_game_for_question(game: Game, questioner: str, respondent: str, card: str) -> Game:
    outcome: bool = game_data_methods.does_player_have_card(game, respondent, card)
    question: Question = Question(questioner, respondent, card, outcome)
    logger.info(question)
    game.player_up_next = Optional(questioner) if outcome else Optional(respondent)
    game.ledger.append(question)
    game_state: DataFrame = game_state_methods.update_state_with_question(game.state, question)
    players: Dict[str, Player] = update_players_for_question(game, question)
    # create new game data
    return Game(game.pin, players, game.teams, game_state, game.ledger, game.player_up_next, game.options)


def update_game_for_declaration(game: Game, player_name: str, card_set: CardSet, declared_list: List) -> Game:
    outcome: bool = outcome_for_declaration(game, declared_list)
    declaration: Declaration = Declaration(player_name, card_set, declared_list, outcome)
    logger.info(f'{declaration}\n{declared_list}')

    # TODO not the most elegant way to do this
    player_who_declared = game.players[player_name]
    team_name = player_who_declared.team_name if outcome else game_data_methods.get_opposing_team_name_for_player(game,
                                                                                                                  player_name)
    game.teams[team_name].sets_won += 1

    game.ledger.append(declaration)
    game_state: DataFrame = game_state_methods.update_state_with_declaration(game.state, declaration)
    players: Dict[str, Player] = update_players_for_declaration(game, declaration)

    up_next: Optional[str] = determine_player_up_next_after_declaration(game, player_who_declared, outcome)
    if up_next.is_present():
        logger.info(f'{up_next.get()} is up next')

    return Game(game.pin, players, game.teams, game_state, game.ledger, up_next, game.options)


def outcome_for_declaration(game: Game, declared_list: List) -> bool:
    outcome = True
    for card_player_pair in declared_list:
        outcome = game_data_methods.does_player_have_card(game, card_player_pair[PLAYER],
                                                          card_player_pair[CARD]) and outcome
    return outcome


def update_state_for_question(game: Game, question: Question) -> DataFrame:
    return game_state_methods.update_state_with_question(game.state, question)


def update_players_for_question(game: Game, question: Question) -> Dict[str, Player]:
    players_out = game_state_methods.get_players_out_of_cards(game.state)
    for key, player in game.players.items():
        player.state = game_state_methods.update_player_state_for_question(player.state, question, players_out)

    return game.players


def update_players_for_declaration(game: Game, declaration: Declaration) -> Dict[str, Player]:
    players_out = game_state_methods.get_players_out_of_cards(game.state)
    for key, player in game.players.items():
        player.state = game_state_methods.update_player_state_for_declaration(player.state, declaration,
                                                                              players_out)
    return game.players


def determine_player_up_next_after_declaration(game: Game, player: Player, outcome: bool) -> Optional[str]:
    eligible_opponents = game_data_methods.get_opponents_in_play(game, player)
    eligible_teammates = game_data_methods.get_teammates_in_play(game, player)
    eligible_teammate_names = map(lambda p: p.name, eligible_teammates)
    eligible_opponent_names = map(lambda p: p.name, eligible_opponents)

    logger.info(
        f'Determining player up next after {"successful" if outcome else "failed"} declaration\nPlayer in play: {player.in_play}\nEligible teammates: {list(eligible_teammate_names)}\nEligible opponents: {list(eligible_opponent_names)}')
    if outcome:
        if player.in_play:
            return Optional(player.name)
        elif len(eligible_teammates) > 0:
            teammate = random.choice(eligible_teammates)
            return Optional(teammate.name)
        elif len(eligible_opponents) > 0:
            opponent = random.choice(eligible_opponents)
            return Optional(opponent.name)
        elif game_data_methods.is_game_over(game):
            return Optional.empty()
        else:
            raise Exception('Everyone is out but the game is not over.')
    else:
        if len(eligible_opponents) > 0:
            opponent = random.choice(eligible_opponents)
            return Optional(opponent.name)
        elif player.in_play:
            return Optional(player.name)
        elif len(eligible_teammates) > 0:
            teammate = random.choice(eligible_teammates)
            return Optional(teammate.name)
        elif game_data_methods.is_game_over(game):
            return Optional.empty()
        else:
            raise Exception('Everyone is out but the game is not over.')
