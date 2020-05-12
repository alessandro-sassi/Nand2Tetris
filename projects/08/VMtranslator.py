from sys import exit, argv
from os import listdir
from os.path import isfile

# Command table for command_type function
command_tab = { 'push'     : 'C_PUSH',
                'pop'      : 'C_POP',
                'label'    : 'C_LABEL',
                'if-goto'  : 'C_IF',
                'goto'     : 'C_GOTO',
                'function' : 'C_FUNCTION',
                'call'     : 'C_CALL',
                'return'   : 'C_RETURN' }

def command_type(command):
    ''' Returns a string representing the type of the command '''
    if command in C_ARITHMETIC.arithmetic_table:
        return 'C_ARITHMETIC'
    else:
        return command_tab[command.split(' ')[0]]


def clean_line(line):
    ''' Removes comments if existing '''
    try:
        return line[:line.index('/')].replace('\n', '').strip()
    except ValueError:
        return line.replace('\n', '')


class C_MEMORY(object):
    ''' Class of memory commands '''

    segment = {'argument' : 'ARG', 'local' : 'LCL', 'this' : 'THIS', 'that' : 'THAT'}

    def __init__(self, command):
        '''
        Attributes: arg1 = segment, arg2 = i
        segment = (argument, local, this, that),
        static, constant,  pointer, temp
        '''
        self.arg1 = command.split()[1]
        self.arg2 = command.split()[2]


class C_POP(C_MEMORY):
    ''' Class of pop commands '''

    pop_table = { 'segment' : '@i\nD=A\n@segmentPointer\nD=D+M\n@addr\nM=D\n@SP\nAM=M-1\nD=M\n@addr\nA=M\nM=D\n',
                  'static'  : '@SP\nAM=M-1\nD=M\n@file.i\nM=D\n',
                  'pointer' : '@SP\nAM=M-1\nD=M\n@THIS/THAT\nM=D\n',
                  'temp'    : '@5+i\nD=A\n@addr\nM=D\n@SP\nAM=M-1\nD=M\n@addr\nA=M\nM=D\n' }

    def __init__(self, command, file_name):
        C_MEMORY.__init__(self, command)
        self.file_name = file_name

    def write_pop(self):
        ''' Translates the pop command in assembly '''
        if self.arg1 in C_MEMORY.segment:
            return C_POP.pop_table['segment'].replace('@i', '@' + self.arg2).replace('segmentPointer', C_MEMORY.segment[self.arg1])
        elif self.arg1 == 'static':
            return C_POP.pop_table['static'].replace('file.i', self.file_name.strip('vm') + self.arg2)
        elif self.arg1 == 'temp':
            return C_POP.pop_table['temp'].replace('5+i', str(5 + int(self.arg2)))
        elif self.arg1 == 'pointer':
            if self.arg2 == '0':
                return C_POP.pop_table['pointer'].replace('THIS/THAT', 'THIS')
            else:
                return C_POP.pop_table['pointer'].replace('THIS/THAT', 'THAT')

class C_PUSH(C_MEMORY):
    ''' Class of push commands '''

    push_table = {'constant' : '@i\nD=A\n@SP\nM=M+1\nA=M-1\nM=D\n',
                  'segment'  : '@i\nD=A\n@segmentPointer\nD=D+M\n@addr\nAM=D\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n',
                  'static'   : '@file.i\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n',
                  'pointer'  : '@THIS/THAT\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n',
                  'temp'     : '@5+i\nD=A\n@addr\nAM=D\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n' }

    def __init__(self, command, file_name):
        C_MEMORY.__init__(self, command)
        self.file_name = file_name

    def write_push(self):
        ''' Translates the push command in assembly '''
        if self.arg1 == 'constant':
            return C_PUSH.push_table['constant'].replace('@i', '@' + self.arg2)
        elif self.arg1 in C_MEMORY.segment:
            return C_PUSH.push_table['segment'].replace('@i', '@' + self.arg2).replace('segmentPointer', C_MEMORY.segment[self.arg1])
        elif self.arg1 == 'static':
            return C_PUSH.push_table['static'].replace('file.i', self.file_name.strip('vm') + self.arg2)
        elif self.arg1 == 'temp':
            return C_PUSH.push_table['temp'].replace('5+i', str(5 + int(self.arg2)))
        elif self.arg1 == 'pointer':
            if self.arg2 == '0':
                return C_PUSH.push_table['pointer'].replace('THIS/THAT', 'THIS')
            else:
                return C_PUSH.push_table['pointer'].replace('THIS/THAT', 'THAT')


