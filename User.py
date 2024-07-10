from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from util import encrypt, validate_string, format_output, search_images, get_profilepic
from secret_keys import GOOGLE_API_KEY, GOOGLE_ACCOUNT_KEY
import sqlite3 as sql
import Encryption
import datetime
import re
import string
import random


user = Blueprint('user', __name__)

@user.route('/userdash')
def userdash():
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
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
            # if no team - unset team variables
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
            # if user in team - set team variables
            else:
                team = True
                inaTeam = "You are in a team"
                number = re.findall(r'\d+', string)
                # Convert the numbers to integers
                teamid = [int(num) for num in number]
                for id in teamid:
                    tid = id
                    break
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
                # get current year
                current_year = datetime.datetime.now().year
                # pull db info - All team info
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
                                   memeberList=memeberList, cartinfo=cartinfo, list_size=list_size, amount=amount,
                                   UserTeamId=UserTeamId, photo=photo, UserTeamLead=UserTeamLead)


@user.route('/signup')
def sign_up():
    if not session.get('logged_in'):
        return render_template('signup.html')
    else:
        try:
            session['UserName'] = str(Encryption.cipher.decrypt(session['UserName']))
        finally:
            return render_template('dashboard-OLD.html', UserName=session['UserName'])

# USER - Add new user to SQL table - USERINFO  DB
@user.route('/adduser', methods=['POST', 'GET'])
def adduser():
    valid_input = True
    err_string = " "
    if request.method == 'POST':
        try:
            # collecting user input data
            nm = request.form['UserName']
            fnm = request.form['UserFName']
            mi = request.form['UserMName']
            lnm = request.form['UserLName']
            gen = request.form['UserGender']
            dob = request.form['UserDOB']
            uhc = request.form['UserHandicap']
            print("l", uhc)
            pn = request.form['UserPhNum']
            email = request.form['UserEmail']
            if request.form.get('RoleLevel'):
                lvl = 0
            else:
                lvl = 1
            pwd = request.form['LoginPassword']

            # input validation
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

            # if no errors save to db
            if valid_input:
                with sql.connect("UserInfoDB.db") as con:
                    cur = con.cursor()
                    cur.execute(
                        "INSERT INTO UserInfo (UserName, UserFName, UserMName, UserLName, UserGender, UserDOB, UserHandicap, UserPhNum, UserEmail, RoleLevel, LoginPassword, ProfilePicture, UserTeamLead) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (encrypt(nm), fnm, mi, lnm, gen, dob, uhc, encrypt(pn), encrypt(email), lvl, encrypt(pwd),
                         'static/css/uploads/default.jpeg', False))
                    con.commit()
                    msg = "Record successfully added. You may now login"
        except:
            con.rollback()
        finally:
            con.close()
            return render_template("login-signup.html", msg=msg)
    else:
        flash('Page not found')
        return render_template('home.html')


