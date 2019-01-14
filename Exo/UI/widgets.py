from PySide2 import QtWidgets
from maya import cmds

from Exo.Core import build, util

reload(build)
reload(util)

class wdg_menu(QtWidgets.QMenu):
    def __init__(self, parent):
        super(wdg_menu, self).__init__(parent)
        
    def addActionMany(self, action_list):
        '''addAction but for many QActions'''
        for action in action_list:
            self.addAction(action)
            
class wdg_action(QtWidgets.QAction):
    def __init__(self, parent):
        super(wdg_action, self).__init__(parent)
        
        self.exo_name = ''
        self.version_number = ''
        self.actionType = 0
        self.triggered.connect(self.doAction)
        
        self.mainWindow = parent
        
    def setActionType(self, value):
        '''
        Set value of self.actionType
        
        0 Control Action
        1 Jiggle Action
        2 FK/IK Match Action
        3 About Action
        '''
        self.actionType = value
        
        return self.actionType
        
    def setVersion(self, exo_name, version_number):
        self.exo_name = exo_name
        self.version_number = version_number
        
        return self.exo_name, self.version_number
        
    def doAction(self):
        '''Call the action's respective function'''
        if self.actionType == 0:
            self.callCtrl()
        elif self.actionType == 1:
            self.callJiggle()
        else:
            self.callAbout()

    def callCtrl(self):
        '''Make a control'''
        build.buildCtrl()
        self.mainWindow.refresh()
            
    def callJiggle(self):
        '''Make a jiggle'''
        build.buildJiggle()
        self.mainWindow.refresh()
            
    def callAbout(self):
        '''About popup'''
        abtBox = QtWidgets.QMessageBox()
        abtBox.setWindowTitle('{0} - About'.format(self.exo_name))
        abtBox.setText('{0} version: {1}\nCreated by: Arthur Yee'.format(self.exo_name, self.version_number))
        
        abtBox.exec_()

class wdg_table(QtWidgets.QTableWidget):
    def __init__(self, parent):
        super(wdg_table, self).__init__(parent)
                
    def clearAll(self):
        '''Clear the table completely'''
        self.setRowCount(0)
        
    def getExo(self):
        '''Get all available Exo tools in the scene file'''
        self.clearAll()
        
        listOfExo = cmds.listRelatives('exo_master', c = True)
        
        if listOfExo is not None:
            for node in listOfExo:
                if cmds.attributeQuery('exo_control', node = node, exists = True):
                    self.createItem(node)
                else:
                    cmds.warning('Invalid node detected!')
                
    def createItem(self, node):
        '''Create a QTableWidgetItem from node'''
        newName, newType = self.nodeToItem(node)
        
        self.insertRow(self.rowCount())
        self.setItem(self.rowCount()-1, 0, newType)
        self.setItem(self.rowCount()-1, 1, newName)
        
    def nodeToItem(self, node):
        '''Extract nice name and exo type from node'''
        exoName = cmds.getAttr('{0}.exo_name'.format(node))
        exoName_item = QtWidgets.QTableWidgetItem(exoName)
        
        exoType = cmds.getAttr('{0}.exo_type'.format(node))
        exoType_item = QtWidgets.QTableWidgetItem(exoType)
        
        return exoName_item, exoType_item
        
class wdg_options(QtWidgets.QGroupBox):
    def __init__(self, parent):
        super(wdg_options, self).__init__(parent)
        
        self.mainWindow = parent
        self.currentCtrl = ''
        
        gb_name = 'Options'
        self.setTitle(gb_name)
        
        btnLay = self.create_buttons()
        
        mainLay = QtWidgets.QVBoxLayout()
        mainLay.addLayout(btnLay)
        self.setLayout(mainLay)
        
    def changeState(self, selCtrl):
        '''Determine if the widget should be disabled'''
        if selCtrl == []:
            self.currentCtrl = ''
            self.setEnabled(False)
        else:
            self.currentCtrl = selCtrl[1].text()
            self.setEnabled(True)
            
            #toggle enabled for bakeBtn
            if selCtrl[0].text() == 'control':
                self.bakeBtn.setEnabled(False)
            else:
                self.bakeBtn.setEnabled(True)
                        
    def create_buttons(self):
        '''Create two buttons. A bake button, and a delete button.'''
        self.bakeBtn = QtWidgets.QPushButton('Bake', self)
        self.bakeBtn.released.connect(self.bakeCtrl)
        
        remBtn = QtWidgets.QPushButton('Delete', self)
        remBtn.setStyleSheet('background-color: darkred')
        remBtn.released.connect(self.removeCtrl)
        
        btnLay = QtWidgets.QHBoxLayout()
        btnLay.addWidget(self.bakeBtn)
        btnLay.addWidget(remBtn)
        
        return btnLay
        
    def bakeCtrl(self):
        '''Bake control'''
        submaster_ctrl = '{0}_master'.format(self.currentCtrl)
        ctrls = cmds.getAttr('{0}.controls_used'.format(submaster_ctrl))
        startTime = cmds.playbackOptions(q = True, minTime = True)
        endTime = cmds.playbackOptions(q = True, maxTime = True)
        
        cmds.bakeResults(ctrls, simulation = True, time = (startTime, endTime))
        
        self.removeCtrl()

    def removeCtrl(self):
        '''Remove control'''
        submaster_ctrl = '{0}_master'.format(self.currentCtrl)
        cmds.delete(submaster_ctrl)
        self.mainWindow.refresh()
        