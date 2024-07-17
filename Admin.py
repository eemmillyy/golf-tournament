from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from util import cartCounter, encrypt, validate_string, format_output, search_images, get_profilepic, reset_cart, count_carts, total
from collections import defaultdict
from secret_keys import GOOGLE_API_KEY, GOOGLE_ACCOUNT_KEY
import sqlite3 as sql
import Encryption
import datetime
import string
import random

admin = Blueprint('admin', __name__)


# ADMIN - directs admin to dash
@admin.route('/dash')
def dash():
    if not session.get('logged_in'):
        return render_template('home.html')
    if not session.get('admin'):
        return render_template('home.html')
    # get current year
    current_year = datetime.datetime.now().year
    # get total
    current_total = total()
    # pull db info - quick team view
    con = sql.connect("TeamInfoDB.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT * FROM TeamInfo WHERE Year = ?', (current_year, ))
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
    # pull db info - total count of needed cart rentals on dash
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
    con = sql.connect("TeamInfoDB.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    # pull db info - team member checked-in status
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
    return render_template("dash.html", rows=rows, UserName=session['UserName'], i=i, AllCartsNeeded=AllCartsNeeded,
                           checkedin=checkedin, all=all, photo=photo, current_total=current_total)

# **********************************************************************************************
#                                       FOR ADMINS                         lines: 1264-2224    *
# **********************************************************************************************
# ADMIN - List all current users information
@admin.route('/adminlist')
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
            photo = get_profilepic()
            return render_template("a_adminlist-OLD.html", rows=rows, UserName=session['UserName'], photo=photo)


# ADMIN - Routes to search for users
@admin.route('/searchUserPage')
def searchUserPage():
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('admin'):
        flash('Page not found')
        return render_template('home.html')
    return render_template('a_searchUser.html')


# ADMIN - Search for users
@admin.route('/searchUser', methods=['POST'])
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
@admin.route('/teamContactsList')
def team_Contacts():
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
        if not session.get('admin'):
            flash('Page not found')
            return render_template('home.html')
        else:
            # Get current year
            current_year = datetime.datetime.now().year
            con = sql.connect("TeamInfoDB.db")
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute('SELECT TeamId, MemberName1, MemberName2, MemberName3, MemberName4, Member1Here, Member2Here, Member3Here, Member4Here, TeamName, ContactFName, ContactLName, ContactPhNum, ContactEmail, ContactPhoto FROM TeamInfo WHERE Year = ?', (current_year, ))

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
            photo = get_profilepic()
            return render_template("a_viewContact.html", rows=rows, UserName=session['UserName'], photo=photo)


# ADMIN - List all current team information
@admin.route('/allteamlist')
def admin_teamlist():
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
        if not session.get('admin'):
            flash('Page not found')
            return render_template('home.html')
        else:
            # Get current year
            current_year = datetime.datetime.now().year
            # pull info - team db info
            con = sql.connect("TeamInfoDB.db")
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute('SELECT * FROM TeamInfo WHERE Year = ?', (current_year, ))
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

            ## pull picture pathfile to html
            photo = get_profilepic()
            return render_template("a_viewTeamsAll.html", rows=rows, UserName=session['UserName'], photo=photo)


# ADMIN - Route to Search for teams by team/member names or contact info
@admin.route('/searchTeamNamePage')
def searchTeamNamePage():
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('admin'):
        flash('Page not found')
        return render_template('home.html')
    return render_template('a_searchTeamName.html')


# ADMIN - Selects one team to view in depth
@admin.route('/showOneTeam/<int:TeamId>', methods=['GET', 'POST'])
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

        result = cur.fetchall()
        rows = []

        for row in result:
            newRow = dict(row)
            newRow['ContactFName'] = str(Encryption.cipher.decrypt(row['ContactFName']))
            newRow['ContactLName'] = str(Encryption.cipher.decrypt(row['ContactLName']))
            newRow['ContactPhNum'] = str(Encryption.cipher.decrypt(row['ContactPhNum']))
            newRow['ContactEmail'] = str(Encryption.cipher.decrypt(row['ContactEmail']))
            rows.append(newRow)
        con.close()

        for row in rows:
            print(row['ContactPhoto'])

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
        session['cart2'] = False
        session['cart1'] = False
        session['cart0'] = False

        ans = count_carts(TeamId)
        print(ans)
        if ans == 2:
            session['cart2'] = True
            print("got 2")
        elif ans == 1:
             session['cart1'] = True
             print("got 1")
        else:
            session['cart0'] = True
            print("got 0")
        con.close()
        # pull picture pathfile to html
        photo = get_profilepic()
        return render_template("/a_viewTeamSelected.html", rows=rows, final=final, UserName=session['UserName'],

                               photo=photo, result=result)


# ADMIN - Dash Team Quick view
@admin.route('/showTeam/<int:TeamId>', methods=['GET', 'POST'])
def showTeam(TeamId):
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('admin'):
        flash('Page not found')
        return render_template('home.html')
    else:
        # get current year
        current_year = datetime.datetime.now().year
        # get team info from db
        con = sql.connect('TeamInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM TeamInfo WHERE TeamId = ? AND Year = ?", (TeamId, current_year))
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
        print(rows)

        return render_template("/a_viewTeamQuick.html", rows=rows)


# ADMIN - View users
@admin.route('/showUser')
def showUser():
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('admin'):
        flash('Page not found')
        return render_template('home.html')
    else:
        # Get current year
        year = datetime.datetime.now().year
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
        photo = get_profilepic()
        return render_template("/a_viewUser.html", rows=rows, UserName=session['UserName'], year=year, photo=photo)


# ADMIN - Directs admin to team sign up page
@admin.route('/adminmaketeam')
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
        photo = get_profilepic()
    return render_template('a_adminteamsignup.html', UserName=session['UserName'], rows=rows, photo=photo)


# ADMIN - sign up teams
@admin.route('/adminteamsignup', methods=['POST', 'GET'])
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
                if m1info != "Name1":
                    word = m1info.split(',')
                    m1id = word[0].strip()
                    m1hc = word[1]
                    mn1 = word[2].strip()
                    cfn = word[3].strip()
                    cln = word[4].strip()
                    cpn = word[5].strip()
                    ce = word[6].strip()
                    cp = word[7].strip()
                    memberCount += 1
                    print(m1id)
                    print(m1hc)
                    print(mn1)
                    print(cfn)
                    print(cln)
                    print(cpn)
                    print(ce)
                    print(cp)
                else:
                    # USER NEEDS ID HERE
                    mn1 = request.form.get('MemberFullName1')
                    ce = request.form.get('MemberEmail1')
                    cpn = request.form.get('MemberPhone1')
                    m1hc = int(request.form.get('Member1Handicap'))
                    cp = "../static/css/uploads/default.jpeg"
                    if len(mn1) > 1:
                        cfn = mn1[0].strip()  # Get the first element
                        cln = mn1[-1].strip()  # Get the last element
                        print(cfn)
                        print(cln)

                m2info = request.form['MemberName2']
                word = m2info.split(',')
                if m2info != "Name2":
                    if len(word) >= 3:
                        m2id = word[0].strip()
                        m2hc = word[1]
                        mn2 = word[2].strip()
                        m2e = word[8].strip()
                        memberCount += 1
                else:
                    # USER NEEDS ID HERE
                    mn2 = request.form.get('MemberFullName2')
                    m2e = request.form.get('MemberEmail2')
                    m2hc = int(request.form.get('Member2Handicap'))

                m3info = request.form['MemberName3']
                word = m3info.split(',')
                if m3info != "Name3":
                    if len(word) >= 3:
                        m3id = word[0].strip()
                        m3hc = word[1]
                        mn3 = word[2].strip()
                        memberCount += 1
                else:
                    # USER NEEDS ID HERE
                    mn3 = request.form.get('MemberFullName3')
                    m3e = request.form.get('MemberEmail3')
                    m3hc = int(request.form.get('Member3Handicap'))

                m4info = request.form['MemberName4']
                word = m4info.split(',')
                if m4info != "Name4":
                    if len(word) >= 3:
                        m4id = word[0].strip()
                        m4hc = word[1]
                        mn4 = word[2].strip()
                        memberCount += 1
                else:
                    # USER NEEDS ID HERE
                    mn4 = request.form.get('MemberFullName4')
                    m4e = request.form.get('MemberEmail4')
                    m4hc = int(request.form.get('Member4Handicap'))

                # search google for logo of sponsor
                query = request.form['SponsorName']
                query += ' logo'
                api_key = GOOGLE_API_KEY
                cx = GOOGLE_ACCOUNT_KEY
                image_urls = search_images(query, api_key, cx)
                print(image_urls)
                if image_urls:
                 sponpic = image_urls[1]
                else:
                    sponpic = None
                print(sponpic)
                # get current year
                year = datetime.datetime.now().year
                # get start hole
                con = sql.connect('TeamInfoDB.db')
                con.row_factory = sql.Row
                cur = con.cursor()
                cur.execute("SELECT StartHole FROM TeamInfo WHERE Year = ?", (year, ))  # get list of all holes
                data = cur.fetchall()

                con.close()
                start_holes = [row[0] for row in data]
                print(start_holes)
                for i in range(1, 36):
                    for i in range(1, 19):
                        if i not in start_holes:
                            print('First available hole:', i)
                            break
                    if i >= 18:  # If i reaches 18, reset it to 0
                        missing_numbers = [i for i in range(1, 19) if start_holes.count(i) != 2]
                        print(missing_numbers)
                        sorted_start_holes = sorted(missing_numbers)
                        print(sorted_start_holes)
                        first_value = sorted_start_holes[0]
                        print(first_value)
                        i = first_value
                        break
                sh = i
                # Generates Join Code
                code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

                # Get current year for team
                #year = 2023
                year = datetime.datetime.now().year

                if not validate_string(tnm):
                    valid_input = False
                    err_string = err_string + "<br>You cannot enter in an empty team name"

                if not validate_string(cfn):
                    valid_input = False
                    err_string = err_string + "<br>You cannot enter in an empty contact first name."

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
                            "INSERT INTO TeamInfo (TeamName, SponsorName, SponsorPhoto, NeedCart, MemberName1, MemberName2,"
                            " MemberName3, MemberName4, Member1ID, Member2ID, Member3ID, Member4ID, Member1Handicap,"
                            " Member2Handicap, Member3Handicap, Member4Handicap, StartHole, Member1Here, Member2Here,"
                            " Member3Here, Member4Here, ContactFName, ContactLName, ContactPhNum, ContactEmail, ContactPhoto, JoinCode, MemberCount, Year) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            (tnm, snm, sponpic, nc, mn1, mn2, mn3, mn4, m1id, m2id, m3id, m4id, m1hc, m2hc,
                             m3hc, m4hc, sh, "✘", "✘", "✘", "✘", encrypt(cfn), encrypt(cln), encrypt(cpn), encrypt(ce), cp,
                             code, memberCount, year))

                        con.commit()

                with sql.connect("TeamInfoDB.db") as con2:
                    cur2 = con2.cursor()
                    cur2.execute("SELECT TeamId FROM TeamInfo WHERE TeamId = ?", (cur.lastrowid,))
                    id = cur2.fetchone()
                    cur2.execute("SELECT Year FROM TeamInfo WHERE TeamId = ?", (cur.lastrowid,))
                    cur_year = cur2.fetchone()

                    con2.commit()

                with sql.connect("UserInfoDB.db") as con3:
                    cur3 = con3.cursor()
                    cur3.execute("UPDATE UserInfo SET UserTeamId = ?,  UserTeamYear = ? WHERE UserId IN (?,?,?,?)",
                                 (id[0], cur_year[0], m1id, m2id, m3id, m4id))

                    con3.commit()
                    con3.close()
                    con2.close()

                    msg = "Team Added successfully"

            except:
                con.rollback()
            finally:
                con.close()
                return render_template("result.html", msg=msg)
        else:
            flash('Page not found')
            return render_template('a_viewTeamsAll.html')


# ADMIN - directs admin to check in page
@admin.route('/admpre_checkin/<int:TeamId>', methods=['GET', 'POST'])
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
        photo = get_profilepic()
        return render_template("a_admincheckin.html", rows=rows, final=final, UserName=session['UserName'], photo=photo)


# ADMIN - checkin: Check off when users arrive and assign cart(s)
@admin.route('/admincheckin/<int:TeamId>', methods=['POST'])
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


# ADMIN - Update teams
@admin.route('/updateTeam/<int:TeamId>', methods=['POST'])
def updateTeamForm(TeamId):
    if not session.get('logged_in'):
        return render_template('home.html')

    elif not session.get('admin') and UserTeamLead != 1:
        flash('Page not found')
        return render_template('home.html')
    try:
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
        mn1_custom_name = request.form.get('Member1CustomName', '')  # Custom name input
        mn1_custom_email = request.form.get('Member1CustomEmail', '')  # Custom email input

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
        # Handle custom member input for Member 1
        if mn1_custom_name and mn1_custom_email:
            # Insert custom member into UserInfo table
            cur.execute("""
                        INSERT INTO UserInfo (UserName, UserEmail, UserTeamId) 
                        VALUES (?, ?, ?)""",
                        (mn1_custom_name, mn1_custom_email, TeamId))
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
        return render_template('a_viewTeamSelected.html')
    finally:
        con3.close()
        con.close()
        conNew.close()


# ADMIN - directs admin to delete team
@admin.route('/a_deleteteam/<int:TeamId>', methods=['GET', 'POST'])
def a_deleteteam(TeamId):
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

    elif not session.get('admin') and UserTeamLead != 1:
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
        print("final second", final)
        con.close()
        # pull picture pathfile to html
        photo = get_profilepic()
        session['Delete'] = TeamId
        return render_template("a_DeleteTeam.html", rows=rows, final=final, UserName=session['UserName'], photo=photo,
                               UserTeamLead=UserTeamLead)


# ADMIN - Delete a team
@admin.route('/a_DeleteTeam', methods=['POST'])
def a_DeleteTeam():
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

    elif not session.get('admin') and UserTeamLead != 1:

        flash('Page not found')
        return render_template('home.html')

    teamId = session['Delete']
    session['Delete'] = ""

    try:
        con2 = sql.connect('UserInfoDB.db')
        cur2 = con2.cursor()
        cur2.execute("UPDATE UserInfo SET UserTeamId = ?, UserTeamLead = ? WHERE UserTeamId = ? ",
                     (None, False, teamId))
        con2.commit()
        con2.close()

        con = sql.connect('TeamInfoDB.db')
        cur = con.cursor()
        cur.execute("DELETE FROM TeamInfo WHERE TeamId = ?", (teamId,))
        con.commit()
        flash("Successfully Delete Team")

        con3 = sql.connect('UserInfoDB.db')
        cur3 = con3.cursor()
        cur3.execute("DELETE FROM UserInfo WHERE UserName IS NULL ")
        con3.commit()
        con3.close()

        return render_template('result.html')

    except Exception as e:
        con.rollback()
        flash("Error")
        return render_template('a_DeleteTeam.html')
    finally:
        con.close()


# ADMIN - View Teams Archive
@admin.route('/showArchive')
def showArchive():
    if not session.get('logged_in'):
        return render_template('home.html')
    elif not session.get('admin'):
        flash('Page not found')
        return render_template('home.html')
    else:
        con = sql.connect('TeamInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT Year, TeamId, TeamName, MemberName1, MemberName2, MemberName3, MemberName4 FROM TeamInfo")
        teams_by_year = defaultdict(list)
        rows1 = cur.fetchall()
        rowz = []
        team_info = []
        for row in rows1:
            year = row['Year']
            info = dict(row)
            team_info.append(info)
            teams_by_year[year].append(team_info)
            newRow = dict(row)
            rowz.append(newRow)
        print(teams_by_year)
        sorted_teams = sorted(teams_by_year.items())
        print("lllllllll ", sorted_teams)
        print(team_info)
        con.close()

        con = sql.connect('TeamInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM TeamInfo")

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
        photo = get_profilepic()
        return render_template("/a_teamArchive.html", rows=rows, sorted_teams=sorted_teams, UserName=session['UserName'], photo=photo)


# ADMIN - Revive a team from Archive
@admin.route('/a_ReviveTeam/<int:TeamId>', methods=['GET', 'POST'])
def a_ReviveTeam(TeamId):
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
        rowz = []
        for row in rows1:
            newRow = dict(row)
            newRow['ContactFName'] = str(Encryption.cipher.decrypt(row['ContactFName']))
            newRow['ContactLName'] = str(Encryption.cipher.decrypt(row['ContactLName']))
            newRow['ContactPhNum'] = str(Encryption.cipher.decrypt(row['ContactPhNum']))
            newRow['ContactEmail'] = str(Encryption.cipher.decrypt(row['ContactEmail']))
            rowz.append(newRow)
        con.close()
        m2id, m2hc, mn2, m2h = None, None, None, None
        m3id, m3hc, mn3, m3h = None, None, None, None
        m4id, m4hc, mn4, m4h = None, None, None, None
        tnm_list = [d['TeamName'] for d in rowz]
        tnm = str(tnm_list[0])
        mc_list = [d['MemberCount'] for d in rowz]
        mc = int(mc_list[0])
        snm_list = [d['SponsorName'] for d in rowz]
        snm = str(snm_list[0])
        sponpic_list = [d['SponsorPhoto'] for d in rowz]
        sponpic = str(sponpic_list[0])
        nc_list = [d['NeedCart'] for d in rowz]
        nc = int(nc_list[0])
        mn1_list = [d['MemberName1'] for d in rowz]
        mn1 = str(mn1_list[0])
        m1id_list = [d['Member1ID'] for d in rowz]
        m1id = int(m1id_list[0])
        m1hc_list = [d['Member1Handicap'] for d in rowz]
        m1hc = str(m1hc_list[0])
        m1h_list = [d['Member1Here'] for d in rowz]
        m1h = str(m1h_list[0])
        if mc >= 2:
            mn2_list = [d['MemberName2'] for d in rowz]
            mn2 = str(mn2_list[0])
            m2id_list = [d['Member2ID'] for d in rowz]
            m2id = int(m2id_list[0])
            m2hc_list = [d['Member2Handicap'] for d in rowz]
            m2hc = str(m2hc_list[0])
            m2h_list = [d['Member2Here'] for d in rowz]
            m2h = str(m2h_list[0])
        if mc >= 3:
            mn3_list = [d['MemberName3'] for d in rowz]
            mn3 = str(mn3_list[0])
            m3id_list = [d['Member3ID'] for d in rowz]
            m3id = int(m3id_list[0])
            m3hc_list = [d['Member3Handicap'] for d in rowz]
            m3hc = str(m3hc_list[0])
            m3h_list = [d['Member3Here'] for d in rowz]
            m3h = str(m3h_list[0])
        if mc == 4:
            mn4_list = [d['MemberName4'] for d in rowz]
            mn4 = str(mn4_list[0])
            m4id_list = [d['Member4ID'] for d in rowz]
            m4id = int(m4id_list[0])
            m4hc_list = [d['Member4Handicap'] for d in rowz]
            m4hc = str(m4hc_list[0])
            m4h_list = [d['Member4Here'] for d in rowz]
            m4h = str(m4h_list[0])
        cfn_list = [d['ContactFName'] for d in rowz]
        cfn = str(cfn_list[0])
        cln_list = [d['ContactLName'] for d in rowz]
        cln = str(cln_list[0])
        cpn_list = [d['ContactPhNum'] for d in rowz]
        cpn = str(cpn_list[0])
        ce_list = [d['ContactEmail'] for d in rowz]
        ce = str(ce_list[0])
        pic_list = [d['ContactPhoto'] for d in rowz]
        pic = str(pic_list[0])
        code_list = [d['JoinCode'] for d in rowz]
        code = str(code_list[0])
        year = datetime.datetime.now().year
        # get start hole
        con = sql.connect('TeamInfoDB.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT StartHole FROM TeamInfo WHERE Year = ?", (year, ))  # get list of all holes
        data = cur.fetchall()

        con.close()
        start_holes = [row[0] for row in data]
        print(start_holes)
        for i in range(1, 36):
            for i in range(1, 19):
                if i not in start_holes:
                    print('First available hole:', i)
                    break
            if i >= 18:  # If i reaches 18, reset it to 0
                missing_numbers = [i for i in range(1, 19) if start_holes.count(i) != 2]
                print(missing_numbers)
                sorted_start_holes = sorted(missing_numbers)
                print(sorted_start_holes)
                first_value = sorted_start_holes[0]
                print(first_value)
                i = first_value
                break
        sh = i

        with sql.connect("TeamInfoDB.db") as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO TeamInfo (TeamName, SponsorName, SponsorPhoto, NeedCart, MemberName1, Member1ID, Member1Handicap,"
                "MemberName2, Member2ID, Member2Handicap, MemberName3, Member3ID, Member3Handicap, MemberName4, Member4ID, Member4Handicap,"
                " StartHole, Member1Here, Member2Here, Member3Here, Member4Here, ContactFName, ContactLName, ContactPhNum, ContactEmail,"
                " ContactPhoto, JoinCode, MemberCount, Year) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (tnm, snm, sponpic, nc, mn1, m1id, m1hc, mn2, m2id, m2hc, mn3, m3id, m3hc, mn4, m4id, m4hc, sh, m1h, m2h, m3h, m4h, encrypt(cfn), encrypt(cln),
                 encrypt(cpn), encrypt(ce), pic, code, mc, year))
            con.commit()
        # pull info - team db info
        con = sql.connect("TeamInfoDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT * FROM TeamInfo WHERE Year = ?', (year, ))
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
        photo = get_profilepic()
    return render_template("a_viewTeamsAll.html", rows=rows, UserName=session['UserName'], photo=photo)
