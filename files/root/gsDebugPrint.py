
import os
import syslog  

class gsDebugPrint : 

    def __init__(self , facility :str ) -> None:
        syslog.openlog(facility)

    terminalPrint = False
    sysLogPrint = True

    # 0 Standard print --> messages along the way 
    # 1 Notice --> signifigant system events --> syslog.LOG_NOTICE
    # 2 Warning --> continue but may have signifigance --> syslog.LOG_WARNING
    # 3 Error --> expected/ handled error  --> syslog.LOG_ERR
    # 4 Major error --> not handled / shuts down functions  --> syslog.LOG_CRIT

    def setPrintToTerminal(self,printTerminal :bool):
        self.terminalPrint = printTerminal

    def setPrintToSysLog(self,printSysLog :bool):
        self.sysLogPrint = printSysLog

    def gsDebugPrint(self,message, verbosity :int =0):
        terminalMessage = "    "
        sysLogVerb = syslog.LOG_INFO

        if verbosity == 1:
            sysLogVerb = syslog.LOG_NOTICE
            terminalMessage ="  NOTICE :"

        if verbosity == 2:
            sysLogVerb = syslog.LOG_WARNING
            terminalMessage ="   WARNING :"

        if verbosity == 3:
            sysLogVerb = syslog.LOG_ERR
            terminalMessage ="   ERROR :"

        if verbosity == 4:
            sysLogVerb = syslog.LOG_CRIT
            terminalMessage ="   CRITICAL ERROR :"

        # sanatize print 

        if type(message) == str :

            if self.terminalPrint:
                terminalMessage += message
                print (terminalMessage)

            if self.sysLogPrint:
                syslog.syslog(sysLogVerb ,message)

        else :

            if self.terminalPrint:
                print ("   CRITICAL ERROR : Debug message type not recognized")

            if self.sysLogPrint:
                syslog.syslog(syslog.LOG_CRIT,"Debug message type not recognized")




        
        


