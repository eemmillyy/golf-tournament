"""
Name:Emily Skipper
About this project: SQL database to store user information
Assumptions:NA
All work below was performed by Emily Skipper
"""
import contextlib
import sqlite3
import Encryption

# ******************************************************
# Connect to SQLITE Database - USER INFORMATION        *
# ******************************************************
conn = sqlite3.connect('UserInfoDB.db')
cur = conn.cursor()
try:
    conn.execute('''DROP TABLE UserInfo''')
    conn.commit()
    print('UserInfo table dropped.')
except:
    print('UserInfo table does not exist')

cur.execute('''CREATE TABLE UserInfo(
UserId INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
UserName TEXT,
UserFName TEXT NOT NULL,
UserMName TEXT,
UserLName TEXT NOT NULL,
UserGender BOOLEAN,
UserDOB INTEGER,
UserHandicap BOOLEAN,
UserPhNum TEXT,
UserEmail TEXT NOT NULL,
RoleLevel BOOLEAN NOT NULL,
LoginPassword TEXT,
UserTeamId INTEGER,
UserTeamYear INTEGER,
ProfilePicture BLOB,
UserTeamLead BOOLEAN);''')


conn.commit()
print('UserInfo Table created.')

# ----- HARDCODE ADMIN LOGIN -----
nm = str(Encryption.cipher.encrypt(b'Admin').decode("utf-8"))
ph = str(Encryption.cipher.encrypt(b'111-111-1111').decode("utf-8"))
email = str(Encryption.cipher.encrypt(b'admin@test.com').decode("utf-8"))
pwd = str(Encryption.cipher.encrypt(b'test123').decode("utf-8"))
cur.execute("Insert Into UserInfo ('UserName', 'UserFName','UserMName', 'UserLName', 'UserGender', 'UserDOB', 'UserHandicap', 'UserPhNum', 'UserEmail', 'RoleLevel', 'LoginPassword', 'ProfilePicture', UserTeamLead) Values (?,?,?,?,?,?,?,?,?,?,?,?,?)",(nm, "adminfirst", "adminmiddle", "adminlast", "Female", "12/12/2000", "✘", ph, email, 3, pwd, 'static/css/uploads/default.jpeg', False))
conn.commit()

# ----- HARDCODE GUEST LOGIN -----
nm = str(Encryption.cipher.encrypt(b'Guest').decode("utf-8"))
ph = str(Encryption.cipher.encrypt(b'123-675-7645').decode("utf-8"))
email = str(Encryption.cipher.encrypt(b'guest@test.com').decode("utf-8"))
pwd = str(Encryption.cipher.encrypt(b'test123').decode("utf-8"))
cur.execute("Insert Into UserInfo ('UserName', 'UserFName','UserMName', 'UserLName', 'UserGender', 'UserDOB', 'UserHandicap', 'UserPhNum', 'UserEmail', 'RoleLevel', 'LoginPassword', 'ProfilePicture', UserTeamLead) Values (?,?,?,?,?,?,?,?,?,?,?,?,?)",(nm, "g-first", "g-middle", "g-last", "Female", "12/12/2000", "✔", ph, email, 1, pwd, 'static/css/uploads/default.jpeg', False))
conn.commit()


for row in cur.execute('SELECT * FROM UserInfo;'):
    print(row)

conn.close()
print('Connection closed.')

# ******************************************************
# Connect to SQLITE Database - TEAM INFORMATION        *
# ******************************************************
conn = sqlite3.connect('TeamInfoDB.db')
cur = conn.cursor()
try:
    conn.execute('''DROP TABLE TeamInfo''')
    conn.commit()
    print('TeamInfo table dropped.')
except:
    print('TeamInfo table does not exist')

cur.execute('''CREATE TABLE TeamInfo(
TeamId INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
TeamName TEXT NOT NULL,
SponsorName TEXT,
SponsorPhoto BLOB,
NeedCart INTEGER,
MemberName1 TEXT,
MemberName2 TEXT,
MemberName3 TEXT,
MemberName4 TEXT,
Member1ID TEXT,
Member2ID TEXT,
Member3ID TEXT,
Member4ID TEXT,
Member1Handicap BOOLEAN,
Member2Handicap BOOLEAN,
Member3Handicap BOOLEAN,
Member4Handicap BOOLEAN,
StartHole INTEGER,
Member1Here BOOLEAN,
Member2Here BOOLEAN,
Member3Here BOOLEAN,
Member4Here BOOLEAN,
AsgnCart1 TEXT,
AsgnCart2 TEXT,
ContactFName TEXT NOT NULL,
ContactLName TEXT NOT NULL,
ContactPhNum TEXT NOT NULL,
ContactEmail TEXT NOT NULL,
ContactPhoto BLOB,
JoinCode TEXT,
MemberCount INTEGER,
Year INTEGER);''')

# save changes
conn.commit()
print('TeamInfo Table created.')

# close database connection
conn.close()
print('Connection closed.')


