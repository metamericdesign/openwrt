import syslog  
import subprocess

import gsDebugPrint

gsdb = gsDebugPrint.gsDebugPrint("testDebug")

gsdb.setPrintToTerminal(True)
gsdb.setPrintToSysLog(True)

test_int = 221
test_float = 4.999
test_complex = 1+2j

test_hex = 0x1a2
test_octal = 0o12
test_binary = 0b101

test_byte = b'1200'

test_string = "this is a test string"

test_bool = False

test_list = ["apples","bottom","jeans"]
test_tuple= ("test",1+2j,211,0x1a2)
test_range = range(3, 6)

test_dict = {'Nepal': 'Kathmandu', 'Italy': 'Rome', 'England': 'London'}

test_set = {112, 114, 116, 118, 115}

gsdb.gsDebugPrint("--------------------------------------------")
gsdb.gsDebugPrint(test_int)
gsdb.gsDebugPrint(test_float)
gsdb.gsDebugPrint(test_complex)
gsdb.gsDebugPrint(test_hex)
gsdb.gsDebugPrint(test_octal)
gsdb.gsDebugPrint(test_binary)
gsdb.gsDebugPrint(test_byte)
gsdb.gsDebugPrint(test_string)
gsdb.gsDebugPrint(test_bool)
gsdb.gsDebugPrint(test_list)
gsdb.gsDebugPrint(test_tuple)
gsdb.gsDebugPrint(test_range)
gsdb.gsDebugPrint(test_dict)
gsdb.gsDebugPrint(test_set)
gsdb.gsDebugPrint("--------------------------------------------")
