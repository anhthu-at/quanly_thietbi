import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor
import cv2
from pyzbar.pyzbar import decode
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify
from templates import *

class QRCodeScanner(QThread):
    qr_data_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Không thể mở camera")
            return

        while self.running:
            
            ret, frame = cap.read()

            if not ret:
                print("Không thể nhận khung hình (không thể đọc từ camera)")
                break

            decoded_objects = decode(frame)
            
            for obj in decoded_objects:
                x, y, w, h = obj.rect
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                qr_data = obj.data.decode("utf-8")
                self.qr_data_signal.emit(qr_data)
                if qr_data != "":
                    count_word = qr_data[41:]
                    word_QR = count_word
                    return word_QR
                else:
                    return "Value not found"
            # frame_html = request.form['cameraframe']
            fram = cv2.imshow('Camera', frame)
            # fram = frame_html

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
        cap.release()
        cv2.destroyAllWindows()
        # print(word_QR)
        return word_QR
    
    def stop(self):
        self.running = False

    def getDataHTML():
        # Đọc nội dung của tệp HTML
        with open('templates/index.html', 'r', encoding='utf-8') as file:
            web_content = file.read()

        # Tạo đối tượng BeautifulSoup
        soup = BeautifulSoup(web_content, 'html.parser')
        input_element = soup.find('input', id='inputMaTB')
        if input_element:
            return input_element.get('value', '')  # Lấy giá trị của thuộc tính value
        return None

    # def getDatafromQR(self, dataQR):
    #     getData = self.getDataHTML
    #     self.inputMaTB.setText(dataQR)
    #     print(getData)
camera = cv2.VideoCapture(0)
word_QR = None
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
                        word_QR = qr_data[41:]
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
        
def getDataFromCam(dataQR):
    return dataQR
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('QR Code Scanner')

        self.text_edit = QTextEdit(self)
        self.text_edit.setGeometry(50, 50, 700, 400)

        self.qr_scanner = QRCodeScanner()
        self.qr_scanner.qr_data_signal.connect(self.appendText)
        self.qr_scanner.start()

# dich data tu qr bat buoc giu
    @pyqtSlot(str)
    def appendText(self, text):
        self.text_edit.moveCursor(QTextCursor.End)
        self.text_edit.insertPlainText(text + '\n')
        self.text_edit.moveCursor(QTextCursor.End)

    def closeEvent(self, event):
        self.qr_scanner.stop()
        self.qr_scanner.wait()
        event.accept()







if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
