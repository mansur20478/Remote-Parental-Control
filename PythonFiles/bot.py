from PyInstallerFix import _append_run_path

# Fixer
_append_run_path()

import time
import sqlite3
import os
import hashlib
import sqlGet
import messageCreate

from PyQt5.QtWidgets import QMainWindow, QMessageBox
from telegram import Bot
from telegram import ParseMode
from telegram import Update
from telegram.ext import MessageHandler, CommandHandler
from telegram.ext import Filters, CallbackContext
from telegram.ext import Updater

class Slave:
    def __init__(self):
        self.data_path = "Database/telegram_config.txt"
        self.sq_path = "Database/data.db"
        self.good_users = {}
        self.con_sql = sqlite3.connect(self.sq_path)
        with open(self.data_path, mode="r", encoding="utf-8") as file:
            readed = file.read().strip()
            self.data = dict(map(lambda x: x.split(' = '), readed.split('\n')))
        if self.data['flag'] == 'False':
            exit(0)
        self.updater = Updater(
            token=self.data['TOKEN'],
            use_context=True
        )

        self.updater.dispatcher.add_handler(CommandHandler('log', self.log_command))
        self.updater.dispatcher.add_handler(CommandHandler('exit', self.exit_command))
        self.updater.dispatcher.add_handler(CommandHandler('duration_of_use', self.duration_of_use_command))
        self.updater.dispatcher.add_handler(CommandHandler('show_message', self.show_message_command))

        self.updater.dispatcher.add_handler(MessageHandler(Filters.all, self.echo_handler))

    def echo_handler(self, update: Update, context: CallbackContext):
        text = "<b>Command list:</b>\n\t" \
               "/log -- <i>authorization</i>\n\t" \
               "/exit -- <i>exit</i>\n\t" \
               "/duration_of_use -- <i>gives duration of use at this moment</i>\n\t" \
               "/show_message -- <i>Shows message to user</i>"

        update.message.reply_text(
            text=text,
            parse_mode=ParseMode.HTML
        )

    def log_command(self, update: Update, context: CallbackContext):
        id = update.effective_user.id
        text = update.effective_message.text.replace("/log", '').strip(" ")
        new_hash = hashlib.md5(bytes(text, 'utf-8')).hexdigest()
        if id in self.good_users and self.good_users[id]:
            update.message.reply_text(
                text='_You are already logged in_',
                parse_mode=ParseMode.MARKDOWN
            )
        elif new_hash == self.data['cur_hash']:
            self.good_users[id] = True
            update.message.reply_text(
                text='_authorization successful_',
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            update.message.reply_text(
                text='_Wrong password_',
                parse_mode=ParseMode.MARKDOWN
            )

    def exit_command(self, update: Update, context: CallbackContext):
        id = update.effective_user.id
        self.good_users[id] = False
        update.message.reply_text(
            text='_You out_',
            parse_mode=ParseMode.MARKDOWN
        )

    def duration_of_use_command(self, update: Update, context: CallbackContext):
        id = update.effective_user.id
        if id not in self.good_users or not self.good_users[id]:
            update.message.reply_text(
                text='_You are not authorized_',
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            result = sqlGet.main()
            text = ""
            for row in result:
                text = text + "From: " + row[1] + ".Duration: " + row[2] + "\n"

            if len(result) > 0:
                update.message.reply_text(
                    text='<i>PC used:</i>\n<b>{}</b>'.format(text),
                    parse_mode=ParseMode.HTML
                )
            else:
                update.message.reply_text(
                    text='_Not used now_',
                    parse_mode=ParseMode.MARKDOWN
                )

    def show_message_command(self, update: Update, context: CallbackContext):
        id = update.effective_user.id
        text = update.effective_message.text.replace("/show_message", "").strip(" ")
        if id not in self.good_users or not self.good_users[id]:
            update.message.reply_text(
                text='_You are not authorized_',
                parse_mode=ParseMode.MARKDOWN
            )
        elif text == '':
            update.message.reply_text(
                text='_Incorrect text_',
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            messageCreate.main(text)
            update.message.reply_text(
                text='<b>Done</b>',
                parse_mode=ParseMode.HTML
            )

    def run_slave(self):
        if self.data['flag'] == 'False':
            return
        self.updater.start_polling()
        self.updater.idle()

def main():
    bot = Slave()
    bot.run_slave()

if __name__ == '__main__':
    main()
