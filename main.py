import random


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
        self.current_round_bet = true_bet
        return true_bet

    def fold(self):
        self.cards = []

    def check_bet(self):
        self.make_bet(0)

    def __repr__(self):
        return f'{self.name} with {self.chip_count} chips at position {self.table_position}'


class PokerHand:
    def __init__(self, active_players, table):
        self.active_players = active_players
        self.players_to_take_action = []
        self.action_history = []
        self.deck = Deck()
        self.pot = [0]
        self.table = table
        self.current_round_bet_size = 0

    def update_active_players_list(self, player_position):
        ordered_list = []
        for x in self.active_players[player_position:]:
            if not x.knocked_out:
                ordered_list.append(x)
        for x in self.active_players[:player_position]:
            if not x.knocked_out:
                ordered_list.append(x)
        self.players_to_take_action = ordered_list

    def collect_blinds(self):
        self.update_active_players_list(0)
        self.pot[0] += self.players_to_take_action[1].make_bet(self.table.small_blind)
        self.pot[0] += self.players_to_take_action[2].make_bet(self.table.big_blind)
        self.current_round_bet_size = self.table.big_blind

    def deal_cards(self):
        self.deck.shuffle()
        for x in range(2):
            for y in self.active_players:
                y.cards.append(self.deck.deal_top_card())


class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def __repr__(self):
        return f'{self.value} of {self.suit}s'


class Deck:
    def __init__(self):
        card_suit_array = ['Heart', 'Diamond', 'Spade', 'Club']
        card_value_array = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
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

    def __repr__(self):
        return f'There were {self.number_of_players} to start, and the button is currently {self.button_position},' \
            f'and the big blind is {self.big_blind_position} '


def main():
    new_table = Table(5, 500, 1, 2)
    poker_round = PokerHand(new_table.player_array, new_table)
    poker_round.deal_cards()
    poker_round.collect_blinds()
    poker_round.update_active_players_list(3)
    print(poker_round.players_to_take_action)
    while poker_round.players_to_take_action[0]:
        x = poker_round.players_to_take_action[0]
        print(x.cards)
        player_input = str.strip(input('What would you like to do? 1 for checking, 2 for betting, 3 for folding'))
        if player_input == '1':
            print(x.current_round_bet, x.chip_count)
            if poker_round.current_round_bet_size == x.current_round_bet or x.chip_count == 0:
                x.check_bet()
                poker_round.players_to_take_action.pop(0)
            else:
                print("You can't check. You need to bet to stay in the hand")
        elif player_input == '2':
            bet_size = int(str.strip(input(f'How much would you like to bet? Between {min(poker_round.current_round_bet_size, x.chip_count)} and {x.chip_count}')))
            if bet_size < min(poker_round.current_round_bet_size, x.chip_count):
                print("Please try again. Your bet was too small.")
            else:
                player_bet = x.make_bet(bet_size)
                poker_round.pot[0] += player_bet
                poker_round.current_round_bet_size = player_bet
                poker_round.update_active_players_list(x.table_position)
                poker_round.players_to_take_action.pop()
        elif player_input == '3':
            x.fold()
            poker_round.players_to_take_action.pop()


if __name__ == "__main__":
    main()


