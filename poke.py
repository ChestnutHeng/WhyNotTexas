import random
import uuid
from enum import IntEnum
import traceback
import copy
import functools

pokerSet = ['♠A', '♠2', '♠3', '♠4', '♠5', '♠6', '♠7', '♠8', '♠9', '♠10', '♠J', '♠Q', '♠K',
            '♥A', '♥2', '♥3', '♥4', '♥5', '♥6', '♥7', '♥8', '♥9', '♥10', '♥J', '♥Q', '♥K',
            '♣A', '♣2', '♣3', '♣4', '♣5', '♣6', '♣7', '♣8', '♣9', '♣10', '♣J', '♣Q', '♣K',
            '♦A', '♦2', '♦3', '♦4', '♦5', '♦6', '♦7', '♦8', '♦9', '♦10', '♦J', '♦Q', '♦K',
            ]
pokerName = IntEnum('PokerName', ('RoyalFlush', 'StraightFlush', 'FourOfAKind', 'FullHouse',
                      'Flush', 'Straight', 'ThreeOfAKind', 'TwoPair', 'OnePair', 'HighCard'))
pokerZhCn = {pokerName.RoyalFlush: '皇家同花顺', pokerName.StraightFlush: '同花顺', pokerName.FourOfAKind:  '四条',
             pokerName.FullHouse: '葫芦', pokerName.Flush: '同花', pokerName.Straight: '顺子',
             pokerName.ThreeOfAKind: '三条', pokerName.TwoPair: '两对',
             pokerName.OnePair: '一对', pokerName.StraightFlush: '高牌'}


class Card:
    color = ''
    number = 0

    def __init__(self, color='', number=0):
        self.color = color
        self.number = number

    def parse(self, strs):
        self.color = strs[0]
        strnum = strs[1:]
        if strnum.isdigit():
            self.number = int(strnum)
        else:
            self.number = {'A':14, 'J':11, 'Q':12, 'K':13}[strnum]

    def __repr__(self):
        strs = self.color
        if 1 < self.number <= 10:
            strs += str(self.number)
        else:
            strs += {11: 'J', 12: 'Q', 13: 'K', 14: 'A', 1:'A', 0:'?'}[self.number]
        return strs


class Table:
    pokers = []
    rivers = []
    users = {}
    needle = 0
    riverPoint = 0
    def __init__(self):
        for v in pokerSet:
            c = Card()
            c.parse(v)
            self.pokers.append(c)
        self.shuffle()

    def shuffle(self):
        self.needle = 0
        self.riverPoint = 0
        random.shuffle(self.pokers)
        self.rivers = None

    def getCards(self, num):
        if self.needle + num >= len(self.pokers):
            self.shuffle()
        cards = self.pokers[self.needle: self.needle+num]
        self.needle += num
        return cards

    def deal(self):
        if not self.rivers:
            self.river()
        return self.getCards(2)

    def river(self):
        if not self.rivers:
            self.rivers = self.getCards(5)
        return self.rivers
    
    def sitUser(self,uid):
        u = User(uid)
        self.users[uid] = u
        return u.userID

    def leaveUser(self,uid):
        del self.users[uid]
    
    def startGame(self):
        self.shuffle()
        for uid in self.users:
            self.users[uid].pick(self.deal())
    
    def userHandCards(self, uid):
        if uid in self.users:
            return self.users[uid].hand
        else:
            return None

    def openCards(self):
        if self.riverPoint == 0:
            self.riverPoint = 3
        else:
            self.riverPoint += 1
    
    def riverCards(self):
        return self.rivers[:self.riverPoint]
    
    def endGame(self):
        if self.riverPoint < 5:
            self.riverPoint = 5
        res = Judge.judge(self, self.users)
        return res
    
    def people(self):
        return self.users.keys


class User():
    hand = []
    userID = ''
    kind = None
    cards = []
    failed = False
    def __init__(self, seed=''):
        if seed:
            self.userID = seed
        else:
            self.userID = uuid.uuid4()
    def pick(self, cards):
        self.hand = cards
    
    def __repr__(self):
        return '{%s:[%s]%s}' % (self.userID, self.kind, self.cards)


class PairCard():
    def __init__(self, card, times):
        self.times = times
        self.card = card
    def __repr__(self):
        return '{Card:%d Times:%d}' % (self.card, self.times)


