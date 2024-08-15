from flask import Flask, flash, redirect, render_template, request, jsonify,  Response, url_for, session
from flask_dropzone import Dropzone
from openCam import *
import qrcode , secrets, cv2
from createQR import QRCodeData
import secrets
from wtforms import StringField, SubmitField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length

from flask_wtf.csrf import CSRFProtect
# Connect zalo
from templates import *
import zalo
from thread import word_QR
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium import webdriver  
import os
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from datetime import datetime
# connect database
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

chrome_options = Options()


app = Flask(__name__)
dropzone = Dropzone(app)
# connect database
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "test-qr-zalo" 
mysql = MySQL(app)

# Cấu hình Dropzone (tùy chọn)
dir_path = os.path.dirname(os.path.realpath(__file__))
app.config.update (
    UPLOAD_PATH=os.path.join(dir_path, "static"),
    DROPZONE_ALLOWED_FILE_TYPE = 'image',
    DROPZONE_MAX_FILE_SIZE = 3,
    DROPZONE_MAX_FILE=1,
    DROPZONE_REDIRECT_VIEW="decoded",
    
)
app.config['SECRET_KEY'] = '862cf0bd8565ae921a2e98b6ec3f2e1a6793b943'

decode_info = None
number_tb = None
name_tb =None
query_number_tb = None
query_name_tb = None
tbimage = None
tbqr = None
departimg = None
departqr = None
camera = cv2.VideoCapture(0)
word_QR = None
user_role = None
tb_number = None

# hàm mở input khi bắt đầu
@app.route('/')
def input():
    return render_template('login.html', title='Đăng nhập')

# hàm mở home cho admin
@app.route('/admin')
def admin():
    role = session.get('role', '0')
    username = session.get('username', '0')
    return render_template('admin.html', role=role,username=username)

@app.route('/index')
def index():
    # Khởi tạo data
    data = {
        'device_name': '',
        'status': '',
        'description': '',
        'location': ''
    }
    # Lấy dữ liệu từ tệp HTML
    # dataQR = get_data_html()
    
    # Kết hợp data và dataQR trong một đối tượng duy nhất
    combined_data = {
        # 'dataQR': dataQR,
        'device_name': data['device_name'],
        'status': data['status'],
        'description': data['description'],
        'location': data['location']
    }
    
    # Render template với dữ liệu kết hợp
    return render_template('index.html', **combined_data)


# Hàm giả định để kiểm tra vai trò của người dùng
def get_user_role():
    # Giả sử bạn đã có logic để lấy vai trò người dùng
    return session.get('role', '0')  # Mặc định là 0 nếu không có vai trò

# danh cho khach va bao tri
@app.route('/home')
def home():
    role = session.get('role', '0')
    username = session.get('username', '0')
    return render_template('home.html', role=role,username=username)

# hàm mở gọi mở hàm camera
@app.route('/open_camera', methods=['GET', 'POST'])
def open_camera():
   # Định nghĩa hàm mở camera
    scanner = generate_frames()
    return Response(scanner, mimetype='multipart/x-mixed-replace; boundary=frame')
# hàm mở camera
def generate_frames():
    while True:
        global word_QR
        running = True
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            decoded_objects = decode(frame)
            for obj in decoded_objects:
                x, y, w, h = obj.rect
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                qr_data = obj.data.decode("utf-8")
                if qr_data!= "":
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    else:
                        word_QR = qr_data[47:]
                        print(word_QR)
                        # getDataFromCam(word_QR)
                        running = False
                        camera.release()
                        cv2.destroyAllWindows()
                        return word_QR
                else:
                    return "Value not found"
            
        frame=buffer.tobytes()

        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame +b'\r\n' )

@app.route('/getcamera', methods=['GET', 'POST'])
def getcamera():
    return render_template('reportCam.html', tittle = 'Success')

