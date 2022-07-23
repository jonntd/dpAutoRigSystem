# importing libraries:
from maya import cmds
from maya import mel
from ..Modules.Library import dpControls
from ..Modules.Library import dpUtils


# global variables to this module:    
CLASS_NAME = "CorrectionManager"
TITLE = "m068_correctionManager"
DESCRIPTION = "m069_correctionManagerDesc"
ICON = "/Icons/dp_correctionManager.png"

DPCORRECTIONMANAGER_VERSION = 2.1


class CorrectionManager(object):
    def __init__(self, dpUIinst, langDic, langName, presetDic, presetName, ui=True, *args, **kwargs):
        # redeclaring variables
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        self.presetDic = presetDic
        self.presetName = presetName
        self.ui = ui
        self.ctrls = dpControls.ControlClass(self.dpUIinst, self.presetDic, self.presetName)
        self.correctionManagerName = self.langDic[self.langName]['m068_correctionManager']
        self.netSuffix = "Net"
        self.correctionManagerDataGrp = "CorrectionManager_Data_Grp"
        self.netList = []
        self.net = None
        # call main UI function
        if self.ui:
            self.closeUI()
            self.mainUI()
            self.refreshUI()
            

    def refreshUI(self, *args):
        """ Just call populate UI and actualize layout methodes.
        """
        self.populateNetUI()
        self.actualizeEditLayout()

        
    def closeUI(self, *args):
        """ Delete existing CorrectionManager window if it exists.
        """
        if cmds.window('dpCorrectionManagerWindow', query=True, exists=True):
            cmds.deleteUI('dpCorrectionManagerWindow', window=True)


    def mainUI(self, *args):
        """ Create window, layouts and elements for the main UI.
            This is based in the old dpPoseReader, now without PyMEL or Qt.
        """
        # window
        correctionManager_winWidth  = 380
        correctionManager_winHeight = 300
        cmds.window('dpCorrectionManagerWindow', title=self.correctionManagerName+" "+str(DPCORRECTIONMANAGER_VERSION), widthHeight=(correctionManager_winWidth, correctionManager_winHeight), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
        cmds.showWindow('dpCorrectionManagerWindow')
        # create UI layout and elements:
        correctionManagerLayout = cmds.columnLayout('correctionManagerLayout', adjustableColumn=True, columnOffset=("both", 10))
        cmds.text("infoTxt", label=self.langDic[self.langName]['m066_selectTwo'], align="left", height=30, font='boldLabelFont', parent=correctionManagerLayout)
        correctionManagerLayoutA = cmds.rowColumnLayout('correctionManagerLayoutA', numberOfColumns=2, columnWidth=[(1, 100), (2, 280)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'both', 10), (2, 'both', 10)], parent=correctionManagerLayout)
        self.createBT = cmds.button('createBT', label=self.langDic[self.langName]['i158_create'], command=self.createCorrectionManager, backgroundColor=(0.7, 1.0, 0.7), parent=correctionManagerLayoutA)
        self.createTF = cmds.textField('createTF', editable=True, parent=correctionManagerLayoutA)
        cmds.separator(style='none', height=10, width=100, parent=correctionManagerLayout)
        refreshLayout = cmds.rowColumnLayout('refreshLayoutA', numberOfColumns=3, columnWidth=[(1, 50), (2, 250), (3, 80)], columnAlign=[(1, 'left'), (2, 'left'), (3, 'left')], columnAttach=[(1, 'both', 10), (2, 'left', 0), (3, 'both', 10)], parent=correctionManagerLayout)
        cmds.text(self.langDic[self.langName]['i138_type'], parent=refreshLayout)
        radioLayout = cmds.columnLayout("radioLayout", parent=refreshLayout)
        self.correctTypeCollection = cmds.radioCollection("correctTypeCollection", parent=radioLayout)
        typeAngle = cmds.radioButton(label=self.langDic[self.langName]['c102_angle'].capitalize(), annotation="Angle", collection=self.correctTypeCollection)
        typeDistance = cmds.radioButton(label=self.langDic[self.langName]['m182_distance'], annotation="Distance", collection=self.correctTypeCollection)
        cmds.radioCollection(self.correctTypeCollection, edit=True, select=typeAngle)
        cmds.refreshBT = cmds.button('refreshBT', label=self.langDic[self.langName]['m181_refresh'], command=self.refreshUI, parent=refreshLayout)
        cmds.separator(style='in', height=15, width=100, parent=correctionManagerLayout)
        # existing:
        cmds.text("existingTxt", label=self.langDic[self.langName]['m071_existing'], align="left", height=25, font='boldLabelFont', parent=correctionManagerLayout)
        self.existingNetTSL = cmds.textScrollList('existingNetTSL', width=20, allowMultiSelection=False, selectCommand=self.actualizeEditLayout, parent=correctionManagerLayout)
        cmds.separator(style='none', height=10, width=100, parent=correctionManagerLayout)
        # edit selected net layout:
        self.editSelectedNetLayout = cmds.frameLayout('editSelectedNetLayout', label=self.langDic[self.langName]['i011_editSelected'], collapsable=True, collapse=False, parent=correctionManagerLayout)
        

    def renameLinkedNodes(self, oldName, name, *args):
        """ List all connected nodes by message into the network and rename them using given parameters.
        """
        messageAttrList = []
        attrList = cmds.listAttr(self.net)
        for attr in attrList:
            if cmds.getAttr(self.net+"."+attr, type=True) == "message":
                messageAttrList.append(attr)
        if messageAttrList:
            for messageAttr in messageAttrList:
                connectedNodeList = cmds.listConnections(self.net+"."+messageAttr)
                if connectedNodeList:
                    childrenList = cmds.listRelatives(connectedNodeList[0], children=True, allDescendents=True)
                    cmds.rename(connectedNodeList[0], connectedNodeList[0].replace(oldName, name))
                    if childrenList:
                        for children in childrenList:
                            try:
                                cmds.rename(children, children.replace(oldName, name))
                            except:
                                pass


    def changeName(self, name=None, *args):
        """ Edit name of the current network node selected.
            If there isn't any given name, it will try to get from the UI.
            Returns the name result.
        """
        oldName = cmds.getAttr(self.net+".name")
        if not name:
            if self.ui:
                name = cmds.textFieldGrp(self.nameTFG, query=True, text=True)
        if name:
            name = dpUtils.resolveName(name, self.netSuffix)[0]
            self.renameLinkedNodes(oldName, name)
            cmds.setAttr(self.net+".name", name, type="string")
            self.net = cmds.rename(self.net, self.net.replace(oldName, name))
            if self.ui:
                self.populateNetUI()
                #self.actualizeEditLayout() #Bug: if we call this method here it will crash Maya! Error report: 322305477
                cmds.textFieldGrp(self.nameTFG, label=self.langDic[self.langName]['m006_name'], edit=True, text=name)
        return name


    def changeAxis(self, axis=None, *args):
        """ Update the setup to read the correct axis to extract angle.
        """
        cmds.setAttr(self.net+".axis", self.axisMenuItemList.index(axis.upper()))
        # get connected nodes
        extractAngleQtE = dpUtils.getNodeByMessage("extractAngleQtE", self.net)
        inputRmV = dpUtils.getNodeByMessage("inputRmV", self.net)
        # clean up old unitConversion node:
        unitConvToDelete = cmds.listConnections(inputRmV+".inputValue", source=True, destination=False)[0]
        cmds.disconnectAttr(unitConvToDelete+".output", inputRmV+".inputValue")
        cmds.setAttr(self.net+".inputValue", lock=False)
        cmds.disconnectAttr(unitConvToDelete+".output", self.net+".inputValue")
        cmds.delete(unitConvToDelete)
        # make a new connection using choose axis:
        cmds.connectAttr(extractAngleQtE+".outputRotate"+axis.upper(), inputRmV+".inputValue", force=True)
        newUnitConv = cmds.listConnections(inputRmV+".inputValue", source=True, destination=False)[0]
        cmds.connectAttr(newUnitConv+".output", self.net+".inputValue", force=True)
        cmds.setAttr(self.net+".inputValue", lock=True)
        
        
    def changeAxisOrder(self, axisOrder=None, *args):
        """ Update the setup to set the correct axis order to extract angle.
        """
        axisOrder = self.axisOrderMenuItemList.index(axisOrder.upper())
        cmds.setAttr(self.net+".axisOrder", axisOrder)
        # get extract angle nodes to change connections from network message attributes:
        extractAngleDM = dpUtils.getNodeByMessage("extractAngleDM", self.net)
        extractAngleQtE = dpUtils.getNodeByMessage("extractAngleQtE", self.net)
        cmds.setAttr(extractAngleDM+".inputRotateOrder", axisOrder)
        cmds.setAttr(extractAngleQtE+".inputRotateOrder", axisOrder)


    def changeInputValues(self, minValue=None, maxValue=None, *args):
        """ Update the setup to set the choose input min and max values.
            That means we can read the angle or distance in this given range.
        """
        cmds.setAttr(self.net+".inputMin", minValue)
        cmds.setAttr(self.net+".inputMax", maxValue)


    def changeOutputValues(self, minValue=None, maxValue=None, *args):
        """ Update the setup to set the choose output min and max values.
            That means we can output the final value in this given range.
        """
        cmds.setAttr(self.net+".outputMin", minValue)
        cmds.setAttr(self.net+".outputMax", maxValue)


    def deleteSetup(self, *args):
        """ Just delete 2 nodes to clear this current system setup:
            - Correction Data Group
            - Network Data Node
        """
        cmds.delete(dpUtils.getNodeByMessage("correctionDataGrp", self.net))
        cmds.delete(self.net)
        if self.ui:
            self.populateNetUI()
            self.actualizeEditLayout()


    def recreateSelectedLayout(self, node=None, *args):
        """ It will recreate the edit layout for the selected network node.
        """
        if self.net:
            if cmds.objExists(self.net):
                # name:
                self.selectedLayout = cmds.columnLayout('selectedLayout', adjustableColumn=True, parent=self.editSelectedNetLayout)
                self.nameLayout = cmds.rowLayout('nameLayout', numberOfColumns=2, columnWidth2=(220, 50), columnAlign=[(1, 'left'), (2, 'right')], adjustableColumn=1, columnAttach=[(1, 'right', 50), (2, 'right', 2)], height=30, parent=self.selectedLayout)
                currentName = cmds.getAttr(self.net+".name")
                self.nameTFG = cmds.textFieldGrp("nameTFG", label=self.langDic[self.langName]['m006_name'], text=currentName, editable=True, columnWidth2=(40, 180), columnAttach=[(1, 'right', 2), (2, 'left', 2)], adjustableColumn2=2, changeCommand=self.changeName, parent=self.nameLayout)
                self.delete_BT = cmds.button('delete_BT', label=self.langDic[self.langName]['m005_delete'], command=self.deleteSetup, backgroundColor=(1.0, 0.7, 0.7), parent=self.nameLayout)
                # axis:
                self.axisLayout = cmds.rowLayout('axisLayout', numberOfColumns=5, columnWidth5=(40, 50, 80, 50, 10), columnAlign=[(1, 'right'), (2, 'left'), (3, 'right'), (4, 'left'), (5, 'left')], adjustableColumn=5, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'right', 2), (4, 'left', 2), (5, 'left', 10)], height=30, parent=self.selectedLayout)
                cmds.text("axisTxt", label=self.langDic[self.langName]['i052_axis'], parent=self.axisLayout)
                self.axisMenu = cmds.optionMenu("axisMenu", label='', changeCommand=self.changeAxis, parent=self.axisLayout)
                self.axisMenuItemList = ['X', 'Y', 'Z']
                for axis in self.axisMenuItemList:
                    cmds.menuItem(label=axis, parent=self.axisMenu)
                currentAxis = cmds.getAttr(self.net+".axis")
                cmds.optionMenu(self.axisMenu, edit=True, value=self.axisMenuItemList[currentAxis])
                # axis order:
                cmds.text("axisOrderTxt", label=self.langDic[self.langName]['i052_axis']+" "+self.langDic[self.langName]['m045_order'], parent=self.axisLayout)
                self.axisOrderMenu = cmds.optionMenu("axisOrderMenu", label='', changeCommand=self.changeAxisOrder, parent=self.axisLayout)
                self.axisOrderMenuItemList = ['XYZ', 'YZX', 'ZXY', 'XZY', 'YXZ', 'ZYX']
                for axisOrder in self.axisOrderMenuItemList:
                    cmds.menuItem(label=axisOrder, parent=self.axisOrderMenu)
                currentAxisOrder = cmds.getAttr(self.net+".axisOrder")
                cmds.optionMenu(self.axisOrderMenu, edit=True, value=self.axisOrderMenuItemList[currentAxisOrder])
                # input and output values:
                currentInputMin = cmds.getAttr(self.net+".inputMin")
                currentInputMax = cmds.getAttr(self.net+".inputMax")
                currentOutputMin = cmds.getAttr(self.net+".outputMin")
                currentOutputMax = cmds.getAttr(self.net+".outputMax")
                rangeLayout = cmds.columnLayout('rangeLayout', adjustableColumn=True, columnAlign="right", parent=self.selectedLayout)
                rangeLabelLayout = cmds.rowLayout('rangeLabelLayout', numberOfColumns=3, adjustableColumn=1, columnWidth=[(1, 10), (2, 58), (3, 80)], columnAttach=[(1, "right", 0), (2, "right", 20), (3, "right", 30)], parent=rangeLayout)
                cmds.text("Range", label=self.langDic[self.langName]['m072_range'], align="right", parent=rangeLabelLayout)
                cmds.text("Min", align="right", parent=rangeLabelLayout)
                cmds.text("Max", align="right", parent=rangeLabelLayout)
                cmds.floatFieldGrp("inputFFG", label=self.langDic[self.langName]['m137_input'], numberOfFields=2, value1=currentInputMin, value2=currentInputMax, columnWidth3=(40, 70, 70), columnAttach=[(1, 'right', 5), (2, 'left', 2), (3, 'left', 0)], adjustableColumn3=1, changeCommand=self.changeInputValues, parent=rangeLayout)
                cmds.floatFieldGrp("outputFFG", label=self.langDic[self.langName]['m138_output'], numberOfFields=2, value1=currentOutputMin, value2=currentOutputMax, columnWidth3=(40, 70, 70), columnAttach=[(1, 'right', 5), (2, 'left', 2), (3, 'left', 0)], adjustableColumn3=1, changeCommand=self.changeOutputValues, parent=rangeLayout)

    
    def actualizeEditLayout(self, *args):
        """ Clean up the current edit layout, check the selected node and update the UI.
        """
        self.clearEditLayout()
        selList = cmds.textScrollList(self.existingNetTSL, query=True, selectItem=True)
        if selList:
            if cmds.objExists(selList[0]):
                cmds.select(selList[0])
                self.net = selList[0]
        self.recreateSelectedLayout()
        

    def populateNetUI(self, *args):
        """ Check existing network node to populate UI.
        """
        cmds.textScrollList(self.existingNetTSL, edit=True, deselectAll=True)
        cmds.textScrollList(self.existingNetTSL, edit=True, removeAll=True)
        currentNetList = cmds.ls(selection=False, type="network")
        if currentNetList:
            self.netList = []
            for item in currentNetList:
                if cmds.objExists(item+".dpNetwork"):
                    if cmds.getAttr(item+".dpNetwork") == 1:
                        if cmds.objExists(item+".dpCorrectionManager"):
                            if cmds.getAttr(item+".dpCorrectionManager") == 1:
                                #TODO validate correctionManager node integrity here
                                self.netList.append(item)
            if self.netList:
                cmds.textScrollList(self.existingNetTSL, edit=True, append=self.netList)
                if self.net:
                    if cmds.objExists(self.net):
                        cmds.textScrollList(self.existingNetTSL, edit=True, selectItem=self.net)


    def clearEditLayout(self, *args):
        """ Just clean up the selected layout.
        """
        try:
            cmds.deleteUI(self.selectedLayout)
        except:
            pass


    def createCorrectiveLocator(self, name, toAttach, *args):
        """ Creates a space locator, zeroOut it to receive a parentConstraint.
            Return the locator to use it as a reader node to the system.
        """
        if cmds.objExists(toAttach):
            loc = cmds.spaceLocator(name=name+"_Loc")[0]
            cmds.addAttr(loc, longName="inputNode", attributeType="message")
            cmds.connectAttr(toAttach+".message", loc+".inputNode", force=True)
            grp = dpUtils.zeroOut([loc])[0]
            cmds.parentConstraint(toAttach, grp, maintainOffset=False, name=grp+"_PaC")
            cmds.parent(grp, dpUtils.getNodeByMessage("correctionDataGrp", self.net))
            return loc
        else:
            mel.eval('warning \"'+toAttach+' '+self.langDic[self.langName]['i061_notExists']+'\";')


    def createCorrectionManager(self, nodeList=None, name=None, correctType=None, *args):
        """ Create nodes to calculate the correction we want to mapper to fix.
        """
        # loading Maya matrix node
        loadedQuatNode = dpUtils.checkLoadedPlugin("quatNodes", self.langDic[self.langName]['e014_cantLoadQuatNode'])
        loadedMatrixPlugin = dpUtils.checkLoadedPlugin("matrixNodes", self.langDic[self.langName]['e002_matrixPluginNotFound'])
        if loadedQuatNode and loadedMatrixPlugin:
            if not nodeList:
                nodeList = cmds.ls(selection=True)
            if nodeList:
                if len(nodeList) == 2:
                    origNode = nodeList[0]
                    actionNode = nodeList[1]
                    cmds.undoInfo(openChunk=True)

                    # main group
                    if not cmds.objExists(self.correctionManagerDataGrp):
                        self.correctionManagerDataGrp = cmds.group(empty=True, name=self.correctionManagerDataGrp)
                        cmds.addAttr(self.correctionManagerDataGrp, longName="dpCorrectionManagerDataGrp", attributeType="bool")
                        cmds.setAttr(self.correctionManagerDataGrp+".dpCorrectionManagerDataGrp", 1)
                        self.ctrls.setLockHide([self.correctionManagerDataGrp], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
                        scalableGrp = dpUtils.getNodeByMessage("scalableGrp")
                        if scalableGrp:
                            cmds.parent(self.correctionManagerDataGrp, scalableGrp)

                    # naming
                    if not name:
                        name = cmds.textField(self.createTF, query=True, text=True)
                        if not name:
                            name = "Correction"
                    correctionName, name = dpUtils.resolveName(name, self.netSuffix)
                    
                    # type
                    if not correctType:
                        typeSelectedRadioButton = cmds.radioCollection(self.correctTypeCollection, query=True, select=True)
                        correctType = cmds.radioButton(typeSelectedRadioButton, query=True, annotation=True)
                        if not correctType:
                            correctType = "Angle"

                    # create the container of the system data using a network node
                    self.net = cmds.createNode("network", name=name)
                    cmds.addAttr(self.net, longName="dpNetwork", attributeType="bool")
                    cmds.addAttr(self.net, longName="dpCorrectionManager", attributeType="bool")
                    cmds.addAttr(self.net, longName="name", dataType="string")
                    cmds.addAttr(self.net, longName="type", dataType="string")
                    cmds.addAttr(self.net, longName="inputValue", attributeType="float")
                    cmds.addAttr(self.net, longName="axis", attributeType='enum', enumName="X:Y:Z")
                    cmds.addAttr(self.net, longName="axisOrder", attributeType='enum', enumName="XYZ:YZX:ZXY:XZY:YXZ:ZYX")
                    cmds.addAttr(self.net, longName="inputMin", attributeType="float", defaultValue=0)
                    cmds.addAttr(self.net, longName="inputMax", attributeType="float", defaultValue=90)
                    cmds.addAttr(self.net, longName="outputMin", attributeType="float", defaultValue=0)
                    cmds.addAttr(self.net, longName="outputMax", attributeType="float", defaultValue=1)
                    messageAttrList = ["correctionDataGrp", "extractAngleMM", "extractAngleDM", "extractAngleQtE", "extractAngleMD", "intensityMD", "smallerThanOneCnd", "overZeroCnd", "inputRmV", "outputSR", "originalLoc", "actionLoc"]
                    for messageAttr in messageAttrList:
                        cmds.addAttr(self.net, longName=messageAttr, attributeType="message")
                    cmds.addAttr(self.net, longName="intensity", attributeType="float", minValue=0, defaultValue=1, maxValue=1)
                    cmds.addAttr(self.net, longName="outputValue", attributeType="float")
                    cmds.setAttr(self.net+".dpNetwork", 1)
                    cmds.setAttr(self.net+".dpCorrectionManager", 1)
                    cmds.setAttr(self.net+".name", correctionName, type="string")
                    cmds.setAttr(self.net+".type", correctType, type="string")
                    correctionDataGrp = cmds.group(empty=True, name=correctionName+"_Grp")
                    cmds.connectAttr(correctionDataGrp+".message", self.net+".correctionDataGrp", force=True)
                    cmds.parent(correctionDataGrp, self.correctionManagerDataGrp)
                    originalLoc = self.createCorrectiveLocator(correctionName+"_Original", origNode)
                    actionLoc = self.createCorrectiveLocator(correctionName+"_Action", actionNode)
                    # serialize locators
                    cmds.connectAttr(originalLoc+".message", self.net+".originalLoc", force=True)
                    cmds.connectAttr(actionLoc+".message", self.net+".actionLoc", force=True)
                    
                    # if rotate extration option:
                    if correctType == "Angle":
                        # write a new dpUtils function to generate these matrix nodes here:
                        extractAngleMM = cmds.createNode("multMatrix", name=correctionName+"_ExtractAngle_MM")
                        extractAngleDM = cmds.createNode("decomposeMatrix", name=correctionName+"_ExtractAngle_DM")
                        extractAngleQtE = cmds.createNode("quatToEuler", name=correctionName+"_ExtractAngle_QtE")
                        extractAngleMD = cmds.createNode("multiplyDivide", name=correctionName+"_ExtractAngle_MD")
                        intensityMD = cmds.createNode("multiplyDivide", name=correctionName+"_Instensity_MD")
                        smallerThanOneCnd = cmds.createNode("condition", name=correctionName+"_ExtractAngle_SmallerThanOne_Cnd")
                        overZeroCnd = cmds.createNode("condition", name=correctionName+"_ExtractAngle_OverZero_Cnd")
                        inputRmV = cmds.createNode("remapValue", name=correctionName+"_Input_RmV")
                        outputSR = cmds.createNode("setRange", name=correctionName+"_Output_SR")
                        cmds.setAttr(extractAngleMD+".operation", 2)
                        cmds.setAttr(smallerThanOneCnd+".operation", 5) #less or equal
                        cmds.setAttr(smallerThanOneCnd+".secondTerm", 1)
                        cmds.setAttr(overZeroCnd+".secondTerm", 0)
                        cmds.setAttr(overZeroCnd+".colorIfFalseR", 0)
                        cmds.setAttr(overZeroCnd+".operation", 3) #greater or equal
                        cmds.connectAttr(actionLoc+".worldMatrix[0]", extractAngleMM+".matrixIn[0]", force=True)
                        cmds.connectAttr(originalLoc+".worldInverseMatrix[0]", extractAngleMM+".matrixIn[1]", force=True)
                        cmds.connectAttr(extractAngleMM+".matrixSum", extractAngleDM+".inputMatrix", force=True)
                        # setup the rotation affection
                        cmds.connectAttr(extractAngleDM+".outputQuatX", extractAngleQtE+".inputQuatX", force=True)
                        cmds.connectAttr(extractAngleDM+".outputQuatY", extractAngleQtE+".inputQuatY", force=True)
                        cmds.connectAttr(extractAngleDM+".outputQuatZ", extractAngleQtE+".inputQuatZ", force=True)
                        cmds.connectAttr(extractAngleDM+".outputQuatW", extractAngleQtE+".inputQuatW", force=True)
                        # axis setup
                        cmds.connectAttr(self.net+".inputMin", inputRmV+".inputMin", force=True)
                        cmds.connectAttr(self.net+".inputMax", inputRmV+".inputMax", force=True)
                        cmds.connectAttr(self.net+".inputMax", inputRmV+".outputMax", force=True)
                        cmds.connectAttr(inputRmV+".outValue", extractAngleMD+".input1X", force=True)
                        cmds.connectAttr(extractAngleQtE+".outputRotateX", inputRmV+".inputValue", force=True) #it'll be updated when changing axis
                        unitConv = cmds.listConnections(inputRmV+".inputValue", source=True, destination=False)[0]
                        cmds.setAttr(self.net+".inputValue", lock=False)
                        cmds.connectAttr(unitConv+".output", self.net+".inputValue", force=True)
                        cmds.setAttr(self.net+".inputValue", lock=True)
                        # axis order setup
                        cmds.connectAttr(self.net+".inputMax", extractAngleMD+".input2X", force=True) #it'll be updated when changing angle
                        cmds.connectAttr(extractAngleMD+".outputX", smallerThanOneCnd+".firstTerm", force=True)
                        cmds.connectAttr(extractAngleMD+".outputX", smallerThanOneCnd+".colorIfTrueR", force=True)
                        cmds.connectAttr(smallerThanOneCnd+".outColorR", overZeroCnd+".firstTerm", force=True)
                        cmds.connectAttr(smallerThanOneCnd+".outColorR", overZeroCnd+".colorIfTrueR", force=True)
                        # intensity setup:
                        cmds.setAttr(outputSR+".oldMaxX", 1)
                        cmds.connectAttr(self.net+".outputMin", outputSR+".minX", force=True)
                        cmds.connectAttr(self.net+".outputMax", outputSR+".maxX", force=True)
                        cmds.connectAttr(overZeroCnd+".outColorR", intensityMD+".input1X", force=True)
                        cmds.connectAttr(self.net+".intensity", intensityMD+".input2X", force=True)
                        cmds.connectAttr(intensityMD+".outputX", outputSR+".valueX", force=True)
                        # TODO create a way to avoid manual connection here, maybe using the UI new tab?
                        cmds.connectAttr(outputSR+".outValueX", self.net+".outputValue", force=True)
                        cmds.setAttr(self.net+".outputValue", lock=True)
                        # serialize message attributes
                        cmds.connectAttr(extractAngleMM+".message", self.net+".extractAngleMM", force=True)
                        cmds.connectAttr(extractAngleDM+".message", self.net+".extractAngleDM", force=True)
                        cmds.connectAttr(extractAngleQtE+".message", self.net+".extractAngleQtE", force=True)
                        cmds.connectAttr(extractAngleMD+".message", self.net+".extractAngleMD", force=True)
                        cmds.connectAttr(intensityMD+".message", self.net+".intensityMD", force=True)
                        cmds.connectAttr(smallerThanOneCnd+".message", self.net+".smallerThanOneCnd", force=True)
                        cmds.connectAttr(overZeroCnd+".message", self.net+".overZeroCnd", force=True)
                        cmds.connectAttr(outputSR+".message", self.net+".outputSR", force=True)
                        cmds.connectAttr(inputRmV+".message", self.net+".inputRmV", force=True)
                    else: #Distance
                        
                        
                        print("Merci distance --- WIP")


                        






                    # update UI                    
                    if self.ui:
                        self.populateNetUI()
                        self.actualizeEditLayout()
                    cmds.undoInfo(closeChunk=True)
                else:
                    mel.eval('warning \"'+self.langDic[self.langName]['m065_selOrigAction']+'\";')
            else:
                mel.eval('warning \"'+self.langDic[self.langName]['m066_selectTwo']+'\";')