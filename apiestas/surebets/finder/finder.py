from collections import defaultdict
from typing import List, Union, Tuple, Iterable
from loguru import logger

from capiestas.api.app.models.bets import Bet
from capiestas.api.app.models.surebets import SureBet, SureBetInUpsert, Outcome
from capiestas.surebets.helpers import recursive_defaultdict


class SureBetsFinder:
    def __init__(self, bets: List[Bet]):
        self.bets_tree = recursive_defaultdict()
        for bet in bets:
            self.bets_tree[bet.bet_type][bet.bet_scope][bet.is_back][bet.handicap][bet.slug] = bet
        # {'Home/Away': {'Full Time': {True: {0.0 {'1xbet': Bet()}}}}}

    def find_all(self) -> List[SureBetInUpsert]:
        all_arbs = []
        # go through different scopes
        for bet_type, bet_scopes in self.bets_tree.items():
            # for every scope go through only the bets that are back
            for bet_scope, is_back_bets in bet_scopes.items():
                # for bets thar are back go through handicap bets
                for is_back, handicap_bets in is_back_bets.items():
                    # go through all handicap bets and find arbs
                    for handicap, bets in handicap_bets.items():
                        arbs = self._find_all(bet_type, bets.values())
                        if arbs:
                            for outcomes, profit in arbs:
                                all_arbs.append(
                                    SureBetInUpsert(
                                        bet_type=bet_type,
                                        bet_scope=bet_scope,
                                        is_back=is_back,
                                        outcomes=outcomes,
                                        profit=profit
                                    )
                                )
        return all_arbs

    def find_two_way(self, bets: List[Bet]) -> Iterable[Tuple[List[Outcome], float]]:
        # for now I will just divide two way bets and three way bets, in next versions I can unify it together
        filtered_bets = tuple(filter(lambda x: len(x.opportunities) == 2, bets))
        rng = range(len(filtered_bets))
        #print(filtered_bets)
        # permutations = []
        # for i in rng:
        #   for j in rng:
        #   dont check betting opportunities from same bookmaker - means we will not see surebets on the same bookmaker
        #       if i != j:
        #          permutations.append((filtered_bets[i], filtered_bets[j]))
        permutations = ((filtered_bets[i], filtered_bets[j]) for i in rng for j in rng if i != j)
        for bet_1, bet_2 in permutations:
            profit = self.get_profit(bet_1.opportunities[0].odd, bet_2.opportunities[1].odd)
            if profit > 0:
                outcomes = [
                    self._get_outcome_from_bet(bet_1, 0),
                    self._get_outcome_from_bet(bet_2, 1)
                ]
                yield outcomes, profit

    def find_three_way(self, bets: List[Bet]) -> Iterable[Tuple[List[Outcome], float]]:
        filtered_bets = tuple(filter(lambda x: len(x.opportunities) == 3, bets))
        rng = range(len(filtered_bets))
        #permutations = []
        #for i in rng:
        #    for j in rng:
        #        for k in rng:
        #            permutations.append((filtered_bets[i], filtered_bets[j], filtered_bets[k]))

        permutations = ((filtered_bets[i], filtered_bets[j], filtered_bets[k]) for i in rng for j in rng for k in rng)
        for bet_1, bet_2, bet_3 in permutations:
            profit = self.get_profit(bet_1.opportunities[0].odd, bet_2.opportunities[1].odd, bet_3.opportunities[2].odd)
            logger.info(profit)
            if profit > 0:
                outcomes = [
                    self._get_outcome_from_bet(bet_1, 0),
                    self._get_outcome_from_bet(bet_2, 1),
                    self._get_outcome_from_bet(bet_3, 2)
                ]
                logger.info(outcomes)
                yield outcomes, profit

    @staticmethod
    def _get_outcome_from_bet(bet: Bet, odd_idx: int) -> Outcome:
        return Outcome(bookmaker=bet.bookmaker,
                       bookmaker_nice=bet.bookmaker_nice,
                       bet_category= bet.bet_category,
                       label=bet.opportunities[odd_idx].label,
                       url=bet.url,
                       odd=bet.opportunities[odd_idx].odd)

    @staticmethod
    def get_profit(odd_1: float, odd_2: float, odd_3: float | None = None):
        if odd_3:
            return 1 - (1 / odd_1 + 1 / odd_2 + 1 / odd_3)
        return 1 - (1 / odd_1 + 1 / odd_2)

    def _find_all(self, bet_type: str, bets: list) -> Union[List[tuple], None]:
        # Two-way handicaps
        #if bet_type in ('Home/Away', 'Draw No Bet', 'Over/Under'):
            #yield from self.find_two_way(bets)
        yield from self.find_two_way(bets)
        yield from self.find_three_way(bets)