#   Lay data tu qr in vao input
@app.route('/getqrcamera', methods=['GET', 'POST'])
def getqrcamera():
    global word_QR 
    global tbqr
    cur = mysql.connection.cursor()
    sql_query = """
    SELECT log_use.Ma_TB, tb_category.Name_TB, depart_category.Name_Depart
    FROM log_use
    INNER JOIN tb_category ON log_use.Ma_TB = tb_category.Ma_TB
    INNER JOIN depart_category ON depart_category.Ma_Depart = log_use.Ma_Depart
    WHERE log_use.Ma_TB = %s
    """
    # Execute the query with the parameter
    cur.execute(sql_query, (word_QR,))
    tb = cur.fetchone()
    if tb:
        for tbi in tb:
            valuetb = tb[1]
            valuedepart = tb[2]
        tbqr = valuetb
        departqr = valuedepart
        # print("hello", departqr)
    else:
        return "no data"
    return render_template('reportCam.html', tittle = 'Success', number_tb = word_QR, name_tb = tbqr, location = departqr)

#  Report
@app.route('/report', methods = ['GET', 'POST'])
def report():
    return render_template('report.html', title='report')

#  Upload QR up html
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    
    if request.method == 'POST':
        global decode_info
        global tbimage
        f = request.files.get("file")
        filename, extension = f.filename.split('.')
        generated_filename = secrets.token_hex(20) + f".{extension}"

        file_location = os.path.join(app.config['UPLOAD_PATH'], generated_filename)
        f.save(file_location)
        # print(f"Đường dẫn tệp: {file_location}")
        if not os.path.exists(file_location):
            return "File not found after saving", 500
        img = cv2.imread(file_location)
        if img is None:
            return "Failed to read the uploaded image", 400
        
        det = cv2.QRCodeDetector()
        val, pts, st_code = det.detectAndDecode(img)
        os.remove(file_location)

        decode_info = val
    else:
        return render_template('upload.html', title='Upload')

# Scan QR send data HTML
@app.route('/decode')
def decoded():
    global decode_info
    global tbimage , departimg
    cur = mysql.connection.cursor()
    # dau , phia sau cua cau lenh select that su quan trong
    # nham muc dich chuyen doi decode_info thanh kieu du liu tuple
    # cur.execute("SELECT * FROM tb_category WHERE ma_TB = %s", (decode_info,))
    sql_query = """
    SELECT log_use.Ma_TB, tb_category.Name_TB, depart_category.Name_Depart
    FROM log_use
    INNER JOIN tb_category ON log_use.Ma_TB = tb_category.Ma_TB
    INNER JOIN depart_category ON depart_category.Ma_Depart = log_use.Ma_Depart
    WHERE tb_category.Ma_TB = %s
    """
    # Execute the query with the parameter
    cur.execute(sql_query, (decode_info,))
    tb = cur.fetchone()
    if tb:
        valuetb = tb[1]
        valuedepart = tb[2]
        tbimage = valuetb
        departimg = valuedepart
    else:
        tbimage = "Thiết bị chưa được đưa vào sử dụng"
        departimg = "Thiết bị chưa được đưa vào sử dụng"
    # print("hello", departimg)
    return render_template('decode.html', title='Decode', data=decode_info, name_tb=tbimage, location = departimg)

# CreateQR
@app.route('/createqr', methods=['GET', 'POST'])
def createqr():
    form = QRCodeData()

    if request.method == 'POST':
        if form.validate_on_submit():
            data = form.data.data
            image_name = f"{secrets.token_hex(10)}.png"
            qrcode_location = f"{app.config['UPLOAD_PATH']}/{image_name}"

            try:
                my_qrcode = qrcode.make(str(data))
                my_qrcode.save(qrcode_location)
            except Exception as e:
                print(e)

            return render_template('createdqr.html', title='Success', image= image_name)
    else:
        return render_template('createqr.html', title='Create_QRCode', form=form)

# Mở zalo thông báo thiết bị hỏng
@app.route('/reportbreak', methods=['GET', 'POST'])
def report_break():
    zalo.openZaloGroup()  # Call useZalo function when accessing /reportbreak
    return redirect(url_for('decoded'))

# login
@app.route('/login', methods=['GET', 'POST'])
def login():

    global user_role  # Khai báo biến toàn cục

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cur = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE mssv =%s AND password = %s", (username, password))
        loginusers = cursor.fetchone()

        if loginusers:
            session['loggedin'] = True
            session['username'] = loginusers[0]
            session['password'] = loginusers[1]
            sql = """SELECT users.name, users.password, depart_category.role
            FROM users
            INNER JOIN depart_category ON users.Ma_Depart = depart_category.Ma_Depart
            WHERE users.mssv = %s;"""
            cur.execute(sql, (username,))

            roleuser = cur.fetchone()
            session['role'] = roleuser[2]

             # Cập nhật biến toàn cục
            user_role = session['role']

            if roleuser:
                    role = roleuser[2]  
                    if role == '0':
                        return redirect(url_for('admin'))
                    elif role == '1':
                        return redirect(url_for('maintenance'))
                    else:
                        return redirect(url_for('home'))
            else:
                return render_template('login.html', error="Không tìm thấy vai trò người dùng.")
        else:
            return render_template('login.html')
    return render_template('login.html')

