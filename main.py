import google
from flask import Flask, render_template, request, session, redirect, url_for
from Login import auth
from util import util, encrypt, get_profilepic
from User import user
from Admin import admin
from General import both
import requests
from werkzeug.utils import secure_filename
from io import BytesIO
import hmac, hashlib
from secrets import compare_digest
from collections import defaultdict
from secret_keys import STRIPE_SECRET_KEYS, STRIPE_PUBLIC_KEYS, GOOGLE_API_KEY, GOOGLE_ACCOUNT_KEY
import sqlite3 as sql
import pandas as pd
import numpy as np
import Encryption
import datetime
import json
import base64
import stripe
import re
import string
import random
import ast
import socket
import os

app = Flask(__name__, static_url_path='/static')
app.register_blueprint(auth)
app.register_blueprint(util)
app.register_blueprint(user)
app.register_blueprint(admin)
app.register_blueprint(both)
counter = 0
#cartCounter = 0

# Personal Stripe Account Connection -- Need company connections!!
app.config['STRIPE_PUBLIC_KEY'] = STRIPE_PUBLIC_KEYS
app.config['STRIPE_SECRET_KEY'] = STRIPE_SECRET_KEYS
stripe.api_key = app.config['STRIPE_SECRET_KEY']

app.config['GOOGLE_API_KEY'] = GOOGLE_API_KEY
app.config['GOOGLE_ACCOUNT_KEY'] = GOOGLE_ACCOUNT_KEY
google.config = app.config['GOOGLE_ACCOUNT_KEY']

# Directory route for profile pictures  ie 'static/css/uploads/______'
UPLOAD_FOLDER = 'static/css/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# work needing to be done:
# provided YouTube links for examples / follow along code

# ------------------ FRONTEND ------------------
# both - signup / remember me is fake                                                                    https://www.youtube.com/watch?v=CRvV9nFKoPI
# both - login forgot password  / route to ask for email, send email, allow for new pass saved!          https://www.youtube.com/watch?v=vutyTx7IaAI


# admin create team    // proper form                                                            
# ADMIN - create team ; better form-show contact info different ; search users by typing             https://www.youtube.com/watch?v=R4owT-LcKOo
#                                                                                                    https://www.youtube.com/watch?v=n8dqXI8kw_Y
# USER - usersjoin.html      //// redesign
# USER - usersjoinshow.html  //// redesign
# USER - userdash.html       //// checkin satus and names display as list along with cart values
# USERS - Need sponsor list display

# admin - checkin,edit,delete / maybe make as popup? // back button - instead of route to team list go back to specific team
# admin - view specific team // sponsor photo & payment activity

# - Ultimately will need to change all front end to be compatible with phones   1. https://www.youtube.com/watch?v=4WvT2cmuZ5M&list=PLL9jEdn7PvoT309qO1E_-fLnfhuw2T9kJ


# -------  ALL PAYMENT RELATED ITEMS
# - TEAMS NEED TO PAY BEFORE entering // ask how they want that handled
# -if team has not paid pop up on dash (ask how company wants handled - possibly ask team if sponsor paying; if not team captain pays?)
# -- maybe when creating a team; before routing to join code, route to payments page first
# both - home / membership link isn't accurate atm... maybe make team payment info page
# ADMIN - dash                // green total sales box need to be connected
# ADMIN - create payment logs
# ADMIN - team, user tables   // finish table information (with payments?)
# admin - view specific team // add payment activity
# STRIPE API - make neater connections (removing excess functions)


# ------------------ BACKEND ------------------
# ADMIN & USER ///// Search function fixed or all cases (possibly), need routing properly (if 0 results 'non found')
# USERS - Need auction house

# TESTING LINK --- will delete
@app.route('/new')
def generate():
    if not session.get('logged_in'):
        return render_template('signup.html')
    else:
        return render_template('assign1.html')



