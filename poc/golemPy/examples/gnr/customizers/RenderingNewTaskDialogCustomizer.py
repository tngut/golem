import os
from PyQt4 import QtCore
from PyQt4.QtGui import QFileDialog
from copy import deepcopy

from examples.gnr.ui.AddTaskResourcesDialog import AddTaskResourcesDialog

from examples.gnr.customizers.NewTaskDialogCustomizer import NewTaskDialogCustomizer

from AddResourcesDialogCustomizer import AddResourcesDialogCustomizer
from examples.gnr.RenderingTaskState import RenderingTaskState, RenderingTaskDefinition, AdvanceRenderingVerificationOptions
from golem.task.TaskState import TaskStatus
from TimeHelper import setTimeSpinBoxes, getTimeValues

import logging

logger = logging.getLogger(__name__)

class RenderingNewTaskDialogCustomizer ( NewTaskDialogCustomizer ):

    #############################
    def _setupConnections( self ):
        NewTaskDialogCustomizer._setupConnections( self )
        self._setupRenderersConnections()
        self._setupOutputConnections()
        self._setupVerificationConnections()

    #############################
    def _setupRenderersConnections( self ):
        QtCore.QObject.connect( self.gui.ui.rendererComboBox, QtCore.SIGNAL( "currentIndexChanged( const QString )" ), self.__rendererComboBoxValueChanged )
        self.gui.ui.rendererOptionsButton.clicked.connect( self.__openRendererOptions )

    #############################
    def _setupOutputConnections( self ):
        self.gui.ui.chooseOutputFileButton.clicked.connect( self.__chooseOutputFileButtonClicked )
        QtCore.QObject.connect(self.gui.ui.outputResXSpinBox, QtCore.SIGNAL("valueChanged( const QString )"), self.__resXChanged)
        QtCore.QObject.connect(self.gui.ui.outputResYSpinBox, QtCore.SIGNAL("valueChanged( const QString )"), self.__resYChanged)

    #############################
    def _setupAdvanceNewTaskConnections( self ):
        NewTaskDialogCustomizer._setupAdvanceNewTaskConnections( self )
        self.gui.ui.testTaskButton.clicked.connect( self.__testTaskButtonClicked )
        self.gui.ui.resetToDefaultButton.clicked.connect( self.__resetToDefaultButtonClicked )

        QtCore.QObject.connect(self.gui.ui.fullTaskTimeoutHourSpinBox, QtCore.SIGNAL("valueChanged( const QString )"), self.__taskSettingsChanged)
        QtCore.QObject.connect(self.gui.ui.fullTaskTimeoutMinSpinBox, QtCore.SIGNAL("valueChanged( const QString )"), self.__taskSettingsChanged)
        QtCore.QObject.connect(self.gui.ui.fullTaskTimeoutSecSpinBox, QtCore.SIGNAL("valueChanged( const QString )"), self.__taskSettingsChanged)
        QtCore.QObject.connect(self.gui.ui.minSubtaskTimeHourSpinBox, QtCore.SIGNAL("valueChanged( const QString )"), self.__taskSettingsChanged)
        QtCore.QObject.connect(self.gui.ui.minSubtaskTimeMinSpinBox, QtCore.SIGNAL("valueChanged( const QString )"), self.__taskSettingsChanged)
        QtCore.QObject.connect(self.gui.ui.minSubtaskTimeSecSpinBox, QtCore.SIGNAL("valueChanged( const QString )"), self.__taskSettingsChanged)
        QtCore.QObject.connect(self.gui.ui.subtaskTimeoutHourSpinBox, QtCore.SIGNAL("valueChanged( const QString )"), self.__taskSettingsChanged)
        QtCore.QObject.connect(self.gui.ui.subtaskTimeoutMinSpinBox, QtCore.SIGNAL("valueChanged( const QString )"), self.__taskSettingsChanged)
        QtCore.QObject.connect(self.gui.ui.subtaskTimeoutSecSpinBox, QtCore.SIGNAL("valueChanged( const QString )"), self.__taskSettingsChanged)
        QtCore.QObject.connect(self.gui.ui.mainProgramFileLineEdit, QtCore.SIGNAL("textChanged( const QString )"), self.__taskSettingsChanged)
        QtCore.QObject.connect(self.gui.ui.outputFormatsComboBox, QtCore.SIGNAL("currentIndexChanged( const QString )"), self.__taskSettingsChanged)
        QtCore.QObject.connect(self.gui.ui.outputFileLineEdit, QtCore.SIGNAL("textChanged( const QString )"), self.__taskSettingsChanged)
        QtCore.QObject.connect(self.gui.ui.totalSpinBox, QtCore.SIGNAL( "valueChanged( const QString )" ), self.__taskSettingsChanged )
        QtCore.QObject.connect(self.gui.ui.verificationSizeXSpinBox, QtCore.SIGNAL( "valueChanged( const QString )" ), self.__taskSettingsChanged )
        QtCore.QObject.connect(self.gui.ui.verificationSizeYSpinBox, QtCore.SIGNAL( "valueChanged( const QString )" ), self.__taskSettingsChanged )
        QtCore.QObject.connect(self.gui.ui.verificationForAllRadioButton, QtCore.SIGNAL( "toggled( bool )" ), self.__taskSettingsChanged )
        QtCore.QObject.connect(self.gui.ui.verificationForFirstRadioButton, QtCore.SIGNAL( "toggled( bool )" ), self.__taskSettingsChanged )
        QtCore.QObject.connect(self.gui.ui.probabilityLineEdit, QtCore.SIGNAL( "valueChanged( const QString )" ), self.__taskSettingsChanged )

    #############################
    def _setupVerificationConnections( self ):
        QtCore.QObject.connect(self.gui.ui.verificationRandomRadioButton, QtCore.SIGNAL( "toggled( bool )" ), self.__verificationRandomChanged )
        QtCore.QObject.connect(self.gui.ui.advanceVerificationCheckBox, QtCore.SIGNAL( "stateChanged( int )" ), self.__advanceVerificationChanged )

    #############################
    def _init( self ):
        self._setUid()

        renderers = self.logic.getRenderers()
        dr = self.logic.getDefaultRenderer()
        self.rendererOptions = dr.options()

        for k in renderers:
            r = renderers[ k ]
            self.gui.ui.rendererComboBox.addItem( r.name )

        self.gui.ui.totalSpinBox.setRange( dr.defaults.minSubtasks, dr.defaults.maxSubtasks )
        self.gui.ui.totalSpinBox.setValue( dr.defaults.defaultSubtasks )

        self.gui.ui.outputResXSpinBox.setValue ( dr.defaults.resolution[0] )
        self.gui.ui.outputResYSpinBox.setValue ( dr.defaults.resolution[1] )
        self.gui.ui.verificationSizeXSpinBox.setMaximum( dr.defaults.resolution[0] )
        self.gui.ui.verificationSizeYSpinBox.setMaximum( dr.defaults.resolution[1] )

    #############################
    def __updateRendererOptions( self, name ):
        r = self.logic.getRenderer( name )

        if r:
            self.logic.setCurrentRenderer( name )
            self.rendererOptions = r.options()

            self.gui.ui.outputFormatsComboBox.clear()
            self.gui.ui.outputFormatsComboBox.addItems( r.outputFormats )

            for i in range( len( r.outputFormats ) ):
                if r.outputFormats[ i ] == r.defaults.outputFormat:
                    self.gui.ui.outputFormatsComboBox.setCurrentIndex( i )

            self.gui.ui.mainProgramFileLineEdit.setText( r.defaults.mainProgramFile )

            setTimeSpinBoxes( self.gui, r.defaults.fullTaskTimeout, r.defaults.subtaskTimeout, r.defaults.minSubtaskTime )

            self.gui.ui.totalSpinBox.setRange( r.defaults.minSubtasks, r.defaults.maxSubtasks )

        else:
            assert False, "Unreachable"

    #############################
    def __resetToDefaults( self ):
        dr = self.__getCurrentRenderer()

        self.rendererOptions = dr.options()
        self.logic.setCurrentRenderer( dr.name )

        self.gui.ui.outputFormatsComboBox.clear()
        self.gui.ui.outputFormatsComboBox.addItems( dr.outputFormats )

        for i in range( len( dr.outputFormats ) ):
            if dr.outputFormats[ i ] == dr.defaults.outputFormat:
                self.gui.ui.outputFormatsComboBox.setCurrentIndex( i )

        self.gui.ui.mainProgramFileLineEdit.setText( dr.defaults.mainProgramFile )

        setTimeSpinBoxes( self.gui, dr.defaults.fullTaskTimeout, dr.defaults.subtaskTimeout, dr.defaults.minSubtaskTime )

        self.gui.ui.outputFileLineEdit.clear()

        self.gui.ui.outputResXSpinBox.setValue( dr.defaults.resolution[0] )
        self.gui.ui.outputResYSpinBox.setValue( dr.defaults.resolution[1] )

        if self.addTaskResourceDialog:
            self.addTaskResourcesDialogCustomizer.resources = set()
            self.addTaskResourcesDialogCustomizer.gui.ui.mainSceneLabel.clear()
            self.addTaskResourceDialog.ui.folderTreeView.model().addStartFiles([])
            self.addTaskResourceDialog.ui.folderTreeView.model().checks = {}

        self._changeFinishState( False )

        self.gui.ui.totalSpinBox.setRange( dr.defaults.minSubtasks, dr.defaults.maxSubtasks )
        self.gui.ui.totalSpinBox.setValue( dr.defaults.defaultSubtasks )
        self.gui.ui.totalSpinBox.setEnabled( True )
        self.gui.ui.optimizeTotalCheckBox.setChecked( False )

    # SLOTS
    #############################
    def __taskTableRowClicked( self, row ):
        if row < self.gui.ui.taskTableWidget.rowCount():
            taskId = self.gui.ui.taskTableWidget.item( row, 0 ).text()
            taskId = "{}".format( taskId )
            self.updateTaskAdditionalInfo( taskId )

    #############################
    def __showNewTaskDialogClicked( self ):
        renderers = self.logic.getRenderers()
            
        self.__setupNewTaskDialogConnections( self.gui.ui )

        self.gui.ui.taskIdLabel.setText( self._generateNewTaskUID() )

        for k in renderers:
            r = renderers[ k ]
            self.gui.ui.rendererComboBox.addItem( r.name )

    #############################
    def __rendererComboBoxValueChanged( self, name ):
        self.__updateRendererOptions( "{}".format( name ) )

    #############################
    def __taskSettingsChanged( self, name = None ):
        self._changeFinishState( False )

    #############################
    def __chooseOutputFileButtonClicked( self ):

        cr = self.logic.getCurrentRenderer()

        outputFileType = u"{}".format( self.gui.ui.outputFormatsComboBox.currentText() )
        filter = u"{} (*.{})".format( outputFileType, outputFileType )

        dir = os.path.dirname( u"{}".format( self.gui.ui.outputFileLineEdit.text() )  )

        fileName = u"{}".format( QFileDialog.getSaveFileName( self.gui.window,
            "Choose output file", dir, filter ) )

        if fileName != '':
            self.gui.ui.outputFileLineEdit.setText( fileName )
            self._changeFinishState( False )

    def _changeFinishState( self, state ):
        self.gui.ui.finishButton.setEnabled( state )
        self.gui.ui.testTaskButton.setEnabled( not state )

    #############################
    def _chooseMainProgramFileButtonClicked( self ):

        dir = os.path.dirname( u"{}".format( self.gui.ui.mainProgramFileLineEdit.text() ) )

        fileName = u"{}".format( QFileDialog.getOpenFileName( self.gui.window,
            "Choose main program file", dir, "Python (*.py)") )

        if fileName != '':
            self.gui.ui.mainProgramFileLineEdit.setText( fileName )
            self._changeFinishState( False )

    ############################
    def _showAddResourcesDialog( self ):
        NewTaskDialogCustomizer._showAddResourcesDialog( self )
        self._changeFinishState( False )

    ############################
    def loadTaskDefinition( self, taskDefinition ):
        assert isinstance( taskDefinition, RenderingTaskDefinition )

        definition = deepcopy( taskDefinition )
        self.gui.ui.taskIdLabel.setText( self._generateNewTaskUID() )

        self._loadRendererParams( definition )
        self._loadBasicTaskParams( definition )
        self._loadAdvanceTaskParams( definition )
        self._loadResources( definition )
        self._loadVerificationParams( definition )

    ############################
    def _loadRendererParams( self, definition ):
        rendererItem = self.gui.ui.rendererComboBox.findText( definition.renderer )
        if rendererItem >= 0:
            self.gui.ui.rendererComboBox.setCurrentIndex( rendererItem )
        else:
            logger.error( "Cannot load task, wrong renderer" )
            return

        self.rendererOptions = deepcopy( definition.rendererOptions )

        self.gui.ui.outputResXSpinBox.setValue( definition.resolution[ 0 ] )
        self.gui.ui.outputResYSpinBox.setValue( definition.resolution[ 1 ] )
        self.gui.ui.outputFileLineEdit.setText( definition.outputFile )

        outputFormatItem = self.gui.ui.outputFormatsComboBox.findText( definition.outputFormat )

        if outputFormatItem >= 0:
            self.gui.ui.outputFormatsComboBox.setCurrentIndex( outputFormatItem )
        else:
            logger.error( "Cannot load task, wrong output format" )
            return

        if os.path.normpath( definition.mainSceneFile ) in definition.resources:
            definition.resources.remove( os.path.normpath( definition.mainSceneFile ) )
        definition.resources = definition.rendererOptions.removeFromResources( definition.resources )

    ############################
    def _loadBasicTaskParms( self, definition ):
        NewTaskDialogCustomizer._loadBasicTaskParams( definition )
        r = self.logic.getRenderer( definition.renderer )
        self.gui.ui.totalSpinBox.setRange( r.defaults.minSubtasks, r.defaults.maxSubtasks )

    ############################
    def _loadResources( self, definition ):
        if os.path.normpath( definition.mainSceneFile ) in definition.resources:
            definition.resources.remove( os.path.normpath( definition.mainSceneFile ) )
        definition.resources = definition.rendererOptions.removeFromResources( definition.resources )

        NewTaskDialogCustomizer._loadResources( self, definition )

        self.addTaskResourcesDialogCustomizer.gui.ui.mainSceneLabel.setText( definition.mainSceneFile )

    ############################
    def _loadVerificationParams( self, definition ):
        enabled = definition.verificationOptions is not None

        self.__setVerificationWidgetsState( enabled )
        if enabled:
            self.gui.ui.advanceVerificationCheckBox.setCheckState( QtCore.Qt.Checked )
            self.gui.ui.verificationSizeXSpinBox.setValue( definition.verificationOptions.boxSize[0])
            self.gui.ui.verificationSizeYSpinBox.setValue( definition.verificationOptions.boxSize[1])
            self.gui.ui.verificationForAllRadioButton.setChecked( definition.verificationOptions.type == 'forAll' )
            self.gui.ui.verificationForFirstRadioButton.setChecked( definition.verificationOptions.type == 'forFirst' )
            self.gui.ui.verificationRandomRadioButton.setChecked( definition.verificationOptions.type == 'random' )
            self.gui.ui.probabilityLabel.setEnabled( definition.verificationOptions.type == 'random')
            self.gui.ui.probabilityLineEdit.setEnabled( definition.verificationOptions.type == 'random')
            if hasattr( definition.verificationOptions, 'probability' ):
                self.gui.ui.probabilityLineEdit.setText( "{}".format( definition.verificationOptions.probability ) )
        else:
            self.gui.ui.advanceVerificationCheckBox.setCheckState( QtCore.Qt.Unchecked )

    ############################
    def __setVerificationWidgetsState( self, state ):
        self.gui.ui.verificationForAllRadioButton.setEnabled( state )
        self.gui.ui.verificationForFirstRadioButton.setEnabled( state )
        self.gui.ui.verificationSizeXSpinBox.setEnabled( state )
        self.gui.ui.verificationSizeYSpinBox.setEnabled( state )
        self.gui.ui.verificationRandomRadioButton.setEnabled( state )
        self.gui.ui.probabilityLabel.setEnabled( state and self.gui.ui.verificationRandomRadioButton.isChecked() )
        self.gui.ui.probabilityLineEdit.setEnabled( state and self.gui.ui.verificationRandomRadioButton.isChecked() )

    ############################
    def __testTaskButtonClicked( self ):
        self.taskState = RenderingTaskState()
        self.taskState.status = TaskStatus.notStarted
        self.taskState.definition = self._queryTaskDefinition()
        
        if not self.logic.runTestTask( self.taskState ):
            logger.error( "Task not tested properly" )

    #############################
    def testTaskComputationFinished( self, success, estMem ):
        if success:
            self.taskState.definition.estimatedMemory  = estMem
            self._changeFinishState( True )

    #############################
    def _finishButtonClicked( self ):
        self._addCurrentTask()

    #############################
    def _cancelButtonClicked( self ):
        self.__resetToDefaults()
        NewTaskDialogCustomizer._cancelButtonClicked( self )

    #############################
    def __resetToDefaultButtonClicked( self ):
        self.__resetToDefaults()

    #############################
    def __getCurrentRenderer( self ):
        index = self.gui.ui.rendererComboBox.currentIndex()
        rendererName = self.gui.ui.rendererComboBox.itemText( index )
        return self.logic.getRenderer( u"{}".format( rendererName ) )

    #############################
    def _queryTaskDefinition( self ):
        definition = RenderingTaskDefinition()
        definition = self._readRendererParams( definition )
        definition = self._readBasicTaskParams( definition )
        definition = self._readAdvanceVerificationParams( definition )

        return definition

    #############################
    def _readRendererParams( self, definition ):
        definition.renderer          = self.__getCurrentRenderer().name
        definition.rendererOptions   = deepcopy( self.rendererOptions )
        definition.resolution        = [ self.gui.ui.outputResXSpinBox.value(), self.gui.ui.outputResYSpinBox.value() ]
        definition.outputFile        = u"{}".format( self.gui.ui.outputFileLineEdit.text() )
        definition.outputFormat      = u"{}".format( self.gui.ui.outputFormatsComboBox.itemText( self.gui.ui.outputFormatsComboBox.currentIndex() ) )

        if self.addTaskResourcesDialogCustomizer:
            definition.resources         = self.rendererOptions.addToResources( self.addTaskResourcesDialogCustomizer.resources )
            definition.mainSceneFile     = u"{}".format( self.addTaskResourcesDialogCustomizer.gui.ui.mainSceneLabel.text() )

            definition.resources.add( os.path.normpath( definition.mainSceneFile ) )
        return definition

    #############################
    def _readAdvanceVerificationParams( self, definition ):
        if self.gui.ui.advanceVerificationCheckBox.isChecked():
            definition.verificationOptions = AdvanceRenderingVerificationOptions()
            if self.gui.ui.verificationForAllRadioButton.isChecked():
                definition.verificationOptions.type = 'forAll'
            elif self.gui.ui.verificationForFirstRadioButton.isChecked():
                definition.verificationOptions.type = 'forFirst'
            else:
                definition.verificationOptions.type = 'random'
                try:
                    definition.verificationOptions.probability = float( self.gui.ui.probabilityLineEdit.text() )
                    if definition.verificationOptions.probability < 0:
                        definition.verificationOptions.probability = 0.0
                        self.gui.ui.probabilityLineEdit.setText( "0.0" )
                    if definition.verificationOptions.probability > 1:
                        definition.verificationOptions.probability = 1.0
                        self.gui.ui.probabilityLineEdit.setText( "1.0" )
                    print definition.verificationOptions.probability
                except:
                    logger.warning("Wrong probability values {}".format( self.gui.ui.probabilityLineEdit.text() ) )
                    definition.verificationOptions.probability = 0.0
                    self.gui.ui.probabilityLineEdit.setText( "0.0" )
            definition.verificationOptions.boxSize = ( int( self.gui.ui.verificationSizeXSpinBox.value() ), int( self.gui.ui.verificationSizeYSpinBox.value() ) )
        else:
            definition.verificationOptions = None

        return definition

    def _optimizeTotalCheckBoxChanged( self ):
        NewTaskDialogCustomizer._optimizeTotalCheckBoxChanged( self )
        self.__taskSettingsChanged()

    #############################
    def __openRendererOptions( self ):
         rendererName = self.gui.ui.rendererComboBox.itemText( self.gui.ui.rendererComboBox.currentIndex() )
         renderer = self.logic.getRenderer( u"{}".format( rendererName ) )
         dialog = renderer.dialog
         dialogCustomizer = renderer.dialogCustomizer
         rendererDialog = dialog( self.gui.window )
         rendererDialogCustomizer = dialogCustomizer( rendererDialog, self.logic, self )
         rendererDialog.show()

    def setRendererOptions( self, options ):
        self.rendererOptions = options
        self.__taskSettingsChanged()

    def getRendererOptions( self ):
        return self.rendererOptions

    #############################
    def __advanceVerificationChanged( self ):
        state = self.gui.ui.advanceVerificationCheckBox.isChecked()
        self.__setVerificationWidgetsState( state )
        self.__taskSettingsChanged()

    #############################
    def __resXChanged( self ):
        self.gui.ui.verificationSizeXSpinBox.setMaximum( self.gui.ui.outputResXSpinBox.value() )
        self.__taskSettingsChanged()

    #############################
    def __resYChanged( self ):
        self.gui.ui.verificationSizeYSpinBox.setMaximum( self.gui.ui.outputResYSpinBox.value() )
        self.__taskSettingsChanged()

    #############################
    def __verificationRandomChanged( self ):
        randSet =  self.gui.ui.verificationRandomRadioButton.isChecked()
        self.gui.ui.probabilityLineEdit.setEnabled( randSet )
        self.gui.ui.probabilityLabel.setEnabled( randSet )
        self.__taskSettingsChanged()