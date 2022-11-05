import sys

from PyQt5.QtWidgets import QMessageBox, QMainWindow, QApplication


class Message(QMainWindow):
    def __init__(self):
        super().__init__()

    def run(self, text):
        self.message = QMessageBox(self)
        self.message.setWindowTitle("Message")
        self.message.setText(text)
        self.message.setStandardButtons(QMessageBox.Yes)
        self.message.button(QMessageBox.Yes).setText("Ok")
        self.message.setStyleSheet("background-color: rgb(213, 207, 255);")
        self.message.button(QMessageBox.Yes).animateClick(5000)

        self.message.exec()

    def close(self):
        try:
            self.message.close()
        except Exception as exc:
            pass



def main(text="Hello World"):
    app = QApplication(sys.argv)
    ex = Message()
    ex.run(text)
    ex.close()


if __name__ == '__main__':
    main()