# USER - directs users to team sign up page
@user.route('/usermakesteam')
def userteamsignups():
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
        # pull picture pathfile to html
        photo = get_profilepic()
        # pull db info - find if teams in db, if so count how many
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
        # if 1 or more teams in db - get unique id
        if i != 0:
            con = sql.connect('TeamInfoDB.db')
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute(
                "SELECT TeamId FROM TeamInfo WHERE TeamId =(SELECT max(TeamId) FROM TeamInfo)")  # get last team
            num = cur.fetchall()
            val = num[0]
            lastTeam = val['TeamId']
            # if 36 teams found in db - no more teams
            if lastTeam >= 36:
                return render_template('u_teamsignupfull.html', UserName=session['UserName'], photo=photo)
        # pull db info - check if a team id is saved to user
        nm = session['UserName']
        con = sql.connect('UserInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute(
            "SELECT UserTeamId, UserTeamLead FROM UserInfo WHERE UserName = ?",
            (encrypt(nm),))
        rows1 = cur.fetchall()
        rows = []
        for row in rows1:
            newRow = dict(row)
            rows.append(newRow)

        if rows1:
            UserTeamId = rows[0]['UserTeamId']
            UserTeamLead = rows[0]['UserTeamLead']
        else:
            UserTeamId = None
            UserTeamLead = None

        print("here", rows)
        con.close()
        string = ','.join(str(x) for x in rows)
        print(string)
        word = 'None'
        if word not in string:
            return render_template('u_teamsignupfull.html', UserName=session['UserName'], photo=photo,
                                   UserTeamLead=UserTeamLead)
        # else pull db info - get user info as team contact info
        else:
            nm = session['UserName']
            con = sql.connect('UserInfoDB.db')
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute(
                "SELECT UserId, UserFName, UserLName, UserHandicap, UserPhNum, UserEmail FROM UserInfo WHERE UserName = ?",
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
            return render_template('u_userteamsignup.html', UserName=session['UserName'], rows=rows, photo=photo)


# USER - allow sign up team
@user.route('/userteamsignup', methods=['POST', 'GET'])
def user_teamSignup():
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
        nm = session['UserName']
        valid_input = True
        err_string = " "
        if request.method == 'POST':
            try:
                # request for team info
                tnm = request.form['TeamName']
                snm = request.form['SponsorName']
                nc = request.form['NeedCart']
                m1info = request.form['MemberName1']
                word = m1info.split(',')
                m1id = word[0].strip()
                m1hc = word[1].strip()
                mn1 = word[2].strip() + ' ' + word[3].strip()
                cfn = word[2].strip()
                cln = word[3].strip()
                cpn = word[4].strip()
                ce = word[5].strip()
                pic = word[6].strip()
                print(m1id)
                print(m1hc)
                print(mn1)
                print(cfn)
                print(cln)
                print(cpn)
                print(ce)
                print(pic)
                # search google for logo of sponsor
                query = request.form['SponsorName']
                query += ' logo'
                api_key = GOOGLE_API_KEY
                cx = GOOGLE_ACCOUNT_KEY
                image_urls = search_images(query, api_key, cx)
                print(image_urls)
                if image_urls:
                    spic = image_urls[1]
                else:
                    spic = None
                print(spic)
                # get current year
                year = datetime.datetime.now().year
                # pull db info - get first available start hole
                con = sql.connect('TeamInfoDB.db')
                con.row_factory = sql.Row
                cur = con.cursor()
                cur.execute("SELECT StartHole FROM TeamInfo WHERE Year = ?", (year, ))
                data = cur.fetchall()
                con.close()
                start_holes = [row[0] for row in data]
                print(start_holes)
                # for 36 teams (only 18 holes)
                for i in range(1, 36):
                    # numerically look through hole 1-18 for missing value
                    for i in range(1, 19):
                        if i not in start_holes:
                            print('First available hole:', i)
                            break
                    # if hole 18 reached, begin searching for first available duplicate
                    if i >= 18:
                        missing_numbers = [i for i in range(1, 19) if start_holes.count(i) != 2]
                        print(missing_numbers)
                        sorted_start_holes = sorted(missing_numbers)
                        print(sorted_start_holes)
                        first_value = sorted_start_holes[0]
                        print(first_value)
                        i = first_value
                        break
                sh = i
                # generate random team-id join link
                code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                print(code)
                # Generate current year for team
                year = datetime.datetime.now().year

                # input validation
                if not validate_string(tnm):
                    valid_input = False
                    err_string = err_string + "<br>You cannot enter in an empty team name"

                if (int(nc) <= -1) or (int(nc) >= 3):
                    valid_input = False
                    err_string = err_string + "<br>You can not enter in an empty cart."

                    if not valid_input:
                        msg = err_string
                        return render_template("result.html", msg=format_output(err_string))

                # if valid input add to db
                if valid_input:
                    with sql.connect("TeamInfoDB.db") as con:
                        cur = con.cursor()
                        cur.execute(
                            "INSERT INTO TeamInfo (TeamName, SponsorName, SponsorPhoto, NeedCart, MemberName1, Member1ID, Member1Handicap, StartHole, Member1Here, Member2Here, Member3Here, Member4Here, ContactFName, ContactLName, ContactPhNum, ContactEmail, ContactPhoto, JoinCode, MemberCount, Year) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            (tnm, snm, spic, nc, mn1, m1id, m1hc, sh, "✘", "✘", "✘", "✘", encrypt(cfn), encrypt(cln),
                             encrypt(cpn), encrypt(ce), pic, code, 1, year))
                        con.commit()

                    with sql.connect("UserInfoDB.db") as con2:
                        cur2 = con2.cursor()
                        cur2.execute("UPDATE UserInfo SET UserTeamLead = ? WHERE UserName = ?", (True, encrypt(nm)))
                        con2.commit()
                    con2.close()
            except:
                con.rollback()
            finally:
                con.close()
                return redirect('joincode')
        else:
            flash('Page not found')
            return render_template('userdash.html')