# **********************************************************************************************
#                                        PAYMENT STRIPE                    lines: 2230-2508    *
# **********************************************************************************************
# USERS - Routes to storefront
@app.route('/index')
def index():
    if 'UserName' not in session:
        return redirect(url_for('log_in'))

    nm = session['UserName']

    con = sql.connect('UserInfoDB.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute(
        "SELECT UserTeamId, UserTeamLead FROM UserInfo WHERE UserName = ?",
        (encrypt(nm),))
    rowz = cur.fetchall()
    if (rowz):
        UserTeamLead = rowz[0]['UserTeamLead']
    else:
        UserTeamLead = None

    rowzz = []
    for row in rowz:
        newRow = dict(row)
        rowzz.append(newRow)
    con.close()

    # pull picture pathfile to html
    photo = get_profilepic()

    return render_template('index.html', UserName=nm, photo=photo, UserTeamLead=UserTeamLead)


@app.route('/stripe_pay')
def stripe_pay():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1P454b2NIIHMdCWBNkGb1Fmc',
            'quantity': 1,

        }],
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('index', _external=True),
    )
    return {
        'checkout_session_id': session['id'],
        'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
    }


@app.route('/stripe_pay2')
def stripe_pay2():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1P4Mgx2NIIHMdCWBQYUuLP3k',
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('index', _external=True),
    )
    return {
        'checkout_session_id': session['id'],
        'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
    }


@app.route('/stripe_pay3')
def stripe_pay3():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1P4Mir2NIIHMdCWBmNk7yzAS',
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('index', _external=True),
    )
    return {
        'checkout_session_id': session['id'],
        'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
    }


@app.route('/stripe_pay4')
def stripe_pay4():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1P3iGJ2NIIHMdCWBy4CoBtc9',
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('index', _external=True),
    )
    return {
        'checkout_session_id': session['id'],
        'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
    }


@app.route('/stripe_pay5')
def stripe_pay5():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1P4Mrj2NIIHMdCWBX8nyAepY',
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('index', _external=True),
    )
    return {
        'checkout_session_id': session['id'],
        'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
    }


@app.route('/stripe_pay6')
def stripe_pay6():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1P4MxC2NIIHMdCWBRsDjynud',
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('index', _external=True),
    )
    return {
        'checkout_session_id': session['id'],
        'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
    }


@app.route('/stripe_pay7')
def stripe_pay7():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1P4Mzi2NIIHMdCWBAIRf7IRL',
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('index', _external=True),
    )
    return {
        'checkout_session_id': session['id'],
        'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
    }


@app.route('/stripe_pay8')
def stripe_pay8():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1P44pa2NIIHMdCWBpwswLOLC',
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('index', _external=True),
    )
    return {
        'checkout_session_id': session['id'],
        'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
    }


@app.route('/stripe_pay9')
def stripe_pay9():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1P44tn2NIIHMdCWBQ2osI7VZ',
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('index', _external=True),
    )
    return {
        'checkout_session_id': session['id'],
        'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
    }


@app.route('/stripe_pay10')
def stripe_pay10():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1P4NTr2NIIHMdCWBa7yv6U4A',
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('index', _external=True),
    )
    return {
        'checkout_session_id': session['id'],
        'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
    }


@app.route('/stripe_pay11')
def stripe_pay11():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1P4NWn2NIIHMdCWBzQ6Mc1Xy',
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('index', _external=True),
    )
    return {
        'checkout_session_id': session['id'],
        'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
    }


@app.route('/stripe_pay12')
def stripe_pay12():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1P4Nzd2NIIHMdCWBXHh88cGb',
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('index', _external=True),
    )
    return {
        'checkout_session_id': session['id'],
        'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
    }


@app.route('/stripe_pay13')
def stripe_pay13():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1P4O1b2NIIHMdCWB1Vp3VZxi',
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('index', _external=True),
    )
    return {
        'checkout_session_id': session['id'],
        'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
    }


@app.route('/thanks')
def thanks():
    return render_template('thanks.html')


@app.route('/stripe_webhook', methods=['POST'])
def stripe_webhook():
    print('WEBHOOK CALLED')

    if request.content_length > 1024 * 1024:
        print('REQUEST TOO BIG')
        abort(400)
    payload = request.get_data()
    sig_header = request.environ.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = 'YOUR_ENDPOINT_SECRET'
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        print('INVALID PAYLOAD')
        return {}, 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print('INVALID SIGNATURE')
        return {}, 400

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print(session)
        line_items = stripe.checkout.Session.list_line_items(session['id'], limit=1)
        print(line_items['data'][0]['description'])

    return {}



if __name__ == '__main__':
    # needed for session
    app.secret_key = os.urandom(12)
    app.run(debug=True)
