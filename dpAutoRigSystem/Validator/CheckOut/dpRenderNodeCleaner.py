# importing libraries:
from maya import cmds
from maya import mel
import os
from .. import dpBaseValidatorClass

# global variables to this module:
CLASS_NAME = "RenderNodeCleaner"
TITLE = "v084_renderNodeCleaner"
DESCRIPTION = "v085_renderNodeCleanerDesc"
ICON = "/Icons/dp_renderNodeCleaner.png"

DP_RENDERNODECLEANER_VERSION = 1.0


class RenderNodeCleaner(dpBaseValidatorClass.ValidatorStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        dpBaseValidatorClass.ValidatorStartClass.__init__(self, *args, **kwargs)
    

    def runValidator(self, verifyMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If verifyMode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked items
                - foundIssueList = True if an issue was found, False if there isn't an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        """
        # starting
        self.verifyMode = verifyMode
        self.cleanUpToStart()
        
        # ---
        # --- validator code --- beginning
        if objList:
            toCheckList = objList
        else:
            toCheckList = cmds.ls(selection=False, type='skinCluster')
        if toCheckList:
            progressAmount = 0
            maxProcess = len(toCheckList)
            for item in toCheckList:
                if self.verbose:
                    # Update progress window
                    progressAmount += 1
                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
                # conditional to check here
                influenceList = cmds.skinCluster(item, query=True, influence=True)
                weightedInfluenceList = cmds.skinCluster(item, query=True, weightedInfluence=True)
                if not len(influenceList) == len(weightedInfluenceList):
                    self.checkedObjList.append(item)
                    self.foundIssueList.append(True)
                    if self.verifyMode:
                        self.resultOkList.append(False)
                    else: #fix
                        try:
                            # loading mel script with the needed procedure
                            mel.eval("source \"cleanUpScene\";")
                            
                            #https://discourse.techart.online/t/python-optimizescenesize/15341/5
                            if "MAYA_TESTING_CLEANUP" not in os.environ:
                                os.environ["MAYA_TESTING_CLEANUP"] = "enable"
                                mel.eval("scOpt_performOneCleanup( {\"shaderOption\"} );")
                                del os.environ["MAYA_TESTING_CLEANUP"]
                            else:
                                mel.eval("scOpt_performOneCleanup( {\"shaderOption\"} );")
                            
                            self.resultOkList.append(True)
                            self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+item)
                        except:
                            self.resultOkList.append(False)
                            self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+item)
        else:
            self.notFoundNodes()
        # --- validator code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgressBar()
        return self.dataLogDic
