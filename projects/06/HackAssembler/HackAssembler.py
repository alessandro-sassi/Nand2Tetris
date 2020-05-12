from sys import argv, exit
from assembly_tables import symbols_table, comp_table, dest_table, jump_table

def del_space():
    ''' Return a list with the lines of the assembly code
    without spaces, empty lines and comments '''
    with open(argv[1]) as file:
        code_lines= []

        #Iterate over lines in the file to remove withe spaces, new lines and comments
        for line in file:
            line = line.replace(" ", "").replace("\n", "")
            if '/' in line:
                index = line.index('/')
                line = line.strip(line[index:])

            # Appends lines of the code to the list
            if line != "":
                code_lines.append(line)

        return code_lines


def C_parser(line, comp = '', dest = '', jump = ''):
    ''' Take a C-instruction from the code list
    and returns a tuple with comp, dest and jump '''
    for e in range(len(line)):
        if line[e] == '=':
            dest = line[:e]
            comp = line[e + 1:]
            jump = 'null'
        elif line[e] == ';':
            jump = line[e + 1:]
            comp = line[:e]
            dest = 'null'

    return comp, dest, jump


def A_translate(value):
    ''' Translate an A-instruction in int form to its binary form as a string '''
    if value == 0:
        return '0000000000000000'

    def dec_to_bin(value, result = ''):
        '''
        Converts a decimal value to binary and returns it in string form
        '''
        while len(result) < 15:
            result = str(value % 2) + result
            value = value // 2

        return result

    return '0' + dec_to_bin(value)


def C_translate(cdj, c = '', d = '', j = ''):
    ''' Returns a string with the c-instruction
    converted in binary '''
    if cdj[0] in comp_table[0]:
        c = '0' + comp_table[0][cdj[0]]
    else:
        c = '1' + comp_table[1][cdj[0]]

    d = dest_table[cdj[1]]
    j = jump_table[cdj[2]]

    return '111' + c + d + j


def check_symbol(symbol, val):
    ''' If the symbol it's new it's a new variable: append it to the symbols table.
    Returns the corresponding value in the table '''
    global n
    n = val
    if symbol not in symbols_table:
        symbols_table[symbol] = str(n)
        n += 1

    return symbols_table[symbol]


def check_labels(code_list, line = 0):
    ''' Check for labels (xxx) in the code list, and add them in the symbols table '''
    while line < len(code_list):
        if code_list[line][0] == '(':
            label = code_list[line].replace('(', '').replace(')', '')
            symbols_table[label] = line
            code_list.remove(code_list[line])
        else:
            line += 1


def main(n = 16):
    ''' M A I N '''
    if len(argv) != 2:
        print("Usage: python HackAssembler.py file.asm")
        exit(1)

    # Code is a list of the code lines
    code = del_space()
    check_labels(code)

    for line in range(len(code)):

        # Manage the a-inst and checks if it's a variable symbol
        if code[line][0] == '@':
            address = code[line].replace('@', '')
            symbol = address[0].isalpha()
            if symbol:
                address = check_symbol(address, n)

            # Translate the a-inst and replace it with its binary value in the code list
            a_inst = A_translate(int(address))
            code[line] = a_inst

        # Unpack the c-inst, translate it and add it to the code list
        else:
            c_pack = C_parser(code[line])
            c_inst = C_translate(c_pack)
            code[line] = c_inst

    #Write the code list in a new file.hack
    program = argv[1].replace('asm', 'hack')
    with open(program, 'w') as file:
        for line in code:
            file.write(line + '\n')

import time
start_time = time.time()
main()
print("--- %s seconds ---" % (time.time() - start_time))
