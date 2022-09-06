# importing libraries:
from maya import cmds
from .. import dpBaseValidatorClass
from importlib import reload
reload(dpBaseValidatorClass)

# global variables to this module:    
CLASS_NAME = "ValidInTest"
TITLE = "m112_arrowFlat"
DESCRIPTION = "m099_cvControlDesc"
ICON = "/Icons/dp_arrowFlat.png"

dpValidInTestVersion = 0.1

class ValidInTest(dpBaseValidatorClass.ValidatorStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        dpBaseValidatorClass.ValidatorStartClass.__init__(self, *args, **kwargs)
    

    def runVerify(self, *args):
        ''' Main method to verify this validator instructions.
        '''
        self.checked = False
        self.okVerified = False
        # WIP
        #TODO
        # ### put code here...

        # if well done
        self.checked = True
        self.okVerified = False
        
        dpBaseValidatorClass.ValidatorStartClass.updateButtonColors(self)


    def runFix(self, *args):
        ''' Main method to fix this validator instructions.
        '''
        self.checked = False
        self.okFixed = False
        # WIP
        #TODO
        
        # if well done
        self.checked = True
        self.okFixed = True
        
        print("Running Fix...")
        dpBaseValidatorClass.ValidatorStartClass.updateButtonColors(self)
    