from flask import Flask, render_template, request, session, flash, redirect, url_for, send_file, jsonify
from werkzeug.utils import secure_filename
from io import BytesIO
import hmac, hashlib
from secrets import compare_digest
import json
import tensorflow as tf
#from secret_keys import STRIPE_SECRET_KEYS, STRIPE_PUBLIC_KEYS, GENERATIVE_PUBLIC_KEYS, GENERATIVE_SECRET_KEYS
import sqlite3 as sql
import pandas as pd
import numpy as np
import Encryption
import base64
import stripe
import re
import string
import random
import ast
import socket
import os

app = Flask(__name__, static_url_path='/static')
counter = 0
cartCounter = 0


# Personal Stripe Account Connection -- Need company connections!!
#app.config['STRIPE_PUBLIC_KEY'] = STRIPE_PUBLIC_KEYS
#app.config['STRIPE_SECRET_KEY'] = STRIPE_SECRET_KEYS
#stripe.api_key = app.config['STRIPE_SECRET_KEY']


# Load pre-trained StyleGAN2 model
# app.config['Generative_PUBLIC_KEY'] = GENERATIVE_PUBLIC_KEYS
# pp.config['Generative_SECRET_KEY'] = GENERATIVE_SECRET_KEYS
# tf.api_key = app.config['Generative_SECRET_KEY']


# Directory route for profile pictures  ie 'static/css/uploads/______'
UPLOAD_FOLDER = 'static/css/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# work needing to be done:
# provided YouTube links for examples / follow along code

# ------------------ FRONTEND ------------------
# both - signup / remember me is fake                                                                    https://www.youtube.com/watch?v=CRvV9nFKoPI
# both - signup / if incorrect input display flash message, if successful flash message to log in page   https://www.youtube.com/watch?v=reumU4CvruA
# both - login forgot password  / route to ask for email, send email, allow for new pass saved!          https://www.youtube.com/watch?v=vutyTx7IaAI


# admin create team    / needs space when entering contact name, need all information passing

# both - search bar results / make look nicer              1. https://www.youtube.com/watch?v=Ay8BXbAmEYM   2. https://www.youtube.com/watch?v=wHspfWWn1II
#                                                             https://www.youtube.com/watch?v=Ay8BXbAmEYM
# ADMIN - create team ; better form-show contact info different ; search users by typing             https://www.youtube.com/watch?v=R4owT-LcKOo
#                                                                                                    https://www.youtube.com/watch?v=n8dqXI8kw_Y
# USER - usersjoin.html      //// redesign
# USER - usersjoinshow.html  //// redesign
# USER - userdash.html       //// checkin satus and names display as list along with cart values

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
# ----- ADMIN cannot search by contact email however can search by contact phone number
# ----- need to .strip() whitespaces before saving to db (makes search results not work if whitespace not included)
# USERS - Need auction house
# USERS - Need sponsor list
# Adding/updating user - make sure extra whitespaces at begging/end are stripped before saving
# creating team -  make sure extra whitespaces at begging/end are stripped before saving