# USER - Routes user to send team join code
@user.route('/joincode', methods=['POST', 'GET'])
def joincode():
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
        nm = session['UserName']
        # pull db info - get most recently created team
        con = sql.connect('TeamInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute(
            "SELECT TeamId FROM TeamInfo WHERE TeamId =(SELECT max(TeamId) FROM TeamInfo)")
        num = cur.fetchall()
        val = num[0]
        lastTeam = val['TeamId']
        con.close()
        # Generate current year for team
        year = datetime.datetime.now().year
        # update db info - pull team-id to user db
        with sql.connect("UserInfoDB.db") as con:
            cur = con.cursor()
            cur.execute("UPDATE UserInfo SET UserTeamId = ?, UserTeamYear = ? WHERE UserName = ?", (lastTeam, year, encrypt(nm)))
            con.commit()
        con.close()
        # pull db info - check team-id in user db
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
        # pull db info - get team joincode
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
        photo = get_profilepic()
        return render_template('u_teamjoin.html', UserName=session['UserName'], rows=rows, photo=photo)


# USER allows users to send team join code
@user.route('/teamjoin', methods=['POST', 'GET'])
def user_teamjoin():
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
        # pull picture pathfile to html
        photo = get_profilepic()
        msg = "cool all done"
    return render_template('result.html', UserName=session['UserName'], msg=msg, photo=photo)


# USER - directs users to join a team
@user.route('/usersjoin')
def usersjoin():
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('user'):
        flash('Page not found')
        return render_template('home.html')
    # pull picture pathfile to html
    photo = get_profilepic()
    return render_template('u_usersjoin.html', UserName=session['UserName'], photo=photo)


# USER - ask to add user to team
@user.route('/userjoin', methods=['POST'])
def userjoin():
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('user'):
        flash('Page not found')
        return render_template('home.html')
    try:
        # pull picture pathfile to html
        photo = get_profilepic()
        # request join code
        info = request.form.get('JoinCode')
        session['JoinCode'] = info
        print(info)
        # pull db info - pull team from joincode
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
        photo = get_profilepic()
        return render_template('u_usersjoin.html', photo=photo)


# USER - add user to team
@user.route('/userteamjoin', methods=['POST', 'GET'])
def user_teamJoin():
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
        nm = session['UserName']
        # pull picture pathfile to html
        photo = get_profilepic()
        ident = session['UserId']
        valid_input = True
        err_string = " "
        print("herenow")
        # join_code = session.pop('JoinCode', None)
        join_code = session['JoinCode']
        session['JoinCode'] = ""

        # pull db info - grab member-count of team with corresponding join-code
        con = sql.connect("TeamInfoDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM TeamInfo WHERE JoinCode = ?", (join_code,))
        inc = cur.fetchall()
        pnt = inc[0]
        memc = pnt['MemberCount']
        tid = pnt['TeamId']
        print(memc)
        # pull db info - get user info for team member info
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

        # if 1 member in team - add team member2
        if memc == 1:
            cur.execute(
                "UPDATE TeamInfo SET MemberName2 = ?, Member2ID = ?, Member2Handicap = ?, MemberCount = ? WHERE TeamId = ?",
                (fullname, memid, handi, memc + 1, tid))
            con.commit()
            member_added = True
        # if 2 members in team - add team member3
        elif memc == 2:
            cur.execute(
                "UPDATE TeamInfo SET MemberName3 = ?, Member3ID = ?, Member3Handicap = ?, MemberCount = ? WHERE TeamId = ?",
                (fullname, memid, handi, memc + 1, tid))
            con.commit()
            member_added = True
        # if 3 members in team - add team member4
        elif memc == 3:
            cur.execute(
                "UPDATE TeamInfo SET MemberName4 = ?, Member4ID = ?, Member4Handicap = ?, MemberCount = ? WHERE TeamId = ?",
                (fullname, memid, handi, memc + 1, tid))
            con.commit()
            member_added = True
        # if 4 members in team - team is full
        elif memc >= 4:
            msg = "This Team is Currenly Full"
            con2.close()
            con.close()
            return render_template('result.html', UserName=session['UserName'], msg=msg, photo=photo)

        # if new member added - update team id for user
        if member_added:
            # Generate current year for team
            year = datetime.datetime.now().year
            cur2.execute("UPDATE UserInfo SET UserTeamId = ?, UserTeamYear = ? WHERE UserId = ?", (tid, year, memid))
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


