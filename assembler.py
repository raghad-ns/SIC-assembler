import re
opcodeTable = {
    'STL': '14', 'JSUB': '48', 'LDA': '00', 'COMP': '28', 'STCH': '54', 'LDCH': '50',
    "RSUB": "4C", "JEQ": "30", "J": "3C", "STA": "0C", "LDL": "08", "LDX": "04", "TD": "E0",
    "RD": "D8", "TIX": "2C", "JLT": "38", "STX": "10", "WD": "DC", "ADD": "18", "AND": "40",
    "DIV": "28", "JGT": "34", "MUL": "20", "OR": "44", "STSW": "E8", "SUB": "1C"
}
directivesTable = ['BYTE', 'RESB', 'WORD', 'RESW', 'START', 'END']

def sumHex (a, b):
   hex1 = int(a, 16)
   hex2 = int(b, 16)
   return (hex(hex1 + hex2) [2:].upper())

def subHex (a, b):
   hex1 = int(a, 16)
   hex2 = int(b, 16)
   return (hex(hex1 - hex2) [2:].upper())

programLength = 0
programName = ""
startingAddress = "000000"
symbolTable = {}
errors = open('errors.txt', 'w')

def pass1() :
   global programName, programLength, startingAddress, symbolTable
   source = open("source3.asm", 'r')
   intermediate = open("intermediate.mdt", 'w')
   pass1Out = open("pass1-out.txt", 'w')
   sourceCode = source.read()
   lines = sourceCode.split('\n')
   locationCounter = "0000" # Initialize location counter to 0

   if lines[0][11:20].strip() == "START": # handle the start of program label
      startingAddress = lines[0][21:39].strip()
      locationCounter = startingAddress # set location counter to the address given in START directive
      intermediate.write(locationCounter + "     "+ lines[0][:30]+ '\n')
      programName = lines[0][:11].strip()
      if lines[0][:10].strip() != "": # if the line contains label
         if lines[0][:10].strip() in symbolTable: # check if it is already defined
            print("Duplicated Label Error: ", lines[0][:10].strip()) # Set error flag
            errors.write("Error: Duplicated Label Error \n")
            errors.write("\t"+ instruction)
         else:
            symbolTable[lines[0][:11].strip()] = startingAddress # insert into the symbol table

   #  Process each line of code
   for instruction in lines[1:] :
      label = instruction[0:10]
      opcode = instruction[11:20].strip()
      operand = instruction[21:39]
      instruction = instruction[:39]

      if instruction[0] == ".": # its a comment line
         continue # skip

      if label.strip() != "": # if the line contains label
         if label.strip() in symbolTable: # check if it is already defined
            print("Duplicated Label Error") # Set error flag
            errors.write("Error: Duplicated Label Error \n")
            errors.write("\t"+ instruction)
            break
         else:
            symbolTable[label.strip()] = locationCounter # insert into the symbol table

      if opcode in opcodeTable: # valid opcode found
         # For optimization purposes, store the machine code for the menimonic in the intermediate file, in order not to access the opcode table another time during pass2
         instruction = instruction[:39] + opcodeTable[opcode] 
         # intermediate.write(locationCounter + "     "+ instruction[:30] + opcodeTable[opcode] + '\n')
         tempLocationCounter = sumHex(locationCounter, "3") # Updata location  counter by adding 3 (size of current instruction)
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
            errors.write("Invalid Opcode Error: "+ opcode)
            errors.write("\t"+ instruction)
            break
      intermediate.write(locationCounter + "     "+ instruction + '\n')
      locationCounter = tempLocationCounter
      if opcode == "END": # end of program reached
         programLength = subHex(locationCounter, startingAddress)
   print("Program Length: ", programLength)
   print("symbol table: ", symbolTable)
   pass1Out.writelines("PRGNAME: "+ programName+ '\n')
   pass1Out.writelines("STARTADR: "+ startingAddress+ '\n')
   pass1Out.writelines("PRGLTH: "+ str(programLength)+ '\n')
   pass1Out.writelines("LOCCTR: "+ locationCounter+ '\n')
   pass1Out.writelines(" \n")
   pass1Out.writelines("SYBTAB: \n")
   pass1Out.writelines("|------------|------------|\n")
   pass1Out.writelines("|   SYMBOL   |   ADDRESS  |\n")
   pass1Out.writelines("|------------|------------|\n")
   for key in sorted(symbolTable):
      pass1Out.writelines("| " + key + ' ' * (11 - len(key)) +"| "+ symbolTable[key] + '       |\n')
      pass1Out.writelines("|------------|------------|\n")
   

