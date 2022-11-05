from PyInstallerFix import _append_run_path

# Fixer
_append_run_path()

import pyautogui
import sqlite3
import time
import os


class Engine:
    def __init__(self):
        data_path = "Database"
        os.makedirs(data_path + "/Screens", exist_ok=True)
        self.mpath = data_path + "/Screens"
        with open(data_path + "/config.txt", mode="r", encoding="utf-8") as file:
            readed = file.read().strip()
            data = dict(map(lambda x: x.split(' = '), readed.split('\n')))
            self.s_flag = (data["s_flag"] == "True")
            self.s_timer = int(data["s_interval"])
            self.limit = int(data["s_limit"])
        self.l_time = time.asctime()
        self.last = 0

        self.con = sqlite3.connect(data_path + "/data.db")
        cur = self.con.cursor()
        cur.execute("""INSERT INTO time(t_from, t_len) VALUES("{}", "{}")""".format(self.l_time, "0 h 0 min 0 sec"))
        self.con.commit()

        time.perf_counter()

    def screen_save(self):

        now = time.perf_counter()
        if not self.s_flag or self.last + self.s_timer > now:
            return
        self.last = int(time.perf_counter())
        text = self.mpath + "/" + time.asctime().replace(":", "_") + ".jpg"
        cur = self.con.cursor()
        cur.execute("""Insert into screen(path) Values("{}")""".format(text))
        self.con.commit()
        result = cur.execute("""Select * from screen""").fetchall()
        self.con.commit()

        pyautogui.screenshot(text)
        while len(result) > self.limit:
            cur.execute("""Delete from screen where id={}""".format(int(result[0][0])))
            self.con.commit()
            try:
                os.remove(result[0][1])
            except Exception as exc:
                pass
            del result[0]

    def time_save(self):
        times = int(time.perf_counter())
        text = "{0} h {1} min {2} sec".format(times // 3600, times % 3600 // 60, times % 60)
        cur = self.con.cursor()
        cur.execute(
            """UPDATE time SET t_len = "{}" WHERE t_from = "{}" """.format(text,
                                                                           self.l_time, ))
        self.con.commit()


if __name__ == '__main__':
    me = Engine()
    while True:
        me.screen_save()
        me.time_save()
