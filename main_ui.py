import sys
import qdarkstyle
from PyQt4 import QtGui
from ui_generated import Ui_MainWindow

# create the application and the main window
app = QtGui.QApplication(sys.argv)
window = QtGui.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(window)

# setup stylesheet
app.setStyleSheet(qdarkstyle.load_stylesheet(pyside=False))

# run
window.show()
app.exec_()