# -*- coding: utf8 -*-
import time
from flask import Flask
from flask import request
from flask import jsonify
from flask import render_template
from flask import redirect,url_for
from flask import make_response
from codecs import open
import logging
import json

import poke

app = Flask('tex')

tableMap = {}
firstTable = '1st'

@app.route('/tex', methods=['GET', 'POST'])
def tex_page():
    plog(request.form)
    if request.method == 'POST':
        table = getTableFromReq(request)
        user = request.form.get('user')
        if user not in ['ji', 'lv', 'long', 'shen']:
            return jsonify({'data': '警戒'})
        if table not in tableMap:
            tableMap[table] = poke.Table()
            tableMap[table].sitUser(user)
        else:
            tableMap[table].sitUser(user)
        resp = make_response(render_template('table.html'))
        resp.set_cookie('user', user)
        resp.set_cookie('table', table)
        return resp
    else:
        return render_template('tex.html')

@app.route('/tex/table', methods=['Get'])
def login():
    return render_template('table.html')

def getTableFromReq(request):
    table = request.form.get('table')
    if table == '':
        table = firstTable
    return table

def plog(sth):
    app.logger.info(sth)
    print(sth)

def init_logger():
    handler = logging.FileHandler('app_logger.log', encoding='UTF-8')
    handler.setLevel(logging.INFO)
    logging_format = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    handler.setFormatter(logging_format)
    app.logger.addHandler(handler)

def main():
    init_logger()

if __name__ == '__main__':
    init_logger()
    #app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run(host="127.0.0.1",port=4640, debug=True)
else:
    init_logger()
    app.debug = True