#! /usr/bin/python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2018-05-21 11:25:12

import logging
import sys
import json
import pandas as pd
from flask import (Flask, request, render_template)
from flask import json
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash


mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'aws_ubuntu'
app.config['MYSQL_DATABASE_PASSWORD'] = 'jay'
app.config['MYSQL_DATABASE_DB'] = 'Flask_DB'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(
        filename, lineno, exc_type, exc_obj))


@app.route('/')
def main():
    return render_template('firstpage.html',PM25=PM25())

def PM25():
    air_box_json=pd.read_json('https://pm25.lass-net.org/data/last-all-airbox.json')
    PM25points=[[s['gps_lat'],s['gps_lon'],s['s_d0']] for s in air_box_json['feeds']]
    return PM25points

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')


@app.route('/showLogIn')
def showSignIn():
    return render_template('login.html')


@app.route('/logIn', methods=['POST'])
def signIn():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        _name = request.form.get('inputName', None)
        _password = request.form.get('inputPassword', None)

        if _name and _password:
            _hashed_password = generate_password_hash(_password)
            cursor.execute('select user_name, user_password from Accounts where\
                           user_name={} and\
                           user_password={}'.format(_name, _hashed_password))
            data = cursor.fetchall()
        if len(data) is 0:
            return json.dumps({'message': 'User login successfully!'})
        else:
            return json.dumps({'message': 'User login failed'})

    except Exception as e:
        PrintException()
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()


@app.route('/signUp', methods=['POST'])
def signUp():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        # read the posted values from the UI
        _name = request.form.get('inputName', None)
        _password = request.form.get('inputPassword', None)

        logging.debug("account:{_name} password:{_password}")
        # validate the received values
        if _name and _password:

            _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_createUser', (_name, _hashed_password))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps({'message': 'User created successfully!'})
            else:
                return json.dumps({'error': str(data[0])})
        else:
            return json.dumps({'html': '<span>Enter the required fields</span>'})

    except Exception as e:
        PrintException()
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    try:
        app.run()
    except:
        PrintException()