# logout
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    global user_role
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('password', None)
    user_role = None  # Xóa biến toàn cục khi đăng xuất
    return redirect(url_for('login'))

# Liệt kê danh sách thiết bị
@app.route('/list', methods=['GET', 'POST'])
def list():
    global name_tb, user_role
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tb_category ")
    tbs = cur.fetchall()
    search_query = request.args.get('search')
    if search_query:
        cur.execute("SELECT * FROM tb_category WHERE Name_TB = %s", (search_query,))
        search = cur.fetchall()
        cur.execute("SELECT * FROM depart_category WHERE role = %s", (user_role,))
        role = cur.fetchone()
        if search:
            for number in search:
                listtb = number[1]
                query_role = role[1]
            name_tb = listtb
        else:
            search = []
            name_tb = None
    else:
        search = []
        name_tb = None
    return render_template('list.html', tbs=tbs, search=search, user_role=user_role)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')

# truy vấn 
@app.route('/query', methods=['GET', 'POST'])
def query():
    global name_tb, user_role
    cur = mysql.connection.cursor()
    
    if name_tb:
        cur.execute("SELECT * FROM tb_category WHERE Name_TB = %s", (name_tb,))
        tbs = cur.fetchone()
        if tbs:
            query_numbertb = tbs[0]
            query_nametb = tbs[1]
        else:
            query_numbertb = 'No data'
            query_nametb = 'No data'
    else:
        query_numbertb = 'No data'
        query_nametb = 'No data'
    
    cur.execute("SELECT * FROM depart_category WHERE role = %s", (user_role,))
    role = cur.fetchone()
    if role:
        query_role = role[1]
    else:
        query_role = 'No data'
    return render_template('query.html', device_number = query_numbertb, device_name= query_nametb, device_address = query_role)

# gửi yêu cầu cần thiết bị
@app.route('/request', methods=['GET', 'POST'])
def submit_request():
    if request.method == 'POST':
        querynumber = request.form['deviceNumber']
        querydepart = request.form['department']
        queryquantity = request.form['quantity']
        
        cur = mysql.connection.cursor()
        try:
            # Check if the department exists
            cur.execute("SELECT * FROM depart_category WHERE Name_Depart = %s", (querydepart,))
            depart_exists = cur.fetchone()

            if depart_exists:
                depart_role = depart_exists[0]
                
                # Check if the same log_request already exists
                cur.execute("SELECT * FROM log_request WHERE Ma_TB = %s AND Ma_Depart = %s", (querynumber, depart_role))
                log_request_exists = cur.fetchone()

                if log_request_exists:
                    # Handle the case where the log_request already exists
                    print("Log request already exists")
                    return "Log request already exists", 400
                else:
                    # Perform the INSERT operation
                    cur.execute("INSERT INTO log_request (Ma_Request, Ma_TB, Ma_Depart, Quantity) VALUES (NULL, %s, %s, %s)", (querynumber, depart_role, queryquantity,))
                    cur.execute("UPDATE tb_category SET Role_TB ='2' WHERE Ma_TB=%s",(querynumber,))
                    # Commit the transaction
                    mysql.connection.commit()
                    # Redirect or render template
                    return redirect(url_for('home'))
            else:
                # Handle the case where the department does not exist
                print("Department does not exist")
                return "Department does not exist", 400
        except Exception as e:
            # In ra lỗi nếu có
            print(f"Error: {e}")
            # Rollback if any error occurs
            mysql.connection.rollback()
            return str(e), 500
        

    # Render the request form template for GET requests
    return redirect(url_for('home'))

@app.route('/maintenance', methods=['GET', 'POST'])
def maintenance ():
    return render_template('index.html')

