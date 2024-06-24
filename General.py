from flask import Blueprint, current_app, render_template, request, session, flash, redirect, url_for, send_file, jsonify
from util import util, encrypt, validate_string, format_output, search_images, is_a_contact, get_profilepic
import sqlite3 as sql
import pandas as pd
import Encryption
import os

both = Blueprint('both', __name__)

# **********************************************************************************************
#                             FOR BOTH USERS / ADMINS                      lines: 1105-1258    *
# **********************************************************************************************
# BOTH ADMIN/USER - Shows the specific user information
@both.route('/view')
def view():
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
        # pull db info - grabs users info
        nm = session['UserName']
        con = sql.connect("UserInfoDB.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute(
            "SELECT UserName, UserFName, UserMName, UserLName, UserGender, UserDOB, UserHandicap, UserPhNum, UserEmail, UserTeamId, UserTeamYear, LoginPassword, ProfilePicture FROM UserInfo "
            "WHERE UserName = ?", (encrypt(nm),))
        data = cur.fetchall()
        df = pd.DataFrame(data,
                          columns=['UserName', 'UserFName', 'UserMName', 'UserLName', 'UserGender', 'UserDOB',
                                   'UserHandicap', 'UserPhNum', 'UserEmail', 'UserTeamId','UserTeamYear', 'LoginPassword',
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
            print(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13])
        # pull picture pathfile to html
        photo = get_profilepic()

        con.close()
        return render_template("profile_view.html", row=row, UserName=session['UserName'], photo=photo)


# BOTH ADMIN/USER - Show info to edit profile
@both.route('/editProfile', methods=['GET', 'POST'])
def edit_profile():
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
        nm = session['UserName']
        # pull db info - grabs users info
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
@both.route('/updateProfile', methods=['POST'])
def update_profile():
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
        try:
            nm = session['UserName']
            # find if user is the contact for a team
            contact, tid = is_a_contact()
            print(contact, tid)
            # request for input into db
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
            # tries to get new profile picture if one is given
            if 'picture' not in request.files:
                pass
            file = request.files['picture']
            if file.filename == '':
                pass
            # upload photo to directory
            if file:
                # ensure each photo has distinct name ie no duplicates (ex: if 2 hi.jpeg uploaded will result in users having someone else's profile pic)
                # count the number of files
                files = os.listdir(current_app.config['UPLOAD_FOLDER'])
                num_files = len(files)
                # Split the filename and extension
                name, ext = os.path.splitext(file.filename)
                # Construct the new filename with the numeric suffix
                new_filename = f"{num_files + 1}{ext}"
                # save photo to directory statics/css/uploads/_____
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename))

                # pull most recent uploaded photo
                files = [os.path.join(current_app.config['UPLOAD_FOLDER'], f) for f in os.listdir(current_app.config['UPLOAD_FOLDER'])
                         if
                         os.path.isfile(os.path.join(current_app.config['UPLOAD_FOLDER'], f))]
                if files:
                    p = max(files, key=os.path.getctime)
                    p = "../" + p
                else:
                    p = None

                # update db - insert new profile picture
                con = sql.connect('UserInfoDB.db')
                cur = con.cursor()
                cur.execute(
                    "UPDATE UserInfo SET ProfilePicture = ? WHERE UserName = ?",
                    (p, encrypt(nm)))
                con.commit()
            # update db - handicap status if not blank
            if newUserHandicap != 'Handicap':
                print("h", newUserHandicap)
                con = sql.connect('UserInfoDB.db')
                cur = con.cursor()
                cur.execute(
                    "UPDATE UserInfo SET UserHandicap = ? WHERE UserName = ?",
                    (newUserHandicap, encrypt(nm)))
                con.commit()
            # update db - gender if not blank
            if newUserGender != 'Gender':
                print("h", newUserGender)
                con = sql.connect('UserInfoDB.db')
                cur = con.cursor()
                cur.execute(
                    "UPDATE UserInfo SET UserGender = ? WHERE UserName = ?",
                    (newUserGender, encrypt(nm)))
                con.commit()
            # update db with typical info
            con = sql.connect('UserInfoDB.db')
            cur = con.cursor()
            cur.execute(
                "UPDATE UserInfo SET UserName = ?, UserFName = ?, UserMName = ?, UserLName = ?,"
                " UserDOB = ?, UserPhNum = ?, UserEmail = ?, LoginPassword = ? WHERE UserName = ?",
                (encrypt(newUserName), newUserFName, newUserMName, newUserLName, newUserDOB,
                 encrypt(newUserPhNum), encrypt(newUserEmail), encrypt(newPassword),
                 encrypt(nm)))
            con.commit()
            # update team info if user is teams contact person (1 == in contact, 0 == not contact)
            if contact == 1:
                con = sql.connect('TeamInfoDB.db')
                cur = con.cursor()
                cur.execute(
                    "UPDATE TeamInfo SET ContactFname = ?, ContactLname = ?, ContactPhNum = ?, ContactEmail = ? WHERE TeamId = ?",
                    (encrypt(newUserFName), encrypt(newUserLName), encrypt(newUserPhNum), encrypt(newUserEmail), tid,))
                con.commit()
                con = sql.connect('TeamInfoDB.db')
                cur = con.cursor()
                cur.execute(
                    "UPDATE TeamInfo SET ContactPhoto = ? WHERE TeamId = ?",
                    (p, tid,))
                con.commit()
            else:
                pass
            flash("Successfully Updated Profile")
            return render_template('result.html')
        except Exception as e:
            con.rollback()
            flash("Error Updated Profile")
            return render_template('profile_view.html')
        finally:
            con.close()


