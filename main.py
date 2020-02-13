import random
import copy
import deuces


class Player:
    def __init__(self, name, chip_number, table_position):
        self.name = name
        self.chip_count = chip_number
        self.cards = []
        self.knocked_out = False
        self.current_round_bet = 0
        self.table_position = table_position

    def make_bet(self, bet_size):
        true_bet = min(bet_size, self.chip_count)
        self.chip_count -= true_bet
        self.current_round_bet += true_bet
        return true_bet

    def fold(self):
        self.cards = []

    def check_bet(self):
        self.make_bet(0)

    def __repr__(self):
        return f'{self.name} with {self.chip_count} chips at position {self.table_position}'


class PokerHand:
    def __init__(self, active_players, table):
        self.active_players = copy.copy(active_players)
        self.players_to_take_action = []
        self.action_history = []
        self.deck = Deck()
        self.pot = [0]
        self.table = table
        self.current_round_bet_size = 0
        self.community_cards = []

    def betting_round(self):
        while len(self.players_to_take_action) > 0 and len(self.active_players) > 1:
            x = self.players_to_take_action[0]
            print(x.cards, x)
            player_input = str.strip(input('What would you like to do? 1 for checking, 2 for betting, 3 for folding'))
            if player_input == '1':
                if self.current_round_bet_size == x.current_round_bet or x.chip_count == 0:
                    x.check_bet()
                    self.players_to_take_action.pop(0)
                else:
                    print("You can't check. You need to bet to stay in the hand")
            elif player_input == '2':
                bet_size = int(str.strip(input(
                    f'How much would you like to bet? Between {min(self.current_round_bet_size - x.current_round_bet, x.chip_count)} and '
                    f'{x.chip_count}')))
                if bet_size < min(self.current_round_bet_size - x.current_round_bet, x.chip_count):
                    print("Please try again. Your bet was too small.")
                else:
                    player_bet = x.make_bet(bet_size)
                    self.pot[0] += player_bet
                    if x.current_round_bet != self.current_round_bet_size:
                        self.current_round_bet_size = x.current_round_bet
                        self.update_active_players_list(x.table_position)
                        self.players_to_take_action.pop(self.players_to_take_action.index(x))
                    else:
                        self.players_to_take_action.pop(0)
            elif player_input == '3':
                x.fold()
                self.active_players.pop(self.active_players.index(x))
                self.players_to_take_action.pop(0)

    def update_active_players_list(self, player_position):
        ordered_list = []
        for x in self.active_players[player_position:]:
            if not (x.knocked_out or len(x.cards) == 0):
                ordered_list.append(x)
        for x in self.active_players[:player_position]:
            if not (x.knocked_out or len(x.cards) == 0):
                ordered_list.append(x)
        self.players_to_take_action = ordered_list

    def collect_blinds(self):
        self.update_active_players_list(self.table.button_position)
        self.pot[0] += self.players_to_take_action[0].make_bet(self.table.small_blind)
        self.pot[0] += self.players_to_take_action[1].make_bet(self.table.big_blind)
        self.current_round_bet_size = max(self.players_to_take_action[0].current_round_bet, self.players_to_take_action[1].current_round_bet)
        self.update_active_players_list(self.table.big_blind_position)

    def deal_cards(self):
        self.deck.shuffle()
        for x in range(2):
            for y in self.active_players:
                y.cards.append(self.deck.deal_top_card())

    def end_hand(self, winner):
        winner.chip_count += self.pot[0]
        for x in self.table.player_array:
            if x.chip_count == 0:
                x.knocked_out = True
            x.current_round_bet = 0
            x.cards = []
        self.table.set_button(self.table.button_position + 1)


class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def __repr__(self):
        return f'{self.value}{self.suit}'


