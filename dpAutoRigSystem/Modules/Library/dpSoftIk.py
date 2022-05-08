###
#
#   THANKS to:
#       Nick Miller Genuine
#       https://vimeo.com/nickmillergenuine
#
#   Based on:
#       https://www.highend3d.com/maya/script/soft-ik-tool-for-maya
#   
#   This module will create a Soft Ik setup to be implemented by dpLimb.py
#
#
# Formula:
#
# y = {                                              
#                     -(x-da)/
#        dsoft(1 - e^  dsoft  ) + da   (da <= x)
#                                                   }
#
# da = dchain - dsoft
# dchain = sum of bone lengths
# dsoft = user set soft distance (how far the effector should fall behind)
# x = distance between root and ik (shoulder and wrist)
#
###


# importing libraries:
from maya import cmds
from . import dpControls


class SoftIkClass(object):

    def __init__(self, dpUIinst, langDic, langName, presetDic, presetName, ctrlRadius, curveDegree, *args):
        # defining variables:
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        self.presetDic = presetDic
        self.presetName = presetName
        self.ctrlRadius = ctrlRadius
        self.curveDegree = curveDegree
        self.ctrls = dpControls.ControlClass(self.dpUIinst, self.presetDic, self.presetName)


    def createSoftIk(self, userName, ctrlName, ikhName, ikJointList, skinJointList, distBetween, worldRef, stretch=True, upAxis="X", primaryAxis="Z", *args):
        """ Create the softIk setup for given parameters.
            Just a general function edited from Nick Miller code.
        """
        # add the dSoft and softIk attributes on the controller:
        cmds.addAttr(ctrlName, longName="softIk", attributeType="double", min=0, defaultValue=0, max=1, keyable=True)
        cmds.addAttr(ctrlName, longName="softDistance", attributeType="double", min=0.001, defaultValue=0.001, keyable=True)
        
        # set up node network for softIk:
        softRmV = cmds.createNode("remapValue", name=userName+"_SoftDistance_RmV")
        daMD = cmds.createNode("plusMinusAverage", name=userName+"_DA_PMA")
        xMinusDaPMA = cmds.createNode("plusMinusAverage", name=userName+"_X_Minus_DA_PMA")
        negateXMinusMD = cmds.createNode("multiplyDivide", name=userName+"_Negate_X_Minus_MD")
        divByDSoftMD = cmds.createNode("multiplyDivide", name=userName+"_DivBy_DSoft_MD")
        powEMD = cmds.createNode("multiplyDivide", name=userName+"_Pow_E_MD")
        oneMinusPowEPMD = cmds.createNode("plusMinusAverage", name=userName+"_One_Minus_Pow_E_PMA")
        timesDSoftMD = cmds.createNode("multiplyDivide", name=userName+"_Times_DSoft_MD")
        plusDAPMA = cmds.createNode("plusMinusAverage", name=userName+"_Plus_DA_PMA")
        daCnd = cmds.createNode("condition", name=userName+"_DA_Cnd")
        distDiffPMA = cmds.createNode("plusMinusAverage", name=userName+"_Dist_Diff_PMA")
        lengthStartMD = cmds.createNode("multiplyDivide", name=userName+"_Length_Start_MD")
        lenghtOutputMD = cmds.createNode("multiplyDivide", name=userName+"_Length_Output_MD")
        softIkRigScaleMD = cmds.createNode("multiplyDivide", name=userName+"_SoftIk_RigScale_MD")
        
        # set default values and operations:
        cmds.setAttr(powEMD+".input1X", 2.718281828)
        cmds.setAttr(softRmV+".outputMin", 0.001)
        cmds.setAttr(softRmV+".outputMax", 2)
        cmds.setAttr(negateXMinusMD+".input2X", -1)
        cmds.setAttr(oneMinusPowEPMD+".input1D[0]", 1)
        cmds.setAttr(daMD+".operation", 2) #divide
        cmds.setAttr(xMinusDaPMA+".operation", 2) #substract
        cmds.setAttr(negateXMinusMD+".operation", 1) #multiply
        cmds.setAttr(divByDSoftMD+".operation", 2) #divide
        cmds.setAttr(powEMD+".operation", 3) #power
        cmds.setAttr(oneMinusPowEPMD+".operation", 2) #substract
        cmds.setAttr(timesDSoftMD+".operation", 1) # multiply
        cmds.setAttr(plusDAPMA+".operation", 1) #sum
        cmds.setAttr(daCnd+".operation", 5) #less or equal
        cmds.setAttr(distDiffPMA+".operation", 2) #substract

        # make connections:
        cmds.connectAttr(ctrlName+".softIk", softRmV+".inputValue", force=True)
        cmds.connectAttr(softRmV+".outValue", ctrlName+".softDistance", force=True)
        cmds.connectAttr(ctrlName+".startChainLength", lengthStartMD+".input1X", force=True)
        cmds.connectAttr(lengthStartMD+".outputX", daMD+".input1D[0]", force=True)
        cmds.connectAttr(ctrlName+"."+self.langDic[self.langName]["c113_length"], lengthStartMD+".input2X", force=True)
        cmds.connectAttr(ctrlName+".softDistance", daMD+".input1D[1]", force=True)
        cmds.connectAttr(distBetween+".distance", xMinusDaPMA+".input1D[0]", force=True)
        cmds.connectAttr(daMD+".output1D", xMinusDaPMA+".input1D[1]", force=True)
        cmds.connectAttr(xMinusDaPMA+".output1D", negateXMinusMD+".input1X", force=True)
        cmds.connectAttr(negateXMinusMD+".outputX", divByDSoftMD+".input1X", force=True)
        cmds.connectAttr(ctrlName+".softDistance", divByDSoftMD+".input2X", force=True)
        cmds.connectAttr(divByDSoftMD+".outputX", powEMD+".input2X", force=True)
        cmds.connectAttr(powEMD+".outputX", oneMinusPowEPMD+".input1D[1]", force=True)
        cmds.connectAttr(oneMinusPowEPMD+".output1D", timesDSoftMD+".input1X", force=True)
        cmds.connectAttr(ctrlName+".softDistance", timesDSoftMD+".input2X", force=True)
        cmds.connectAttr(timesDSoftMD+".outputX", plusDAPMA+".input1D[0]", force=True)
        cmds.connectAttr(daMD+".output1D", plusDAPMA+".input1D[1]", force=True)
        cmds.connectAttr(daMD+".output1D", daCnd+".firstTerm", force=True)
        cmds.connectAttr(distBetween+".distance", daCnd+".secondTerm", force=True)
        cmds.connectAttr(distBetween+".distance", daCnd+".colorIfFalseR", force=True)
        cmds.connectAttr(plusDAPMA+".output1D", daCnd+".colorIfTrueR", force=True)
        cmds.connectAttr(daCnd+".outColorR", distDiffPMA+".input1D[0]", force=True)
        cmds.connectAttr(distBetween+".distance", distDiffPMA+".input1D[1]", force=True)        
        cmds.connectAttr(distDiffPMA+".output1D", softIkRigScaleMD+".input1X", force=True)
        cmds.connectAttr(softIkRigScaleMD+".outputX", ikhName+".translate"+primaryAxis, force=True)
        cmds.connectAttr(worldRef+".scaleX", softIkRigScaleMD+".input2X", force=True)

        self.ctrls.setLockHide([ctrlName], ["softDistance"])

        # if stretch exists, we need to do this...
        if stretch:
            softRatioMD = cmds.createNode("multiplyDivide", name=userName+"_Soft_Ratio_MD")
            stretchBC = cmds.createNode("blendColors", name=userName+"_Stretch_BC")
            cmds.setAttr(softRatioMD+".operation", 2) #divide
            cmds.setAttr(stretchBC+".color2R", 1)
            cmds.connectAttr(ctrlName+".stretchable", stretchBC+".blender", force=True)
            cmds.connectAttr(distBetween+".distance", softRatioMD+".input1X", force=True)
            cmds.connectAttr(daCnd+".outColorR", softRatioMD+".input2X", force=True)
            cmds.connectAttr(distDiffPMA+".output1D", stretchBC+".color2G", force=True)
            cmds.connectAttr(softRatioMD+".outputX", stretchBC+".color1R", force=True)
            cmds.connectAttr(stretchBC+".outputR", lenghtOutputMD+".input1X", force=True)
            cmds.connectAttr(ctrlName+"."+self.langDic[self.langName]["c113_length"], lenghtOutputMD+".input2X", force=True)
            cmds.connectAttr(stretchBC+".outputG", softIkRigScaleMD+".input1X", force=True)
            cmds.connectAttr(softIkRigScaleMD+".outputX", ikhName+".translate"+primaryAxis, force=True)
            i = 0
            while ( i < len(ikJointList)-1 ):
                cmds.connectAttr(lenghtOutputMD+".outputX", ikJointList[i]+".scale"+primaryAxis, force=True)
                cmds.connectAttr(stretchBC+".outputR", skinJointList[i]+".scale"+primaryAxis, force=True)
                i += 1