# thêm/sửa/xóa thiết bị
@app.route('/editTB', methods=['GET', 'POST'])
def editTB():
    cur = mysql.connection.cursor()
    
    if request.method == 'POST':
        # Update device details
        device_id = request.form['device_id']
        device_name = request.form['device_name']
        origin = request.form['origin']
        date_received = request.form['date_received']
        supplier = request.form['supplier']
        
        # Update the device in the database
        cur.execute("""UPDATE tb_category SET Name_TB = %s, Country_TB = %s, Recive_date_TB = %s, Provide_TB = %s WHERE Ma_TB = %s""", (device_name, origin, date_received, supplier, device_id))
        
        mysql.connection.commit()
        cur.close()
        
        flash('Thiết bị đã được cập nhật thành công!', 'success')
        return redirect(url_for('editTB'))

    if request.method == 'GET':
        device_id = request.args.get('device_id')
        if device_id:
            cur.execute("SELECT * FROM tb_category WHERE Ma_TB = %s", (device_id,))
            device = cur.fetchone()
            cur.close()
            return render_template('editTB.html', device=device)
    
    # Fetch all devices for display
    cur.execute("SELECT * FROM tb_category")
    devices = cur.fetchall()
    cur.close()
    
    return render_template('editTB.html', devices=devices)

@app.route('/addTB', methods=['GET', 'POST'])
def addTB():
    if request.method == 'POST':
        device_number = request.form['device_number']
        device_name = request.form['device_name']
        origin = request.form['origin']
        date_received = request.form['date_received']
        supplier = request.form['supplier']
        
        # Convert date_received to a date object
        date_received = datetime.strptime(date_received, '%Y-%m-%d').date()
        
        # Insert the new device into the database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO tb_category (Ma_TB, Name_TB, Country_TB, Recive_date_TB, Provide_TB, Role_TB) VALUES (%s, %s, %s, %s, %s,'0')", 
                    (device_number, device_name, origin, date_received, supplier))
        mysql.connection.commit()
        cur.close()
        
        return redirect(url_for('editTB'))
    
    return render_template('addTB.html')

@app.route('/deleteTB', methods=['GET', 'POST'])
def deleteTB():
    if request.method == 'POST':
        device_id = request.form['device_id']
        
        # Check the status of the device before attempting to delete
        cur = mysql.connection.cursor()
        cur.execute("SELECT Role_TB FROM tb_category WHERE Ma_TB = %s", [device_id])
        device_status = cur.fetchone()
        cur.close()
        
        if device_status and device_status[0] == '1':
            # Device cannot be deleted, set an error message
            flash('Không thể xóa thiết bị với trạng thái đang được sử dụng', 'error')
        else:
            # Proceed with deletion
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM tb_category WHERE Ma_TB = %s", [device_id])
            mysql.connection.commit()
            cur.close()
            flash('Thiết bị đã được xóa thành công', 'success')
        
        return redirect(url_for('deleteTB'))
    
    # Retrieve all devices to display on the delete page
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tb_category")
    devices = cur.fetchall()
    cur.close()
    
    return render_template('editTB.html', devices=devices)

# yêu cầu thiết bị mới từ phòng ban
@app.route('/requestTB', methods=['GET', 'POST'])
def requestTB():
    global tb_number

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM log_request")
    log_request = cur.fetchall()
    tb_number

    # Fetch tb_category information for each log request
    for log in log_request:
        tb_id = log[1]  # Assuming the second column is Ma_TB
        cur.execute("SELECT Ma_TB, Role_TB FROM tb_category WHERE Ma_TB = %s", (tb_id,))
        tb_category = cur.fetchone()
        if tb_category:
            tb_number = tb_category[0]

    return render_template('requestTB.html', log_request=log_request)

# phê duyệt yêu cầu thiết bị mới
@app.route('/accept', methods=['GET', 'POST'])
def accept():
    global tb_number
    if tb_number:
        cur = mysql.connection.cursor()
        cur.execute("UPDATE tb_category SET Role_TB ='1' WHERE Ma_TB=%s",(tb_number,))
        cur.execute("DELETE FROM log_request WHERE Ma_TB = %s",(tb_number,))
        mysql.connection.commit()
        return "message :Update successful 200 "
    else:
        return "message :No device number provided 400"

# truy xuất lịch sử sử dụng thiết bị
@app.route('/history', methods=['GET', 'POST'])
def history():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM log_use")
    log_use = cur.fetchall()
    cur.close()  # Always close the cursor after usage
    return render_template('history.html', log_use=log_use)




if __name__ == '__main__':
    app.run(debug=True)