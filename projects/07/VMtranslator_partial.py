from sys import exit, argv
from os import listdir
from os.path import isfile

# Command table for command_type function
command_tab = { 'push'     : 'C_PUSH', 
                'pop'      : 'C_POP',
                'label'    : 'C_LABEL',
                'if'       : 'C_IF',
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
        return line[:line.index('/')].replace('\n', '')
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
        
    def __init__(self, command):
        C_MEMORY.__init__(self, command)
        
    def write_pop(self):
        ''' Translates the pop command in assembly '''
        if self.arg1 in C_MEMORY.segment:
            return C_POP.pop_table['segment'].replace('@i', '@' + self.arg2).replace('segmentPointer', C_MEMORY.segment[self.arg1])
        elif self.arg1 == 'static':
            return C_POP.pop_table['static'].replace('file.i', argv[1].strip('vm') + self.arg2)
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

    def __init__(self, command):
        C_MEMORY.__init__(self, command)

    def write_push(self):
        ''' Translates the push command in assembly '''
        if self.arg1 == 'constant':
            return C_PUSH.push_table['constant'].replace('@i', '@' + self.arg2)
        elif self.arg1 in C_MEMORY.segment:
            return C_PUSH.push_table['segment'].replace('@i', '@' + self.arg2).replace('segmentPointer', C_MEMORY.segment[self.arg1])
        elif self.arg1 == 'static':
            return C_PUSH.push_table['static'].replace('file.i', argv[1].strip('vm') + self.arg2)
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
        return '(f$b)'.replace('f', self.f_name).replace('b', self.label)
    

class C_IF(object):
    ''' Class of if-goto commands '''
    
    def __init__(self, label, f_name):
        ''' Attribute: label , functionName'''
        self.label = label.split()[1]
        self.f_name = f_name
        
    def write_if(self):
        return '@SP\nM=M-1\n' + '@' + self.f_name + '$' + self.label + '\nD;JNE\n'
    
    
class C_GOTO(object):
    ''' Class of unconditional goto commands '''
    
    def __init__(self, label, f_name):
        ''' Attribute: label , functionName'''
        self.label = label.split()[1]
        self.f_name = f_name
        
    def write_goto(self):
        return '@SP\nM=M-1\n' + '@' + self.f_name + '$' + self.label + '\n0;JMP\n'


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
    
    def __init__(self, command, next_command):
        ''' Attributes: functionName, nArgs, returnAddress'''
        self.f_name = command.split()[1]
        self.n_args = command.split()[2]
        self.ret_addr = str(next_command)
        
    def write_call(self):
        '''
        Returns:
        push returnAddress, push LCL, push ARG, push THIS, push THAT,
        ARG = SP - 5 - nArgs, LCL = SP, goto functionName, (returnAddress)
        '''
        return '@retAddr\nD=A\n@SP\nAM=M+1\nA=A-1\nM=D\n'.replace('retAddr', self.ret_addr) +\
               '@LCL\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n' +\
               '@ARG\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n' +\
               '@THIS\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n' +\
               '@THAT\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n' +\
               '@nArgs\nD=A\n@5\nD=D+A\n@SP\nD=M-D\n@ARG\nM=D\n'.replace('nArgs', self.n_args) +\
               '@SP\nD=M\n@LCL\nM=D\n' +\
               '@f_name\n0;JMP\n'.replace('f_name', self.f_name) +\
               '(retAddr)\n'.replace('retAddr', self.ret_addr)    
               

class C_RETURN(object):
    ''' Class of function return commands '''
    def write_return(self):
        ''' 
        Returns: 
        endFrame = LCL, retAddr= *(endFrane - 5),
        *ARG = pop(), SP = ARG + 1, THAT = *(endFrame - 1),
        THIS = *(endFrame - 2), ARG = *(endFrame - 3), 
        LCL = *(endFrame - 4)
        '''
        return '@LCL\nD=M\n@end_frame\nM=D\n' +\
               '@5\nD=A\n@end_frame\nA=M-D\nD=M\n@retAddr\nM=D\n' +\
               '@SP\nA=M-1\nD=M\n@ARG\nA=M\nM=D\n' +\
               '@ARG\nD=M+1\n@SP\nM=D\n' +\
               '@end_frame\nAM=M-1\nD=M\n@THAT\nM=D\n' +\
               '@end_frame\nAM=M-1\nD=M\n@THIS\nM=D\n' +\
               '@end_frame\nAM=M-1\nD=M\n@ARG\nM=D\n' +\
               '@end_frame\nAM=M-1\nD=M\n@LCL\nM=D\n' +\
               '@retAddr\nA=M\n0;JMP\n'
               
       
def code_writer(c_type, command, next_command, f_name):
    ''' 
    Argument: function command_type, command, (int) next command
    Returns the translation of the command 
    '''
    if c_type == 'C_PUSH':
        return C_PUSH(command).write_push()
    elif c_type == 'C_POP':
        return C_POP(command).write_pop()
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
        return C_CALL(command, next_command).write_call()
    elif c_type == 'C_RETURN':
        return C_RETURN.write_return(C_RETURN)
    
    
def write_init():
    ''' Returns bootstrap code '''
    return '@256\nD=A\n@SP\nM=D\n'


def file_writer(vm_file, asm_file):
    ''' Translate all the lines of a vm file in the asm file'''
    PC = 0
    f_name = vm_file
    for line in vm_file:
            line = clean_line(line)
            if line != '':
                
                # Save the name of the function for later use
                if line.strip()[0] == 'function':
                    f_name = line.strip()[1]
                    
                PC += 1
                asm_file.write('// ' + line + '\n' + code_writer(command_type(line), line, PC+1, f_name))
    

def main():
    ''' Main function '''
    if len(argv) != 2:
        print("Usage: VMtranslator.py fileName.vm/directoryName")
        exit(1)
     
    # Open an asm file for writing
    asm_file = open(argv[1].replace('vm', 'asm'), 'w')

    if isfile(argv[1]):
        vm_file = open(argv[1], 'r')
        file_writer(vm_file, asm_file)
    else:
        # Create a list with all the .vm files in the directory
        files = [vm for vm in listdir(argv[1]) if '.vm' in vm]
        
        # Move sys.vm at the beginning of the files list
        files[files.index('sys.vm')], files[0] = files[0], files[files.index('sys.vm')]
        
        # Write the bootstrap code 
        write_init()
        
        # Write each vm translated into the asm file, starting with sys
        for vm_file in files:
            file_writer(vm_file, asm_file)
     
    #Close the asm_file
    asm_file.close()

main()