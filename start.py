import re
# opcodeTable={
#    'STL':'14',
#    'JSUB':'48',
#    'LDA':'00',
#    'COMP':'28',
#    'STCH':'54',
#    'LDCH':'50',
#    "RSUB":"4C",
#    "JEQ":"30",
#    "J":"3C",
#    "STA":"0C",
#    "LDL":"08",
#    "LDX":"04",
#    "TD":"E0",
#    "RD":"D8",
#    "TIX":"2C",
#    "JLT":"38",
#    "STX":"10",
#    "WD":"DC",
#    } 
opcodeTable = {
    'STL': '14', 'JSUB': '48', 'LDA': '00', 'COMP': '28', 'STCH': '54', 'LDCH': '50',
    "RSUB": "4C", "JEQ": "30", "J": "3C", "STA": "0C", "LDL": "08", "LDX": "04", "TD": "E0",
    "RD": "D8", "TIX": "2C", "JLT": "38", "STX": "10", "WD": "DC",
}
directivesTable = ['BYTE', 'RESB', 'WORD', 'RESW', 'START', 'END']
# print(opcodeTable["LDA"]) 

def sumHex (a, b):
   hex1 = int(a, 16)
   hex2 = int(b, 16)
   return (hex(hex1 + hex2) [2:].upper())

def subHex (a, b):
   hex1 = int(a, 16)
   hex2 = int(b, 16)
   return (hex(hex1 - hex2) [2:].upper())

source = open("source.asm", 'r')
intermediate = open("intermediate.mdt", 'w')
sourceCode = source.read()
lines = sourceCode.split('\n')
symbolTable = {}
locationCounter = "0000"
programLength = 0
programName = ""
startingAddress = ""
if lines[0][11:21].strip() == "START": # handle the start of program label
   startingAddress = lines[0][21:30].strip()
   locationCounter = startingAddress
   intermediate.write(locationCounter + "     "+ lines[0]+ '\n')
for instruction in lines[1:] :
   label = instruction[0:11].strip()
   opcode = instruction[11:21].strip()
   operand = instruction[21:30].strip()
   if label.strip() == ".": # its a comment line
      continue
   if label.strip() != "": # if the line contains label
      if label in symbolTable: # check if it is already defined
         print("Duplicated Label Error")
         break
      else:
         symbolTable[label] = locationCounter # insert into the symbol table
   if opcode in opcodeTable: # valid opcode found
      tempLocationCounter = sumHex(locationCounter, "3")
    #   print("location counter: ", locationCounter)
   elif opcode == "WORD": 
      tempLocationCounter = sumHex(locationCounter, "3")
   elif opcode == "RESW": 
      tempLocationCounter = sumHex(locationCounter, str(hex(3 * int(operand))))
   elif opcode == "BYTE": 
      value = re.findall(r"'(.*?)'", operand)[0]
      if operand[0] == 'C': 
        print('value: ', value)
        tempLocationCounter = sumHex(locationCounter, str(len(value)))
   elif opcode == "RESB": 
      tempLocationCounter = sumHex(locationCounter, str(hex(int(operand))))
   elif opcode not in opcodeTable and opcode not in directivesTable: # invalid opcode
      print("Invalid Opcode Error", opcode)
      break
   intermediate.write(locationCounter + "     "+ instruction+ '\n')
   locationCounter = tempLocationCounter
   if opcode == "END": # end of program reached
      programLength = subHex(locationCounter, startingAddress)
print("Program Length: ", programLength)
print("symbol table: ", symbolTable)