import sys
import cv2
from pyzbar.pyzbar import decode
from flask import Flask, Response, jsonify, render_template
from threading import Thread
import time

app = Flask(__name__)
camera = cv2.VideoCapture(0)
word_QR = None

class QRCodeScanner(Thread):
    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        global word_QR
        while self.running:
            success, frame = camera.read()
            if not success:
                break

            decoded_objects = decode(frame)
            for obj in decoded_objects:
                qr_data = obj.data.decode("utf-8")
                count_word = qr_data[41:]
                word_QR = count_word
                print(f"Scanned QR code: {word_QR}")

                # Dừng khi quét được QR code đầu tiên
                self.running = False
                break

            # Hiển thị frame trên cửa sổ
            cv2.imshow('Camera', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        camera.release()
        cv2.destroyAllWindows()

@app.route('/')
def index():
    return render_template('flask.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/get_data')
def get_data():
    global word_QR
    if word_QR:
        data = {'qr_data': word_QR}
    else:
        data = {'qr_data': 'No QR data available'}
    return jsonify(data)

if __name__ == '__main__':
    qr_scanner = QRCodeScanner()
    qr_scanner.start()

    # Khởi động Flask app
    app.run(debug=True, threaded=True)

    # Đợi khi kết thúc và dọn dẹp
    qr_scanner.join()