class Judge:
    @staticmethod
    def judge(table, users, handler=None):
        ansArr = []
        maxuser = list(users.keys())[0]
        maxusers = set()
        for uid in users:
            if users[uid].failed:
                continue
            kind, cards = Judge.judge7(table.rivers + users[uid].hand)
            users[uid].kind = kind
            users[uid].cards = cards
            ansArr.append(users[uid])
            if Judge.judgeRes(users[uid], users[maxuser]) > 0:
                maxuser = uid
            if handler:
                handler.handle(kind, cards)
        for uid in users:
            if users[uid].failed:
                continue
            if Judge.judgeRes(users[uid], users[maxuser]) == 0:
                maxusers.add(uid)
        return maxusers
    @staticmethod
    def judgeRes(x, y):
        if x.kind > y.kind:
            return -1
        elif x.kind < y.kind:
            return 1
        else:
            for i in range(0, 5):
                if x.cards[i].number < y.cards[i].number:
                    return -1
                elif x.cards[i].number > y.cards[i].number:
                    return 1
        return 0 
        

    @staticmethod
    def findBiggest(cards, num):
        return sorted(cards, reverse=True, key=lambda x:x.number)[:num]

    @staticmethod
    def findBiggestFromGrouped(cards, num):
        newc = []
        for c in cards:
            for v in c:
                newc.append(v)
        return Judge.findBiggest(newc, num)
        

    # cards : bigger than 5 members
    @staticmethod
    def judgeStraight(cards):
        if cards[-1].number == 14:
            cards = [Card(cards[-1].color, 1)] + cards
        cards.append(Card('', 0))
        incr = 1
        incrCard = [cards[0]]
        groupedIncrs = []
        for i in range(1, len(cards)):
            if cards[i].number == cards[i-1].number + 1:
                incr += 1
                incrCard.append(cards[i])
            else:
                groupedIncrs.append(incrCard)
                incrCard = [cards[i]]
                incr = 1
        for inc in groupedIncrs:
            if len(inc) >= 5:
                return inc[-5:].reverse()
        return None
    
    @staticmethod
    def judgeFlush(cards):
        # is flush
        flushCards = None
        samingC = {'♣':[], '♦':[], '♠':[], '♥':[]}
        for v in cards:
            samingC[v.color].append(v)
        for k in samingC:
            if len(samingC[k]) >= 5:
                sf =  Judge.judgeStraight(samingC[k])
                if sf:
                    return sf, True
                return Judge.findBiggest(samingC[k], 5), False
        return flushCards, False

    @staticmethod
    def judgePair(cards):
        saming = 1
        groupedPairs = []
        sameCard = [cards[0]]
        cards.append(Card())
        for i in range(1, len(cards)):
            if cards[i].number == cards[i-1].number:
                saming += 1
                sameCard.append(cards[i])
            else:
                groupedPairs.append(sameCard)
                sameCard = [cards[i]]
                saming = 1
        # 先按组数排，再按牌面排，前面牌面已经排过
        groupedPairs = sorted(groupedPairs, key=lambda x : len(x))
        #print(groupedPairs)
        return groupedPairs

    @staticmethod
    def judge7(cards):
        #print(cards)
        cards = sorted(cards, key=lambda x:x.number)
        cardsFlush, isSF = Judge.judgeFlush(cards)
        cardsStraight = Judge.judgeStraight(cards)
        # special straight
        if isSF:
            if cardsFlush[-1].number == 14:
                return pokerName.RoyalFlush, cardsFlush
            else:
                return pokerName.StraightFlush, cardsFlush
        # pairs
        groupedPairs = Judge.judgePair(cards)
        biggestPair = groupedPairs.pop()
        if len(biggestPair) == 4:
            single = Judge.findBiggestFromGrouped(groupedPairs, 1)
            return pokerName.FourOfAKind, biggestPair + single
        elif len(biggestPair) == 3:
            if len(groupedPairs[-1]) == 2:
                return pokerName.FullHouse, biggestPair + groupedPairs[-1]
        if cardsFlush:
            return pokerName.Flush, cardsFlush
        if cardsStraight:
            return pokerName.Straight, cardsStraight
        if len(biggestPair) == 3:
            return pokerName.ThreeOfAKind, biggestPair + Judge.findBiggestFromGrouped(groupedPairs, 2)
        if len(biggestPair) == 2:
            if len(groupedPairs[-1]) == 2:
                secondPair = groupedPairs.pop()
                others = Judge.findBiggestFromGrouped(groupedPairs, 1)
                return pokerName.TwoPair, biggestPair + secondPair + others
            else:
                return pokerName.OnePair, biggestPair + Judge.findBiggestFromGrouped(groupedPairs, 3)
        return pokerName.HighCard, Judge.findBiggest(cards, 5)


class Handler:
    kindMap = {}
    allC = 0
    def handle(self, kind, card):
        print(kind, card)
        # if kind in [pokerName.Flush, pokerName.StraightFlush]:
        #     print(kind, card)
        self.allC += 1
        if kind in self.kindMap:
            self.kindMap[kind] += 1
        else:
            self.kindMap[kind] = 1

def main():
    d = Table()
    h = Handler()
    users = []
    for i in range(0, 6):
        users.append(User())
    i = 0
    C = 100000
    while i < C:
        d.shuffle()
        for user in users:
            user.pick(d.deal())
        #print(d.rivers)
        Judge.judge(d, users, h)
        i += 1
    print(h.kindMap)
    for k in h.kindMap:
        print(k, h.kindMap[k]/float(h.allC)*100)

if __name__ == '__main__':
    main()

