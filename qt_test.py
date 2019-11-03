import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt


# noinspection PyPep8Naming
class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(200, 200, 1000, 1000)
        # self.begin = QtCore.QPoint()
        # self.end = QtCore.QPoint()
        self.a = QtCore.QRect(50, 50, 400, 400)
        self.show()

    def drawRectangles(self):
        qp = QtGui.QPainter(self)
        # qp.setPen(QtGui.QBrush(Qt.blue))
        qp.setBrush(QtGui.QBrush(Qt.black))
        qp.drawRect(self.a)

    def paintEvent(self, event):
        self.drawRectangles()

    def mousePressEvent(self, event):
        # if self.a.contains(event.pos()):
        self.a.setBrush(QtGui.QBrush(Qt.red))
        self.update()
    #
    # def mouseMoveEvent(self, event):
    #     self.end = event.pos()
    #     self.update()
    #
    # def mouseReleaseEvent(self, event):
    #     self.begin = event.pos()
    #     self.end = event.pos()
    #     self.update()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWidget()
    window.show()
    app.aboutToQuit.connect(app.deleteLater)
    sys.exit(app.exec_())