# User - Edit teams
@user.route('/editTeam/<int:TeamId>', methods=['GET', 'POST'])
def edit_TeamForm(TeamId):
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

    if not session.get('logged_in'):
        return render_template('home.html')

    elif UserTeamLead != 1:
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
            # newRow['UserPhNum'] = str(Encryption.cipher.decrypt(row['UserPhNum']))
            newRow['UserEmail'] = str(Encryption.cipher.decrypt(row['UserEmail']))
            rows1.append(newRow)
        con.close()
        # pull picture pathfile to html
        photo = get_profilepic()

        return render_template("a_updateTeam.html", rows=rows, final=final, UserName=session['UserName'], rows1=rows1,
                               photo=photo, UserTeamLead=UserTeamLead)


# USER - list all current team information
@user.route('/u_allteamlist')
def user_teamlist():
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
        if not session.get('user'):
            flash('Page not found')
            return render_template('home.html')
        else:
            nm = session['UserName']
            # pull db info - all teams and their info
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

            # if no team - unset team variables
            if word in string:
                team = None
                print('no team found')
                team_names = None
                memeberList = None
                sponsor = None
                sponsorpic = None

            # if user in team - set team variables
            else:
                team = True
                print("You are in a team")
                number = re.findall(r'\d+', string)
                # Convert the numbers to integers
                teamid = [int(num) for num in number]
                for id in teamid:
                    tid = id
                    break
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
                sponsorpic = [d['SponsorPhoto'] for d in rowzz]
                sponsorpic = sponsorpic[0]
                sponsor = [d['SponsorName'] for d in rowzz]
                sponsor = sponsor[0]

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
                memeberList = [item for item in memebers if item is not None]
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
                # pull db info - All team info
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

            return render_template("u_viewTeamAll.html", rows=rows, UserName=nm, photo=photo, team=team,
                                   team_names=team_names, memeberList=memeberList, sponsor=sponsor,
                                   sponsorpic=sponsorpic, UserTeamLead=UserTeamLead)


# USER - team quickview on dashboard
@user.route('/u_showTeam/<int:TeamId>', methods=['GET'])
def user_showTeam(TeamId):
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('user'):
        flash('Page not found')
        return render_template('home.html')
    else:
        # pull db info - all teams and their info
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
        return render_template("/u_viewTeamQuick.html", rows=rows)


@user.route('/uc_editTeam')
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
        cur.execute('SELECT UserTeamId, UserTeamLead FROM UserInfo WHERE UserName = ?', (encrypt(nm),))

        result = cur.fetchone()
        con.close()

        tid, tcpt = result

        con = sql.connect('TeamInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT * FROM TeamInfo WHERE TeamId =?', (tid,))
        session['Delete'] = tid

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