# **********************************************************************************************
#                                   USER / ADMIN  DASHBOARDS                    lines:  1-461  *
# **********************************************************************************************
# Presents home page until logged in, then shows dashboard.
@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('home.html')
    #  -------------------------------- ADMIN DASH --------------------------------
    session['UserName'] = str(Encryption.cipher.decrypt(session['UserName']))
    if session.get('admin'):
        # gets information for quick team view on dash
        con = sql.connect("TeamInfoDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT * FROM TeamInfo')
        rows1 = cur.fetchall()
        rows = []
        i = 0
        for row in rows1:
            newRow = dict(row)
            newRow['ContactFName'] = str(Encryption.cipher.decrypt(row['ContactFName']))
            newRow['ContactLName'] = str(Encryption.cipher.decrypt(row['ContactLName']))
            newRow['ContactPhNum'] = str(Encryption.cipher.decrypt(row['ContactPhNum']))
            newRow['ContactEmail'] = str(Encryption.cipher.decrypt(row['ContactEmail']))
            rows.append(newRow)
            i += 1
        con.close()
        # gets information for total count of needed cart rentals on dash
        con = sql.connect("TeamInfoDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT NeedCart FROM TeamInfo')
        counter = cur.fetchall()
        count = []
        for cnt in counter:
            newRow = dict(cnt)
            count.append(newRow)
        new = []
        string = ','.join(str(x) for x in count)
        for char in string:
            if char.isdigit():
                new.append(int(char))
        AllCartsNeeded = sum(new)
        con.close()
        # get information for count of checked-in team members vs total members in general on dash (only admins can check members in)
        con = sql.connect('TeamInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT MemberName1, MemberName2,  MemberName3, MemberName4 FROM TeamInfo')
        row = cur.fetchall()
        rowz = []
        for row in row:
            newRow = dict(row)
            rowz.append(newRow)
        all = 0
        for entry in rowz:
            for key, value in entry.items():
                if value is not None:
                    all += 1
        con = sql.connect("TeamInfoDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT Member1Here, Member2Here, Member3Here, Member4Here  FROM TeamInfo')
        counter = cur.fetchall()
        count = []
        for cnt in counter:
            newRow = dict(cnt)
            count.append(newRow)
        string = ','.join(str(x) for x in count)
        checkedin = string.count('✔')
        con.close()
        # pull picture pathfile to html
        nm = session['UserName']
        con = sql.connect("UserInfoDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT ProfilePicture FROM UserInfo WHERE UserName= ?', (encrypt(nm),))
        data = cur.fetchall()
        df = pd.DataFrame(data,
                          columns=['ProfilePicture'])
        con.close()
        for row in df.itertuples():
            print(row[1])
        file = df['ProfilePicture']
        photo = np.array([file.values])
        string_representation = photo[0]
        photo = ' '.join(map(str, string_representation))
        # ^get^ and return all information from SQL DB that needs to be shown on dash screen
        return render_template('dash.html', rows=rows, UserName=session['UserName'], i=i,
                               AllCartsNeeded=AllCartsNeeded, checkedin=checkedin, all=all, photo=photo)

    #  ----------------------------------- USER DASH  ------------------------------------
    elif session.get('user'):
        try:
            nm = session['UserName']
            # pull picture pathfile to html
            con = sql.connect("UserInfoDB.db")
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute('SELECT ProfilePicture FROM UserInfo WHERE UserName= ?', (encrypt(nm),))
            data = cur.fetchall()
            df = pd.DataFrame(data,
                              columns=['ProfilePicture'])
            con.close()
            for row in df.itertuples():
                print(row[1])
            file = df['ProfilePicture']
            photo = np.array([file.values])
            string_representation = photo[0]
            photo = ' '.join(map(str, string_representation))
            print(photo)
            con = sql.connect('UserInfoDB.db')
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute(
                "SELECT UserTeamId FROM UserInfo WHERE UserName = ?",
                (encrypt(nm),))
            rowz = cur.fetchall()
            if (rowz):
                UserTeamId = rowz[0]['UserTeamId']
            else:
                UserTeamId = None
            rowzz = []
            for row in rowz:
                newRow = dict(row)
                rowzz.append(newRow)
            con.close()
            string = ','.join(str(x) for x in rowzz)
            print(string)
            word = 'None'
            if word in string:
                inaTeam = "You currently have no team"
                print(inaTeam)
                team_names = 0
                starthole = 0
                checkin = 0
                memeberList = 0
                cartinfo = -1
                joincode = 0
                list_size = -1
                amount = -1
                team = False
                con = sql.connect("TeamInfoDB.db")
                con.row_factory = sql.Row
                cur = con.cursor()
                cur.execute('SELECT * FROM TeamInfo')
                rows1 = cur.fetchall()
                rows = []
                for row in rows1:
                    newRow = dict(row)
                    rows.append(newRow)
                con.close()
            else:
                team = True
                inaTeam = "Welcome team "
                print(inaTeam)
                number = re.findall(r'\d+', string)
                # Convert the numbers to integers
                teamid = [int(num) for num in number]
                for id in teamid:
                    tid = id
                con = sql.connect("TeamInfoDB.db")
                con.row_factory = sql.Row
                cur = con.cursor()
                cur.execute("SELECT * FROM TeamInfo WHERE TeamId = ?", (tid,))
                rowz = cur.fetchall()
                rowzz = []
                i = 0
                for row in rowz:
                    newRow = dict(row)
                    newRow['ContactFName'] = str(Encryption.cipher.decrypt(row['ContactFName']))
                    newRow['ContactLName'] = str(Encryption.cipher.decrypt(row['ContactLName']))
                    newRow['ContactPhNum'] = str(Encryption.cipher.decrypt(row['ContactPhNum']))
                    newRow['ContactEmail'] = str(Encryption.cipher.decrypt(row['ContactEmail']))
                    rowzz.append(newRow)
                    i += 1
                print("there ", rowzz)
                con.close()
                team_names = [d['TeamName'] for d in rowzz]
                team_names = team_names[0]
                starthole = [d['StartHole'] for d in rowzz]
                starthole = starthole[0]
                joincode = [d['JoinCode'] for d in rowzz]
                joincode = joincode[0]
                needacart = [d['NeedCart'] for d in rowzz]
                amount = needacart[0]
                print(starthole)
                print(team_names)
                print(joincode)
                print(amount)
                if amount == 1:
                    cartinfo = [d['AsgnCart1'] for d in rowzz]
                    cartinfo = ['--' if x is None else x for x in cartinfo]
                    cartinfo = ' '.join(cartinfo)
                    print(cartinfo)
                elif amount == 2:
                    cartinfo = [d['AsgnCart1'] for d in rowzz] + [d['AsgnCart2'] for d in rowzz]
                    cartinfo = [' -- ' if x is None else x for x in cartinfo]
                    cartinfo = ' '.join(cartinfo)
                    print(cartinfo)
                else:
                    cartinfo = 'not renting'
                    print(cartinfo)
                memebers = [d['MemberName1'] for d in rowzz] + [d['MemberName2'] for d in rowzz] + [d['MemberName3'] for
                                                                                                    d in rowzz] + [
                               d['MemberName4'] for d in rowzz]
                print(memebers)
                memeberList = [item for item in memebers if item is not None]
                print(memeberList)
                list_size = len(memeberList)
                memeberList = ' '.join(map(str, memeberList))
                print("new ", memeberList)
                print("Size of list:", list_size)
                if list_size == 1:
                    checkin = [d['Member1Here'] for d in rowzz] + [d['MemberName1'] for d in rowzz]
                    checkin = ' '.join(map(str, checkin))
                elif list_size == 2:
                    checkin = [d['Member1Here'] for d in rowzz] + [d['MemberName1'] for d in rowzz] + [d['Member2Here']
                                                                                                       for d in
                                                                                                       rowzz] + [
                                  d['MemberName2'] for d in rowzz]
                    checkin = ' '.join(map(str, checkin))
                elif list_size == 3:
                    checkin = ([d['Member1Here'] for d in rowzz] + [d['MemberName1'] for d in rowzz] + [d['Member2Here']
                                                                                                        for d in rowzz]
                               + [d['MemberName2'] for d in rowzz] + [d['Member3Here'] for d in rowzz] + [
                                   d['MemberName3'] for d in rowzz])
                    checkin = ' '.join(map(str, checkin))
                elif list_size == 4:
                    checkin = ([d['Member1Here'] for d in rowzz] + [d['MemberName1'] for d in rowzz] + [d['Member2Here']
                                                                                                        for d in
                                                                                                        rowzz] + [
                                   d['MemberName2'] for d in rowzz]
                               + [d['Member3Here'] for d in rowzz] + [d['MemberName3'] for d in rowzz] + [
                                   d['Member4Here'] for d in rowzz] + [d['MemberName4'] for d in rowzz])
                    checkin = ' '.join(map(str, checkin))
                print(checkin)

                items = checkin.split()
                output = ''

                # Loop through the items, skipping every two elements to separate the mark and name
                for i in range(0, len(items), 3):
                    mark = items[i]
                    name = items[i + 1] + ' ' + items[i + 2]
                    output += f" {mark} {name} \n"  # Wrap each item in a div and add '\n' for new line

                # Print the HTML output
                print(output)
                con = sql.connect("TeamInfoDB.db")
                con.row_factory = sql.Row
                cur = con.cursor()
                cur.execute('SELECT * FROM TeamInfo')
                rows1 = cur.fetchall()
                rows = []
                for row in rows1:
                    newRow = dict(row)
                    rows.append(newRow)
                con.close()
        finally:
            return render_template('userdash.html', team=team, inaTeam=inaTeam, rows=rows, UserName=session['UserName'],
                                   team_names=team_names, starthole=starthole, checkin=checkin, joincode=joincode,
                                   cartinfo=cartinfo, list_size=list_size, amount=amount, UserTeamId=UserTeamId,
                                   photo=photo)


# ADMIN - directs admin to dash
@app.route('/dash')
def dash():
    if not session.get('logged_in'):
        return render_template('home.html')
    # gets information for quick team view on dash
    con = sql.connect("TeamInfoDB.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT * FROM TeamInfo')
    rows1 = cur.fetchall()
    rows = []
    i = 0
    for row in rows1:
        newRow = dict(row)
        newRow['ContactFName'] = str(Encryption.cipher.decrypt(row['ContactFName']))
        newRow['ContactLName'] = str(Encryption.cipher.decrypt(row['ContactLName']))
        newRow['ContactPhNum'] = str(Encryption.cipher.decrypt(row['ContactPhNum']))
        newRow['ContactEmail'] = str(Encryption.cipher.decrypt(row['ContactEmail']))
        rows.append(newRow)
        i += 1
    con.close()
    # gets information for total count of needed cart rentals on dash
    con = sql.connect("TeamInfoDB.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT NeedCart FROM TeamInfo')
    counter = cur.fetchall()
    count = []
    for cnt in counter:
        newRow = dict(cnt)
        count.append(newRow)
    new = []
    string = ','.join(str(x) for x in count)
    for char in string:
        if char.isdigit():
            new.append(int(char))
    AllCartsNeeded = sum(new)
    con.close()
    # get information for count of checked-in team members vs total members in general on dash (only admins can check members in)
    con = sql.connect('TeamInfoDB.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT MemberName1, MemberName2,  MemberName3, MemberName4 FROM TeamInfo')
    row = cur.fetchall()
    rowz = []
    for row in row:
        newRow = dict(row)
        rowz.append(newRow)
    all = 0
    for entry in rowz:
        for key, value in entry.items():
            if value is not None:
                all += 1
    con = sql.connect("TeamInfoDB.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT Member1Here, Member2Here, Member3Here, Member4Here  FROM TeamInfo')
    counter = cur.fetchall()
    count = []
    for cnt in counter:
        newRow = dict(cnt)
        count.append(newRow)
    string = ','.join(str(x) for x in count)
    checkedin = string.count('✔')
    con.close()
    # pull picture pathfile to html
    nm = session['UserName']
    con = sql.connect("UserInfoDB.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT ProfilePicture FROM UserInfo WHERE UserName= ?', (encrypt(nm),))
    data = cur.fetchall()
    df = pd.DataFrame(data,
                      columns=['ProfilePicture'])
    con.close()
    for row in df.itertuples():
        print(row[1])
    file = df['ProfilePicture']
    photo = np.array([file.values])
    string_representation = photo[0]
    photo = ' '.join(map(str, string_representation))
    # ^get^ and return all information from SQL DB that needs to be shown on dash screen
    return render_template("dash.html", rows=rows, UserName=session['UserName'], i=i, AllCartsNeeded=AllCartsNeeded,
                           checkedin=checkedin, all=all, photo=photo)


# USER - directs users to dash
@app.route('/userdash')
def userdash():
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
        try:
            nm = session['UserName']
            # pull picture pathfile to html
            con = sql.connect("UserInfoDB.db")
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute('SELECT ProfilePicture FROM UserInfo WHERE UserName= ?', (encrypt(nm),))
            data = cur.fetchall()
            df = pd.DataFrame(data,
                              columns=['ProfilePicture'])

            con.close()
            for row in df.itertuples():
                print(row[1])
            file = df['ProfilePicture']
            photo = np.array([file.values])
            string_representation = photo[0]
            photo = ' '.join(map(str, string_representation))
            print(photo)
            con = sql.connect('UserInfoDB.db')
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute(
                "SELECT UserTeamId FROM UserInfo WHERE UserName = ?",
                (encrypt(nm),))
            rowz = cur.fetchall()

            if (rowz):
                UserTeamId = rowz[0]['UserTeamId']
            else:
                UserTeamId = None

            rowzz = []
            for row in rowz:
                newRow = dict(row)
                rowzz.append(newRow)
            con.close()
            string = ','.join(str(x) for x in rowzz)
            print(string)
            word = 'None'
            if word in string:
                inaTeam = "You currently have no team"
                print(inaTeam)
                team_names = 0
                starthole = 0
                checkin = 0
                memeberList = 0
                cartinfo = -1
                joincode = 0
                list_size = -1
                amount = -1
                team = False
                con = sql.connect("TeamInfoDB.db")
                con.row_factory = sql.Row
                cur = con.cursor()
                cur.execute('SELECT * FROM TeamInfo')
                rows1 = cur.fetchall()
                rows = []
                for row in rows1:
                    newRow = dict(row)
                    rows.append(newRow)
                con.close()
            else:
                team = True
                inaTeam = "You are in a team"
                print(inaTeam)
                number = re.findall(r'\d+', string)
                # Convert the numbers to integers
                teamid = [int(num) for num in number]
                for id in teamid:
                    tid = id
                con = sql.connect("TeamInfoDB.db")
                con.row_factory = sql.Row
                cur = con.cursor()
                cur.execute("SELECT * FROM TeamInfo WHERE TeamId = ?", (tid,))
                rowz = cur.fetchall()
                rowzz = []
                i = 0
                for row in rowz:
                    newRow = dict(row)
                    newRow['ContactFName'] = str(Encryption.cipher.decrypt(row['ContactFName']))
                    newRow['ContactLName'] = str(Encryption.cipher.decrypt(row['ContactLName']))
                    newRow['ContactPhNum'] = str(Encryption.cipher.decrypt(row['ContactPhNum']))
                    newRow['ContactEmail'] = str(Encryption.cipher.decrypt(row['ContactEmail']))
                    rowzz.append(newRow)
                    i += 1
                print("there ", rowzz)
                con.close()
                team_names = [d['TeamName'] for d in rowzz]
                team_names = team_names[0]
                starthole = [d['StartHole'] for d in rowzz]
                starthole = starthole[0]
                joincode = [d['JoinCode'] for d in rowzz]
                joincode = joincode[0]
                needacart = [d['NeedCart'] for d in rowzz]
                amount = needacart[0]
                print(starthole)
                print(team_names)
                print(joincode)
                print(amount)
                if amount == 1:
                    cartinfo = [d['AsgnCart1'] for d in rowzz]
                    cartinfo = ['--' if x is None else x for x in cartinfo]
                    cartinfo = ' '.join(cartinfo)
                    print(cartinfo)
                elif amount == 2:
                    cartinfo = [d['AsgnCart1'] for d in rowzz] + [d['AsgnCart2'] for d in rowzz]
                    cartinfo = [' -- ' if x is None else x for x in cartinfo]
                    cartinfo = ' '.join(cartinfo)
                    print(cartinfo)
                else:
                    cartinfo = 'not renting'
                    print(cartinfo)
                memebers = [d['MemberName1'] for d in rowzz] + [d['MemberName2'] for d in rowzz] + [d['MemberName3'] for
                                                                                                    d in rowzz] + [
                               d['MemberName4'] for d in rowzz]
                print(memebers)
                memeberList = [item for item in memebers if item is not None]
                print(memeberList)
                list_size = len(memeberList)
                memeberList = ' '.join(map(str, memeberList))
                print("new ", memeberList)
                print("Size of list:", list_size)
                if list_size == 1:
                    checkin = [d['Member1Here'] for d in rowzz] + [d['MemberName1'] for d in rowzz]
                    checkin = ' '.join(map(str, checkin))
                elif list_size == 2:
                    checkin = [d['Member1Here'] for d in rowzz] + [d['MemberName1'] for d in rowzz] + [d['Member2Here']
                                                                                                       for d in
                                                                                                       rowzz] + [
                                  d['MemberName2'] for d in rowzz]
                    checkin = ' '.join(map(str, checkin))
                elif list_size == 3:
                    checkin = ([d['Member1Here'] for d in rowzz] + [d['MemberName1'] for d in rowzz] + [d['Member2Here']
                                                                                                        for d in rowzz]
                               + [d['MemberName2'] for d in rowzz] + [d['Member3Here'] for d in rowzz] + [
                                   d['MemberName3'] for d in rowzz])
                    checkin = ' '.join(map(str, checkin))
                elif list_size == 4:
                    checkin = ([d['Member1Here'] for d in rowzz] + [d['MemberName1'] for d in rowzz] + [d['Member2Here']
                                                                                                        for d in
                                                                                                        rowzz] + [
                                   d['MemberName2'] for d in rowzz]
                               + [d['Member3Here'] for d in rowzz] + [d['MemberName3'] for d in rowzz] + [
                                   d['Member4Here'] for d in rowzz] + [d['MemberName4'] for d in rowzz])
                    checkin = ' '.join(map(str, checkin))
                print(checkin)
                con = sql.connect("TeamInfoDB.db")
                con.row_factory = sql.Row
                cur = con.cursor()
                cur.execute('SELECT * FROM TeamInfo')
                rows1 = cur.fetchall()
                rows = []
                for row in rows1:
                    newRow = dict(row)
                    rows.append(newRow)
                con.close()
        finally:
            return render_template('userdash.html', team=team, inaTeam=inaTeam, rows=rows, UserName=session['UserName'],
                                   team_names=team_names, starthole=starthole, checkin=checkin, joincode=joincode,
                                   memeberList=memeberList, cartinfo=cartinfo, list_size=list_size, amount=amount,
                                   UserTeamId=UserTeamId, photo=photo)


# **********************************************************************************************
#                                      WORKING FUNCTIONS                       lines: 470-549  *
# **********************************************************************************************
# WORKING - Under Constructions
@app.route('/construction')
def construction():
    return render_template('construction.html')


# WORKING - validates input is an integer between the min-max range
def validate_int(value, min_value, max_value):
    if (value < min_value) or (value > max_value):
        return False
    else:
        return True


# WORKING - validates input is not empty or 'space filled' string
def validate_string(string):
    if string == " " or string == "":
        return False
    else:
        return True


# WORKING - formats error message
def format_output(string):
    return "<br>".join(string.replace("\n"))


# WORKING - encrypt passed in value
def encrypt(txt):
    return Encryption.cipher.encrypt(bytes(txt, 'utf-8')).decode('utf-8')


# WORKING - increment for starting hole
def increment():
    global counter
    counter += 1


# WORKING - reset start hole
def reset():
    global counter
    counter = 1


# WORKING - set start hole
def set(value):
    global counter
    counter = value


# WORKING - check if sql table empty
def is_empty():
    con = sql.connect('TeamInfoDB.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("""SELECT COUNT(*) FROM TeamInfo""")
    cnt = cur.fetchone()[0]
    con.close()
    return cnt == 0  # true if empty, false otherwise


# WORKING - count needed cart amount
def count_carts(TeamId):
    con = sql.connect('TeamInfoDB.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("""SELECT NEEDCART FROM TeamInfo WHERE TeamId = ?""", (TeamId,))
    cart = cur.fetchall()
    val = cart[0]
    final = val['NEEDCART']
    print(final)
    global cartCounter
    cartCounter = final
    return final


# WORKING - reset start hole
def reset_cart():
    global cartCounter
    cartCounter = 0


# WORKING - handle file uploads
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


# WORKING -check if a user is point of contact on team
def is_a_contact():
    nm = session['UserName']
    con = sql.connect('UserInfoDB.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM UserInfo WHERE UserName = ?", (encrypt(nm),))
    rows1 = cur.fetchall()
    rows = []
    for row in rows1:
        newRow = dict(row)
        newRow['UserName'] = str(Encryption.cipher.decrypt(row['UserName']))
        newRow['UserPhNum'] = str(Encryption.cipher.decrypt(row['UserPhNum']))
        newRow['UserEmail'] = str(Encryption.cipher.decrypt(row['UserEmail']))
        newRow['LoginPassword'] = str(Encryption.cipher.decrypt(row['LoginPassword']))
        rows.append(newRow)
    con.close()
    # check if user is a team contact
    con = sql.connect('UserInfoDB.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute(
        "SELECT UserTeamId FROM UserInfo WHERE UserName = ?",
        (encrypt(nm),))
    rowz = cur.fetchall()
    if (rowz):
        UserTeamId = rowz[0]['UserTeamId']
    else:
        UserTeamId = None
    rowzz = []
    for row in rowz:
        newRow = dict(row)
        rowzz.append(newRow)
    con.close()
    string = ','.join(str(x) for x in rowzz)
    print(string)
    word = 'None'
    if word in string:
        inaTeam = "You currently have no team"
        print(inaTeam)
        team = False
        iscontact = 0
        tid = 0
    else:
        team = True
        inaTeam = "You are in a team"
        print(inaTeam)
        number = re.findall(r'\d+', string)
        # Convert the numbers to integers
        teamid = [int(num) for num in number]
        for id in teamid:
            tid = id
        print(tid)
        con = sql.connect("TeamInfoDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT ContactEmail FROM TeamInfo WHERE TeamId = ?", (tid,))
        rowz = cur.fetchall()
        rowzz = []
        i = 0
        for row in rowz:
            newRow = dict(row)
            newRow['ContactEmail'] = str(Encryption.cipher.decrypt(row['ContactEmail']))
            rowzz.append(newRow)
            i += 1
        print("there ", rowzz)
        first = rows[0]['UserEmail']
        email = rowzz[0]['ContactEmail'].strip()
        if email == first:
            iscontact = 1
        else:
            iscontact = 0
        print("contact", iscontact)
    return iscontact, tid


@app.route('/generate_image', methods=['POST'])
def generate_image():
    # Get parameters from request (e.g., image size, latent vector, etc.)
    # For simplicity, let's assume we receive latent vector as a parameter
    latent_vector = request.json.get('latent_vector')

    # Generate image using the model
    generated_image = model.predict(np.array([latent_vector]))

    # Preprocess generated image (e.g., scale pixel values to [0, 255])
    generated_image = (generated_image * 127.5 + 127.5).astype(np.uint8)

    # Serve generated image as response
    return jsonify({'image': generated_image.tolist()})


# **********************************************************************************************
#                                        FOR USERS                           lines: 555-1099   *
# **********************************************************************************************
# USER - directs user to sign up page
@app.route('/signup')
def sign_up():
    if not session.get('logged_in'):
        return render_template('signup.html')
    else:
        try:
            session['UserName'] = str(Encryption.cipher.decrypt(session['UserName']))
        finally:
            return render_template('dashboard-OLD.html', UserName=session['UserName'])


# USER - directs user to sign up page
@app.route('/new')
def generate():
    if not session.get('logged_in'):
        return render_template('signup.html')
    else:


     return render_template('assign1.html')



# USER - Add new user to SQL table - USERINFO  DB
@app.route('/adduser', methods=['POST', 'GET'])
def adduser():
    valid_input = True
    err_string = " "
    if request.method == 'POST':
        try:
            nm = request.form['UserName']
            fnm = request.form['UserFName']
            mi = request.form['UserMName']
            lnm = request.form['UserLName']
            gen = request.form['UserGender']
            dob = request.form['UserDOB']
            uhc = request.form['UserHandicap']
            pn = request.form['UserPhNum']
            email = request.form['UserEmail']
            if request.form.get('RoleLevel'):
                lvl = 0
            else:
                lvl = 1
            pwd = request.form['LoginPassword']

            if not validate_string(nm):
                valid_input = False
                err_string = err_string + "<br>You can not enter in an empty username."

            if not validate_string(fnm):
                valid_input = False
                err_string = err_string + "<br>You can not enter in an empty first name."

            if not validate_string(mi):
                valid_input = False
                err_string = err_string + "<br>You can not enter in an empty middle initial."

            if not validate_string(lnm):
                valid_input = False
                err_string = err_string + "<br>You can not enter in an empty last name."

            if not validate_string(gen):
                valid_input = False
                err_string = err_string + "<br>You can not enter in an empty gender space."

            if not validate_string(dob):
                valid_input = False
                err_string = err_string + "<br>You can not enter in an empty date of birth."

            if not validate_string(pn):
                valid_input = False
                err_string = err_string + "<br>You can not enter in an empty phone number."

            if not validate_string(email):
                valid_input = False
                err_string = err_string + "<br>You can not enter in an empty email."

            if not validate_string(pwd):
                valid_input = False
                err_string = err_string + "<br>You can not enter in an empty pwd."

                if not valid_input:
                    msg = err_string
                    return render_template("result.html", msg=format_output(err_string))

            if valid_input:
                with sql.connect("UserInfoDB.db") as con:
                    cur = con.cursor()
                    cur.execute(
                        "INSERT INTO UserInfo (UserName, UserFName, UserMName, UserLName, UserGender, UserDOB, UserHandicap, UserPhNum, UserEmail, RoleLevel, LoginPassword, ProfilePicture, UserTeamLead) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (encrypt(nm), fnm, mi, lnm, gen, dob, uhc, encrypt(pn), encrypt(email), lvl, encrypt(pwd),
                         'static/css/uploads/default.jpeg', False))
                    con.commit()
                    msg = "Record successfully added You may now login"
        except:
            con.rollback()
        finally:
            con.close()
            return render_template("login-signup.html", msg=msg)
    else:
        flash('Page not found')
        return render_template('home.html')


# USER - directs users to team sign up page
@app.route('/usermakesteam')
def userteamsignups():
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
        con = sql.connect('TeamInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT * FROM TeamInfo')
        rows1 = cur.fetchall()
        rows = []
        i = 0
        for row in rows1:
            newRow = dict(row)
            rows.append(newRow)
            i += 1
        print(i)
        con.close()
        # pull picture pathfile to html
        nm = session['UserName']
        con = sql.connect("UserInfoDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT ProfilePicture FROM UserInfo WHERE UserName= ?', (encrypt(nm),))
        data = cur.fetchall()
        df = pd.DataFrame(data,
                          columns=['ProfilePicture'])

        con.close()
        for row in df.itertuples():
            print(row[1])
        file = df['ProfilePicture']
        photo = np.array([file.values])
        string_representation = photo[0]
        photo = ' '.join(map(str, string_representation))
        print(photo)
        if i != 0:
            con = sql.connect('TeamInfoDB.db')
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute(
                "SELECT TeamId FROM TeamInfo WHERE TeamId =(SELECT max(TeamId) FROM TeamInfo)")  # get last team
            num = cur.fetchall()
            val = num[0]
            lastTeam = val['TeamId']
            if lastTeam >= 36:
                return render_template('u_teamsignupfull.html', UserName=session['UserName'], photo=photo)

        nm = session['UserName']
        # pull picture pathfile to html
        nm = session['UserName']
        con = sql.connect("UserInfoDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT ProfilePicture FROM UserInfo WHERE UserName= ?', (encrypt(nm),))
        data = cur.fetchall()
        df = pd.DataFrame(data,
                          columns=['ProfilePicture'])

        con.close()
        for row in df.itertuples():
            print(row[1])
        file = df['ProfilePicture']
        photo = np.array([file.values])
        string_representation = photo[0]
        photo = ' '.join(map(str, string_representation))
        print(photo)
        con = sql.connect('UserInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute(
            "SELECT UserTeamId FROM UserInfo WHERE UserName = ?",
            (encrypt(nm),))
        rows1 = cur.fetchall()
        rows = []
        for row in rows1:
            newRow = dict(row)
            rows.append(newRow)
        print("here", rows)
        con.close()
        string = ','.join(str(x) for x in rows)
        print(string)
        word = 'None'
        if word not in string:
            print('success')
            return render_template('u_teamsignupfull.html', UserName=session['UserName'], photo=photo)
        else:
            nm = session['UserName']
            con = sql.connect('UserInfoDB.db')
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute(
                "SELECT UserId, UserFName, UserLName, UserHandicap, UserPhNum, UserEmail FROM UserInfo  WHERE UserName = ?",
                (encrypt(nm),))
            rows1 = cur.fetchall()
            rows = []
            for row in rows1:
                newRow = dict(row)
                newRow['UserPhNum'] = str(Encryption.cipher.decrypt(row['UserPhNum']))
                newRow['UserEmail'] = str(Encryption.cipher.decrypt(row['UserEmail']))
                rows.append(newRow)
            print(rows)
            con.close()
            # pull picture pathfile to html
            nm = session['UserName']
            con = sql.connect("UserInfoDB.db")
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute('SELECT ProfilePicture FROM UserInfo WHERE UserName= ?', (encrypt(nm),))
            data = cur.fetchall()
            df = pd.DataFrame(data,
                              columns=['ProfilePicture'])

            con.close()
            for row in df.itertuples():
                print(row[1])
            file = df['ProfilePicture']
            photo = np.array([file.values])
            string_representation = photo[0]
            photo = ' '.join(map(str, string_representation))
            print(photo)
            return render_template('u_userteamsignup.html', UserName=session['UserName'], rows=rows, photo=photo)


# USER - allow sign up team
@app.route('/userteamsignup', methods=['POST', 'GET'])
def user_teamSignup():
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
        nm = session['UserName']
        valid_input = True
        err_string = " "
        if request.method == 'POST':
            try:
                tnm = request.form['TeamName']
                snm = request.form['SponsorName']
                nc = request.form['NeedCart']
                m1info = request.form['MemberName1']
                word = m1info.split(',')
                m1id = word[0]
                m1hc = word[1]
                mn1 = word[2] + word[3]
                cfn = word[2]
                cln = word[3]
                cpn = word[4]
                ce = word[5]
                pic = word[6]
                print(m1id)
                print(m1hc)
                print(mn1)
                print(cfn)
                print(cln)
                print(cpn)
                print(ce)
                print(pic)
                check = is_empty()
                if check is False:
                    con = sql.connect('TeamInfoDB.db')
                    con.row_factory = sql.Row
                    cur = con.cursor()
                    cur.execute(
                        "SELECT StartHole FROM TeamInfo WHERE TeamId =(SELECT max(TeamId) FROM TeamInfo)")  # get last hole
                    num = cur.fetchall()
                    val = num[0]
                    lastASGNDhole = val['StartHole']
                    print("last hole:", lastASGNDhole)
                    set(lastASGNDhole + 1)
                    print(counter)
                    con.close()
                else:
                    increment()
                if counter <= 18:
                    sh = counter
                else:
                    reset()
                    sh = counter
                code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                print(code)

                if not validate_string(tnm):
                    valid_input = False
                    err_string = err_string + "<br>You cannot enter in an empty team name"

                if (int(nc) <= -1) or (int(nc) >= 3):
                    valid_input = False
                    err_string = err_string + "<br>You can not enter in an empty cart."

                    if not valid_input:
                        msg = err_string
                        return render_template("result.html", msg=format_output(err_string))

                if valid_input:
                    with sql.connect("TeamInfoDB.db") as con:
                        cur = con.cursor()
                        cur.execute(
                            "INSERT INTO TeamInfo (TeamName, SponsorName, NeedCart, MemberName1, Member1ID, Member1Handicap, StartHole, Member1Here, Member2Here, Member3Here, Member4Here, ContactFName, ContactLName, ContactPhNum, ContactEmail, ContactPhoto, JoinCode, MemberCount) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            (tnm, snm, nc, mn1, m1id, m1hc, sh, "✘", "✘", "✘", "✘", encrypt(cfn), encrypt(cln),
                             encrypt(cpn), encrypt(ce), pic, code, 1))
                        con.commit()
                    msg = "Team Added successfully"
            except:
                con.rollback()
            finally:
                con.close()
                return redirect('joincode')
        else:
            flash('Page not found')
            return render_template('userdash.html')


# USER - Routes user to send team join code
@app.route('/joincode', methods=['POST', 'GET'])
def joincode():
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
        nm = session['UserName']
        con = sql.connect('TeamInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute(
            "SELECT TeamId FROM TeamInfo WHERE TeamId =(SELECT max(TeamId) FROM TeamInfo)")
        num = cur.fetchall()
        val = num[0]
        lastTeam = val['TeamId']
        con.close()
        with sql.connect("UserInfoDB.db") as con:
            cur = con.cursor()
            cur.execute("UPDATE UserInfo SET UserTeamId = ? WHERE UserName = ?", (lastTeam, encrypt(nm)))
            con.commit()
        con.close()
        con = sql.connect('UserInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute(
            "SELECT UserTeamId FROM UserInfo WHERE UserName = ?", (encrypt(nm),))
        rows1 = cur.fetchall()
        rows = []
        for row in rows1:
            newRow = dict(row)
            rows.append(newRow)
        print("yes: ", rows)
        con.close()

        con = sql.connect('TeamInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute(
            "SELECT JoinCode FROM TeamInfo WHERE TeamId = ?", (lastTeam,))
        rows1 = cur.fetchall()
        rows = []
        for row in rows1:
            newRow = dict(row)
            rows.append(newRow)
        print(rows)
        con.close()
        # pull picture pathfile to html
        nm = session['UserName']
        con = sql.connect("UserInfoDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT ProfilePicture FROM UserInfo WHERE UserName= ?', (encrypt(nm),))
        data = cur.fetchall()
        df = pd.DataFrame(data,
                          columns=['ProfilePicture'])
        con.close()
        for row in df.itertuples():
            print(row[1])
        file = df['ProfilePicture']
        photo = np.array([file.values])
        string_representation = photo[0]
        photo = ' '.join(map(str, string_representation))
        print(photo)
        return render_template('u_teamjoin.html', UserName=session['UserName'], rows=rows, photo=photo)


# USER allows users to send team join code
@app.route('/teamjoin', methods=['POST', 'GET'])
def user_teamjoin():
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
        # pull picture pathfile to html
        nm = session['UserName']
        con = sql.connect("UserInfoDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT ProfilePicture FROM UserInfo WHERE UserName= ?', (encrypt(nm),))
        data = cur.fetchall()
        df = pd.DataFrame(data,
                          columns=['ProfilePicture'])

        con.close()
        for row in df.itertuples():
            print(row[1])
        file = df['ProfilePicture']
        photo = np.array([file.values])
        string_representation = photo[0]
        photo = ' '.join(map(str, string_representation))
        print(photo)
        msg = "cool all done"
    return render_template('result.html', UserName=session['UserName'], msg=msg, photo=photo)


# USER - directs users to join a team
@app.route('/usersjoin')
def usersjoin():
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('user'):
        flash('Page not found')
        return render_template('home.html')
    # pull picture pathfile to html
    nm = session['UserName']
    con = sql.connect("UserInfoDB.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT ProfilePicture FROM UserInfo WHERE UserName= ?', (encrypt(nm),))
    data = cur.fetchall()
    df = pd.DataFrame(data,
                      columns=['ProfilePicture'])
    con.close()
    for row in df.itertuples():
        print(row[1])
    file = df['ProfilePicture']
    photo = np.array([file.values])
    string_representation = photo[0]
    photo = ' '.join(map(str, string_representation))
    print(photo)

    return render_template('u_usersjoin.html', UserName=session['UserName'], photo=photo)


# USER - ask to add user to team
@app.route('/userjoin', methods=['POST'])
def userjoin():
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('user'):
        flash('Page not found')
        return render_template('home.html')
    try:
        # pull picture pathfile to html
        nm = session['UserName']
        con = sql.connect("UserInfoDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT ProfilePicture FROM UserInfo WHERE UserName= ?', (encrypt(nm),))
        data = cur.fetchall()
        df = pd.DataFrame(data,
                          columns=['ProfilePicture'])
        con.close()
        for row in df.itertuples():
            print(row[1])
        file = df['ProfilePicture']
        photo = np.array([file.values])
        string_representation = photo[0]
        photo = ' '.join(map(str, string_representation))
        print(photo)
        info = request.form.get('JoinCode')
        session['JoinCode'] = info
        print(info)
        with sql.connect("TeamInfoDB.db") as con:  # Connect to the userInfo database
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM TeamInfo WHERE JoinCode = ?", (info,))
            rows = []
            for row in cur.fetchall():
                newRow = dict(row)
                newRow['ContactFName'] = str(Encryption.cipher.decrypt(row['ContactFName']))
                newRow['ContactLName'] = str(Encryption.cipher.decrypt(row['ContactLName']))
                newRow['ContactPhNum'] = str(Encryption.cipher.decrypt(row['ContactPhNum']))
                newRow['ContactEmail'] = str(Encryption.cipher.decrypt(row['ContactEmail']))
                rows.append(newRow)

            return render_template("u_usersjoinshow.html", rows=rows, UserName=session['UserName'], photo=photo)
    except Exception as e:
        flash("Search Error")
        # pull picture pathfile to html
        nm = session['UserName']
        con = sql.connect("UserInfoDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT ProfilePicture FROM UserInfo WHERE UserName= ?', (encrypt(nm),))
        data = cur.fetchall()
        df = pd.DataFrame(data,
                          columns=['ProfilePicture'])
        con.close()
        for row in df.itertuples():
            print(row[1])
        file = df['ProfilePicture']
        photo = np.array([file.values])
        string_representation = photo[0]
        photo = ' '.join(map(str, string_representation))
        print(photo)
        return render_template('u_usersjoin.html', photo=photo)


# USER - add user to team
@app.route('/userteamjoin', methods=['POST', 'GET'])
def user_teamJoin():
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
        nm = session['UserName']
        # pull picture pathfile to html
        con_p = sql.connect("UserInfoDB.db")
        con_p.row_factory = sql.Row
        cur = con_p.cursor()
        cur.execute('SELECT ProfilePicture FROM UserInfo WHERE UserName= ?', (encrypt(nm),))
        data = cur.fetchall()
        df = pd.DataFrame(data,
                          columns=['ProfilePicture'])
        for row in df.itertuples():
            print(row[1])
        file = df['ProfilePicture']
        photo = np.array([file.values])
        string_representation = photo[0]
        photo = ' '.join(map(str, string_representation))
        print(photo)
        con_p.close()
        ident = session['UserId']
        valid_input = True
        err_string = " "
        print("herenow")
        # join_code = session.pop('JoinCode', None)
        join_code = session['JoinCode']
        session['JoinCode'] = ""

        # connect to team database and grab membercount of team with corresponding joincode
        con = sql.connect("TeamInfoDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM TeamInfo WHERE JoinCode = ?", (join_code,))
        inc = cur.fetchall()
        pnt = inc[0]
        memc = pnt['MemberCount']
        tid = pnt['TeamId']
        print(memc)

        con2 = sql.connect("UserInfoDB.db")
        con2.row_factory = sql.Row
        cur2 = con2.cursor()
        cur2.execute("SELECT * FROM UserInfo WHERE UserId = ?", (ident,))
        user = cur2.fetchall()
        pnt = user[0]
        fname = pnt['UserFName']
        lname = pnt['UserLName']
        memid = pnt['UserId']
        handi = pnt['UserHandicap']
        print(fname)
        print(lname)
        print(memid)
        print(handi)
        fullname = fname + " " + lname
        member_added = False

        if (memc == 1):
            cur.execute(
                "UPDATE TeamInfo SET MemberName2 = ?, Member2ID = ?, Member2Handicap = ?, MemberCount = ? WHERE TeamId = ?",
                (fullname, memid, handi, memc + 1, tid))
            con.commit()
            member_added = True

        elif (memc == 2):
            cur.execute(
                "UPDATE TeamInfo SET MemberName3 = ?, Member3ID = ?, Member3Handicap = ?, MemberCount = ? WHERE TeamId = ?",
                (fullname, memid, handi, memc + 1, tid))
            con.commit()
            member_added = True
        elif (memc == 3):
            cur.execute(
                "UPDATE TeamInfo SET MemberName4 = ?, Member4ID = ?, Member4Handicap = ?, MemberCount = ? WHERE TeamId = ?",
                (fullname, memid, handi, memc + 1, tid))
            con.commit()
            member_added = True
        elif (memc >= 4):
            msg = "This Team is Currenly Full"
            con2.close()
            con.close()
            return render_template('result.html', UserName=session['UserName'], msg=msg, photo=photo)

        if member_added:
            cur2.execute("UPDATE UserInfo SET UserTeamId = ? WHERE UserId = ?", (tid, memid))
            con2.commit()
            msg = "You have successfully joined this team!"
            con2.close()
            con.close()
            return render_template('result.html', UserName=session['UserName'], msg=msg, photo=photo)
        else:
            msg = "error in team addition"
            con2.close()
            con.close()

            return render_template('result.html', UserName=session['UserName'], msg=msg, photo=photo)


# USER - list all current team information
@app.route('/u_allteamlist')
def user_teamlist():
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
        if not session.get('user'):
            flash('Page not found')
            return render_template('home.html')
        else:
            con = sql.connect("TeamInfoDB.db")
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute('SELECT * FROM TeamInfo')
            rows1 = cur.fetchall()
            rows = []
            for row in rows1:
                newRow = dict(row)
                rows.append(newRow)
            con.close()
            # pull picture pathfile to html
            nm = session['UserName']
            con = sql.connect("UserInfoDB.db")
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute('SELECT ProfilePicture FROM UserInfo WHERE UserName= ?', (encrypt(nm),))
            data = cur.fetchall()
            df = pd.DataFrame(data,
                              columns=['ProfilePicture'])
            con.close()
            for row in df.itertuples():
                print(row[1])
            file = df['ProfilePicture']
            photo = np.array([file.values])
            string_representation = photo[0]
            photo = ' '.join(map(str, string_representation))
            print(photo)
            return render_template("u_allteamlist.html", rows=rows, UserName=session['UserName'], photo=photo)


# USER - team quickview on dashboard
@app.route('/u_showTeam/<int:TeamId>', methods=['GET'])
def user_showTeam(TeamId):
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('user'):
        flash('Page not found')
        return render_template('home.html')
    else:
        con = sql.connect('TeamInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM TeamInfo WHERE TeamId = ?", (TeamId,))
        rows1 = cur.fetchall()
        rows = []
        for row in rows1:
            newRow = dict(row)
            rows.append(newRow)
        con.close()
        return render_template("/u_viewTeam.html", rows=rows)


@app.route('/uc_editTeam')
def cap_editTeam():
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('user'):
        flash('Page not found')
        return render_template('home.html')
    else:
        nm = session['UserName']
        con = sql.connect('UserInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT UserTeamId, UserTeamLead FROM UserInfo WHERE UserName =?', (encrypt(nm),))

        result = cur.fetchone()
        con.close()

        tid, tcpt = result


        con = sql.connect('TeamInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT * FROM TeamInfo WHERE TeamId =?', (tid,))
        rows1 = cur.fetchall()
        rows = []
        for row in rows1:
            newRow = dict(row)
            newRow['ContactFName'] = str(Encryption.cipher.decrypt(row['ContactFName']))
            newRow['ContactLName'] = str(Encryption.cipher.decrypt(row['ContactLName']))
            newRow['ContactPhNum'] = str(Encryption.cipher.decrypt(row['ContactPhNum']))
            newRow['ContactEmail'] = str(Encryption.cipher.decrypt(row['ContactEmail']))
            rows.append(newRow)
        con.close()

        return render_template('c-userEditTeam.html', rows=rows)

@app.route('/uc_addMember', methods=['POST','GET'])
def cap_addMember():
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('user'):
        flash('Page not found')
        return render_template('home.html')
    else:
        nm = session['UserName']
        mFn = request.form.get('MemberFName')
        mLn = request.form.get('MemberLName')
        mEm = request.form.get('MemberEmail')
        mEm = encrypt(mEm)
        mHandi = request.form.get('MemberHCap')
        fullname = mFn + " " + mLn

        con = sql.connect('UserInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT UserTeamId FROM UserInfo WHERE UserName =?', (encrypt(nm),))

        result = cur.fetchone()
        tid = result[0]
        print(tid)

        cur.execute(
            "Insert Into UserInfo ('UserFName', 'UserLName', 'UserHandicap', 'UserEmail', 'RoleLevel', UserTeamLead) Values (?,?,?,?,?,?)",
            (mFn, mLn, mHandi, mEm, 1, False))
        con.commit()
        cur.execute("SELECT UserId FROM UserInfo WHERE UserEmail =?", (mEm,))
        result3 = cur.fetchone()
        memID = result3[0]
        con.close()

        con = sql.connect('TeamInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT MemberCount FROM TeamInfo WHERE TeamId = ?", (tid,))
        result2 = cur.fetchone()
        memc = result2[0]

        member_added = False

        if (memc == 1):
            cur.execute(
                "UPDATE TeamInfo SET MemberName2 = ?, Member2ID = ?, Member2Handicap = ?, MemberCount = ? WHERE TeamId = ?",
                (fullname, memID, mHandi, memc + 1, tid))
            con.commit()
            con.close()
            member_added = True

        elif (memc == 2):
            cur.execute(
                "UPDATE TeamInfo SET MemberName3 = ?, Member3ID = ?, Member3Handicap = ?, MemberCount = ? WHERE TeamId = ?",
                (fullname, memID, mHandi, memc + 1, tid))
            con.commit()
            con.close()
            member_added = True
        elif (memc == 3):
            cur.execute(
                "UPDATE TeamInfo SET MemberName4 = ?, Member4ID = ?, Member4Handicap = ?, MemberCount = ? WHERE TeamId = ?",
                (fullname, memID, mHandi, memc + 1, tid))
            con.commit()
            con.close()
            member_added = True
        elif (memc >= 4):
            msg = "This Team is Currenly Full"
            con.close()
            return render_template('result.html', UserName=session['UserName'], msg=msg)

        if member_added:
            con = sql.connect('UserInfoDB.db')
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute("UPDATE UserInfo SET UserTeamId = ? WHERE UserId = ?", (tid, memID))
            con.commit()
            msg = "You have successfully joined this team!"
            con.close()
            return render_template('result.html', UserName=session['UserName'], msg=msg)
        else:
            msg = "error in team addition"
            con.close()

            return render_template('result.html', UserName=session['UserName'], msg=msg)


'''
# USER - Leave Team
@app.route('/u_leaveTeam/<int:TeamId>', methods=['GET'])
def u_leaveTeam(TeamId):
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
        if not session.get('user'):
            flash('Page not found')
            return render_template('home.html')
        else:
            con = sql.connect('TeamInfoDB.db')
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM TeamInfo WHERE TeamId = ?", (TeamId,))
            rows1 = cur.fetchall()
            rows = []
            for row in rows1:
                newRow = dict(row)
                rows.append(newRow)
            print("User Leave Test: ", rows)
            con.close()

            return render_template('/u_LeaveTeam.html', rows=rows)


@app.route('/u_LeaveTeam/<int:TeamId>', methods=['POST'])
def u_LeaveTeam(TeamId):
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('user'):
        flash('Page not found')
        return render_template('home.html')
    try:
        con = sql.connect('UserInfoDB.db')
        cur = con.cursor()
        cur.execute("SELECT UserId FROM UserInfo WHERE UserId = ? ", (session['UserId'],))
        id = cur.fetchone()

        print("User ID: ", id[0])

        con1 = sql.connect('UserInfoDB.db')
        cur1 = con1.cursor()
        cur1.execute("UPDATE UserInfo SET UserTeamId = ? WHERE UserId = ? ", (None, id[0]))
        con1.commit()
        con1.close()

        con2 = sql.connect('TeamInfoDB.db')
        cur2 = con2.cursor()
        cur2.execute(
            "UPDATE TeamInfo SET Member1Name = NULL, Member1Handicap = NULL, Member1Here = NULL, Member1ID = NULL WHERE Member1ID = ?", (id[0],))
        cur2.execute(
            "UPDATE TeamInfo SET Member2ID = NULL WHERE Member2ID = ? ", (id[0],))
        cur2.execute(
            "UPDATE TeamInfo SET Member3ID = NULL WHERE Member3ID = ?", (id[0],))
        cur2.execute(
            "UPDATE TeamInfo SET Member4ID = NULL WHERE Member4ID = ?", (id[0],))
        con2.close()
        con.close()

        flash("Successfully Left Team")
        return render_template('result.html')
    except Exception as e:
        flash("Error")
        return render_template('u_leaveTeam.html')
'''


# **********************************************************************************************
#                             FOR BOTH USERS / ADMINS                      lines: 1105-1258    *
# **********************************************************************************************
# BOTH ADMIN/USER - Shows the specific user information
@app.route('/view')
def view():
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
        nm = session['UserName']
        con = sql.connect("UserInfoDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute(
            "SELECT UserName, UserFName, UserMName, UserLName, UserGender, UserDOB, UserHandicap, UserPhNum, UserEmail, UserTeamId, LoginPassword, ProfilePicture FROM UserInfo "
            "WHERE UserName = ?", (encrypt(nm),))
        data = cur.fetchall()
        df = pd.DataFrame(data,
                          columns=['UserName', 'UserFName', 'UserMName', 'UserLName', 'UserGender', 'UserDOB',
                                   'UserHandicap', 'UserPhNum', 'UserEmail', 'UserTeamId', 'LoginPassword',
                                   'ProfilePicture'])
        con.close()
        # convert to an array
        index = 0
        for nm in df['UserName']:
            # print("before = ",nm)
            nm = str(Encryption.cipher.decrypt(nm))
            # print("after = ",nm)
            df._set_value(index, 'UserName', nm)
            index += 1
        index = 0
        for pn in df['UserPhNum']:
            pn = str(Encryption.cipher.decrypt(pn))
            df._set_value(index, 'UserPhNum', pn)
            index += 1
        index = 0
        for email in df['UserEmail']:
            email = str(Encryption.cipher.decrypt(email))
            df._set_value(index, 'UserEmail', email)
            index += 1
        index = 0
        for pwd in df['LoginPassword']:
            pwd = str(Encryption.cipher.decrypt(pwd))
            df._set_value(index, 'LoginPassword', pwd)
            index += 1

        for row in df.itertuples():
            print(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12])
        # pull picture pathfile to html
        file = df['ProfilePicture']
        photo = np.array([file.values])
        string_representation = photo[0]
        photo = ' '.join(map(str, string_representation))
        print(photo)

        con.close()
        return render_template("profile_view.html", row=row, UserName=session['UserName'], photo=photo)


# BOTH ADMIN/USER - Show info to edit profile
@app.route('/editProfile', methods=['GET', 'POST'])
def edit_profile():
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
        nm = session['UserName']
        con = sql.connect('UserInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM UserInfo WHERE UserName = ?", (encrypt(nm),))

        rows1 = cur.fetchall()
        rows = []

        for row in rows1:
            newRow = dict(row)
            newRow['UserName'] = str(Encryption.cipher.decrypt(row['UserName']))
            newRow['UserPhNum'] = str(Encryption.cipher.decrypt(row['UserPhNum']))
            newRow['UserEmail'] = str(Encryption.cipher.decrypt(row['UserEmail']))
            newRow['LoginPassword'] = str(Encryption.cipher.decrypt(row['LoginPassword']))
            rows.append(newRow)

        con.close()
    return render_template("profile_update.html", rows=rows, UserName=session['UserName'])


# BOTH ADMIN/USER - Update profile
@app.route('/updateProfile', methods=['POST'])
def update_profile():
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
        try:
            contact, tid = is_a_contact()
            print(contact, tid)
            nm = session['UserName']
            newUserName = request.form['UserName']
            newUserFName = request.form['UserFName']
            newUserMName = request.form['UserMName']
            newUserLName = request.form['UserLName']
            newUserGender = request.form['UserGender']
            newUserDOB = request.form['UserDOB']
            newUserHandicap = request.form['UserHandicap']
            newUserPhNum = request.form['UserPhNum']
            newUserEmail = request.form['UserEmail']
            newPassword = request.form['LoginPassword']
            if 'picture' not in request.files:
                pass
            file = request.files['picture']
            if file.filename == '':
                pass
            # upload photo to directory
            if file:
                # ensure each photo has distinct name ie no duplicates (ex: if 2 hi.jpeg uploaded will result in users having someone else's profile pic)
                # count the number of files
                files = os.listdir(app.config['UPLOAD_FOLDER'])
                num_files = len(files)
                # Split the filename and extension
                name, ext = os.path.splitext(file.filename)
                # Construct the new filename with the numeric suffix
                new_filename = f"{num_files + 1}{ext}"
                # save photo to directory statics/css/uploads/_____
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))

                # pull most recent uploaded photo
                files = [os.path.join(app.config['UPLOAD_FOLDER'], f) for f in os.listdir(app.config['UPLOAD_FOLDER'])
                         if
                         os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]
                if files:
                    p = max(files, key=os.path.getctime)
                    p = "../" + p
                else:
                    p = None

                con = sql.connect('UserInfoDB.db')
                cur = con.cursor()
                cur.execute(
                    "UPDATE UserInfo SET ProfilePicture = ? WHERE UserName = ?",
                    (p, encrypt(nm)))
                con.commit()

            if newUserHandicap != 'Handicap':
                print("h", newUserHandicap)
                con = sql.connect('UserInfoDB.db')
                cur = con.cursor()
                cur.execute(
                    "UPDATE UserInfo SET UserHandicap = ? WHERE UserName = ?",
                    (newUserHandicap, encrypt(nm)))
                con.commit()

            if newUserGender != 'Gender':
                print("h", newUserGender)
                con = sql.connect('UserInfoDB.db')
                cur = con.cursor()
                cur.execute(
                    "UPDATE UserInfo SET UserGender = ? WHERE UserName = ?",
                    (newUserGender, encrypt(nm)))
                con.commit()

            con = sql.connect('UserInfoDB.db')
            cur = con.cursor()
            cur.execute(
                "UPDATE UserInfo SET UserName = ?, UserFName = ?, UserMName = ?, UserLName = ?,"
                " UserDOB = ?, UserPhNum = ?, UserEmail = ?, LoginPassword = ? WHERE UserName = ?",
                (encrypt(newUserName), newUserFName, newUserMName, newUserLName, newUserDOB,
                 encrypt(newUserPhNum), encrypt(newUserEmail), encrypt(newPassword),
                 encrypt(nm)))
            con.commit()

            # update team info if user is contact person (1 == in contact, 0 == not contact)
            if contact == 1:
                con = sql.connect('TeamInfoDB.db')
                cur = con.cursor()
                cur.execute(
                    "UPDATE TeamInfo SET ContactFname = ?, ContactLname = ?, ContactPhNum = ?, ContactEmail = ? WHERE TeamId = ?",
                    (encrypt(newUserFName), encrypt(newUserLName), encrypt(newUserPhNum), encrypt(newUserEmail), tid, ))
                con.commit()
                con = sql.connect('TeamInfoDB.db')
                cur = con.cursor()
                cur.execute(
                    "UPDATE TeamInfo SET ContactPhoto = ? WHERE TeamId = ?",
                    (p, tid, ))
                con.commit()
            else:
                pass

            # Not Sure if this is old may need to be deleted
            #con2 = sql.connect('TeamInfoDB.db')
            #cur2 = con2.cursor()
            # cur2.execute("UPDATE TeamInfo SET ")

            flash("Successfully Updated Profile")
            return render_template('result.html')
        except Exception as e:
            con.rollback()
            flash("Error Updated Profile")
            return render_template('profile_view.html')
        finally:
            con.close()


# BOTH ADMIN/USER - Search by team/member names or contact info (user output doesnt have all info)
@app.route('/searchTeamName', methods=['POST'])
def searchTeamName():
    if not session.get('logged_in'):
        return render_template('home.html')
    try:

        searchInfo = request.form.get('TeamName')

        with sql.connect("TeamInfoDB.db") as con:
            con.row_factory = sql.Row
            cur = con.cursor()

            cur.execute(
                "SELECT * FROM TeamInfo WHERE TeamName = ? OR SponsorName = ? OR MemberName1 = ? OR MemberName2 = ? OR "
                "MemberName3 = ? OR MemberName4 = ? OR ContactLName = ? OR ContactLName = ? OR ContactPhNum = ? OR "
                "ContactEmail = ? OR SponsorName = ?",
                (searchInfo, searchInfo, searchInfo, searchInfo, searchInfo, searchInfo,
                 encrypt(searchInfo), encrypt(searchInfo), encrypt(searchInfo), searchInfo, searchInfo))

            rows = []

            for row in cur.fetchall():
                newRow = dict(row)
                newRow['ContactFName'] = Encryption.cipher.decrypt(newRow['ContactFName'])
                newRow['ContactLName'] = str(Encryption.cipher.decrypt(newRow['ContactLName']))
                newRow['ContactPhNum'] = str(Encryption.cipher.decrypt(newRow['ContactPhNum']))
                newRow['ContactEmail'] = str(Encryption.cipher.decrypt(newRow['ContactEmail']))
                rows.append(newRow)

            if session.get('admin'):
                return render_template("a_viewTeamSelected.html", rows=rows, UserName=session['UserName'])
            if session.get('user'):
                return render_template("u_viewTeam.html", rows=rows, UserName=session['UserName'])

    except Exception as e:
        flash("Search Error")
        return render_template('dash.html')


# **********************************************************************************************
#                                       FOR ADMINS                         lines: 1264-2224    *
# **********************************************************************************************
# ADMIN - List all current users information
@app.route('/adminlist')
def admin_list():
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
        if not session.get('admin'):
            flash('Page not found')
            return render_template('home.html')
        else:
            con = sql.connect("UserInfoDB.db")
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute('SELECT * FROM UserInfo')

            rows1 = cur.fetchall()
            rows = []

            for row in rows1:
                newRow = dict(row)
                newRow['UserName'] = str(Encryption.cipher.decrypt(row['UserName']))
                newRow['UserPhNum'] = str(Encryption.cipher.decrypt(row['UserPhNum']))
                newRow['UserEmail'] = str(Encryption.cipher.decrypt(row['UserEmail']))
                rows.append(newRow)

            con.close()
            # pull picture pathfile to html
            nm = session['UserName']
            con = sql.connect("UserInfoDB.db")
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute('SELECT ProfilePicture FROM UserInfo WHERE UserName= ?', (encrypt(nm),))
            data = cur.fetchall()
            df = pd.DataFrame(data,
                              columns=['ProfilePicture'])

            con.close()
            for row in df.itertuples():
                print(row[1])
            file = df['ProfilePicture']
            photo = np.array([file.values])
            string_representation = photo[0]
            photo = ' '.join(map(str, string_representation))
            print(photo)
            return render_template("a_adminlist-OLD.html", rows=rows, UserName=session['UserName'], photo=photo)


# ADMIN - Routes to search for users
@app.route('/searchUserPage')
def searchUserPage():
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('admin'):
        flash('Page not found')
        return render_template('home.html')
    return render_template('a_searchUser.html')


# ADMIN - Search for users
@app.route('/searchUser', methods=['POST'])
def searchUser():
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('admin'):
        flash('Page not found')
        return render_template('home.html')

    try:
        nm = request.form.get('UserLName')


        with sql.connect("UserInfoDB.db") as con:  # Connect to the userInfo database
            con.row_factory = sql.Row
            cur = con.cursor()

            cur.execute("SELECT * FROM UserInfo WHERE UserLName = ?", (nm,))

            rows = []

            for row in cur.fetchall():
                newRow = dict(row)
                newRow['UserName'] = Encryption.cipher.decrypt(newRow['UserName'])
                newRow['UserPhNum'] = str(Encryption.cipher.decrypt(newRow['UserPhNum']))
                newRow['UserEmail'] = str(Encryption.cipher.decrypt(newRow['UserEmail']))
                newRow['LoginPassword'] = str(Encryption.cipher.decrypt(newRow['LoginPassword']))
                rows.append(newRow)

            return render_template("a_searchAndEdit.html", rows=rows)

    except Exception as e:
        flash("Search Error")
        return render_template('a_searchUser.html')


# ADMIN - List all contacts
@app.route('/teamContactsList')
def team_Contacts():
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
        if not session.get('admin'):
            flash('Page not found')
            return render_template('home.html')

        else:
            con = sql.connect("TeamInfoDB.db")
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute('SELECT TeamId, MemberName1, MemberName2, MemberName3, MemberName4, Member1Here, Member2Here, Member3Here, Member4Here, TeamName, ContactFName, ContactLName, ContactPhNum, ContactEmail, ContactPhoto FROM TeamInfo')

            rows1 = cur.fetchall()
            rows = []

            for row in rows1:
                newRow = dict(row)
                newRow['ContactFName'] = str(Encryption.cipher.decrypt(row['ContactFName']))
                newRow['ContactLName'] = str(Encryption.cipher.decrypt(row['ContactLName']))
                newRow['ContactPhNum'] = str(Encryption.cipher.decrypt(row['ContactPhNum']))
                newRow['ContactEmail'] = str(Encryption.cipher.decrypt(row['ContactEmail']))
                rows.append(newRow)

            con.close()
            # pull picture pathfile to html
            nm = session['UserName']
            con = sql.connect("UserInfoDB.db")
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute('SELECT ProfilePicture FROM UserInfo WHERE UserName= ?', (encrypt(nm),))
            data = cur.fetchall()
            df = pd.DataFrame(data,
                              columns=['ProfilePicture'])

            con.close()
            for row in df.itertuples():
                print(row[1])
            file = df['ProfilePicture']
            photo = np.array([file.values])
            string_representation = photo[0]
            photo = ' '.join(map(str, string_representation))
            print(photo)
            return render_template("a_viewContact.html", rows=rows, UserName=session['UserName'], photo=photo)


# ADMIN - List all current team information
@app.route('/allteamlist')
def admin_teamlist():
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
        if not session.get('admin'):
            flash('Page not found')
            return render_template('home.html')
        else:
            con = sql.connect("TeamInfoDB.db")
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute('SELECT * FROM TeamInfo')
            rows1 = cur.fetchall()
            rows = []

            for row in rows1:
                newRow = dict(row)
                newRow['ContactFName'] = str(Encryption.cipher.decrypt(row['ContactFName']))
                newRow['ContactLName'] = str(Encryption.cipher.decrypt(row['ContactLName']))
                newRow['ContactPhNum'] = str(Encryption.cipher.decrypt(row['ContactPhNum']))
                newRow['ContactEmail'] = str(Encryption.cipher.decrypt(row['ContactEmail']))
                rows.append(newRow)

            con.close()

            # pull picture pathfile to html
            nm = session['UserName']
            con = sql.connect("UserInfoDB.db")
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute('SELECT ProfilePicture FROM UserInfo WHERE UserName= ?', (encrypt(nm),))
            data = cur.fetchall()
            df = pd.DataFrame(data,
                              columns=['ProfilePicture'])
            con.close()
            file = df['ProfilePicture']
            photo = np.array([file.values])
            string_representation = photo[0]
            photo = ' '.join(map(str, string_representation))
            print(photo)
            return render_template("a_viewTeamsAll.html", rows=rows, UserName=session['UserName'], photo=photo)


# ADMIN - Route to Search for teams by team/member names or contact info
@app.route('/searchTeamNamePage')
def searchTeamNamePage():
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('admin'):
        flash('Page not found')
        return render_template('home.html')
    return render_template('a_searchTeamName.html')


# ADMIN - Selects one team to view in depth
@app.route('/showOneTeam/<int:TeamId>', methods=['GET', 'POST'])
def showOneTeam(TeamId):
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('admin'):
        flash('Page not found')
        return render_template('home.html')
    else:
        con = sql.connect('TeamInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM TeamInfo WHERE TeamId = ?", (TeamId,))
        session['Delete'] = TeamId

        rows1 = cur.fetchall()
        rows = []

        for row in rows1:
            newRow = dict(row)
            newRow['ContactFName'] = str(Encryption.cipher.decrypt(row['ContactFName']))
            newRow['ContactLName'] = str(Encryption.cipher.decrypt(row['ContactLName']))
            newRow['ContactPhNum'] = str(Encryption.cipher.decrypt(row['ContactPhNum']))
            newRow['ContactEmail'] = str(Encryption.cipher.decrypt(row['ContactEmail']))
            rows.append(newRow)
        con.close()
        con = sql.connect("TeamInfoDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT TeamName FROM TeamInfo WHERE TeamId = ?', (TeamId,))
        counter = cur.fetchall()
        count = []
        for cnt in counter:
            newRow = dict(cnt)
            count.append(newRow)
        string = ',:'.join(str(x) for x in count)
        print(string)
        splitter = string.split("{'TeamName': '")
        strr = ""
        print(splitter)
        for ele in splitter:
            strr += ele
        new = []
        for char in strr:
            if char.isalnum():
                new.append(str(char))
        split = new
        print(split)
        final = ""
        for ele in split:
            final += ele
        print("final", final)
        con.close()
        # pull picture pathfile to html
        nm = session['UserName']
        con = sql.connect("UserInfoDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT ProfilePicture FROM UserInfo WHERE UserName= ?', (encrypt(nm),))
        data = cur.fetchall()
        df = pd.DataFrame(data,
                          columns=['ProfilePicture'])

        con.close()
        for row in df.itertuples():
            print(row[1])
        file = df['ProfilePicture']
        photo = np.array([file.values])
        string_representation = photo[0]
        photo = ' '.join(map(str, string_representation))
        print(photo)
        return render_template("/a_viewTeamSelected.html", rows=rows, final=final, UserName=session['UserName'],
                               photo=photo)
    con.close()


# ADMIN - Dash Team Quick view
@app.route('/showTeam/<int:TeamId>', methods=['GET', 'POST'])
def showTeam(TeamId):
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('admin'):
        flash('Page not found')
        return render_template('home.html')
    else:
        con = sql.connect('TeamInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM TeamInfo WHERE TeamId = ?", (TeamId,))

        rows1 = cur.fetchall()
        rows = []

        for row in rows1:
            newRow = dict(row)
            newRow['ContactFName'] = str(Encryption.cipher.decrypt(row['ContactFName']))
            newRow['ContactLName'] = str(Encryption.cipher.decrypt(row['ContactLName']))
            newRow['ContactPhNum'] = str(Encryption.cipher.decrypt(row['ContactPhNum']))
            newRow['ContactEmail'] = str(Encryption.cipher.decrypt(row['ContactEmail']))
            rows.append(newRow)
        con.close()

        return render_template("/a_viewTeamQuick.html", rows=rows)


# ADMIN - View users
@app.route('/showUser')
def showUser():
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('admin'):
        flash('Page not found')
        return render_template('home.html')
    else:
        con = sql.connect('UserInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM UserInfo")
        rows1 = cur.fetchall()
        rows = []
        for row in rows1:
            newRow = dict(row)
            rows.append(newRow)
        con.close()
        # pull picture pathfile to html
        nm = session['UserName']
        con = sql.connect("UserInfoDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT ProfilePicture FROM UserInfo WHERE UserName= ?', (encrypt(nm),))
        data = cur.fetchall()
        df = pd.DataFrame(data,
                          columns=['ProfilePicture'])

        con.close()
        for row in df.itertuples():
            print(row[1])
        file = df['ProfilePicture']
        photo = np.array([file.values])
        string_representation = photo[0]
        photo = ' '.join(map(str, string_representation))
        print(photo)
        return render_template("/a_viewUser.html", rows=rows, UserName=session['UserName'], photo=photo)


# ADMIN - Directs admin to team sign up page
@app.route('/adminmaketeam')
def teamsignup():
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('admin'):
        flash('Page not found')
        return render_template('home.html')
    else:
        con = sql.connect('UserInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM UserInfo WHERE RoleLevel = 1")

        rows1 = cur.fetchall()
        rows = []
        for row in rows1:
            newRow = dict(row)
            newRow['UserPhNum'] = str(Encryption.cipher.decrypt(row['UserPhNum']))
            newRow['UserEmail'] = str(Encryption.cipher.decrypt(row['UserEmail']))
            rows.append(newRow)
        con.close()
        # pull picture pathfile to html
        nm = session['UserName']
        con = sql.connect("UserInfoDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT ProfilePicture FROM UserInfo WHERE UserName= ?', (encrypt(nm),))
        data = cur.fetchall()
        df = pd.DataFrame(data,
                          columns=['ProfilePicture'])

        con.close()
        for row in df.itertuples():
            print(row[1])
        file = df['ProfilePicture']
        photo = np.array([file.values])
        string_representation = photo[0]
        photo = ' '.join(map(str, string_representation))
        print(photo)
    return render_template('a_adminteamsignup.html', UserName=session['UserName'], rows=rows, photo=photo)


# ADMIN - sign up teams
@app.route('/adminteamsignup', methods=['POST', 'GET'])
def admin_teamSignup():
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('admin'):
        flash('Page not found')
        return render_template('home.html')
    else:
        con = sql.connect('UserInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM UserInfo")

        rows1 = cur.fetchall()
        rows = []
        for row in rows1:
            newRow = dict(row)
            newRow['UserPhNum'] = str(Encryption.cipher.decrypt(row['UserPhNum']))
            newRow['UserEmail'] = str(Encryption.cipher.decrypt(row['UserEmail']))
            rows.append(newRow)
        con.close()

        valid_input = True
        err_string = " "

        m2id, m2hc, mn2 = None, None, None
        m3id, m3hc, mn3 = None, None, None
        m4id, m4hc, mn4 = None, None, None

        memberCount = 0

        if request.method == 'POST':
            try:
                tnm = request.form['TeamName']
                snm = request.form['SponsorName']
                nc = request.form['NeedCart']

                m1info = request.form['MemberName1']
                word = m1info.split(',')
                m1id = word[0].strip()
                m1hc = word[1]
                mn1 = word[2].strip()
                memberCount += 1

                m2info = request.form['MemberName2']
                word = m2info.split(',')
                if len(word) >= 3:
                    m2id = word[0].strip()
                    m2hc = word[1]
                    mn2 = word[2].strip()
                    memberCount += 1

                m3info = request.form['MemberName3']
                word = m3info.split(',')
                if len(word) >= 3:
                    m3id = word[0].strip()
                    m3hc = word[1]
                    mn3 = word[2].strip()
                    memberCount += 1

                m4info = request.form['MemberName4']
                word = m4info.split(',')
                if len(word) >= 3:
                    m4id = word[0].strip()
                    m4hc = word[1]
                    mn4 = word[2].strip()
                    memberCount += 1

                # select menu based off previous answers
                cfn = request.form['ContactFName']
                cln = request.form['ContactLName']
                cpn = request.form['ContactPhNum']
                ce = request.form['ContactEmail']
                check = is_empty()
                if check is False:
                    con = sql.connect('TeamInfoDB.db')
                    con.row_factory = sql.Row
                    cur = con.cursor()
                    cur.execute(
                        "SELECT StartHole FROM TeamInfo WHERE TeamId =(SELECT max(TeamId) FROM TeamInfo)")  # get last hole
                    num = cur.fetchall()
                    val = num[0]
                    lastASGNDhole = val['StartHole']
                    set(lastASGNDhole + 1)
                    con.close()
                else:
                    increment()
                if counter <= 18:
                    sh = counter
                else:
                    reset()
                    sh = counter

                code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                print("The code is:", code)

                if not validate_string(tnm):
                    valid_input = False
                    err_string = err_string + "<br>You cannot enter in an empty team name"

                if not validate_string(cfn):
                    valid_input = False
                    err_string = err_string + "<br>You cannot enter in an empty contact first name."

                if (int(nc) <= -1) or (int(nc) >= 3):
                    valid_input = False
                    err_string = err_string + "<br>You cannot enter in an empty cart."

                if not validate_string(cln):
                    valid_input = False
                    err_string = err_string + "<br>You can not enter in an empty contact last name."

                if not validate_string(cpn):
                    valid_input = False
                    err_string = err_string + "<br>You cannot enter in an empty contact phone number."

                if not validate_string(ce):
                    valid_input = False
                    err_string = err_string + "<br>You cannot enter in an empty contact email."

                    if not valid_input:
                        msg = err_string
                        return render_template("result.html", msg=format_output(err_string))

                if valid_input:
                    with sql.connect("TeamInfoDB.db") as con:
                        cur = con.cursor()
                        cur.execute(
                            "INSERT INTO TeamInfo (TeamName, SponsorName, NeedCart, MemberName1, MemberName2,"
                            " MemberName3, MemberName4, Member1ID, Member2ID, Member3ID, Member4ID, Member1Handicap,"
                            " Member2Handicap, Member3Handicap, Member4Handicap, StartHole, Member1Here, Member2Here,"
                            " Member3Here, Member4Here, ContactFName, ContactLName, ContactPhNum, ContactEmail, JoinCode, MemberCount) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            (tnm, snm, nc, mn1, mn2, mn3, mn4, m1id, m2id, m3id, m4id, m1hc, m2hc,
                             m3hc, m4hc, sh, "✘", "✘", "✘", "✘", encrypt(cfn), encrypt(cln), encrypt(cpn), encrypt(ce),
                             code, memberCount))

                        con.commit()

                with sql.connect("TeamInfoDB.db") as con2:
                    cur2 = con2.cursor()
                    cur2.execute("SELECT TeamId FROM TeamInfo WHERE TeamId = ?", (cur.lastrowid,))
                    id = cur2.fetchone()

                    con2.commit()

                with sql.connect("UserInfoDB.db") as con3:
                    cur3 = con3.cursor()
                    cur3.execute("UPDATE UserInfo SET UserTeamId = ? WHERE UserId IN (?,?,?,?)",
                                 (id[0], m1id, m2id, m3id, m4id))

                    con3.commit()
                    con3.close()
                    con2.close()

                    msg = "Team Added successfully"

                    '''cur.execute(
                            "SELECT * FROM TeamInfo WHERE TeamId =(SELECT max(TeamId) FROM TeamInfo)")
                        inc = cur.fetchall()
                        pnt = inc[0]
                        if(pnt['MemberName2'] == None):
                            memc = 1
                        elif(pnt['MemberName3'] == None and pnt['MemberName2'] != None):
                            memc = 2
                        elif(pnt['MemberName4'] == None and pnt['MemberName3'] != None):
                            memc = 3
                        elif(pnt['MemberName4'] != None):
                            memc = 4
                        print(memc)

                        cur.execute("UPDATE TeamInfo SET MemberCount = ? WHERE TeamId =(SELECT max(TeamId) FROM TeamInfo)", memc)
                        con.commit()'''

            except:
                con.rollback()
            finally:
                con.close()
                return render_template("result.html", msg=msg)
        else:
            flash('Page not found')
            return render_template('a_viewTeamsAll.html')


# ADMIN - directs admin to check in page
@app.route('/admpre_checkin/<int:TeamId>', methods=['GET', 'POST'])
def checkin(TeamId):
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('admin'):
        flash('Page not found')
        return render_template('home.html')
    else:
        session['cart2'] = False
        session['cart1'] = False
        session['cart0'] = False
        con = sql.connect('TeamInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM TeamInfo WHERE TeamId = ?", (TeamId,))

        rows1 = cur.fetchall()
        rows = []
        ans = count_carts(TeamId)
        print(ans)
        print("this is count1:", cartCounter)
        for row in rows1:
            newRow = dict(row)
            rows.append(newRow)
            if cartCounter == 2:
                session['cart2'] = True
                print("got 2")
            elif cartCounter == 1:
                session['cart1'] = True
                print("got 1")
            else:
                session['cart0'] = True
                print("got 0")

        con.close()
        con = sql.connect("TeamInfoDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT TeamName FROM TeamInfo WHERE TeamId = ?', (TeamId,))
        counter = cur.fetchall()
        count = []
        for cnt in counter:
            newRow = dict(cnt)
            count.append(newRow)
        string = ',:'.join(str(x) for x in count)
        print(string)
        splitter = string.split("{'TeamName': '")
        strr = ""
        print(splitter)
        for ele in splitter:
            strr += ele
        new = []
        for char in strr:
            if char.isalnum():
                new.append(str(char))
        split = new
        print(split)
        final = ""
        for ele in split:
            final += ele
        print("final", final)
        con.close()
        # pull picture pathfile to html
        nm = session['UserName']
        con = sql.connect("UserInfoDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT ProfilePicture FROM UserInfo WHERE UserName= ?', (encrypt(nm),))
        data = cur.fetchall()
        df = pd.DataFrame(data,
                          columns=['ProfilePicture'])

        con.close()
        for row in df.itertuples():
            print(row[1])
        file = df['ProfilePicture']
        photo = np.array([file.values])
        string_representation = photo[0]
        photo = ' '.join(map(str, string_representation))
        print(photo)
        return render_template("a_admincheckin.html", rows=rows, final=final, UserName=session['UserName'], photo=photo)


# ADMIN - checkin: Check off when users arrive and assign cart(s)
@app.route('/admincheckin/<int:TeamId>', methods=['POST'])
def admin_checkin(TeamId):
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('admin'):
        flash('Page not found')
        return render_template('home.html')
    try:
        if request.form.get('Member1Here'):
            m1h = "✔"
        else:
            m1h = "✘"
        if request.form.get('Member2Here'):
            m2h = "✔"
        else:
            m2h = "✘"
        if request.form.get('Member3Here'):
            m3h = "✔"
        else:
            m3h = "✘"
        if request.form.get('Member4Here'):
            m4h = "✔"
        else:
            m4h = "✘"

        while cartCounter == 2:
            print("getting 2nd loop")
            c1 = request.form['AsgnCart1']
            c2 = request.form['AsgnCart2']
            con = sql.connect('TeamInfoDB.db')
            cur = con.cursor()
            cur.execute(
                "UPDATE TeamInfo SET Member1Here = ?, Member2Here = ?, Member3Here = ?,Member4Here = ?, AsgnCart1 = ?, AsgnCart2 = ? WHERE TeamId = ?",
                (m1h, m2h, m3h, m4h, c1, c2, TeamId))
            con.commit()
            reset_cart()
            session['cart2'] = False
            session['cart1'] = False
            session['cart0'] = False
            flash("Successful Team Check In")
            return render_template('result.html')

        if cartCounter == 1:
            print("getting 1st loop")
            c1 = request.form['AsgnCart1']
            con = sql.connect('TeamInfoDB.db')
            cur = con.cursor()
            cur.execute(
                "UPDATE TeamInfo SET Member1Here = ?, Member2Here = ?, Member3Here = ?,Member4Here = ?, AsgnCart1 = ? WHERE TeamId = ?",
                (m1h, m2h, m3h, m4h, c1, TeamId))
            con.commit()
            reset_cart()
            session['cart2'] = False
            session['cart1'] = False
            session['cart0'] = False
            flash("Successful Team Check In")
            return render_template('result.html')

        else:
            print("getting 3rd loop")
            con = sql.connect('TeamInfoDB.db')
            cur = con.cursor()
            cur.execute(
                "UPDATE TeamInfo SET Member1Here = ?, Member2Here = ?, Member3Here = ?,Member4Here = ? WHERE TeamId = ?",
                (m1h, m2h, m3h, m4h, TeamId))
            con.commit()
            reset_cart()
            session['cart2'] = False
            session['cart1'] = False
            session['cart0'] = False
            flash("Successful Team Check In")
            return render_template('result.html')

    except Exception as e:
        con.rollback()
        return render_template('a_admincheckin.html')
    finally:
        con.close()


# ADMIN - Edit teams
@app.route('/editTeam/<int:TeamId>', methods=['GET', 'POST'])
def edit_TeamForm(TeamId):
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('admin'):
        flash('Page not found')
        return render_template('home.html')
    else:
        con = sql.connect('TeamInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM TeamInfo WHERE TeamId = ?", (TeamId,))

        rows1 = cur.fetchall()
        rows = []

        for row in rows1:
            newRow = dict(row)
            newRow['ContactFName'] = str(Encryption.cipher.decrypt(row['ContactFName']))
            newRow['ContactLName'] = str(Encryption.cipher.decrypt(row['ContactLName']))
            newRow['ContactPhNum'] = str(Encryption.cipher.decrypt(row['ContactPhNum']))
            newRow['ContactEmail'] = str(Encryption.cipher.decrypt(row['ContactEmail']))
            rows.append(newRow)

        con.close()
        con = sql.connect("TeamInfoDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT TeamName FROM TeamInfo WHERE TeamId = ?', (TeamId,))
        counter = cur.fetchall()
        count = []
        for cnt in counter:
            newRow = dict(cnt)
            count.append(newRow)
        string = ',:'.join(str(x) for x in count)
        print(string)
        splitter = string.split("{'TeamName': '")
        strr = ""
        print(splitter)
        for ele in splitter:
            strr += ele
        new = []
        for char in strr:
            if char.isalnum():
                new.append(str(char))
        split = new
        print(split)
        final = ""
        for ele in split:
            final += ele
        print("final", final)
        con.close()

        con = sql.connect('UserInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM UserInfo WHERE RoleLevel = 1")

        rows2 = cur.fetchall()
        rows1 = []
        for row in rows2:
            newRow = dict(row)
            newRow['UserPhNum'] = str(Encryption.cipher.decrypt(row['UserPhNum']))
            newRow['UserEmail'] = str(Encryption.cipher.decrypt(row['UserEmail']))
            rows1.append(newRow)
        con.close()
        # pull picture pathfile to html
        nm = session['UserName']
        con = sql.connect("UserInfoDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT ProfilePicture FROM UserInfo WHERE UserName= ?', (encrypt(nm),))
        data = cur.fetchall()
        df = pd.DataFrame(data,
                          columns=['ProfilePicture'])

        con.close()
        for row in df.itertuples():
            print(row[1])
        file = df['ProfilePicture']
        photo = np.array([file.values])
        string_representation = photo[0]
        photo = ' '.join(map(str, string_representation))
        print(photo)

        return render_template("a_updateTeam.html", rows=rows, final=final, UserName=session['UserName'], rows1=rows1,
                               photo=photo)


# ADMIN - Update teams
@app.route('/updateTeam/<int:TeamId>', methods=['POST'])
def updateTeamForm(TeamId):
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('admin'):
        flash('Page not found')
        return render_template('home.html')
    try:
        conNew = sql.connect("TeamInfoDB.db")
        conNew.row_factory = sql.Row
        cur = conNew.cursor()
        cur.execute('SELECT MemberCount, Member1ID,Member2ID, Member3ID, Member4ID FROM TeamInfo WHERE TeamId = ?',
                    (TeamId,))
        infoRows = cur.fetchone()

        memberCount = infoRows['MemberCount']
        newMemberCount = 0

        oldMem2ID = infoRows['Member2ID']
        oldMem3ID = infoRows['Member3ID']

        newTeamName = request.form['TeamName']
        newSponsorName = request.form['SponsorName']
        newNeedCart = request.form['NeedCart']

        mn1 = request.form['MemberName1']

        if request.form.get('Member1Handicap'):
            m1hc = "✔"
        else:
            m1hc = "✘"

        if memberCount == 1:
            m2id, m2hc, mn2 = None, None, None
            m3id, m3hc, mn3 = None, None, None
            m4id, m4hc, mn4 = None, None, None

            m2info = request.form['MemberName2']
            word = m2info.split(',')
            if len(word) >= 3:
                m2id = word[0].strip()
                if word[1] == " ✔":
                    m2hc = "✔"
                else:
                    m2hc = "✘"
                mn2 = word[2].strip()
                newMemberCount += 1

            m3info = request.form['MemberName3']
            word = m3info.split(',')
            if len(word) >= 3:
                m3id = word[0].strip()
                if word[1] == " ✔":
                    m3hc = "✔"
                else:
                    m3hc = "✘"
                mn3 = word[2].strip()
                newMemberCount += 1

            m4info = request.form['MemberName4']
            word = m4info.split(',')
            if len(word) >= 3:
                m4id = word[0].strip()
                if word[1] == " ✔":
                    m4hc = "✔"
                else:
                    m4hc = "✘"
                mn4 = word[2].strip()
                newMemberCount += 1

        if memberCount == 2:
            mn2 = request.form['MemberName2']
            m2id = oldMem2ID

            if request.form.get('Member2Handicap'):
                m2hc = "✔"
            else:
                m2hc = "✘"

            m3id, m3hc, mn3 = None, None, None
            m4id, m4hc, mn4 = None, None, None

            m3info = request.form['MemberName3']
            word = m3info.split(',')
            if len(word) >= 3:
                m3id = word[0].strip()
                if word[1] == " ✔":
                    m3hc = "✔"
                else:
                    m3hc = "✘"
                mn3 = word[2].strip()
                newMemberCount += 1

            m4info = request.form['MemberName4']
            word = m4info.split(',')
            if len(word) >= 3:
                m4id = word[0].strip()
                if word[1] == " ✔":
                    m4hc = "✔"
                else:
                    m4hc = "✘"
                mn4 = word[2].strip()
                newMemberCount += 1

        if memberCount == 3:
            mn2 = request.form['MemberName2']
            m2id = oldMem2ID

            if request.form.get('Member2Handicap'):
                m2hc = "✔"
            else:
                m2hc = "✘"

            mn3 = request.form['MemberName3']
            m3id = oldMem3ID

            if request.form.get('Member3Handicap'):
                m3hc = "✔"
            else:
                m3hc = "✘"

            m4id, m4hc, mn4 = None, None, None

            m4info = request.form['MemberName4']
            word = m4info.split(',')
            if len(word) >= 3:
                m4id = word[0].strip()
                if word[1] == " ✔":
                    m4hc = "✔"
                else:
                    m4hc = "✘"
                mn4 = word[2].strip()
                newMemberCount += 1

        memberCount += newMemberCount
        newStartHole = request.form['StartHole']
        newContactFName = request.form['ContactFName']
        newContactLName = request.form['ContactLName']
        newContactPhNum = request.form['ContactPhNum']
        newContactEmail = request.form['ContactEmail']

        con = sql.connect('TeamInfoDB.db')
        cur = con.cursor()
        cur.execute("UPDATE TeamInfo SET TeamName = ?, SponsorName = ?, NeedCart = ?, MemberName1 = ?, MemberName2 = ?,"
                    " MemberName3 = ?, MemberName4 = ?, Member2ID = ?, Member3ID = ?, Member4ID = ?, Member1Handicap = ?, Member2Handicap = ?, Member3Handicap = ?, Member4Handicap = ?, StartHole = ?, ContactFName = ?, ContactLName = ?, ContactPhNum = ?, "
                    "ContactEmail = ?, MemberCount = ? WHERE TeamId = ?",
                    (newTeamName, newSponsorName, newNeedCart, mn1, mn2, mn3,
                     mn4, m2id, m3id, m4id, m1hc, m2hc, m3hc, m4hc, newStartHole, encrypt(newContactFName),
                     encrypt(newContactLName), encrypt(newContactPhNum), encrypt(newContactEmail), memberCount, TeamId))
        con.commit()

        with sql.connect("UserInfoDB.db") as con3:
            cur3 = con3.cursor()
            cur3.execute("UPDATE UserInfo SET UserTeamId = ? WHERE UserId IN (?,?,?)",
                         (TeamId, m2id, m3id, m4id))
            con3.commit()

        flash("Successfully Updated Team")
        return render_template('result.html')
    except Exception as e:
        print("An error occurred:", e)
        return render_template('a_updateTeam.html')
    finally:
        con3.close()
        con.close()
        conNew.close()


# ADMIN - directs admin to delete team
@app.route('/a_deleteteam/<int:TeamId>', methods=['GET', 'POST'])
def a_deleteteam(TeamId):
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('admin'):
        flash('Page not found')
        return render_template('home.html')
    else:
        con = sql.connect('TeamInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM TeamInfo WHERE TeamId = ?", (TeamId,))

        rows1 = cur.fetchall()
        rows = []

        for row in rows1:
            newRow = dict(row)
            newRow['ContactFName'] = str(Encryption.cipher.decrypt(row['ContactFName']))
            newRow['ContactLName'] = str(Encryption.cipher.decrypt(row['ContactLName']))
            newRow['ContactPhNum'] = str(Encryption.cipher.decrypt(row['ContactPhNum']))
            newRow['ContactEmail'] = str(Encryption.cipher.decrypt(row['ContactEmail']))
            rows.append(newRow)

        con.close()
        con = sql.connect("TeamInfoDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT TeamName FROM TeamInfo WHERE TeamId = ?', (TeamId,))
        counter = cur.fetchall()
        count = []
        for cnt in counter:
            newRow = dict(cnt)
            count.append(newRow)
        string = ',:'.join(str(x) for x in count)
        print(string)
        splitter = string.split("{'TeamName': '")
        strr = ""
        print(splitter)
        for ele in splitter:
            strr += ele
        new = []
        for char in strr:
            if char.isalnum():
                new.append(str(char))
        split = new
        print(split)
        final = ""
        for ele in split:
            final += ele
        print("final", final)
        con.close()
        # pull picture pathfile to html
        nm = session['UserName']
        con = sql.connect("UserInfoDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT ProfilePicture FROM UserInfo WHERE UserName= ?', (encrypt(nm),))
        data = cur.fetchall()
        df = pd.DataFrame(data,
                          columns=['ProfilePicture'])

        con.close()
        for row in df.itertuples():
            print(row[1])
        file = df['ProfilePicture']
        photo = np.array([file.values])
        string_representation = photo[0]
        photo = ' '.join(map(str, string_representation))
        print(photo)
        session['Delete'] = TeamId
        return render_template("a_DeleteTeam.html", rows=rows, final=final, UserName=session['UserName'], photo=photo)


# ADMIN - Delete a team
@app.route('/a_DeleteTeam', methods=['POST'])
def a_DeleteTeam():
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('admin'):
        flash('Page not found')
        return render_template('home.html')

    teamId = session['Delete']
    session['Delete'] = ""
    try:
        # TName = request.form['TeamId']
        con2 = sql.connect('UserInfoDB.db')
        cur2 = con2.cursor()
        cur2.execute("UPDATE UserInfo SET UserTeamId = ? WHERE UserTeamId = ? ", (None, teamId))
        con2.commit()
        con2.close()

        con = sql.connect('TeamInfoDB.db')
        cur = con.cursor()
        cur.execute("DELETE FROM TeamInfo WHERE TeamId = ?", (teamId,))
        con.commit()
        flash("Successfully Delete Team")
        return render_template('result.html')
    except Exception as e:
        con.rollback()
        flash("Error")
        return render_template('a_DeleteTeam.html')
    finally:
        con.close()


# **********************************************************************************************
#                                        PAYMENT STRIPE                    lines: 2230-2508    *
# **********************************************************************************************
# USERS - Routes to storefront
@app.route('/index')
def index():
    # pull picture pathfile to html
    nm = session['UserName']
    con = sql.connect("UserInfoDB.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT ProfilePicture FROM UserInfo WHERE UserName= ?', (encrypt(nm),))
    data = cur.fetchall()
    df = pd.DataFrame(data,
                      columns=['ProfilePicture'])
    con.close()
    for row in df.itertuples():
        print(row[1])
    file = df['ProfilePicture']
    photo = np.array([file.values])
    string_representation = photo[0]
    photo = ' '.join(map(str, string_representation))
    print(photo)
    return render_template('index.html', UserName=nm, photo=photo)


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


# **********************************************************************************************
#                                        LOGIN / LOGOUT                                        *
# **********************************************************************************************

# Returning user login, pulls username
@app.route('/login-signup')
def log_in():
    if not session.get('logged_in'):
        return render_template('login-signup.html')
    else:
        try:
            session['UserName'] = str(Encryption.cipher.decrypt(session['UserName']))
            # pull picture pathfile to html
            nm = session['UserName']
            con = sql.connect("UserInfoDB.db")
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute('SELECT ProfilePicture FROM UserInfo WHERE UserName= ?', (encrypt(nm),))
            data = cur.fetchall()
            df = pd.DataFrame(data,
                              columns=['ProfilePicture'])

            con.close()
            for row in df.itertuples():
                print(row[1])
            file = df['ProfilePicture']
            photo = np.array([file.values])
            string_representation = photo[0]
            photo = ' '.join(map(str, string_representation))
            print(photo)
        finally:
            return render_template('login-signup.html', UserName=session['UserName'], photo=photo)


@app.route('/login', methods=['POST'])
def do_admin_login():
    try:
        nm = request.form['username']
        nm = str(Encryption.cipher.encrypt(bytes(nm, 'utf-8')).decode("utf-8"))
        pwd = request.form['password']
        pwd = str(Encryption.cipher.encrypt(bytes(pwd, 'utf-8')).decode("utf-8"))

        with sql.connect("UserInfoDB.db") as con:
            con.row_factory = sql.Row
            cur = con.cursor()

            sql_select_query = """select * from UserInfo where UserName = ? and LoginPassword = ?"""
            cur.execute(sql_select_query, (nm, pwd))

            row = cur.fetchone()
            if row is not None:
                session['logged_in'] = True
                session['UserName'] = nm
                session['LoginPassword'] = pwd
                session['UserId'] = row[0]
                uid = row[0]
                # print(uid)
                if int(row['RoleLevel']) == 3:
                    session['admin'] = True
                    session['management'] = False
                    session['user'] = False
                else:
                    if int(row['RoleLevel']) == 2:
                        session['user'] = False
                        session['admin'] = False
                        session['management'] = True
                    else:
                        session['user'] = True
                        session['management'] = False
                        session['admin'] = False

            else:
                session['logged_in'] = False
                flash('invalid username and/or password!')
    except:
        con.rollback()
        flash("error in insert operation")
    finally:
        con.close()
    return home()


@app.route("/logout")
def logout():
    session['logged_in'] = False
    session['admin'] = False
    session['management'] = False
    session['user'] = False
    session['username'] = ""
    return home()


if __name__ == '__main__':
    # needed for session
    app.secret_key = os.urandom(12)
    app.run(debug=True)
