from flask import render_template, request, session, flash, Blueprint
import sqlite3 as sql
import pandas as pd
import numpy as np
import Encryption
import datetime
import re

auth = Blueprint('auth', __name__)


@auth.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('home.html')
    #  -------------------------------- ADMIN DASH --------------------------------
    session['UserName'] = str(Encryption.cipher.decrypt(session['UserName']))
    if session.get('admin'):
        # get current year
        current_year = datetime.datetime.now().year
        # pull db info - quick team view
        con = sql.connect("TeamInfoDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT * FROM TeamInfo WHERE Year = ?', (current_year,))
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
        # pull db info - total count of needed cart rentals
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
        # pull db info - count of checked-in team members vs total team members
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
        # pull db info - display team member checkin status
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
        photo = get_profilepic()
        # ^get^ and return all information from SQL DB that needs to be shown on dash screen
        return render_template('dash.html', rows=rows, UserName=session['UserName'], i=i,
                               AllCartsNeeded=AllCartsNeeded, checkedin=checkedin, all=all, photo=photo)

    #  ----------------------------------- USER DASH  ------------------------------------
    elif session.get('user'):
        try:
            nm = session['UserName']
            # pull picture pathfile to html
            photo = get_profilepic()
            # pull db info - find if user in a team
            con = sql.connect('UserInfoDB.db')
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute(
                "SELECT UserTeamId, UserTeamLead FROM UserInfo WHERE UserName = ?",
                (encrypt(nm),))
            rowz = cur.fetchall()
            if (rowz):
                UserTeamId = rowz[0]['UserTeamId']
                UserTeamLead = rowz[0]['UserTeamLead']
            else:
                UserTeamId = None
                UserTeamLead = None
            rowzz = []
            for row in rowz:
                newRow = dict(row)
                rowzz.append(newRow)
            con.close()
            string = ','.join(str(x) for x in rowzz)
            print(string)
            word = 'None'
            # if user not in team - unset team variables
            if word in string:
                inaTeam = "You currently have no team"
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
            # if user is in team - pull team info
            else:
                team = True
                inaTeam = "Welcome team "
                number = re.findall(r'\d+', string)
                # Convert the numbers to integers
                teamid = [int(num) for num in number]
                for id in teamid:
                    tid = id
                    break
                # pull db info - pull all team info for variables
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
                    output += f" {mark} {name} \n"

                # Print the HTML output
                print(output)
                # get current year
                current_year = datetime.datetime.now().year
                # pull db info - All db info
                con = sql.connect("TeamInfoDB.db")
                con.row_factory = sql.Row
                cur = con.cursor()
                cur.execute('SELECT * FROM TeamInfo WHERE Year = ?', (current_year, ))
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
                                   photo=photo, UserTeamLead=UserTeamLead)




@auth.route('/login-signup')
def log_in():
    if not session.get('logged_in'):
        return render_template('login-signup.html')
    else:
        try:
            # session['UserName'] = str(Encryption.cipher.decrypt(session['UserName']))
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


@auth.route('/login', methods=['POST'])
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
                flash('Invalid Username or Password')
    except:
        con.rollback()
        flash("error in insert operation")
    finally:
        con.close()
        if not session['logged_in']:
            return log_in()
        else:
            return home()

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

def encrypt(txt):
    return Encryption.cipher.encrypt(bytes(txt, 'utf-8')).decode('utf-8')

@auth.route("/logout")
def logout():
    session['logged_in'] = False
    session['admin'] = False
    session['management'] = False
    session['user'] = False
    session['username'] = ""
    return home()