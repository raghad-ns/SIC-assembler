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

def pass1() :
   source = open("source.asm", 'r')
   intermediate = open("intermediate.mdt", 'w')
   errors = open('errors.txt', "w")
   pass1Out = open("pass1-out", 'w')
   sourceCode = source.read()
   lines = sourceCode.split('\n')
   symbolTable = {}
   locationCounter = "0000" # Initialize location counter to 0
   programLength = 0
   programName = ""
   startingAddress = ""

   if lines[0][11:21].strip() == "START": # handle the start of program label
      startingAddress = lines[0][21:30].strip()
      locationCounter = startingAddress # set location counter to the address given in START directive
      intermediate.write(locationCounter + "     "+ lines[0][:30]+ '\n')
      programName = lines[0][21:30].strip()

   #  Process each line of code
   for instruction in lines[1:] :
      label = instruction[0:11]
      opcode = instruction[11:21].strip()
      operand = instruction[21:30]

      if instruction[0] == ".": # its a comment line
         continue # skip

      if label.strip() != "": # if the line contains label
         if label in symbolTable: # check if it is already defined
            print("Duplicated Label Error") # Set error flag
            errors.write("Error: Duplicated Label Error \n")
            errors.write("\t"+ instruction)
            break
         else:
            symbolTable[label] = locationCounter # insert into the symbol table

      if opcode in opcodeTable: # valid opcode found
         tempLocationCounter = sumHex(locationCounter, "3") # Updata location  counter by adding 3 (size of current instruction)
       #   print("location counter: ", locationCounter)
      else :
         if opcode == "WORD": 
            tempLocationCounter = sumHex(locationCounter, "3")
         elif opcode == "RESW": 
            tempLocationCounter = sumHex(locationCounter, str(hex(3 * int(operand))))
         elif opcode == "BYTE": 
            value = re.findall(r"'(.*?)'", operand)[0]
            if operand[0] == 'C': 
               tempLocationCounter = sumHex(locationCounter, str(len(value)))
            elif operand[0] == 'X': 
               tempLocationCounter = sumHex(locationCounter, str(int(len(value) / 2) +  int(len(value) % 2))) 
         elif opcode == "RESB": 
            tempLocationCounter = sumHex(locationCounter, str(hex(int(operand))[2:]))
         elif opcode not in opcodeTable and opcode not in directivesTable: # invalid opcode
            errors.write("Invalid Opcode Error", opcode)
            errors.write("\t"+ instruction)
            break
      intermediate.write(locationCounter + "     "+ instruction[:30]+ '\n')
      locationCounter = tempLocationCounter
      if opcode == "END": # end of program reached
         programLength = subHex(locationCounter, startingAddress)
   print("Program Length: ", programLength)
   print("symbol table: ", symbolTable)
   pass1Out.writelines("PRGNAME: "+ programName+ '\n')
   pass1Out.writelines("PRGLTH: "+ programLength+ '\n')
   pass1Out.writelines("LOCCTR: "+ locationCounter+ '\n')
   pass1Out.writelines(" \n")
   pass1Out.writelines("SYBTAB: \n")
   pass1Out.writelines("|------------|------------|\n")
   # pass1Out.writelines("__________________________\n")
   pass1Out.writelines("|   SYMBOL   |   ADDRESS  |\n")
   # pass1Out.writelines("|____________|____________|\n")
   pass1Out.writelines("|------------|------------|\n")
   for key in sorted(symbolTable):
      pass1Out.writelines("| "+ key+"| "+ symbolTable[key] + '       |\n')
      pass1Out.writelines("|------------|------------|\n")
      # pass1Out.writelines("|____________|____________|\n")
   

def pass2(): 
   intermediate = open('intermediate.mdt', 'r')

pass1()