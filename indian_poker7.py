import random
import time
from colorama import Fore, Back, Style, init

init(autoreset=True)


class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def __str__(self):
        return f"{self.value} of {self.suit}"

    def get_color(self):
        return Fore.RED if self.suit in ["Hearts♥", "Diamonds♦"] else Fore.BLUE

    def ascii_rep(self):
        suit_symbol = self.suit[-1]
        value = (
            self.value
        )  # if self.value not in ['10', 'Jack', 'Queen', 'King', 'Ace'] else self.value[0]
        color = self.get_color()
        return [
            f"{color}┌───────┐",
            f"{color}| {value:<2}    |",
            f"{color}|       |",
            f"{color}|   {suit_symbol}   |",
            f"{color}|       |",
            f"{color}|    {value:>2} |",
            f"{color}└───────┘{Style.RESET_ALL}",
        ]


class Deck:
    def __init__(self):
        suits = ["Hearts♥", "Diamonds♦", "Clubs♣", "Spades♠"]
        values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        self.cards = [Card(suit, value) for suit in suits for value in values]
        for i in range(2):
            self.cards.append(Card("JokerΦ", "JK"))  # ジョーカーを追加
        random.shuffle(self.cards)

    def draw(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        return None


class Player:
    def __init__(self, name, is_human=False):
        self.name = name
        self.card = None
        self.score = 0
        self.visible = 0
        self.expect_card = None
        self.expect = 0
        self.is_human = is_human

    def draw_card(self, deck):
        self.card = deck.draw()

    def play_turn(self, game_state):
        if self.is_human:
            return self.human_turn(game_state)
        else:
            return self.ai_turn(game_state)

    def human_turn(self, game_state):
        print(f"\n{Fore.CYAN}Your visible total is {self.visible}.")
        print(f"{Fore.CYAN}The current call number is {game_state['call']}.")
        if game_state["call"] != 0:
            guess1 = input(
                f"{Fore.YELLOW}Would you like to proceed with the call? (Y/N) "
            ).upper()
        else:
            guess1 = "Y"  # コールナンバーが0の時は必ずゲームを続ける
        if guess1 == "Y":
            while True:
                try:
                    guess2 = int(input(f"{Fore.YELLOW}Your raised number: "))
                    return True, guess2
                except:
                    print(f"{Fore.RED}Please enter integer !!")
        else:
            return False, 0

    def ai_turn(self, game_state):
        if self.visible > game_state["call"]:
            raise_num = random.randint(1, self.visible - game_state["call"])
            print(f"{Fore.GREEN}{self.name} raises {raise_num}")
            return True, raise_num
        else:
            if self.expect > game_state["call"]:
                raise_num = random.randint(1, self.expect - game_state["call"])
                print(f"{Fore.GREEN}{self.name} raises {raise_num}")
                return True, raise_num
            else:
                # 初手でコールストップはできない
                if game_state["call"] == 0:
                    return True, 1
                print(f"{Fore.RED}{self.name} stops the call")
                return False, 0

    # プレイヤーに見えている数だけ計算
    def calc_visible(self, players):
        Ace_count_each = 0
        for other in players:
            if self != other:
                self.visible += get_card_value(other.card)
                if other.card.value == "A":
                    Ace_count_each += 1
        self.visible *= 2**Ace_count_each

    # プレイヤーの予想値を計算
    def calc_expect(self, players, deck):
        self.expect_card = random.choice(
            deck.cards + [self.card]
        )  # 完全に残りのデッキを覚えている
        Ace_count_each = 0
        self.expect += get_card_value(self.expect_card)
        if self.expect_card.value == "A":
            Ace_count_each += 1
        for other in players:
            if self != other:
                self.expect += get_card_value(other.card)
                if other.card.value == "A":
                    Ace_count_each += 1
        self.expect *= 2**Ace_count_each


def get_card_value(card):
    values = {
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6,
        "7": 7,
        "8": 8,
        "9": 9,
        "10": 10,
        "J": 11,
        "Q": 12,
        "K": 13,
        "A": 0,  # エースはそれ以外の合計を2倍にする
        "JK": -7,
    }
    return values[card.value]


def display_cards_except_you(players):
    card_displays = []
    for player in players:
        if player.name != "You":
            card_displays.append(player.card.ascii_rep())
    for i in range(7):
        print(" ".join(card[i] for card in card_displays))
    for player in players:
        if player.name != "You":
            print(f"{player.name:^9}", end=" ")
    print()


def display_cards(players):
    card_displays = [
        player.card.ascii_rep() if player.card else [" " * 9] * 7 for player in players
    ]
    for i in range(7):
        print(" ".join(card[i] for card in card_displays))
    for player in players:
        print(f"{player.name:^9}", end=" ")
    print()


def play_round(players, deck, start_index):
    while len(players) > 1:
        print(
            f"\n{Fore.MAGENTA}***********************New Game!!***********************"
        )
        game_state = {"sum": 0, "call": 0, "Ace_count": 0}

        for player in players:
            player.visible = 0
            player.expect = 0
            player.draw_card(deck)

        # 各プレイヤーの値を計算
        for i in players:
            i.calc_visible(players)
            i.calc_expect(players, deck)

        # フィールドの合計値を計算
        for i in players:
            game_state["sum"] += get_card_value(i.card)
            if i.card.value == "A":
                game_state["Ace_count"] += 1
        game_state["sum"] *= 2 ** game_state["Ace_count"]

        time.sleep(2)

        display_cards_except_you(players)
        time.sleep(4)
        stopper = None
        while True:
            for i in range(len(players)):
                index = (i + start_index) % len(players)
                player = players[index]
                print(f"\n{Fore.CYAN}**********************************************")
                print(f"{Fore.YELLOW}It's {player.name}'s turn!")
                continue_call, raise_amount = player.play_turn(game_state)
                if continue_call:
                    game_state["call"] += raise_amount
                    print(f"{Fore.GREEN}Call is now {game_state['call']}")
                    time.sleep(2)
                else:
                    stopper = player
                    break
            if stopper:
                break

        print(
            f"\n{Fore.MAGENTA}*********************** Result !! ***********************"
        )
        display_cards(players)
        print(f"{Fore.CYAN}Field sum is {game_state['sum']}")
        print(f"{Fore.CYAN}Final call number is {game_state['call']}")
        time.sleep(4)

        stopper_index = players.index(stopper)
        previous_player = players[stopper_index - 1]

        if game_state["call"] > game_state["sum"]:
            print(f"{Fore.RED}{previous_player.name} drops out!")
            players.remove(previous_player)
            if stopper_index == 0:
                start_index = stopper_index
            else:
                start_index = stopper_index - 1
        else:
            print(f"{Fore.RED}{stopper.name} drops out!")
            players.remove(stopper)
            start_index = stopper_index - 1

        time.sleep(1.5)

    print(f"\n{Fore.MAGENTA}**********************************************")
    print(f"{Fore.YELLOW}The winner is {players[0].name}!!!")
    print(f"{Fore.MAGENTA}**********************************************")


def main():
    flag = True
    while flag == True:
        deck = Deck()
        players = [
            Player("You", is_human=True),
            Player("Player 1"),
            Player("Player 2"),
            Player("Player 3"),
            Player("Player 4"),
            Player("Player 5"),
        ]
        start_index = random.randint(0, 5)
        play_round(players, deck, start_index)
        guess = input(
            f"{Fore.YELLOW}Would you like to continue the game? (Y/N) "
        ).upper()
        if guess != "Y":
            flag = False


if __name__ == "__main__":
    main()
