from flask import render_template, request, session, jsonify, Blueprint
import requests
import sqlite3 as sql
import pandas as pd
import numpy as np
import Encryption
import re

util = Blueprint('util', __name__)

cartCounter = 0

@util.route('/construction')
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

# WORKING - verify UserName is NOT taken
@util.route('/check_username', methods=['POST'])
def check_username():
    username = request.form['username']
    # pull db info - find if username in db
    con = sql.connect('UserInfoDB.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT UserName FROM UserInfo')
    rows1 = cur.fetchall()
    rows = []
    for row in rows1:
        newRow = dict(row)
        newRow['UserName'] = str(Encryption.cipher.decrypt(row['UserName']))
        rows.append(newRow)
    con.close()
    names = [d['UserName'] for d in rows]
    # Check if the username already exists in the database
    if username in names:
        return jsonify({'status': 'error', 'message': 'Username already exists'})
    else:
        return jsonify({'status': 'success'})


# WORKING - verify Phone Number is NOT in use
@util.route('/check_ph-number', methods=['POST'])
def check_phnumber():
    ph_number = request.form['number']
    # pull db info - find if phone number in db
    con = sql.connect('UserInfoDB.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT UserPhNum FROM UserInfo')
    rows1 = cur.fetchall()
    rows = []
    for row in rows1:
        newRow = dict(row)
        newRow['UserPhNum'] = str(Encryption.cipher.decrypt(row['UserPhNum']))
        rows.append(newRow)
    con.close()
    nums = [d['UserPhNum'] for d in rows]
    # Check if the username already exists in the database
    if ph_number in nums:
        return jsonify({'status': 'error', 'message': 'Phone Number already in use'})
    else:
        return jsonify({'status': 'success'})

# WORKING - verify Email is NOT in use
@util.route('/check_email', methods=['POST'])
def check_email():
    email = request.form['email']
    # pull db info - find if phone number in db
    con = sql.connect('UserInfoDB.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT UserEmail FROM UserInfo')
    rows1 = cur.fetchall()
    rows = []
    for row in rows1:
        newRow = dict(row)
        newRow['UserEmail'] = str(Encryption.cipher.decrypt(row['UserEmail']))
        rows.append(newRow)
    con.close()
    emails = [d['UserEmail'] for d in rows]
    # Check if the username already exists in the database
    if email in emails:
        return jsonify({'status': 'error', 'message': 'Email already in use'})
    else:
        return jsonify({'status': 'success'})


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


# WORKING - get user profile picture
def get_profilepic():
    nm = session['UserName']
    con = sql.connect("UserInfoDB.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT ProfilePicture FROM UserInfo WHERE UserName= ?', (encrypt(nm),))
    data = cur.fetchall()
    df = pd.DataFrame(data, columns=['ProfilePicture'])
    con.close()
    file = df['ProfilePicture']
    photo = np.array([file.values])
    string_representation = photo[0]
    photo = ' '.join(map(str, string_representation))
    return photo


# WORKING - google api search to get a sponsor photo
def search_images(query, api_key, cx):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={cx}&searchType=image&key={api_key}"
    response = requests.get(url)
    data = response.json()
    if 'items' in data:
        image_urls = [item['link'] for item in data['items']]
    else:
        image_urls = []  # If no items are found, return an empty list
    return image_urls

# WORKING - get registered users for dropbox population (admin - edit team)
@util.route('/get_registered_users')
def get_registered_users():
    con = sql.connect('UserInfoDB.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT UserId, UserHandicap, UserFName, UserLName FROM UserInfo WHERE UserTeamId is NULL")
    rows1 = cur.fetchall()
    registered_users = []
    for row in rows1:
        user_dict = {
            'id': row['UserId'],
            'handicap': row['UserHandicap'],
            'name': row['UserFName'] + ' ' + row['UserLName']
        }
        registered_users.append(user_dict)

    con.close()
    print(registered_users)

    # Query your database to fetch registered users
    # Assuming you have fetched the data into a variable named 'registered_users'
    # Convert the data to a list of dictionaries

    # Return the registered users in JSON format
    return jsonify(registered_users)
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
        team = False
        iscontact = 0
        tid = 0
    else:
        team = True
        inaTeam = "You are in a team"
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
