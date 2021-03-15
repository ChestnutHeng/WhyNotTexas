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
             pokerName.OnePair: '一对', pokerName.HighCard: '高牌'}

DIZHU = 1

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
    # user info
    users = {}
    # user sit, as long with table exists
    userEmptySit = list(range(1, 11))
    userSit = []
    bankerIndex = 0
    turnIndex = 0
    sitUidMap = {}
    # all deck cards deal pointers
    needle = 0
    # river cards pointers
    riverPoint = 0
    # is all user prepered
    isPrepared = False
    IsEnd = False
    # max stake
    maxStake = DIZHU
    # how many people fold
    foldCount = 0
    # next n action will open cards
    openActionStep = -1
    def __init__(self):
        for v in pokerSet:
            c = Card()
            c.parse(v)
            self.pokers.append(c)
        self._shuffle()
        self.userEmptySit = list(range(1, 11))
        self.userSit = []

    def _shuffle(self):
        self.needle = 0
        self.riverPoint = 0
        random.shuffle(self.pokers)
        self.rivers = None

    def _getCards(self, num):
        if self.needle + num >= len(self.pokers):
            self._shuffle()
        cards = self.pokers[self.needle: self.needle+num]
        self.needle += num
        return cards

    def deal(self):
        if not self.rivers:
            self._river()
        return self._getCards(2)

    def _river(self):
        if not self.rivers:
            self.rivers = self._getCards(5)
        return self.rivers
    
    def sitUser(self,uid):
        if not self.userEmptySit:
            return 'no empty sit!'
        sitIndex = self.userEmptySit.pop(0)
        u = User(uid)
        u.sitIndex = sitIndex
        self.users[uid] = u
        self.userSit.append(sitIndex)
        self.sitUidMap[sitIndex] = uid
        return u.userID
    
    def prepareUser(self, uid):
        if uid in self.users:
            if not self.users[uid].isPrepared:
                self.users[uid].isPrepared = True
            else:
                return False
        isAllPrepared = True
        for u in self.users:
            if not self.users[u].isPrepared:
                isAllPrepared = False
        self.isPrepared = isAllPrepared
        return True

    def leaveUser(self,uid):
        if uid in self.users:
            sitIndex = self.users[uid].sitIndex
            self.userEmptySit.insert(0, sitIndex)
            self.userSit.remove(sitIndex)
            del self.users[uid]
            return ''
        else:
            return 'del %s not found user' % (uid)
    
    def startGame(self):
        if not self.isPrepared:
            return 'some user not prepared'
        self._shuffle()
        for uid in self.users:
            self.users[uid].pick(self.deal())
            self.users[uid].table_money = DIZHU
        self.turnIndex = self.bankerIndex + 1 % len(self.userSit)
        self.maxStake = DIZHU
        self.foldCount = 0
        self.resetSteps()
        return ''
    
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
        if self.isPrepared:
            return self.rivers[:self.riverPoint]
        else:
            return []
    
    def endGame(self):
        if self.riverPoint < 5:
            self.riverPoint = 5
        res = Judge.judge(self, self.users)
        self.bankerIndex = (self.bankerIndex + 1) % len(self.userSit)
        # feng chen
        allMoney = 0
        for uid in self.users:
            allMoney += self.users[uid].table_money
        for uid in self.users:
            self.users[uid].isPrepared = False
            self.users[uid].money -= self.users[uid].table_money
            if uid in res:
                self.users[uid].money += int(allMoney / len(res))
        return res
    
    def people(self):
        return self.users.keys

    # turnIndex + 1
    def setNextTurnIndex(self):
        self.turnIndex = (self.turnIndex + 1) % len(self.userSit)
        moveuid = self.sitUidMap[self.userSit[self.turnIndex]]
        user : User = self.users[moveuid]
        if user.fold:
            self.setNextTurnIndex()
    
    # now act user's id
    def needMoveUser(self):
        uid = self.sitUidMap[self.userSit[self.turnIndex]]
        return self.users[uid]

    def resetSteps(self):
        self.openActionStep = len(self.userSit) - self.foldCount

    def userMove(self, uid, ops, extra):
        moveuid = self.sitUidMap[self.userSit[self.turnIndex]]
        if moveuid != uid:
            return None, 'NotYourTurn'
        user : User = self.users[uid]
        hook_func = ''
        if ops == 'add':
            self.maxStake = extra
            user.table_money = self.maxStake
            self.resetSteps()
            self.openActionStep -= 1
            self.setNextTurnIndex()
            return None, hook_func
        if ops == 'check':
            user.table_money = self.maxStake
        if ops == 'fold':
            if user.table_money == self.maxStake:
                return None, 'CantFold'
            user.fold = True
            self.foldCount += 1
            if len(self.userSit) - self.foldCount <= 1:
                return self.endGame(), 'endGame'
        self.openActionStep -= 1
        if self.openActionStep == 0:
            if self.riverPoint == 5:
                return self.endGame(), 'endGame'
            self.openCards()
            self.resetSteps()
            hook_func = 'openCards'
        self.setNextTurnIndex()
        return None, hook_func


class User():
    hand = []
    userID = ''
    kind = None
    cards = []
    fold = False
    isPrepared = False
    # sit
    sitIndex = -1
    # money
    money = 0
    table_money = 0
    def __init__(self, seed=''):
        if seed:
            self.userID = seed
        else:
            self.userID = uuid.uuid4()
    def pick(self, cards):
        self.hand = cards
    
    def __repr__(self):
        return '{uid:%s|kind:%s|cards:%s|hand:%s|fold:%s}' % (self.userID, self.kind, self.cards, self.hand, self.fold)


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
        maxuser = None
        maxusers = set()
        for uid in users:
            if users[uid].fold:
                continue
            kind, cards = Judge.judge7(table.riverCards() + users[uid].hand)
            users[uid].kind = kind
            users[uid].cards = cards
            ansArr.append(users[uid])
            if maxuser is None or Judge.judgeRes(users[uid], users[maxuser]) > 0:
                maxuser = uid
            if handler:
                handler.handle(kind, cards)
        for uid in users:
            if users[uid].fold:
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
                if x.cards[i].number == 1 and y.cards[i].number != 1:
                    return 1
                if y.cards[i].number == 1 and x.cards[i].number != 1:
                    return -1
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
        d._shuffle()
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

