'''
@author: Thomas Bores
'''

from PySide.QtCore import QThread
from PySide.QtCore import Signal
from PySide.QtCore import QObject

import time
import win32com.client
import pythoncom
import pywintypes
import sys

class SignalFromThreadToDialog(QObject):
    sig = Signal(str)

class LotusDBConnector(QThread):

#     LOTUS_EMAIL_ITEMS_NAMES = ('DeliveredDate', 'Subject', 'From', 'SendTo', 'Body')

    LOTUS_EMAIL_ITEMS_NAMES = ('Subject', 'From', 'Body')

    def __init__(self, parent):
        super(LotusDBConnector, self).__init__(parent)
        self.dlg = parent
        self.signal = SignalFromThreadToDialog()

    def run(self):
        self._configure()
        self._connect_to_db()
        print('LotusDBConnector thread started')
        while True:
            for doc in self._make_document_generator('$Inbox'):
#                 self.dlg.trayIcon.showMessage(doc.GetItemValue('Subject')[0], doc.GetItemValue('Body')[0], int = 3000)
                str = ''
                for item in self.LOTUS_EMAIL_ITEMS_NAMES:
                    str = str + item + ': '+ (doc.GetItemValue(item)[0]) + '\r\n'
                self.signal.sig.emit(str)
                time.sleep(5)
            time.sleep(10*60) # Check for new incoming Email every ten minutes

    def _configure(self):
        self.notesServer = self.dlg.config['notesServer']
        self.notesFile = self.dlg.config['notesFile']
        self.notesPass = self.dlg.config['notesPass']

    def _connect_to_db(self):
        print('Connect to database with parameters: ' + self.notesServer + ', '+ self.notesFile + ', ' + self.notesPass)
        # Connect to notes database (returns NotesDatabase object)
        pythoncom.CoInitialize()
        notesSession = win32com.client.Dispatch('Lotus.NotesSession')
        try:
            notesSession.Initialize(self.notesPass)
            self._notesDatabase = notesSession.GetDatabase(self.notesServer, self.notesFile)
            print('Connected to Lotus Notes Database: ' + self._notesDatabase.Title)
            return True
        except pywintypes.com_error:
            raise Exception('Cannot access mail using %s on %s' % (self.notesFile, self.notesServer))

    def _make_document_generator(self, folderName):
        # Get folder
        folder = self._notesDatabase.GetView(folderName)
        if not folder:
            raise Exception('Folder "%s" not found' % folderName)
        # Get the first document
        document = folder.GetFirstDocument()
        # If the document exists,
        while document:
            # Yield it
            yield document
            # Get the next document
            document = folder.GetNextDocument(document)
