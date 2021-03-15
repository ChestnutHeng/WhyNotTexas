import poke
from user import get_name_by_id

class Context:
    def __init__(self, uid, tid):
        self.uid = uid
        self.tid = tid
    def __repr__(self):
        return 'uid:%s tid:%s' % (self.uid, self.tid)

class MsgBox:
    msgQ = []
    def push(self, text):
        self.msgQ.append({'text':text, 'uid':set(), 'type':1})
    def pushMsg(self, msg):
        self.msgQ.append({'msg':msg, 'uid':set(), 'type':2})
    def travel(self, uid):
        ans = []
        for v in self.msgQ:
            if v['type'] == 1 and uid not in v['uid']:
                ans.append(v['text'])
                v['uid'].add(uid)
        return ans
    def consume(self, uid):
        ans = []
        for v in self.msgQ:
            if v['type'] == 2 and uid not in v['uid']:
                ans.append(v['msg'])
                v['uid'].add(uid)
        return ans

class ServerHandler:

    def __init__(self, tableMap : dict, boxMap : MsgBox):
        self.tableMap = tableMap
        self.msgBox = boxMap

    def _check_ctx(self, ctx : Context):
        resp = {"msg" : "", "retcode" : 0, 'textbox': []}
        resp['myuid'] = ctx.uid
        resp['mytid'] = ctx.tid
        if ctx.tid not in self.tableMap:
            return False, {"msg" : "bad table", "retcode" : 1}, None
        table : poke.Table = self.tableMap[ctx.tid]
        if ctx.uid not in table.users:
            return False, {"msg" : "bad user", "retcode" : 2}, None
        return True, resp, table
    
    def _defer(self, ctx : Context, resp, table, user):
        resp['textbox'] = self.msgBox.travel(ctx.uid)
        resp['msgQ'] = self.msgBox.consume(ctx.uid)
        resp['moving_uid'] = table.needMoveUser().userID
        resp['river'] = []
        for v in table.riverCards():
            resp['river'].append(v.__repr__())
        resp['user_hand'] = []
        for card in table.userHandCards(user.userID):
            resp['user_hand'].append(card.__repr__())
        resp['user_table_money'] = user.table_money
        resp['user_money'] = user.money
        return resp

    def ticker(self, ctx : Context):
        ok, resp, tablee = self._check_ctx(ctx)
        table : poke.Table = tablee
        if not ok:
            return resp
        me : poke.User = table.users[ctx.uid]
        return self._defer(ctx, resp, table, me)

    def prepare(self, ctx : Context):
        ok, resp, tablee = self._check_ctx(ctx)
        table : poke.Table = tablee
        if not ok:
            return resp
        me : poke.User = table.users[ctx.uid]
        # ...
        ok = table.prepareUser(me.userID)
        if not ok:
            return self._defer(ctx, resp, table, me)
        self.msgBox.push('%s 准备完成.\n' % (get_name_by_id(me.userID)))
        if table.isPrepared:
            table.startGame()
            self.msgBox.push('全部准备完成\n')
            self.msgBox.push('开始！\n')
            resp['hook_func'] = ['showUserHands']
        return self._defer(ctx, resp, table, me)
    
    def checkAddFold(self, ctx : Context, ops : str, extra):
        ok, resp, tablee = self._check_ctx(ctx)
        table : poke.Table = tablee
        if not ok:
            return resp
        me : poke.User = table.users[ctx.uid]
        nowuser : poke.User = table.needMoveUser()
        # not you
        if nowuser.userID != me.userID:
            resp['msg'] = 'not your turn'
            self.msgBox.push('%s 请等待%s行动.\n' % (get_name_by_id(me.userID), get_name_by_id(nowuser.userID)))
            return self._defer(ctx, resp, table, me)
        if ops == 'add':
            self.msgBox.push('%s 加了%s美元.\n' % (get_name_by_id(me.userID), extra))
        elif ops == 'check':
            self.msgBox.push('%s 跟了.\n' % (get_name_by_id(me.userID)))
        winner, hook = table.userMove(me.userID, ops, extra)
        if hook == 'endGame':
            return self.endGame(ctx, winner, table, me, resp)
        elif hook == 'openCards':
            self.msgBox.pushMsg({"hook_func" : "openCards"})
        if ops == 'fold':
            if hook != 'CantFold':
                self.msgBox.push('%s 飞了.\n' % (get_name_by_id(me.userID)))
            else:
                self.msgBox.push('%s 不能飞.一样的注.\n' % (get_name_by_id(me.userID)))
        return self._defer(ctx, resp, table, me)
    
    def endGame(self, ctx, winner, table, me, resp):
        for winid in winner:
            self.msgBox.push('%s 以牌型 %s [%s]获胜\n' % (get_name_by_id(winid), table.users[winid].cards, poke.pokerZhCn[table.users[winid].kind]))
        otherHands = {}
        for uid in table.users:
            otherHands[uid] = []
            for card in table.users[uid].hand:
                otherHands[uid].append(card.__repr__())
            if uid in winner:
                continue
            if table.users[uid].fold:
                self.msgBox.push('%s 飞牌\n' % (get_name_by_id(uid)))
            else:
                self.msgBox.push('%s 牌型 %s[%s] 落败\n' % (get_name_by_id(uid), table.users[uid].cards, poke.pokerZhCn[table.users[uid].kind]))
        self.msgBox.pushMsg({'winner':list(winner), 'other_hand' : otherHands, "hook_func" : "endGame"})
        return self._defer(ctx, resp, table, me)

no = 1
def printl(text):
    global no
    print(no, text)
    no += 1

if __name__ == '__main__':
    tableMap = {}
    tableid = '1'
    tableMap[tableid] = poke.Table()
    tableMap[tableid].sitUser('1')
    tableMap[tableid].sitUser('2')
    tableMap[tableid].sitUser('3')

    msg = MsgBox()
    s = ServerHandler(tableMap, msg)

    printl(s.ticker(Context('1', '1')))
    print(s.prepare(Context('1', '1')))
    print(s.prepare(Context('2', '1')))
    print(s.prepare(Context('3', '1')))

    printl(s.ticker(Context('1', '1')))
    printl(s.ticker(Context('2', '1')))
    printl(s.ticker(Context('1', '1')))

    printl(s.checkAddFold(Context('1', '1'), 'add', None))
    printl(s.checkAddFold(Context('2', '1'), 'add', 6))
    no  = 0
    printl(s.checkAddFold(Context('3', '1'), 'check', None))
    printl(s.checkAddFold(Context('1', '1'), 'fold', None))
    printl(s.checkAddFold(Context('2', '1'), 'check', None))

    printl(s.checkAddFold(Context('3', '1'), 'check', None))
    printl(s.ticker(Context('2', '1')))
    printl(s.checkAddFold(Context('2', '1'), 'check', None))
    printl(s.checkAddFold(Context('3', '1'), 'check', None))
    printl(s.checkAddFold(Context('2', '1'), 'check', None))
    printl(s.checkAddFold(Context('3', '1'), 'check', None))

    printl(s.ticker(Context('1', '1')))
    printl(s.ticker(Context('2', '1')))
    printl(s.ticker(Context('3', '1')))
        
        
        

        