from flask import Flask, redirect, render_template, request, jsonify,  Response, url_for, session, g

import os
# connect database
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)

app.config['SECRET_KEY'] = '862cf0bd8565ae921a2e98b6ec3f2e1a6793b943'

# connect database
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "test-qr-zalo" 

mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (mssv,password) VALUES (%s,%s)",(username,password))

        mysql.connection.commit()

        return 'success'

    return render_template('home.html')

@app.route('/users', methods=['GET', 'POST'])
def user():
    cur = mysql.connection.cursor()
    users = cur.execute("SELECT * FROM users")
    if users > 0:
        userDetails = cur.fetchall()
        for user in userDetails:
            if user[2] == 2:
                print("hello",user[2])
                return render_template('loginvideo.html', userDetails=userDetails)
    
    return render_template('loginvideo.html', userDetails=userDetails)
    
@app.route('/test', methods=['GET', 'POST'])
def login1():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cur = mysql.connection.cursor()
        # cursor.execute("INSERT INTO users (mssv, password) VALUES  (%s,%s)", (username,password))
        cursor.execute("SELECT * FROM users WHERE mssv =%s AND password = %s", (username, password))
        users = cursor.fetchone()
        
        if users:
            session['loggedin'] = True
            session['username'] = users[1]
            roles = cur.execute("SELECT * FROM users")
            print(roles)
            print("hi")
            # if roles == 1:
            #     return redirect(url_for('index'))
            # else: 
            #     return "hellooo"
        else:
            return redirect(url_for('home'))
        
    return redirect(url_for('user'))

def test2():
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor()
    users = cur.execute("SELECT * FROM users WHERE role")
    if users:
            session['loggedin'] = True
            if users > 0:
                userDetails = cur.fetchall()
                for user in userDetails:
                    if user:
                        role = user[2]
                        print( "hello",role)
                        if role == 2:
                            print( "hello 2",role)
                            # return render_template('index.html',role=role)
                        else:
                            print( "hello 1",role)
                            # return redirect(url_for('home'))
                    else:
                    # khi login thanh cong tren thanh url se hien /index 
                    # cong dung cua redirect
                        role = user[2]
                        print(role)
if __name__ == '__main__':
    app.run(debug=True)