class C_ARITHMETIC(object):
    ''' Class of arithmetic commands '''

    # variable for unique labels
    x = 0
    arithmetic_table = { 'add' : '@SP\nAM=M-1\nD=M\nA=A-1\nM=M+D\n',
                         'sub' : '@SP\nAM=M-1\nD=M\nA=A-1\nM=M-D\n',
                         'neg' : '@SP\nA=M-1\nM=-M\n',
                         'eq'  : '@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\nM=-1\n@END_EQx\nD;JEQ\n@SP\nA=M-1\nM=0\n(END_EQx)\n',
                         'gt'  : '@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\nM=-1\n@END_GTx\nD;JGT\n@SP\nA=M-1\nM=0\n(END_GTx)\n',
                         'lt'  : '@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\nM=-1\n@END_LTx\nD;JLT\n@SP\nA=M-1\nM=0\n(END_LTx)\n',
                         'and' : '@SP\nAM=M-1\nD=M\nA=A-1\nM=D&M\n',
                         'or'  : '@SP\nAM=M-1\nD=M\nA=A-1\nM=D|M\n',
                         'not' : '@SP\nA=M-1\nM=!M\n' }

    def __init__(self, command):
        ''' Attribute: arithmetic command '''
        self.command = command

    def write_arithmetic(self):
        ''' Translates the arithmetic command in assembly '''
        C_ARITHMETIC.x += 1
        return C_ARITHMETIC.arithmetic_table[self.command].replace('x', str(C_ARITHMETIC.x))


class C_LABEL(object):
    ''' Class of label commands '''

    def __init__(self, label, f_name):
        ''' Attribute: label , functionName'''
        self.label = label.split()[1]
        self.f_name = f_name

    def write_label(self):
        return f'({self.f_name}${self.label}{str(C_CALL.id)})\n'


class C_IF(object):
    ''' Class of if-goto commands '''

    def __init__(self, label, f_name):
        ''' Attribute: label , functionName'''
        self.label = label.split()[1]
        self.f_name = f_name

    def write_if(self):
        return '@SP\nAM=M-1\nD=M\n' +\
               '@' + self.f_name + '$' + self.label + str(C_CALL.id) + '\nD;JNE\n'


class C_GOTO(object):
    ''' Class of unconditional goto commands '''

    def __init__(self, label, f_name):
        ''' Attribute: label , functionName'''
        self.label = label.split()[1]
        self.f_name = f_name

    def write_goto(self):
        return '@' + self.f_name + '$' + self.label + str(C_CALL.id) + '\n0;JMP\n'


class C_FUNCTION(object):
    ''' Class of function commands '''

    def __init__(self, command):
        ''' Attributes: functionName, nVars'''
        self.f_name = command.split()[1]
        self.n_vars = int(command.split()[2])

    def write_function(self):
        '''
        Returns: (functionName)
                 repeat n_vars times:
                     push 0
        '''
        return '(' + self.f_name + ')' + '\n' +\
               '@SP\nM=M+1\nA=M-1\nM=0\n' * self.n_vars


class C_CALL(object):
    ''' Class of call function commands '''

    # Unique id for labels and return addresses of functions
    id = 0

    def __init__(self, command):
        ''' Attributes: functionName, nArgs, returnAddress '''
        self.f_name = command.split()[1]
        self.n_args = command.split()[2]
        C_CALL.id += 1

    def write_call(self):
        '''
        Returns:
        push returnAddress, push LCL, push ARG, push THIS, push THAT,
        ARG = SP - 5 - nArgs, LCL = SP, goto functionName, (returnAddress)
        '''
        return f'@return_address_{self.f_name}_{C_CALL.id}\nD=A\n@SP\nAM=M+1\nA=A-1\nM=D\n' +\
               '@LCL\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n' +\
               '@ARG\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n' +\
               '@THIS\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n' +\
               '@THAT\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n' +\
               '@nArgs\nD=A\n@5\nD=D+A\n@SP\nD=M-D\n@ARG\nM=D\n'.replace('nArgs', self.n_args) +\
               '@SP\nD=M\n@LCL\nM=D\n' +\
               '@f_name\n0;JMP\n'.replace('f_name', self.f_name) +\
               f'(return_address_{self.f_name}_{C_CALL.id})\n'


