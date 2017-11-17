import itertools
"""
cards1 = [[0, 2], [0, 3], [0, 4], [0, 5], [0, 6]]  # 8
cards2 = [[0, 2], [0, 3], [0, 4], [0, 5], [0, 14]]  # 8
cards3 = [[0, 2], [1, 2], [2, 2], [3, 2], [3, 4]]
cards4 = [[0, 2], [1, 2], [2, 3], [3, 3], [3, 4]]
cards5 = [[0, 3], [1, 4], [2, 5], [3, 6], [0, 7]]
cards6 = [[0, 4], [1, 4], [2, 4], [3, 5], [2, 6]]
cards7 = [[0, 2], [1, 3], [0, 4], [1, 2], [0, 12]]
cards8 = [[0, 2], [1, 5], [0, 7], [1, 12], [0, 9]]
card = [['1', 1], ['J', 1], ['Q', 2], ['K', 3], ['10', 2], ['9', 3], ['2', 0], ['2', 1], ['5', 3]]
my = [['2', 1], ['2', 2], ['7', 1], ['7', 3], ['7', 2], ['J', 3], ['3', 2]]
"""
# suit 0-3
# number 2-14 (2, 3, ...10, J, Q, K, A)

"""
input:
    card: [[Num, Color], ...,]
    card[0-4]: public card
    card[5-6]: robot card
    card[7-8]: my card
"""

"""
output value:
    names = [[num_1,color_1],[num_2,color_2],...[]]
    card = '1',...,'10','J','Q','K'
    color = 0,1,2,3
"""


def shuffle_card():
    nums = []
    for i in range(52):
        nums.append(i)
    ans = random.sample(nums, len(nums))[0:9]  #

    names = []
    for rand in ans:
        color = (int)(rand - rand % 13) / 13
        index = rand - color * 13
        name = []

        if index >= 0 and index <= 9:
            name.append(str(int(index + 1)))
        elif index == 10:
            name.append('J')
        elif index == 11:
            name.append('Q')
        elif index == 12:
            name.append('K')

        name.append(color)
        names.append(name)

    return names


"""
input:
    card: [[Num, Color], ...,]
    card[0-4]: public card
    card[5-6]: robot card
    card[7-8]: my card
return:
    "You win!"
    "You lose!"
"""


def decide_winner(card):
    print(card)
    my = test_compare.transfer(card[0:5] + card[7:9])
    robot = test_compare.transfer(card[0:7])
    my_level, my_score, my_type, my_card = test_compare.highest(my)
    robot_level, robot_score, robot_type, robot_card = test_compare.highest(
        robot)
    if (my_level >
            robot_level) or my_level == robot_level and my_score > robot_score:
        return my_type + " V.S." + robot_type + "<br> You win!"
    elif my_level == robot_level and my_score == robot_score:
        return my_type + " V.S." + robot_type + "<br> Draw!"
    else:
        return my_type + " V.S." + robot_type + "<br> You lose!"

def second(elem):
    return elem[1]


def transfer(my):
    my_card_list = []
    my_cards = []
    for m in my:
        if m[0] == '1':
            my_card_list.append([m[1], 14])
        elif m[0] == 'J':
            my_card_list.append([m[1], 11])
        elif m[0] == 'Q':
            my_card_list.append([m[1], 12])
        elif m[0] == 'K':
            my_card_list.append([m[1], 13])
        else:
            my_card_list.append([m[1], int(m[0])])
    #print(my_card_list)
    cards_com = itertools.combinations(my_card_list, 5)
    for c in cards_com:
        my_cards.append(sorted(list(c), key=second))
    return my_cards

def transfer_reverse(my):
    my_cards = []
    for m in my:
        if m[1] == 14:
            my_cards.append(['1', m[0]])
        elif m[1] == 13:
            my_cards.append(['K', m[0]])
        elif m[1] == 12:
            my_cards.append(['Q', m[0]])
        elif m[1] == 11:
            my_cards.append(['J', m[0]])
        else:
            my_cards.append([str(m[1]), m[0]])
    return my_cards


# whether cards are suited
def is_suited(cards):
    suit = cards[0][0]
    for c in cards:
        if c[0] != suit:
            return [False, 0]
    return [True, get_num_list(cards)[-1]]


# edge case for "A,2,3,4,5"
def is_smallest_junko(cards):
    number = 2
    for c in cards[:-1]:
        if c[1] != number:
            return False
        number += 1
    return cards[-1][1] == 14


