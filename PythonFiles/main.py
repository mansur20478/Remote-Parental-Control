from PyInstallerFix import _append_run_path

# Fixer
_append_run_path()

import sys
from PyQt5.QtWidgets import QApplication
from tc_func import MyMainWidget

print(len("822970120:AAG3G4OSG0I1XUqUh45MwkHrEa7PZjb6TeU"))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MyMainWidget()
    main.run_widget()
    sys.exit(app.exec_())


