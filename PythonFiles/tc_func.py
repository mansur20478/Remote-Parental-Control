# -*- coding: utf-8 -*-

import hashlib
import re
import webbrowser
import sys
import sqlite3
import os

from PyQt5 import Qt
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QInputDialog, QErrorMessage, QLineEdit, QTableWidgetItem, \
    QFileDialog, QApplication
from PyQt5.QtCore import Qt
from tc_ui import Ui_MainWindow
from pathlib import Path


class MyMainWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.database_path = "Database"
        self.con = sqlite3.connect(self.database_path + "/data.db")
        self.initUI()
        self.load_table()

    def run_widget(self):
        if not self.login_phase():
            sys.exit(0)
        self.show()

    def initUI(self):
        self.setupUi(self)
        self.save_act.triggered.connect(self.save_file)
        self.clear_act.triggered.connect(self.clear_file)
        self.chpass_act.triggered.connect(self.option_change_password)
        self.s_flag_act.triggered.connect(self.option_change_s_flag)
        self.s_limit_act.triggered.connect(self.option_change_s_limit)
        self.s_interval_act.triggered.connect(self.option_change_s_interval)
        self.actionTurn_on_off.triggered.connect(self.option_change_t_flag)
        self.actionChange_password.triggered.connect(self.option_change_t_password)
        self.actionToken.triggered.connect(self.option_change_token)
        self.guide_act.triggered.connect(self.about_guide)

    def get_data(self, need, tpath=''):
        path = self.database_path + "/config.txt"
        if tpath != '':
            path = tpath
        with open(path, mode="r", encoding="utf-8") as file:
            readed = file.read().strip()
            data = dict(map(lambda x: x.split(' = '), readed.split('\n')))
        return data[need]

    def change_data(self, need, new_val, tpath=''):
        path = self.database_path + "/config.txt"
        if tpath != '':
            path = tpath
        if type(new_val) == type(str):
            new_val = "\"" + new_val + "\""

        with open(path, mode="r", encoding="utf-8") as file:
            readed = file.read().strip()
            data = dict(map(lambda x: x.split(' = '), readed.split('\n')))
        data[need] = new_val
        with open(path, mode="w", encoding="utf-8") as file:
            wrote = ""
            for line in data:
                wrote = wrote + line + " = " + data[line] + "\n"
            file.write(wrote)

    def relaunch_message(self):
        message = QMessageBox(self)

        message.setWindowTitle("Warning")
        message.setText("To apply changes reload PC")
        message.setStyleSheet("background-color: rgb(213, 207, 255);")
        message.setStandardButtons(QMessageBox.Yes)
        message.button(QMessageBox.Yes).setText("Ok")

        message.exec()

    def login_phase(self):
        dialog = QInputDialog(self)
        dialog.setInputMode(QInputDialog.TextInput)
        dialog.resize(100, 100)
        dialog.setWindowTitle("Login")
        dialog.setLabelText("Password:")
        dialog.setOkButtonText("Entry")
        dialog.setCancelButtonText("Exit")
        dialog.setTextEchoMode(QLineEdit.Password)
        dialog.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        dialog.setStyleSheet("background-color: rgb(213, 207, 255);")

        error_message = QErrorMessage(dialog)
        error_message.setModal(True)
        error_message.setWindowTitle("Error")

        while True:
            status = dialog.exec_()
            get_line = dialog.textValue()
            if status == 0:
                return False
            else:
                new_hash = hashlib.md5(bytes(get_line, 'utf-8')).hexdigest()
                cur_hash = self.get_data("cur_hash")
                if new_hash == cur_hash:
                    return True
                else:
                    error_message.showMessage("Wrong Password")
                    error_message.exec()

    def load_table(self):
        cur = self.con.cursor()
        result = cur.execute("Select * from time").fetchall()
        self.con.commit()

        self.time_shower.setRowCount(0)
        for i, row in enumerate(result):
            self.time_shower.setRowCount(self.time_shower.rowCount() + 1)
            for j, elem in enumerate(row):
                if j == 0:
                    continue
                self.time_shower.setItem(i, j - 1, QTableWidgetItem(elem))
        self.time_shower.resizeColumnsToContents()

    def save_file(self):
        try:
            path = QFileDialog.getSaveFileName(self, "Save history", "history", "text(*.txt)")
            with open(path[0], mode="w+", encoding="utf-8") as file:
                text = ""
                for i in range(self.time_shower.rowCount()):
                    text = text + "Date: " + self.time_shower.item(i, 0).text() + ". Duration of use" \
                           + self.time_shower.item(i, 1).text() + "\n"
                file.write(text)
        except Exception as exc:
            pass

    def clear_file(self):
        cur = self.con.cursor()
        result = cur.execute("Delete from time").fetchall()
        self.con.commit()
        self.load_table()

    def good_pass(self, text):
        status = True
        if len(text) < 6 or len(text) > 12:
            status = False
        elif not re.search("[a-z]", text):
            status = False
        elif not re.search("[0-9]", text):
            status = False
        elif not re.search("[A-Z]", text):
            status = False
        elif not re.search("[$#@]", text):
            status = False
        return status

    def option_change_password(self):
        dialog = QInputDialog(self)
        dialog.setInputMode(QInputDialog.TextInput)
        dialog.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        dialog.setLabelText("New Password:")
        dialog.setOkButtonText("Save")
        dialog.setCancelButtonText("Back")
        dialog.resize(100, 100)
        dialog.setStyleSheet("background-color: rgb(213, 207, 255);")
        dialog.setWindowTitle("Changing Password")

        error_message = QErrorMessage(dialog)
        error_message.setModal(True)
        error_message.setWindowTitle("Error")

        while True:
            status = dialog.exec_()
            get_line = dialog.textValue()
            if status == 0:
                return
            elif self.good_pass(get_line):
                new_hash = hashlib.md5(bytes(get_line, 'utf-8')).hexdigest()
                self.change_data("cur_hash", str(new_hash))
                return
            else:
                error_message.showMessage(
                    "Password must have: "
                    "6 - 12 Characters and "
                    "Includes Numbers, Symbols, Capital Letters, and Lower-Case Letters"
                )

    def option_change_s_flag(self):
        text = "Current: "
        if self.get_data("s_flag") == "True":
            text = text + "ON"
        else:
            text = text + "OFF"

        message = QMessageBox(self)
        message.setWindowTitle("Turn on/off")
        message.setText(text)
        message.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        message.button(QMessageBox.Yes).setText("ON")
        message.button(QMessageBox.No).setText("OFF")
        message.setStyleSheet("background-color: rgb(213, 207, 255);")
        status = message.exec()

        if status == QMessageBox.Yes:
            self.change_data("s_flag", "True")
        elif status == QMessageBox.No:
            self.change_data("s_flag", "False")

    def option_change_s_limit(self):
        dialog = QInputDialog(self)
        dialog.setInputMode(QInputDialog.IntInput)
        dialog.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        dialog.setLabelText("New limit:")
        dialog.setOkButtonText("Save")
        dialog.setCancelButtonText("Back")
        dialog.setIntMinimum(1)
        dialog.setIntMaximum(100001)
        dialog.setIntValue(int(self.get_data("s_limit")))
        dialog.resize(100, 100)
        dialog.setStyleSheet("background-color: rgb(213, 207, 255);")
        dialog.setWindowTitle("Set count photo")

        status = dialog.exec_()
        get_line = str(dialog.intValue())

        if status == 1:
            self.change_data("s_limit", get_line)

    def option_change_s_interval(self):
        dialog = QInputDialog(self)
        dialog.setInputMode(QInputDialog.IntInput)
        dialog.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        dialog.setLabelText("Interval(in seconds):")
        dialog.setOkButtonText("Save")
        dialog.setCancelButtonText("Back")
        dialog.setIntMinimum(60)
        dialog.setIntMaximum(100001)
        dialog.setIntValue(int(self.get_data("s_interval")))
        dialog.resize(100, 100)
        dialog.setStyleSheet("background-color: rgb(213, 207, 255);")
        dialog.setWindowTitle("Set interval")

        status = dialog.exec_()
        get_line = str(dialog.intValue())

        if status == 1:
            self.change_data("s_interval", get_line)

    def option_change_t_flag(self):
        text = "Current: "
        if self.get_data("flag", self.database_path + "/telegram_config.txt") == "True":
            text = text + "ON"
        else:
            text = text + "OFF"

        message = QMessageBox(self)
        message.setWindowTitle("Turn on/off")
        message.setText(text)
        message.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        message.button(QMessageBox.Yes).setText("ON")
        message.button(QMessageBox.No).setText("OFF")
        message.setStyleSheet("background-color: rgb(213, 207, 255);")
        status = message.exec()

        if status == QMessageBox.Yes:
            self.change_data("flag", "True", self.database_path + "/telegram_config.txt")
        elif status == QMessageBox.No:
            self.change_data("flag", "False", self.database_path + "/telegram_config.txt")

    def option_change_t_password(self):
        dialog = QInputDialog(self)
        dialog.setInputMode(QInputDialog.TextInput)
        dialog.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        dialog.setLabelText("New Password:")
        dialog.setOkButtonText("Save")
        dialog.setCancelButtonText("Back")
        dialog.resize(100, 100)
        dialog.setStyleSheet("background-color: rgb(213, 207, 255);")
        dialog.setWindowTitle("Changing Password")

        error_message = QErrorMessage(dialog)
        error_message.setModal(True)
        error_message.setWindowTitle("Error")

        while True:
            status = dialog.exec_()
            get_line = dialog.textValue()
            if status == 0:
                return
            elif self.good_pass(get_line):
                new_hash = hashlib.md5(bytes(get_line, 'utf-8')).hexdigest()
                self.change_data("cur_hash", str(new_hash), self.database_path + "/telegram_config.txt")
                return
            else:
                error_message.showMessage(
                    "Password must have: "
                    "6 - 12 Characters and "
                    "Includes Numbers, Symbols, Capital Letters, and Lower-Case Letters"
                )

    def option_change_token(self):
        dialog = QInputDialog(self)
        dialog.setInputMode(QInputDialog.TextInput)
        dialog.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        dialog.setLabelText("New Token:")
        dialog.setOkButtonText("Save")
        dialog.setCancelButtonText("Back")
        dialog.setTextValue(self.get_data("TOKEN", self.database_path + "/telegram_config.txt"))
        dialog.resize(500, 100)
        dialog.setStyleSheet("background-color: rgb(213, 207, 255);")
        dialog.setWindowTitle("Changing Token")

        error_message = QErrorMessage(dialog)
        error_message.setModal(True)
        error_message.setWindowTitle("Error")

        while True:
            status = dialog.exec_()
            get_line = dialog.textValue()
            if status == 0:
                return
            elif get_line == 45:
                self.change_data("TOKEN", get_line, self.database_path + "/telegram_config.txt")
                return
            else:
                error_message.showMessage(
                    "Incorrect token"
                )

    def about_guide(self):
        webbrowser.open_new(r'{}\guide.pdf'.format(self.database_path))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyMainWidget()
    ex.run_widget()
    sys.exit(app.exec_())
