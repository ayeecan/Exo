from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtWidgets
from maya import cmds

import widgets as wdg
from Exo.Core import build

reload(wdg)
reload(build)

class ExoWindow(MayaQWidgetDockableMixin, QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        super(ExoWindow, self).__init__(parent = parent)
    
        #INFO
        self.version_number = '1.0.0'
        self.exo_name = 'Exo Tools'
        self.setWindowTitle(self.exo_name)
        
        #MENU BAR
        createBar = self.createMenu('Create')
        self.menuBar().addMenu(createBar)
        self.ctrl_name = 'Control'
        self.jig_name = 'Jiggle'
        self.fkik_name = 'FK/IK Match'
        
        createActions_list = []
        
        act_ctrl = self.createAction(self.ctrl_name, 0)
        createActions_list.append(act_ctrl)
        
        act_jig  = self.createAction(self.jig_name, 1)
        createActions_list.append(act_jig)
        
        act_fkik = self.createAction(self.fkik_name, 2)
        ###
        act_fkik.setVisible(False)
        ###
        createActions_list.append(act_fkik)
        
        createBar.addActionMany(createActions_list)

        self.about_name = 'About'
        act_abt = self.createAction(self.about_name, 3)
        self.menuBar().addAction(act_abt)
        
        #MAIN WIDGET
        mainWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(mainWidget)
        
        self.createMaster()
        
        self.exoList = self.createList()
        self.exoList.itemSelectionChanged.connect(self.changeOptions)
        exoList_update = QtWidgets.QPushButton('Refresh', self)
        exoList_update.released.connect(self.refresh)
        
        exoList_lay = QtWidgets.QVBoxLayout()
        exoList_lay.addWidget(exoList_update)
        exoList_lay.addWidget(self.exoList)
        exoList_lay.addStretch()
        
        self.exoOptions = wdg.wdg_options(self)
        self.changeOptions()
        
        mainLayout = QtWidgets.QVBoxLayout(mainWidget)
        mainLayout.addLayout(exoList_lay)
        mainLayout.addStretch()
        mainLayout.addWidget(self.exoOptions)
        
    def createMenu(self, name):
        '''Create a QMenu'''
        newMenu = wdg.wdg_menu(self)
        newMenu.setTitle(name)
        
        return newMenu
    
    def createAction(self, name, actType):
        '''Create a QAction'''
        newAction = wdg.wdg_action(self)
        newAction.setText(name)
        newAction.setVersion(self.exo_name, self.version_number)
        newAction.setActionType(actType)
        
        return newAction
        
    def createList(self):
        '''Create a QTableWidget'''
        newList = wdg.wdg_table(self)
        newList.setColumnCount(2)
        newList.setHorizontalHeaderLabels(['Type', 'Name'])
        newList.horizontalHeader().setStretchLastSection(True)
        newList.verticalHeader().hide()
        newList.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        newList.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        newList.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        
        newList.getExo()
        
        return newList

    def changeOptions(self):
        '''Change options widget'''
        selCtrl = self.exoList.selectedItems()
        self.exoOptions.changeState(selCtrl)
        
    def createMaster(self):
        '''Create a master Exo node if there is none'''
        master_name = 'exo_master'
        if not cmds.objExists(master_name):
            build.null(master_name)
            
        cmds.select(clear = True)
            
        return master_name
        
    def refresh(self):
        '''Refresh exoList'''
        self.exoList.getExo()
        
def launchUI():
    window = None
    uiName = 'ExoUI'
    
    if uiName in globals() and globals()[uiName].isVisible():
        window = globals()[uiName]
        if window.isVisible():
            window.show()
            window.raise_()
            return None
        
    nuWindow = ExoWindow()
    globals()[uiName] = nuWindow
    nuWindow.show(dockable = True, floating = True)