from maya import cmds
from ..Modules.Library import dpUtils

class UpdateGuides(object):

    def __init__(self, dpUIinst, *args, **kwargs):
        # defining variables
        self.dpUIinst = dpUIinst
        
        # Dictionary that will hold data for update, whatever don't need update will not be saved
        self.updateData = {}
        self.currentDpArVersion = dpUIinst.dpARVersion
        # Receive the guides list from hook function
        self.guidesDictionary = dpUtils.hook()
        # List that will hold all new guides instances
        self.newGuidesInstanceList = []
        # Dictionary where the keys are the guides that will be used and don't need update
        # and values are its current parent, this is used to search for possible new parent
        self.guidesToReParentDict = {}
        self.TRANSFORM_LIST = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ']
        # If there are guides on the dictionary go on.
        if len(self.guidesDictionary) > 0:
            # Get all info nedeed and store in updateData dictionary
            self.getGuidesToUpdateData()
        else:
            print('There is no guides in the scene')
        # Open the UI
        self.updateGuidesUI()

    def summaryUI(self):
        newData = self.listNewAttr()
        cmds.window('updateSummary', title="Update Summary")
        cmds.columnLayout('updateSummaryBaseColumn', adjustableColumn=1, rowSpacing=10, parent='updateSummary')
        if newData:
            cmds.rowColumnLayout('updateSummaryLayoutBase', numberOfColumns=2, columnSpacing=[(1, 0), (2,20)], parent='updateSummaryBaseColumn')
            cmds.text(label='Guide', align='center', parent='updateSummaryLayoutBase')
            cmds.text(label='New Attribute', align='center', parent='updateSummaryLayoutBase')
            for guide in newData:
                for newAttr in newData[guide]:
                    cmds.text(label=guide, align='left', parent='updateSummaryLayoutBase')
                    cmds.text(label=newAttr, align='left', parent='updateSummaryLayoutBase')
        else:
            cmds.text(label='There is no new attributes in the updated guides.', align='left', parent='updateSummaryBaseColumn')
        
        cmds.button(label='Delete Old Guides', command=self.doDelete, backgroundColor=(1.0, 0.0, 0.0), parent='updateSummaryBaseColumn')
        cmds.showWindow( 'updateSummary' )


    def updateGuidesUI(self):
        cmds.window('updateGuidesWindow', title="Guides Info")
        cmds.columnLayout('updateGuidesBaseColumn', adjustableColumn=1, rowSpacing=10, parent='updateGuidesWindow')
        cmds.text(label='Current DPAR Version '+str(self.currentDpArVersion), align='left', parent='updateGuidesBaseColumn')
        if len(self.updateData) > 0:
            cmds.rowColumnLayout('updateGuidesLayoutBase', numberOfColumns=3, columnSpacing=[(1, 0), (2,20), (3,20)], parent='updateGuidesBaseColumn')
            cmds.text(label='Transform', align='center', parent='updateGuidesLayoutBase')
            cmds.text(label='Custom Name', align='center', parent='updateGuidesLayoutBase')
            cmds.text(label='Version', align='center', parent='updateGuidesLayoutBase')
            for guide in self.updateData:
                cmds.text(label=guide, align='left', parent='updateGuidesLayoutBase')
                cmds.text(label=self.updateData[guide]['attributes']['customName'], align='left', parent='updateGuidesLayoutBase')
                cmds.text(label=self.updateData[guide]['attributes']['dpARVersion'], align='left', parent='updateGuidesLayoutBase')
            
            cmds.button(label='Update Guides', command=self.doUpdate, backgroundColor=(0.6, 1.0, 0.6), parent='updateGuidesBaseColumn')
        else:
            cmds.text(label='There is no guides to update.', align='left', parent='updateGuidesBaseColumn')

        cmds.showWindow( 'updateGuidesWindow' )

    def setProgressBar(self, progressAmount, status):
        cmds.progressWindow(edit=True, progress=progressAmount, status=status, isInterruptable=False)
    
    # Remove objects different from transform and nurbscurbe from list.
    def filterNotNurbsCurveAndTransform(self, mayaObjList):
        returList = []
        for obj in mayaObjList:
            objType = cmds.objectType(obj)
            if objType == 'nurbsCurve' or objType == 'transform':
                returList.append(obj)
        return returList
    
    # Remove _Ant(Anotations) items from list of transforms
    def filterAnotation(self, dpArTransformsList):
        returList = []
        for obj in dpArTransformsList:
            if not '_Ant' in obj:
                returList.append(obj)
        return returList

    def getAttrValue(self, dpGuide, attr):
        try:
            return cmds.getAttr(dpGuide+'.'+attr, silent=True)
        except:
            return ''
    
    def getNewGuideInstance(self, newGuideName):
        newGuidesNamesList = list(map(lambda moduleInstance : moduleInstance.moduleGrp, self.newGuidesInstanceList))
        currentGuideInstanceIdx = newGuidesNamesList.index(newGuideName)
        return self.newGuidesInstanceList[currentGuideInstanceIdx]
    
    def translateLimbStyleValue(self, enumValue):
        if enumValue == 1:
            return self.dpUIinst.langDic[self.dpUIinst.langName]['m026_biped']
        elif enumValue == 2:
            return self.dpUIinst.langDic[self.dpUIinst.langName]['m037_quadruped']
        elif enumValue == 3:
            return self.dpUIinst.langDic[self.dpUIinst.langName]['m043_quadSpring']
        elif enumValue == 4:
            return self.dpUIinst.langDic[self.dpUIinst.langName]['m155_quadrupedExtra']
        else:
            return self.dpUIinst.langDic[self.dpUIinst.langName]['m042_default']
    
    def translateLimbTypeValue(self, enumValue):
        if enumValue == 1:
            return self.dpUIinst.langDic[self.dpUIinst.langName]['m030_leg']
        else:
            return self.dpUIinst.langDic[self.dpUIinst.langName]['m028_arm']

    def setAttrValue(self, dpGuide, attr, value):
        try:
            cmds.setAttr(dpGuide+'.'+attr, value)
        except:
            print('the attr '+attr+' from '+dpGuide+' could not be set.')

    def setAttrStrValue(self, dpGuide, attr, value):
        try:
            cmds.setAttr(dpGuide+'.'+attr, value, type='string')
        except:
            print('the attr '+attr+' from '+dpGuide+' could not be set.')
    
    def setEyelidGuideAttribute(self, dpGuide, value):
        currentInstance = self.getNewGuideInstance(dpGuide)
        cvUpperEyelidLoc = currentInstance.guideName+"_UpperEyelidLoc"
        cvLowerEyelidLoc = currentInstance.guideName+"_LowerEyelidLoc"
        jEyelid = currentInstance.guideName+"_JEyelid"
        jUpperEyelid = currentInstance.guideName+"_JUpperEyelid"
        jLowerEyelid = currentInstance.guideName+"_JLowerEyelid"
        cmds.setAttr(dpGuide+".eyelid", value)
        cmds.setAttr(cvUpperEyelidLoc+".visibility", value)
        cmds.setAttr(cvLowerEyelidLoc+".visibility", value)
        cmds.setAttr(jEyelid+".visibility", value)
        cmds.setAttr(jUpperEyelid+".visibility", value)
        cmds.setAttr(jLowerEyelid+".visibility", value)

    def setIrisGuideAttribute(self, dpGuide, value):
        currentInstance = self.getNewGuideInstance(dpGuide)
        cvIrisLoc = currentInstance.guideName+"_IrisLoc"
        cmds.setAttr(dpGuide+".iris", value)
        cmds.setAttr(cvIrisLoc+".visibility", value)

    def setPupilGuideAttribute(self, dpGuide, value):
        currentInstance = self.getNewGuideInstance(dpGuide)
        cvPupilLoc = currentInstance.guideName+"_PupilLoc"
        cmds.setAttr(dpGuide+".pupil", value)
        cmds.setAttr(cvPupilLoc+".visibility", value)

    def setNostrilGuideAttribute(self, dpGuide, value):
        currentInstance = self.getNewGuideInstance(dpGuide)
        cmds.setAttr(dpGuide+".nostril", value)
        cmds.setAttr(currentInstance.cvLNostrilLoc+".visibility", value)
        cmds.setAttr(currentInstance.cvRNostrilLoc+".visibility", value)
    
    def checkSetNewGuideToAttr(self, dpGuide, attr, value):
        if value in self.updateData:
            self.setAttrStrValue(dpGuide, attr, self.updateData[value]['newGuide'])
        else:
            self.setAttrStrValue(dpGuide, attr, value)
            
    def setGuideAttributes(self, dpGuide, attr, value):
        ignoreList = ['version', 'controlID', 'className', 'direction', 'pinGuideConstraint', 'moduleNamespace', 'customName', 'moduleInstanceInfo', 'hookNode', 'guideObjectInfo', 'rigType', 'dpARVersion']
        if attr not in ignoreList:
            if attr == 'nJoints':
                currentInstance = self.getNewGuideInstance(dpGuide)
                currentInstance.changeJointNumber(value)
            elif attr == 'style':
                currentInstance = self.getNewGuideInstance(dpGuide)
                expectedValue = self.translateLimbStyleValue(value)
                currentInstance.changeStyle(expectedValue)
            elif attr == 'type':
                currentInstance = self.getNewGuideInstance(dpGuide)
                expectedValue = self.translateLimbTypeValue(value)
                currentInstance.changeType(expectedValue)
            elif attr == 'mirrorAxis':
                currentInstance = self.getNewGuideInstance(dpGuide)
                currentInstance.changeMirror(value)
            elif attr == 'mirrorName':
                currentInstance = self.getNewGuideInstance(dpGuide)
                currentInstance.changeMirrorName(value)
            # EYE ATTRIBUTES
            elif attr == 'eyelid':
                self.setEyelidGuideAttribute(dpGuide, value)
            elif attr == 'iris':
                self.setIrisGuideAttribute(dpGuide, value)
            elif attr == 'pupil':
                self.setPupilGuideAttribute(dpGuide, value)
            elif attr == 'aimDirection':
                currentInstance = self.getNewGuideInstance(dpGuide)
                aimMenuItemList = ['+X', '-X', '+Y', '-Y', '+Z', '-Z']
                currentInstance.changeAimDirection(aimMenuItemList[value])
            # NOSE ATTRIBUTES
            elif attr == 'nostril':
                self.setNostrilGuideAttribute(dpGuide, value)
            # SUSPENSION ATTRIBUTES AND WHEEL ATTRIBUTES
            elif attr == 'fatherB' or attr == 'geo':
                self.checkSetNewGuideToAttr(dpGuide, attr, value)
            else:
                self.setAttrValue(dpGuide, attr, value)
    
    # Return a list of attributes, keyable and userDefined
    def listKeyUserAttr(self, objWithAttr):
        returnList = []
        keyable = cmds.listAttr(objWithAttr, keyable=True)
        if keyable:
            returnList.extend(keyable)
        userAttr = cmds.listAttr(objWithAttr, userDefined=True)
        if userAttr:
            returnList.extend(userAttr)
        # Guaranty no duplicated attr
        returnList = list(set(returnList))
        return returnList
    
    def getGuideParent(self, baseGuide):
        try:
            return cmds.listRelatives(baseGuide, parent=True)[0]
        except:
            return None

    def listChildren(self, baseGuide):
        childrenList = cmds.listRelatives(baseGuide, allDescendents=True, children=True, type='transform')
        childrenList = self.filterNotNurbsCurveAndTransform(childrenList)
        childrenList = self.filterAnotation(childrenList)
        return childrenList

    # Scan a dictionary for old guides and gather data needed to update them.
    def getGuidesToUpdateData(self):

        instancedModulesStrList = list(map(str, self.dpUIinst.modulesToBeRiggedList))

        for baseGuide in self.guidesDictionary:
            guideVersion = cmds.getAttr(baseGuide+'.dpARVersion', silent=True)
            if guideVersion != self.currentDpArVersion:
                # Create the database holder where the key is the baseGuide
                self.updateData[baseGuide] = {}
                guideAttrList = self.listKeyUserAttr(baseGuide)
                # Create de attributes dictionary for each baseGuide
                self.updateData[baseGuide]['attributes'] = {}
                for attribute in guideAttrList:
                    attributeValue = self.getAttrValue(baseGuide, attribute)
                    self.updateData[baseGuide]['attributes'][attribute] = attributeValue

                self.updateData[baseGuide]['idx'] = instancedModulesStrList.index(self.updateData[baseGuide]['attributes']['moduleInstanceInfo'])
                
                self.updateData[baseGuide]['children'] = {}
                self.updateData[baseGuide]['parent'] = self.getGuideParent(baseGuide)
                childrenList = self.listChildren(baseGuide)
                for child in childrenList:
                    self.updateData[baseGuide]['children'][child] = {'attributes': {}}
                    guideAttrList = self.listKeyUserAttr(child)
                    for attribute in guideAttrList:
                        attributeValue = self.getAttrValue(child, attribute)
                        self.updateData[baseGuide]['children'][child]['attributes'][attribute] = attributeValue
            else:
                self.guidesToReParentDict[baseGuide] = self.getGuideParent(baseGuide)

    def createNewGuides(self):
        for guide in self.updateData:
            guideType = self.dpUIinst.modulesToBeRiggedList[self.updateData[guide]['idx']].guideModuleName
            # create the new guide
            currentNewGuide = self.dpUIinst.initGuide("dp"+guideType, "Modules")
            # rename as it's predecessor
            guideName = self.updateData[guide]['attributes']['customName']
            currentNewGuide.editUserName(guideName)
            self.updateData[guide]['newGuide'] = currentNewGuide.moduleGrp
            self.updateData[guide]['guideModuleName'] = guideType
            self.newGuidesInstanceList.append(currentNewGuide)

    def renameOldGuides(self):
        for guide in self.updateData:
            currentCustomName = self.updateData[guide]['attributes']['customName']
            if currentCustomName == '' or currentCustomName == None:
                self.dpUIinst.modulesToBeRiggedList[self.updateData[guide]['idx']].editUserName(self.dpUIinst.modulesToBeRiggedList[self.updateData[guide]['idx']].moduleGrp.split(':')[0]+'_OLD')
            else:
                self.dpUIinst.modulesToBeRiggedList[self.updateData[guide]['idx']].editUserName(currentCustomName+'_OLD')

    def retrieveNewParent(self, currentParent):
        currentParentBase = currentParent.split(':')[0]+":Guide_Base"
        if currentParentBase in self.updateData.keys():
            newParentBase = self.updateData[currentParentBase]['newGuide']
            newParentFinal = newParentBase.split(':')[0]+':'+currentParent.split(':')[1]
            return newParentFinal
        else:
            return currentParent

    def parentNewGuides(self):
        for guide in self.updateData:
            hasParent = self.updateData[guide]['parent']
            if hasParent != None:
                newParentFinal = self.retrieveNewParent(hasParent)
                try:
                    cmds.parent(self.updateData[guide]['newGuide'], newParentFinal)
                except:
                    print('It was not possible to find '+self.updateData[guide]['newGuide']+' parent.')

    def parentRetainGuides(self):
        if len(self.guidesToReParentDict) > 0:
            for retainGuide in self.guidesToReParentDict:
                hasParent = self.guidesToReParentDict[retainGuide]
                if hasParent != None:
                    newParentFinal = self.retrieveNewParent(hasParent)
                    try:
                        cmds.parent(retainGuide, newParentFinal)
                    except:
                        print('It was not possible to parent '+retainGuide)
    
    def sendTransformsToListEnd(self, elementList):
        toMoveList = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']
        for element in toMoveList:
            elementList.append(elementList.pop(elementList.index(element)))

    def copyAttrFromGuides(self, newGuide, oldGuideAttrDic):
        newGuideAttrList = self.listKeyUserAttr(newGuide)
        if 'translateX' in newGuideAttrList and 'rotateX' in newGuideAttrList:
            self.sendTransformsToListEnd(newGuideAttrList)
        # For each attribute in the new guide check if exists equivalent in the old one, and if its value is different, in that case
        # set the new guide attr value to the old one.
        for attr in newGuideAttrList:
            if attr in oldGuideAttrDic:
                currentValue = self.getAttrValue(newGuide, attr)
                if currentValue != oldGuideAttrDic[attr]:
                    self.setGuideAttributes(newGuide, attr, oldGuideAttrDic[attr])

    def setNewBaseGuidesTransAttr(self):
        for guide in self.updateData:
            onlyTransformDic = {}
            for attr in self.TRANSFORM_LIST:
                if attr in self.updateData[guide]['attributes']:
                    onlyTransformDic[attr] = self.updateData[guide]['attributes'][attr]
            self.copyAttrFromGuides(self.updateData[guide]['newGuide'], onlyTransformDic)
    
    def filterChildrenFromAnotherBase(self, childrenList, baseGuide):
        filteredList = []
        filterStr = baseGuide.split(':')[0]
        for children in childrenList:
            if filterStr in children:
                filteredList.append(children)
        return filteredList
    
    # Set all attributes from children with same BaseGuide to avoid double set
    def setChildrenGuides(self):
        for guide in self.updateData:
            newGuideChildrenList = self.listChildren(self.updateData[guide]['newGuide'])
            newGuideChildrenList = self.filterChildrenFromAnotherBase(newGuideChildrenList, self.updateData[guide]['newGuide'])
            oldGuideChildrenList = self.updateData[guide]['children'].keys()
            oldGuideChildrenList = self.filterChildrenFromAnotherBase(oldGuideChildrenList, guide)
            newGuideChildrenOnlyList = list(map(lambda name : name.split(':')[1], newGuideChildrenList))
            oldGuideChildrenOnlyList = list(map(lambda name : name.split(':')[1], oldGuideChildrenList))
            for i, newChild in enumerate(newGuideChildrenList):
                if newGuideChildrenOnlyList[i] in oldGuideChildrenOnlyList:
                    self.copyAttrFromGuides(newChild, self.updateData[guide]['children'][guide.split(':')[0]+':'+newGuideChildrenOnlyList[i]]['attributes'])
    
    # List new attributes from created guides for possible input.
    def listNewAttr(self):
        newDataDic = {}
        for guide in self.updateData:
            oldGuideSet = set(self.updateData[guide]['attributes'])
            newGuideSet = set(self.listKeyUserAttr(self.updateData[guide]['newGuide']))
            newAttributesSet = newGuideSet - oldGuideSet
            if len(newAttributesSet) > 0:
                for attr in newAttributesSet:
                    if guide in newDataDic:
                        newDataDic[guide].append(attr)
                    else:
                        newDataDic[guide] = [attr]
        if len(newDataDic.keys()) == 0:
            return False
        else:
            return newDataDic
    
    def setNewNonTransformAttr(self):
        nonTransformDic = {}
        for guide in self.updateData:
            for attr in self.updateData[guide]['attributes']:
                if attr not in self.TRANSFORM_LIST:
                    nonTransformDic[attr] = self.updateData[guide]['attributes'][attr]
            self.copyAttrFromGuides(self.updateData[guide]['newGuide'], nonTransformDic)

    def doDelete(self, *args):
        cmds.deleteUI('updateSummary', window=True)
        for guide in self.updateData:
            try:
                cmds.parent(guide, world=True)
            except Exception as e:
                print(e)
        cmds.delete(*self.updateData.keys())

        self.dpUIinst.jobReloadUI()


    def doUpdate(self, *args):
        cmds.deleteUI('updateGuidesWindow', window=True)
        # Starts progress bar feedback
        cmds.progressWindow(title='Operation Progress', progress=0, maxValue=7, status='Renaming old guides')
        # Rename guides to discard as *_OLD
        self.renameOldGuides()
        self.setProgressBar(1, 'Creating guides')
        # Create the new base guides to replace the old ones
        self.createNewGuides()
        self.setProgressBar(2, 'Setting attributes')
        # Set all attributes except transforms, it's needed for parenting
        self.setNewNonTransformAttr()
        self.setProgressBar(3, 'Parenting guides')
        # Parent all new guides;
        self.parentNewGuides()
        self.setProgressBar(4, 'Setting transforms')
        # Set new base guides transform attrbutes
        self.setNewBaseGuidesTransAttr()
        self.setProgressBar(5, 'Setting child guides')
        # Set all children attributes
        self.setChildrenGuides()
        self.setProgressBar(6, 'Parenting guides')
        # After all new guides parented and set, reparent old ones that will be used.
        self.parentRetainGuides()
        self.setProgressBar(7, 'Finish')
        # Ends progress bar feedback
        cmds.progressWindow(endProgress=True)
        # Calls for summary window
        self.summaryUI()