# BOTH ADMIN/USER - Search by team/member names or contact info (user output doesn't have all info)
@both.route('/searchTeamName', methods=['POST'])
def searchTeamName():
    if not session.get('logged_in'):
        return render_template('home.html')
    try:
        # receive user search input
        searchInfo = request.form.get('TeamName')

        # user search info to find the team
        with sql.connect("TeamInfoDB.db") as con:
            con.row_factory = sql.Row
            cur = con.cursor()

            cur.execute(
                "SELECT * FROM TeamInfo WHERE TeamName = ? OR SponsorName = ? OR MemberName1 = ? OR MemberName2 = ? OR "
                "MemberName3 = ? OR MemberName4 = ? OR ContactFName = ? OR ContactLName = ? OR ContactPhNum = ? OR "
                "ContactEmail = ? OR SponsorName = ?",
                (searchInfo.strip(), searchInfo.strip(), searchInfo.strip(), searchInfo.strip(), searchInfo.strip(),
                 searchInfo.strip(),
                 encrypt(searchInfo.strip()), encrypt(searchInfo.strip()), encrypt(searchInfo.strip()),
                 encrypt(searchInfo.strip()), searchInfo.strip()))

            rows = []
            result = cur.fetchall()
            for row in result:
                newRow = dict(row)
                newRow['ContactFName'] = Encryption.cipher.decrypt(newRow['ContactFName'])
                newRow['ContactLName'] = str(Encryption.cipher.decrypt(newRow['ContactLName']))
                newRow['ContactPhNum'] = str(Encryption.cipher.decrypt(newRow['ContactPhNum']))
                newRow['ContactEmail'] = str(Encryption.cipher.decrypt(newRow['ContactEmail']))
                rows.append(newRow)

            if session.get('admin'):
                return render_template("a_viewTeamSelected.html", rows=rows, UserName=session['UserName'],
                                       result=result)
            if session.get('user'):
                return render_template("u_viewTeamQuick.html", rows=rows, UserName=session['UserName'], result=result)

    except Exception as e:
        flash("Search Error")
        return render_template('dash.html')