# whether cards are junko
def is_junko(cards):
    if is_smallest_junko(cards):
        return [True, 5]
    else:
        number = cards[0][1]
        for c in cards[1:]:
            if c[1] != number + 1:
                return [False, 0]
            number += 1
        return [True, get_num_list(cards)[-1]]


# gets all the numbers of cards
def get_num_list(cards):
    return sorted([c[1] for c in cards])


# get all the suits of cards
def get_suit_list(cards):
    return sorted([c[0] for c in cards])


def is_quads(cards):
    num_list = get_num_list(cards)
    for num in range(2, 15):
        if num_list.count(num) == 4:
            return [True, num]
    return [False, 0]


def is_full_house(cards):
    num_list = get_num_list(cards)
    for num in range(2, 15):
        if num_list.count(num) == 2:
            return is_trip(cards)
    return [False,0]


def is_trip(cards):
    num_list = get_num_list(cards)
    for num in range(2, 15):
        if num_list.count(num) == 3:
            return [True, num]
    return [False, 0]


def is_two_pair(cards):
    num_list = get_num_list(cards)
    pair_num = 0
    pair = []
    single = 0
    for num in range(2, 15):
        if num_list.count(num) == 2:
            pair_num += 1
            pair.append(num)
        elif num_list.count(num) == 1:
            single = num
    if pair_num == 2:
        # print(max(pair), min(pair), single)
        return [True, max(pair) * 10000 + min(pair) * 100 + single]
    else:
        return [False, 0]


def is_pair(cards):
    num_list = get_num_list(cards)
    pair = 0
    single = []
    for num in range(2, 15):
        if num_list.count(num) == 2:
            pair = num
        elif num_list.count(num) == 1:
            single.append(num)
    if pair != 0:
        sorted(single)
        #print(single, cards)
        return [True, pair * (10 ** 6) + single[2] * (10 ** 4) + single[1] * (10 ** 2) + single[0] * (10 ** 0)]
    else:
        return [False, 0]


# get the highest number
def high(cards):
    single = get_num_list(cards)
    return single[4] * (10 ** 8) + single[3] * (10 ** 6) + single[2] * (10 ** 4) + single[1] * (10 ** 2) + single[0] * (
        10 ** 0)


# level:
# SUITED_JUNKO   = 8  #同花顺
# QUADS          = 7  #四条
# FULL_HOUSE     = 6  #葫芦
# SUITED         = 5  #同花
# JUNKO          = 4  #顺子
# TRIPS          = 3  #三条
# TWO_PAIRS      = 2  #两对
# PAIR           = 1  #一对
# HIGH           = 0  #高牌
LEVEL = {8:"Straight Flush",7:"Four of a Kind",6:"Full House",5:" Flush", 4:"Straight",3:"Three of a Kind",2:"Two Pair",1:"Pair",0:"High"}

def calculate_level(cards):
    if is_junko(cards)[0] and is_suited(cards)[0]:
        return [8, is_junko(cards)[1]]
    elif is_quads(cards)[0]:
        return [7, is_quads(cards)[1]]
    elif is_full_house(cards)[0]:
        return [6, is_trip(cards)[1]]
    elif is_suited(cards)[0]:
        return [5, high(cards)]
    elif is_junko(cards)[0]:
        return [4, is_junko(cards)[1]]
    elif is_trip(cards)[0]:
        return [3, is_trip(cards)[1]]
    elif is_two_pair(cards)[0]:
        return [2, is_two_pair(cards)[1]]
    elif is_pair(cards)[0]:
        return [1, is_pair(cards)[1]]
    else:
        return [0, high(cards)]


def highest(all_cards):
    max_level, max_score = calculate_level(all_cards[0])
    max_card = all_cards[0]
    for cards in all_cards[1:]:
        level, score = calculate_level(cards)
        if level > max_level:
            max_level = level
            max_score = score
            max_card = cards
        elif level == max_level:
            if score > max_score:
                max_level = level
                max_score = score
                max_card = cards
    print (max_level, max_score, LEVEL[max_level], transfer_reverse(max_card))
    return max_level, max_score, LEVEL[max_level], transfer_reverse(max_card)

"""
print(calculate_level(cards1))
print(calculate_level(cards2))
print(calculate_level(cards3))
print(calculate_level(cards4))
print(calculate_level(cards5))
print(calculate_level(cards6))
print(calculate_level(cards7))
print(calculate_level(cards8))
print(transfer(my))
print(highest(transfer(my)))
"""
