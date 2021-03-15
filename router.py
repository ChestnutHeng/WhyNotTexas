# -*- coding: utf8 -*-
import time
import os
import json
from codecs import open

import flask
from flask import Flask, session
from flask import request
from flask import jsonify
from flask import render_template
from flask import redirect,url_for
from flask import make_response


from flask_login import LoginManager
from flask_login import logout_user, login_user, login_required
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from flask_restful import reqparse
#from flask_wtf.csrf import exempt


# from geventwebsocket.handler import WebSocketHandler
# from gevent.pywsgi import WSGIServer

import logging
import poke
from user import get_user, create_user, get_user_by_id, User
from view import SignupForm, LoginForm, ManageForm, ManageTableForm
from server import ServerHandler, MsgBox, Context

app = Flask('tex')
app.config['SECRET_KEY'] = os.urandom(24)
app.secret_key = os.urandom(24)
login_manager = LoginManager()  # 实例化登录管理对象
CSRFProtect(app)
#socketio = SocketIO(app)


tableMap = {}
msgMap = {}
firstTable = '1'

@login_manager.user_loader  # 定义获取登录用户的方法
def load_user(user_id):
    return User.get(user_id)

@app.route('/tex', methods=['GET', 'POST'])
def tex_page():
    return redirect(url_for("login"))

@app.route('/tex/signup/', methods=('GET', 'POST'))  # 注册
def signup():
    form = SignupForm()
    emsg = None
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user_info = get_user(user_name)  # 用用户名获取用户信息
        if user_info is None:
            #create_user(user_name, password)  # 如果不存在则创建用户
            return redirect(url_for("login"))  # 创建后跳转到登录页
        else:
            emsg = "用户名已存在"  # 如果用户已存在则给出错误提示
    return render_template('signup.html', form=form, emsg=emsg)

@app.route('/tex/login/', methods=('GET', 'POST'))  # 登录
def login():
    form = LoginForm()
    emsg = None
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        tableid = form.tableid.data
        if tableid == '':
            tableid = firstTable
        user_info = get_user(user_name)
        if user_info is None:
            emsg = "用户名或密码密码有误"
        else:
            user = User(user_info)
            if user.verify_password(password):
                login_user(user)
                if tableid not in tableMap:
                    tableMap[tableid] = poke.Table()
                    msgMap[tableid] = MsgBox()
                    tableMap[tableid].sitUser(user.id)
                else:
                    tableMap[tableid].sitUser(user.id)
                session['tableid'] = tableid
                session['uid'] = user.id
                plog('User %s logined with table:%s' % (user.username, tableid))
                return redirect(request.args.get('next') or url_for('table'))
            else:
                emsg = "用户名或密码密码有误"
    return render_template('login.html', form=form, emsg=emsg)

@app.route('/tex/manage/', methods=('GET', 'POST'))  # 管理
@login_required
#@csrf.exempt
def manage():
    form = ManageForm()
    for k in tableMap:
        for uk in tableMap[k].users:
            form.table.append_entry(data={
                'tableid' : k,
                'uid' : uk,
                'hands' : tableMap[k].users[uk].__repr__(),
                'username' : get_user_by_id(uk).get("name")
            })
    emsg = None
    if form.validate_on_submit():
        hisuid = form.uid.data
        tableid = form.tableid.data
        uid = session.get('uid', '')
        plog('%s want to kick %s on table %s.' % (uid, hisuid , tableid))
        if uid == '888':
            if tableid in tableMap: 
                err = tableMap[tableid].leaveUser(hisuid)
                if err:
                    emsg = '%s want to kick %s on table %s err: %s' % (uid, hisuid , tableid, err)
                else:
                    emsg = '%s on table %s is kicked.' % (hisuid , tableid)
        else:
            emsg = 'No Permission'
    plog('manage emsg:%s' % emsg)
    return render_template('manage.html', form=form, emsg=emsg)

@app.route('/tex/table', methods=['Get'])
@login_required
def table():
    return render_template('table.html')

@app.route('/tex/logout')  # 登出
@login_required
def logout():
    logout_user()
    tableid = session.get('tableid', '')
    uid = session.get('uid', '')
    if tableid and uid and tableid in tableMap:
        err = tableMap[tableid].leaveUser(uid)
        if err:
            plog('logout err:' % err)
    return redirect(url_for('login'))

def parse_arg_from_requests(arg, **kwargs):
    parse = reqparse.RequestParser()
    parse.add_argument(arg, **kwargs)
    args = parse.parse_args()
    return args[arg]

@app.route('/tex/api', methods=['POST'])
@login_required
def api():
    data = request.get_json('data')
    tableid = session.get('tableid', '')
    uid = session.get('uid', '')
    plog('api: %s on table %s |req:%s|reqdata:%s' % (uid , tableid, data, request.data))
    s = ServerHandler(tableMap, msgMap[tableid])
    ctx = Context(uid, tableid)
    resp = None
    if 'func' in data:
        if data['func'] == 'prepare':
            resp = s.prepare(ctx)
        elif data['func'] == 'tick':
            resp = s.ticker(ctx)
        elif data['func'] == 'add':
            resp = s.checkAddFold(ctx, 'add', data['add_money'])
        elif data['func'] in ['fold', 'check']:
            resp = s.checkAddFold(ctx, data['func'], None)
        else:
            resp = {'msg':'invaild cmd', 'retcode':-1}
    else:
        resp = {'msg':'empty cmd', 'retcode':-2}
    plog('api: %s on table %s |resp:%s' % (uid , tableid, resp))
    return jsonify(resp)

def plog(sth):
    app.logger.info(sth)
    print(sth)

def init_logger():
    handler = logging.FileHandler('app_logger.log', encoding='UTF-8')
    handler.setLevel(logging.INFO)
    logging_format = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    handler.setFormatter(logging_format)
    app.logger.addHandler(handler)

def init_login():
    login_manager.init_app(app)  # 初始化应用
    login_manager.session_protection = 'strong'
    login_manager.login_view = 'login'  # 设置用户登录视图函数 endpoint

def main():
    init_logger()

if __name__ == '__main__':
    init_logger()
    init_login()
    #app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run(host="127.0.0.1",port=4640, debug=True,threaded=True)
    #socketio.run(app)
else:
    init_logger()
    app.debug = True