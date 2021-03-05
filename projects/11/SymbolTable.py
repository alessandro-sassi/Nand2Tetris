class SymbolTable:
    '''
    Provides a symbol table abstraction. The symbol table associates the identifier
    names found in the program with identifier properties needed for compilation:
    type, kind, and running index.
    The symbol table for Jack programs has two nested scopes (class/subroutine)
    '''

    def __init__(self):
        '''
        Creates a class scope symbol table and
        a subroutine scope symbol table
        '''
        self.class_symbol_table, self.sub_symbol_table = {}, {}
        self.index = {'var' : 0,
                      'argument' : 0,
                      'static' : 0,
                      'field' : 0}


    def start_subroutine(self):
        '''
        Starts a new subroutine scope
        (i.e., resets the subroutine's symbol table)
        '''
        self.sub_symbol_table = {}
        for kind in ['var', 'argument']:
            self.index[kind] = 0


    def var_count(self, kind):
        '''
        Returns the number of variables (int) of the given KIND
        already defined in the current scope
        Arguments:
            - kind (STATIC, FIELD, ARG, VAR)
        '''
        return self.index[kind]


    def define(self, name, typ, kind):
        '''
        Defines a new identifier of a given NAME, TYPE, and KIND
        and assigns it a running INDEX. STATIC and FIELD indentifiers
        have a class scope, while ARG and VAR identifiers have a subroutine scope
        Arguments:
            - name (string)
            - typ (string)
            - kind (STATIC, FIELD, ARG, VAR)
        '''
        if name in self.class_symbol_table or name in self.sub_symbol_table:
            return
        if kind in ['field', 'static']:
            self.class_symbol_table[name] = [typ, kind, self.var_count(kind)]
        else:
            self.sub_symbol_table[name] = [typ, kind, self.var_count(kind)]
        self.index[kind] += 1


    def kind_of(self, name):
        '''
        Returns the KIND (STATIC, FIELD, ARG, VAR, NONE)
        of the named identifier in the current scope.
        If the identifier is unknown in the current scope, returns NONE
        Arguments:
            - name (string)
        '''
        try:
            return self.sub_symbol_table[name][1]
        except KeyError:
            pass
        try:
            return self.class_symbol_table[name][1]
        except KeyError:
            pass

        return


    def type_of(self, name):
        '''
        Returns the TYPE (string) of the named identifier in the current scope
        Arguments:
            - name (string)
        '''
        try:
            return self.sub_symbol_table[name][0]
        except KeyError:
            return self.class_symbol_table[name][0]


    def index_of(self, name):
        '''
        Returns the INDEX (int) assigned to the named identifier
        Arguments:
            - name (string)
        '''
        try:
            return self.sub_symbol_table[name][2]
        except KeyError:
            return self.class_symbol_table[name][2]


    def count_locals(self):
        ''' return the sum of locals in the subroutine symbols table '''
        n_locals = 0
        for v in self.sub_symbol_table:
            if self.kind_of(v) == 'var':
                n_locals += 1
        return n_locals


    def handle_variables(self, tokens, i):
        '''
        Arguments:
            - list of tokens
            - index of the tokens's list
        Loop over the tokens in thecurrent statement and
        check if it's a variables declaration or
        a variables expression/statement and handles them using other methods
        '''

        self.i = i

        def handle_var_dec():
            '''
            Handles variables declarations and add the variables
            to the symbol table calling the define method
            '''
            name_list = []
            kind = tokens[self.i]
            typ = tokens[self.i+1]
            name_list.append(tokens[self.i+2])
            while tokens[self.i+3] != ';':
                # Add to name_list every var declared in the code's line
                name_list.append(tokens[self.i+4])
                self.i += 2
            # set tokens[i] to ';' to exit the while loop
            self.i += 3
            # Call the define method for every variable name
            for name in range(len(name_list)):
                self.define(name_list[name], typ, kind)

        def handle_sub_args():
            '''
            Handles subroutine's arguments declaration and add the args
            to the symbol table calling the define method.
            Return 'NO ARGS' if the subroutine has no arguments
            '''
             # handle methods's first argument
            if tokens[self.i] == 'method':
                self.define('this', tokens[1], 'argument')
            # break from wile loop if the subroutine has no arguments
            if tokens[self.i+4] == ')':
                return 'NO ARGS'
            else:
                # set tokens[i] to the first argument's name
                self.i += 5
            # loop over every arg of the subroutine and call define for everyone
            while tokens[self.i] != ')':
                self.define(tokens[self.i], tokens[self.i-1], 'argument')
                self.i += 1
                if tokens[self.i] == ',':
                    self.i += 2

        def var_lookup():
            '''
            Looks up in the symbol tables a variable detected
            in some statement or expression. If no symbol is found
            it can be assumed to be either a subroutine name or a class name.
            Return 'used' (string) for later use in the compiler,
            because in this statement the identifier is used and not declared
            '''
            try:
                self.sub_symbol_table[tokens[self.i]]
            except KeyError:
                pass
            try:
                self.class_symbol_table[tokens[self.i]]
            except KeyError:
                pass

            return 'used'

        # loop that prevents handling previous statements
        while tokens[self.i] not in [';', '{', ')', 'class']:
            if tokens[self.i] in ['field', 'static', 'var']:
                handle_var_dec()
                return 'defined'
            elif tokens[self.i] in ['constructor', 'function', 'method']:
                self.start_subroutine()
                if handle_sub_args() == 'NO ARGS':
                    return 'used'
            # go backward in the current statement
            else:
                self.i -= 1
        # lookup the variable in the symbol table, since no
        # var declaration was detected in the statement by the while loop
        return var_lookup()