class C_RETURN(object):
    ''' Class of function return commands '''

    def write_return(self):
        '''
        Returns:
        endFrame = LCL, retAddr = *(endFrame - 5),
        *ARG = pop(), SP = ARG + 1, THAT = *(endFrame - 1),
        THIS = *(endFrame - 2), ARG = *(endFrame - 3),
        LCL = *(endFrame - 4)
        '''
        return '@LCL\nD=M\n@end_frame\nM=D\n' +\
               '@5\nD=A\n@end_frame\nA=M-D\nD=M\n@R14\nM=D\n' +\
               '@SP\nA=M-1\nD=M\n@ARG\nA=M\nM=D\n' +\
               '@ARG\nD=M+1\n@SP\nM=D\n' +\
               '@end_frame\nAM=M-1\nD=M\n@THAT\nM=D\n' +\
               '@end_frame\nAM=M-1\nD=M\n@THIS\nM=D\n' +\
               '@end_frame\nAM=M-1\nD=M\n@ARG\nM=D\n' +\
               '@end_frame\nAM=M-1\nD=M\n@LCL\nM=D\n' +\
               '@R14\nA=M\n0;JMP\n'


def code_writer(c_type, command, f_name, file_name):
    '''
    Arguments: function command_type, command, function_name, file_name
    Returns the translation of the command
    '''
    if c_type == 'C_PUSH':
        return C_PUSH(command, file_name).write_push()
    elif c_type == 'C_POP':
        return C_POP(command, file_name).write_pop()
    elif c_type == 'C_ARITHMETIC':
        return C_ARITHMETIC(command).write_arithmetic()
    elif c_type == 'C_LABEL':
        return C_LABEL(command, f_name).write_label()
    elif c_type == 'C_IF':
        return C_IF(command, f_name).write_if()
    elif c_type == 'C_GOTO':
        return C_GOTO(command, f_name).write_goto()
    elif c_type == 'C_FUNCTION':
        return C_FUNCTION(command).write_function()
    elif c_type == 'C_CALL':
        return C_CALL(command).write_call()
    elif c_type == 'C_RETURN':
        return C_RETURN().write_return()


def write_init():
    ''' 
    Returns bootstrap code:
    SP = 256, call Sys.init()
    '''
    return '// Boostrap code\n' +\
           '@256\nD=A\n@SP\nM=D\n' +\
           code_writer('C_CALL', 'call Sys.init 0', 'Sys.init', '')


def file_writer(vm_file, asm_file, file_name):
    '''
    Arguments: file.vm, file.asm, (str) name of file
    Translate all the lines of a vm file in the asm file
    '''
    function_name = ''
    for line in vm_file:
            line = clean_line(line)
            if line != '':
                # Save the name of the function for later use
                if line.split()[0] == 'function':
                    function_name = line.split()[1]

                # Increase the line counter and translate the command into the asm file
                asm_file.write('// ' + line + '\n' + code_writer(command_type(line), line, function_name, file_name))

def main():
    ''' Main function '''
    if len(argv) != 2:
        print("Usage: VMtranslator.py fileName.vm/directoryName")
        exit(1)

    try:
        # Open an asm file for writing
        asm_file = open(argv[1].replace('vm', 'asm'), 'w')

    except IsADirectoryError:
        # asm file name = DirectoryName.asm
        asm_file = open(argv[1].split('/')[-1] + '.asm', 'w')

    # if input == file.vm
    if isfile(argv[1]):
        with open(argv[1], 'r') as vm_file:
            file_writer(vm_file, asm_file, argv[1])

    # If input == directory
    else:
        # Create a list with all the .vm files in the directory
        files = [vm for vm in listdir(argv[1]) if '.vm' in vm]

        # Write the bootstrap code if Sys.vm exist
        if 'Sys.vm' in files:
            asm_file.write(write_init())

        # Iterate over vm files in the list and translate each one
        for file in files:
            with open(argv[1] + '/' + file, 'r') as vm_file:
                file_writer(vm_file, asm_file, file)

    #Close the asm_file
    asm_file.close()

main()
