from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template("login.html")

# Database đơn giản với thông tin người dùng
database = {'b12': 'password123'}

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        name1 = request.form['username']
        pw1 = request.form['password']
        if name1 not in database:
            return render_template('login.html', info='User không tồn tại')
        else:
            if database[name1] != pw1:
                return render_template('login.html', info='Sai mật khẩu')
            else:
                return render_template('home.html', name=name1)
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
