import poke
# mine card


# host
# add user
# leave user

# start game
# open 3,4,5

# get result and shuffle
class Server:
    def __init__(self):
        self.table = poke.Table()

    def start(self):
        self.table.startGame()
    
    def sitUser(uid):
        self.table.sitUser()

    def leaveUser(uid):
        self.table.leaveUser()
        
    def myCard(uid):
        pass

class Commander:
    def __init__(self):
        self.table = poke.Table()
    def cmd(self, cmds, args):
        if cmds == 'sit':
            for user in args:
                self.table.sitUser(user)
        elif cmds == 'leave':
            for user in args:
                self.table.leaveUser(user)
        elif cmds == 'look':
            if args:
                return self.table.userHandCards(args[0])
            else:
                return self.table.riverCards()
        elif cmds == 'start':
            self.table.startGame()
        elif cmds == 'end':
            res =  self.table.endGame()
            text = 'River: %s\n' % self.table.river()
            for uid in res:
                user = self.table.users[uid]
                text += 'User [%s] %s %s(%s) Win\n' % (uid, user.hand, user.kind, user.cards)
            for uid in self.table.users:
                if self.table.users[uid].failed:
                    text += 'User [%s] Droped' % (uid)
                if uid not in res:
                    user = self.table.users[uid]
                    text += 'User [%s] %s %s(%s) Lose\n' % (uid, user.hand, user.kind, user.cards)
            return text
        elif cmds == 'open':
            self.table.openCards()
            return self.table.riverCards()
        elif cmds == 'people':
            return self.table.people()
    
    def run(self):
        x = input('>>> ')
        while x:
            xl = x.split()
            if len(xl) > 1:
                ans = self.cmd(xl[0], xl[1:])
            else:
                ans = self.cmd(xl[0], [])
            if ans is not None:
                print(ans)
            x = input('>>> ')

def main():
    c = Commander()
    c.run()

if __name__ == '__main__':
    main()



        