class Deck:
    def __init__(self):
        card_suit_array = ['h', 'd', 's', 'c']
        card_value_array = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.number_of_cards = 52
        self.deck_array = [Card(value, suit) for value in card_value_array for suit in card_suit_array]

    def shuffle(self):
        return random.shuffle(self.deck_array)

    def deal_top_card(self):
        return self.deck_array.pop()

    def burn_top_card(self):
        self.deck_array.pop()

    def __repr__(self):
        return f'{self.deck_array}'


class Table:
    def __init__(self, number_of_players, starting_chips, small_blind, big_blind):
        self.number_of_players = number_of_players
        self.starting_chips = starting_chips
        self.player_array = [Player(f'Player{x}', starting_chips, x) for x in range(1, number_of_players + 1)]
        self.ordered_active_players_array = self.player_array
        self.button_position = 1
        self.small_blind_position = 2
        self.big_blind_position = 3
        self.deck = Deck()
        self.small_blind = small_blind
        self.big_blind = big_blind

    def set_button(self, player_position):
        if player_position > self.number_of_players:
            player_position = 1
        self.update_active_players_list(player_position)
        self.button_position = player_position
        self.small_blind_position = self.ordered_active_players_array[0].table_position
        self.big_blind_position = self.ordered_active_players_array[1].table_position

    def update_active_players_list(self, player_position):
        ordered_list = []
        for x in self.player_array[player_position:]:
            if not x.knocked_out:
                ordered_list.append(x)
        for x in self.player_array[:player_position]:
            if not x.knocked_out:
                ordered_list.append(x)
        self.ordered_active_players_array = ordered_list

    def number_active_players(self):
        active = 0
        for player in self.player_array:
            if not player.knocked_out:
                active += 1
        return active

    def __repr__(self):
        return f'There were {self.number_of_players} to start, and the button is currently {self.button_position},' \
            f'and the big blind is {self.big_blind_position} '


def main():
    # Set up table and hand of poker
    new_table = Table(5, 500, 1, 2)

    while new_table.number_of_players > 1:
        print("THIS IS THE START OF A NEW ROUND!!")
        poker_round = PokerHand(new_table.player_array, new_table)
        poker_round.deal_cards()
        poker_round.collect_blinds()

        # cycle through all players pre-flop
        poker_round.betting_round()

        # Check how many players are in the hand. If only 1, then give money to remaining player. Else, go to the flop
        if len(poker_round.players_to_take_action) == 1:
            poker_round.end_hand(poker_round.players_to_take_action[0])

        else:
            poker_round.deck.burn_top_card()
            for x in range(3):
                poker_round.community_cards.append(poker_round.deck.deal_top_card())
            print(f'The flop is: {poker_round.community_cards}')
            poker_round.update_active_players_list(poker_round.table.button_position - 1)
            poker_round.betting_round()

            # Check how many players are in the hand. If only 1, then give money to remaining player. Else, go to the turn
            if len(poker_round.players_to_take_action) == 1:
                poker_round.end_hand(poker_round.players_to_take_action[0])

            else:
                poker_round.deck.burn_top_card()
                poker_round.community_cards.append(poker_round.deck.deal_top_card())
                print(f'The turn is: {poker_round.community_cards}')
                poker_round.update_active_players_list(poker_round.table.button_position - 1)
                poker_round.betting_round()

                # Check how many players are in the hand. If only 1, then give money to remaining player. Else, go to river
                if len(poker_round.players_to_take_action) == 1:
                    poker_round.end_hand(poker_round.players_to_take_action[0])

                else:
                    poker_round.deck.burn_top_card()
                    poker_round.community_cards.append(poker_round.deck.deal_top_card())
                    print(f'The river is: {poker_round.community_cards}')
                    poker_round.update_active_players_list(poker_round.table.button_position - 1)
                    poker_round.betting_round()

                    if len(poker_round.players_to_take_action) == 1:
                        poker_round.end_hand(poker_round.players_to_take_action[0])

                    else:
                        # determine who wins the hand

                        poker_round.end_hand(poker_round.active_players[0]) # TODO: calc who should win based on hand and replace thiw
                        print('END of round')

if __name__ == "__main__":
    main()