@user.route('/uc_deleteMember', methods=['POST', 'GET'])
def cap_deleteMember():
    if 'UserName' not in session:
        return redirect(url_for('auth.log_in'))

    nm = session['UserName']
    con = sql.connect('UserInfoDB.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute(
        "SELECT UserTeamId, UserTeamLead FROM UserInfo WHERE UserName = ?",
        (encrypt(nm),))
    rowz = cur.fetchall()

    if rowz:
        UserTeamLead = rowz[0]['UserTeamLead']
    else:
        UserTeamLead = None

    rowzz = []
    for row in rowz:
        newRow = dict(row)
        rowzz.append(newRow)
    con.close()

    if not session.get('logged_in'):
        return render_template('home.html')

    elif not session.get('admin') and UserTeamLead != 1:
        flash('Page not found')
        return render_template('home.html')

    print("hey working......")
    con = sql.connect('TeamInfoDB.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute(
        "SELECT MemberName2, MemberName3, MemberName4 FROM TeamInfo WHERE TeamId = ?",
        (UserTeamLead,))
    rowz = cur.fetchall()

    if rowz:
        MemberName2 = rowz[0]['MemberName2']
        MemberName3 = rowz[0]['MemberName3']
        MemberName4 = rowz[0]['MemberName4']
    else:
        MemberName2 = None
        MemberName3 = None
        MemberName4 = None

    rowzz = []
    for row in rowz:
        newRow = dict(row)
        rowzz.append(newRow)
    con.close()
    print("ll ", MemberName2)
    print("ll ", MemberName3)
    print("llz ", MemberName4)

    deleteMembers = request.form.getlist('members')
    if deleteMembers:
        with sql.connect('TeamInfoDB.db') as con:
            cur = con.cursor()
            for member in deleteMembers:
                print("p ", member)
                if member == MemberName2:
                    print("jiiiiiii")
                    cur.execute(
                        "UPDATE TeamInfo SET "
                        "MemberName2 = MemberName3, "
                        "Member2Handicap = Member3Handicap, "
                        "Member2ID = Member3ID, "
                        "MemberName3 = MemberName4, "
                        "Member3ID = Member4ID, "
                        "Member3Handicap = Member4Handicap, "
                        "MemberName4 = NULL, "
                        "Member4ID = NULL, "
                        "Member4Handicap = NULL "
                        "WHERE MemberName2 = ?",
                        (member,))
                elif member == MemberName3:
                    cur.execute(
                        "UPDATE TeamInfo SET "
                        "MemberName3 = MemberName4, "
                        "Member3ID = Member4ID, "
                        "Member3Handicap = Member4Handicap, "
                        "MemberName4 = NULL, "
                        "Member4ID = NULL, "
                        "Member4Handicap = NULL "
                        "WHERE MemberName3 = ?",
                        (member,))
                elif member == MemberName4:
                    cur.execute(
                        "UPDATE TeamInfo SET "
                        "MemberName4 = NULL, "
                        "Member4ID = NULL, "
                        "Member4Handicap = NULL "
                        "WHERE MemberName4 = ?",
                        (member,))

                # Delete from UserInfo table based on last name
                splitName = member.split()
                con3 = sql.connect('UserInfoDB.db')
                cur3 = con3.cursor()
                cur3.execute("DELETE FROM UserInfo WHERE UserLName = ? AND UserName IS NULL", (splitName[1],))

            # Update MemberCount in TeamInfo table
            cur.execute("UPDATE TeamInfo SET MemberCount = MemberCount - ?", (len(deleteMembers),))
            con.commit()

    try:
        return render_template('result.html', rows=rowz)

    finally:
        con.close()
        con3.close()


@user.route('/uc_addMember', methods=['POST', 'GET'])
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

        if memc == 1:
            cur.execute(
                "UPDATE TeamInfo SET MemberName2 = ?, Member2ID = ?, Member2Handicap = ?, MemberCount = ? WHERE TeamId = ?",
                (fullname, memID, mHandi, memc + 1, tid))
            con.commit()
            con.close()
            member_added = True

        elif memc == 2:
            cur.execute(
                "UPDATE TeamInfo SET MemberName3 = ?, Member3ID = ?, Member3Handicap = ?, MemberCount = ? WHERE TeamId = ?",
                (fullname, memID, mHandi, memc + 1, tid))
            con.commit()
            con.close()
            member_added = True
        elif memc == 3:
            cur.execute(
                "UPDATE TeamInfo SET MemberName4 = ?, Member4ID = ?, Member4Handicap = ?, MemberCount = ? WHERE TeamId = ?",
                (fullname, memID, mHandi, memc + 1, tid))
            con.commit()
            con.close()
            member_added = True
        elif memc >= 4:
            msg = "This Team is Currently Full"
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
            msg = "Error in team addition"
            con.close()

            return render_template('result.html', UserName=session['UserName'], msg=msg)
