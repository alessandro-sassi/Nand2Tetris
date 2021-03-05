class VMWriter:

    def __init__(self, vmfile):
        ''' Creates a new file and prepares it for writing '''
        self.vmfile = open(vmfile, 'w')


    def write_push(self, segment, index):
        '''
        Writes a VM push command.
        Arguments:
            - segment (const, arg, local, static, this, that, pointer, temp)
            - index (int)
        '''
        segment = segment.replace('var', 'local').replace('field', 'this')
        self.vmfile.write(f'push {segment} {index}' +'\n')


    def write_pop(self, segment, index):
        '''
        Writes a VM pop command.
        Arguments:
            - segment (const, arg, local, static, this, that, pointer, temp)
            - index (int)
        '''
        segment = segment.replace('var', 'local')
        self.vmfile.write(f'pop {segment} {index}' + '\n')


    def write_arithmetic(self, command):
        '''
        Writes a VM arithmetic command.
        Arguments:
            - command (add, sub, neg, eq, gt, lt, and, or, not)
        '''
        if command == '*':
            self.write_call('Math.multiply', 2)
        elif command == '/':
            self.write_call('Math.divide', 2)
        else:
            command = command.replace('+', 'add').replace('-', 'sub').replace('~', 'not')\
                         .replace('=', 'eq').replace('&gt;', 'gt').replace('&lt;', 'lt')\
                         .replace('&amp;', 'and').replace('|', 'or')
            self.vmfile.write(command + '\n')



    def write_label(self, label):
        '''
        Writes a VM label command.
        Arguments:
            - label (string)
        '''
        self.vmfile.write(f'label {label}' + '\n')


    def write_goto(self, label):
        '''
        Writes a VM goto command.
        Arguments:
            - label (string)
        '''
        self.vmfile.write(f'goto {label}' + '\n')


    def write_if(self, label):
        '''
        Writes a VM if-goto command.
        Arguments:
            - label (string)
        '''
        self.vmfile.write(f'if-goto {label}' + '\n')


    def write_call(self, name, n_args):
        '''
        Writes a VM call command.
        Arguments:
            - name (string)
            - n_args (int)
        '''
        self.vmfile.write(f'call {name} {n_args}' + '\n')


    def write_function(self, name, n_locals):
        '''
        Writes a VM function command.
        Arguments:
            - name (string)
            - n_locals (int)
        '''
        self.vmfile.write(f'function {name} {n_locals}' +'\n')


    def write_return(self, subroutine_type):
        ''' Writes a VM return command '''
        if 'void' in subroutine_type:
            self.vmfile.write('push constant 0' + '\n')
        self.vmfile.write('return' +'\n')


    def close(self):
        ''' Closes the output file '''
        self.vmfile.close()
