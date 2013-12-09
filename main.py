'''
Created on 05.12.2013

@author: Thomas Bores
'''

import sys

from PySide import QtCore, QtGui
from PySide.QtCore import Slot

from ui.dialog import Ui_Dialog
from core.lotus_interface import LotusDBConnector

import base64
import configparser

class LotusConfigDialogController(QtGui.QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(LotusConfigDialogController, self).__init__(parent)
        self.setupUi(self)

        self.config = {'notesServer': '', 'notesFile' : '', 'notesPass' : ''}

        self.createActions()
        self.createTrayIcon()

        self.trayIcon.setVisible(True)
        self.trayIcon.showMessage('pyLotusNotifier started', 'Right click on this icon to configure your Lotus Notes access.', int = 5000)
        # self.trayIcon.messageClicked.connect(self.messageClicked)
        # self.trayIcon.activated.connect(self.iconActivated)

        # Lotus thread configuration
        self.lotus_thread = LotusDBConnector(self)
        self.lotus_thread.signal.sig.connect(self.new_email)

        # We look for a previous configuration
        # If it is found then we start the lotus thread directly
        if self.load_config():
            self.run_lotus_thread()

    def iconActivated(self, reason):
        self.showMessage()

    def showMessage(self):
       self.trayIcon.showMessage(self.titleEdit.text(),
                self.bodyEdit.toPlainText(), 1,
                self.durationSpinBox.value() * 1000)

    def showConfig(self):
        self.show()

    def createActions(self):
        self.showConfigAction = QtGui.QAction("Configure", self, triggered=self.showConfig)
        self.minimizeAction = QtGui.QAction("Mi&nimize", self,
                triggered=self.hide)
        self.restoreAction = QtGui.QAction("&Restore", self,
                triggered=self.showNormal)

        self.quitAction = QtGui.QAction("&Quit", self,
                triggered=QtGui.qApp.quit)

    def createTrayIcon(self):
        self.trayIconMenu = QtGui.QMenu(self)
        self.trayIconMenu.addAction(self.showConfigAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.minimizeAction)
        self.trayIconMenu.addAction(self.restoreAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.quitAction)

        self.trayIcon = QtGui.QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)
        self.trayIcon.setIcon(QtGui.QIcon(":/lotus/img/pylotus_24px.png"))

    def update_config(self):
        configChange = False
        if self.lineEdit_server.text() != self.config['notesServer']:
            self.config['notesServer'] = self.lineEdit_server.text()
            configChange = True
        if self.lineEdit_db.text() != self.config['notesFile']:
            self.config['notesFile'] = self.lineEdit_db.text()
            configChange = True
        if self.lineEdit_password.text() != self.config['notesPass']:
            self.config['notesPass'] = self.lineEdit_password.text()
            configChange = True
        return configChange

    def save_config(self):
        with open('pylotusnotifier.cfg', 'w') as configfile:
            config = configparser.RawConfigParser()
            config.add_section('lotus')
            config.set('lotus', 'notesServer', self.config['notesServer'])
            config.set('lotus', 'notesFile', self.config['notesFile'])
            config.set('lotus', 'notesPass', base64.standard_b64encode(self.config['notesPass'].encode('utf-8')).decode('utf-8'))
            config.write(configfile)

    def load_config(self):
        try:
            config = configparser.RawConfigParser()
            config.read('pylotusnotifier.cfg')
            self.config['notesServer'] = config.get('lotus', 'notesServer')
            self.config['notesFile'] = config.get('lotus', 'notesFile')
            self.config['notesPass'] = base64.standard_b64decode(config.get('lotus', 'notesPass').encode('utf-8')).decode('utf-8')
            print('Lotus configuration loaded from configuration file')

            self.lineEdit_server.setText(self.config['notesServer'])
            self.lineEdit_db.setText(self.config['notesFile'])
            self.lineEdit_password.setText(self.config['notesPass'])
            return True

        except configparser.NoSectionError:
            print('No configuration file found or lotus section not found.')
            return False

    @Slot()
    def accept(self):
        self.hide()

        if self.update_config():
            self.save_config()
            self.lotus_thread.exiting=True
            self.lotus_thread.stop()
            self.run_lotus_thread()

    def run_lotus_thread(self):
        if not self.lotus_thread.isRunning():
            self.lotus_thread.start()

    def new_email(self, data):
        self.trayIcon.showMessage('New Email waiting for you', data)

def main():
    print('***************************')
    print('* pyLotusNotifier started *')
    print('***************************')
    print('Configure pyLotusNotifier using the GUI.')
    print('Check your systray.')

    app = QtGui.QApplication(sys.argv)

    if not QtGui.QSystemTrayIcon.isSystemTrayAvailable():
        QtGui.QMessageBox.critical(None, "Systray", "I couldn't detect any system tray on this system.")
        sys.exit(1)
    QtGui.QApplication.setQuitOnLastWindowClosed(False)

    dlg = LotusConfigDialogController()
    sys.exit(app.exec_())
    print('END')

if __name__ == "__main__":
    main()