def pass2(): 
   global programName, programLength, startingAddress, symbolTable
   intermediate = open('intermediate.mdt', 'r')
   objectProgram = open('object.obj', 'w')
   listingFile = open('listing.lst','w')
   sourceCode = intermediate.read()
   lines = sourceCode.split('\n')
   Hrecord = ' ' * 19 
   if lines[0][20:29].strip() == "START": # handle the start of program label
      listingFile.write(lines[0] + '\n')
      Hrecord = 'H' + programName + ' ' * (6 - len(programName)) +  '0' * (6 - len(startingAddress)) + startingAddress + '0' * (6 - len(str(programLength))) + str(programLength)
      objectProgram.write(Hrecord + '\n')

   tRecord = ''
   tRecordStart = ''
   tRecordSize = 0
   tRecordMaxSize = 30

   for instruction in lines[1:] :
      opcode = instruction[20:29].strip()
      operand = instruction[30:48]
      locCtr = instruction[:9].strip()
      objectCode = ''
      instruction += (' ' * (40 - len(instruction)))
      if len(instruction) and instruction[0] == ".": # its a comment line
         continue # skip

      if opcode == "END": # end of program reached
         if (tRecord): objectProgram.write('T' + tRecordStart + '0' * (2 - len(hex(tRecordSize)[2:])) + hex(tRecordSize)[2:].upper() + tRecord + '\n')
         endRecord = 'E' + '0' * (6 - len(startingAddress)) + startingAddress
         objectProgram.write(endRecord+'\n')
         listingFile.write(instruction)
         continue
      
      if opcode in opcodeTable: # valid opcode found
         if tRecordStart == '': 
            tRecordStart = '0' * (6 - len(locCtr)) + locCtr
         if (len(operand.strip( ) ) > 0): # there is an operand
            objectCode = instruction[48:50]
            indexed = False
            if len(operand.strip()) > 2 and operand.strip()[-2:] == ",X" :
               operand = operand.strip()[:-2]
               indexed = True

            if operand.strip() in symbolTable: # check if operand existed in the symbol table
               targetAddress = '0' * (4 - len(symbolTable[operand.strip()])) + symbolTable[operand.strip()]  # get address from symbol table
               objectCode = (targetAddress if indexed == False else sumHex(targetAddress, '8000'))
            else:
               print("Undefined Label Error, in pass2: "+ operand.strip()) # Set error flag
               errors.write("Error: Undefined Label Error \n")
               errors.write("\t"+ instruction)
               break
         else: 
            objectCode = "0000" # no operands so add zeros
         if (tRecordSize + 3 <= tRecordMaxSize): 
            tRecordSize += 3
            tRecord += (instruction[48:50]+ objectCode)
         else: 
            objectProgram.write('T' + tRecordStart + '0' * (2 - len(hex(tRecordSize)[2:])) + hex(tRecordSize)[2:].upper() + tRecord + '\n')
            tRecordStart = '0' * (6 - len(locCtr)) + locCtr
            tRecord = instruction[48: 50] + objectCode
            tRecordSize = 3
         instruction += objectCode
      else :
         if opcode == "WORD":
            tRecordSize += 3 
            objectCode = '0' * (6 - len(hex(int(operand))[2:])) + hex(int(operand))[2:]
            tRecord += '0' * (6 - len(hex(int(operand))[2:])) + hex(int(operand))[2:]
            instruction += objectCode
         elif opcode == "BYTE": 
            value = re.findall(r"'(.*?)'", operand)[0]
            if operand[0] == 'C': 
               hex_representation = ''.join([hex(ord(char))[2:] for char in value])
               tRecord += hex_representation
               objectCode = hex_representation
               tRecordSize += len(value)
            elif operand[0] == 'X': 
               objectCode = value
               tRecordSize += int(len(value) / 2) +  int(len(value) % 2)
               tRecord += value
            instruction += objectCode
         elif opcode == "RESW" or opcode == "RESB": # write text record in the object file
            if (tRecord): objectProgram.write('T' + tRecordStart + '0' * (2 - len(hex(tRecordSize)[2:])) + hex(tRecordSize)[2:].upper() + tRecord + '\n')
            tRecord = ''
            tRecordStart = ''
            tRecordSize = 0
         elif len(opcode.strip()) and opcode not in opcodeTable and opcode not in directivesTable: # invalid opcode
            errors.write("Invalid Opcode Error: "+ opcode)
            errors.write("\t"+ instruction)
            break
      listingFile.write(instruction + '\n')
   



print("\nPass 1 in progress...")
pass1()
print("\nPass 1 completed successfully.")
print("Pass 2 in progress...")
pass2()
print("\nPass 2 completed successfully.")