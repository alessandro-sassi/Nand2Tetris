from JackTokenizer import *
from SymbolTable import *
from VMWriter import *


class CompilationEngine(Tokenizer):
    '''
    Gets its input from the Tokenizer and
    emits its parsed structure into an output xml file.
    Call VMWriter to translate to VM code
    '''

    subroutine_dec = ['constructor', 'method', 'function']
    class_var_dec = ['field', 'static']
    statements = ['let', 'if', 'while', 'do', 'return']
    op = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
    unary_op = ['-', '~']
    keyword_constant = ['true', 'false', 'null', 'this']


    def __init__(self, input_file, xml_file, vm_file):
        ''' Initialize the xml file, the symbol table adn the VMwriter '''
        super().__init__(input_file)
        self.xml_file = xml_file
        self.symbol_tab = SymbolTable()
        self.vm_writer = VMWriter(vm_file)
        self.subroutine_type = None
        self.if_label, self.while_label = 0, 0
        self.isarray = None


    def compile_symbol(self):
        ''' Compile a symbol and advance to the next token '''
        self.xml_file.write(f'<symbol> {self.symbol()} </symbol>' + '\n')
        self.advance()


    def compile_keyword(self):
        ''' Compile a keyword and advance to the next token '''
        self.xml_file.write(f'<keyword> {self.key_word()} </keyword>' + '\n')
        self.advance()


    def compile_keyword_const(self):
        ''' Compile a keyword constant '''
        if self.current_token in ['false', 'null']:
            self.vm_writer.write_push('constant', 0)
        elif self.current_token == 'true':
            self.vm_writer.write_push('constant', 0)
            self.vm_writer.write_arithmetic('not')
        elif self.current_token == 'this':
            self.vm_writer.write_push('pointer', 0)


    def compile_identifier(self):
        '''
        Compile an identifier and call SymbolTable class
        to handle variables declarations, expressiones and statements
        '''
        identifier = self.identifier()
        being = self.symbol_tab.handle_variables(self.tokens, self.i - 1)
        category = self.symbol_tab.kind_of(identifier)
        if category == None and (self.next_token == '.' or self.tokens[self.i - 2] == 'class'):
            category = 'class'
        elif category == None:
            category = 'subroutine'

        self.xml_file.write(f'<identifier> {identifier} </identifier>' + '\n' +
                            f'<category> {category} </category>'+ '\n' +
                            f'<being> {being} </being>' + '\n')
        if category not in ['class', 'subroutine']:
            self.xml_file.write(f'<kind> {self.symbol_tab.kind_of(identifier)} </kind>'+ '\n' +
                                f'<index> {self.symbol_tab.index_of(identifier)} </index>' + '\n')

        self.advance()


    def compile_int_const(self):
        ''' Compile and write an integer constant '''
        self.xml_file.write(f'<integerConstant> {self.current_token} </integerConstant>' + '\n')
        self.vm_writer.write_push('constant', self.current_token )
        self.advance()


    def compile_string_const(self):
        ''' Compile and write a string constant '''
        self.xml_file.write(f'<stringConstant> {self.string_val()} </stringConstant>' + '\n')
        self.vm_writer.write_push('constant', len(self.string_val()))
        self.vm_writer.write_call('String.new', 1)
        for char in self.string_val():
            self.vm_writer.write_push('constant', ord(char))
            self.vm_writer.write_call('String.appendChar', 2)
        self.advance()


    def compile_type(self):
        ''' Compile the type of a variable (int, boolean, char)'''
        if self.current_token in self.types:
            self.compile_keyword()
        elif self.is_identifier(self.current_token):
            self.compile_identifier()
        else:
            raise SyntaxError


    def compile_var_name(self):
        ''' Compile a variable name '''
        if self.is_identifier(self.current_token):
            self.compile_identifier()
        else:
            raise SyntaxError


    def compile_semicolon(self):
        ''' Compile a semicolon '''
        if self.current_token == ';':
            self.compile_symbol()
        else:
            raise SyntaxError


    def compile_open_round_par(self):
        ''' Compile an open rounded parenthesis '''
        if self.current_token == '(':
            self.compile_symbol()
        else:
            raise SyntaxError


    def compile_closed_round_par(self):
        ''' Compile a closed rounded parenthesis '''
        if self.current_token == ')':
            self.compile_symbol()
        else:
            raise SyntaxError


    def compile_open_curly_bracket(self):
        ''' Compile an open curly bracket '''
        if self.current_token == '{':
            self.compile_symbol()
        else:
            raise SyntaxError


    def compile_closed_curly_bracket(self):
        ''' Compile a closed curly bracket '''
        if self.current_token == '}':
            self.compile_symbol()
        else:
            raise SyntaxError


    def compile_array(self):
        ''' Write the vm code to handle array manipulation '''
        self.vm_writer.write_pop('temp', 0)
        self.vm_writer.write_pop('pointer', 1)
        self.vm_writer.write_push('temp', 0)
        self.vm_writer.write_pop('that', 0)


    def write_constructor(self):
        '''
        The compiler figures out the size of an object of this
        class (n), and writes code that calls Memory.alloc(n).
        This OS method finds a memory block of the required
        size, and returns its base address.
        '''
        self.vm_writer.write_push('constant', self.symbol_tab.index['field'])
        self.vm_writer.write_call('Memory.alloc', 1)
        self.vm_writer.write_pop('pointer', 0)


    def compile_class(self):
        '''
        Compiles a complete class.
        class structure:
            'class' className '{' classVarDec* subroutineDec* '}'
        '''
        # Compiles class
        self.xml_file.write('<class>' + '\n')
        if self.current_token == 'class':
            self.compile_keyword()
        else:
            raise SyntaxError
        # Compiles className
        if self.is_identifier(self.current_token):
            self.compile_identifier()
        else:
            raise SyntaxError
        # Compiles open curly bracket
        self.compile_open_curly_bracket()
        # Calls compile method for every class variable declaration
        while self.current_token in self.class_var_dec:
            self.compile_class_var_dec()
        # Calls compile method for every subroutine declaration
        while self.current_token in self.subroutine_dec:
            self.compile_subroutine()
        # Compiles closed curly bracket
        self.compile_closed_curly_bracket()
        # Compiles end of class
        self.xml_file.write('</class>')


    def compile_class_var_dec(self):
        '''
        Compiles a static declaration or a field declaration.
        classVarDec structure:
            ('static' | 'field') type varName (',' varName)* ';'
        '''
        # Compiles classVarDec
        self.xml_file.write('<classVarDec>' + '\n')
        if self.current_token in self.class_var_dec:
            self.compile_keyword()
        else:
            raise SyntaxError
        # Compiles type
        self.compile_type()
        # Compiles varName (',' varName)*
        while self.current_token != ';':
            self.compile_var_name()
            if self.current_token == ',' and self.is_identifier(self.next_token):
                 self.compile_symbol()
            elif self.current_token == ',' and not self.is_type(self.next_token):
                raise SyntaxError
        # Compiles semicolon
        self.compile_semicolon()
        # Compiles end of classvarDec
        self.xml_file.write('</classVarDec>' + '\n')


    def compile_subroutine(self):
        '''
        Compiles a complete method, function or constructor.
        subroutineDec structure:
            ('constructor' | 'function' | 'method' |)
            ('void' | type) subroutineName '(' parameterList ')'
        '''
        # Compiles subroutine declaration
        self.xml_file.write('<subroutineDec>' + '\n')
        if self.current_token in self.subroutine_dec:
            # set subroutine type: ex. [method, void]
            self.subroutine_type = [self.current_token, self.next_token]
            self.compile_keyword()
            # reset flow control labels
            self.if_label, self.while_label = 0, 0
        else:
            raise SyntaxError
        # Compiles ('void' | type)
        if self.current_token == 'void':
            self.compile_keyword()
        elif self.current_token in self.types:
            self.compile_keyword()
        elif self.is_identifier(self.current_token):
            self.compile_identifier()
        else:
            raise SyntaxError
        # Compiles subroutineName
        if self.is_identifier(self.current_token):
            f_name = f'{self.tokens[1]}.{self.current_token}'
            self.compile_identifier()
        else:
            raise SyntaxError
        # Compiles open rounded parenthesis
        self.compile_open_round_par()
        # Compiles parameterList
        self.compile_parameter_list()
        # Compiles closed rounded parenthesis
        self.compile_closed_round_par()

        # Compiles subroutineBody: '{' varDec* statements '}'
        self.xml_file.write('<subroutineBody>' + '\n')
        # Compiles open curly bracket
        self.compile_open_curly_bracket()
        # Compiles varDec*
        while self.current_token == 'var':
            self.compile_var_dec()

        # Write subroutine dec in vm file
        self.vm_writer.write_function(f_name, self.symbol_tab.count_locals())
        if 'constructor' in self.subroutine_type:
            self.write_constructor()
        elif 'method' in self.subroutine_type:
            self.vm_writer.write_push('argument', 0)
            self.vm_writer.write_pop('pointer', 0)

        # Compiles statements
        self.compile_statements()
        # Compiles closed curly bracket
        self.compile_closed_curly_bracket()
        # Compiles end of subroutineBody
        self.xml_file.write('</subroutineBody>' + '\n')
        # Compiles end of subroutineDec
        self.xml_file.write('</subroutineDec>' + '\n')


    def compile_parameter_list(self):
        '''
        Compiles a (possibly empty) parameter list, not including the enclosing "()".
        parameterList structure:
            ((type varName) (',' type varName)*)?
        '''
        # Compiles parameterList
        self.xml_file.write('<parameterList>' + '\n')
        # Compiles (type varName) (',' type varName)*
        while self.current_token != ')':
            # Compiles type
            self.compile_type()
            # Compiles varName
            self.compile_var_name()
            # Compiles ',' if existing
            if self.current_token == ',' and self.is_type(self.next_token):
                self.compile_symbol()
            elif self.current_token == ',' and not self.is_type(self.next_token):
                raise SyntaxError
            elif self.current_token != ')':
                raise SyntaxError
            else:
                break
        # Compiles end of parameterList
        self.xml_file.write('</parameterList>' + '\n')


    def compile_var_dec(self):
        '''
        Compiles a var declaration.
        varDec structure:
            'var' type varName (',' varName)* ';'
        '''
        # Compiles start of varDec
        self.xml_file.write('<varDec>' + '\n')
        # Compiles var
        if self.current_token == 'var':
            self.compile_keyword()
        else:
            raise SyntaxError
        # Compiles type
        self.compile_type()
        # Compiles varName (',' varName)*
        while self.current_token != ';':
            self.compile_var_name()
            if self.current_token == ',' and self.is_identifier(self.next_token):
                 self.compile_symbol()
            elif self.current_token == ',' and not self.is_type(self.next_token):
                raise SyntaxError
        # Compiles semicolon
        self.compile_semicolon()
        # Compiles end of varDec
        self.xml_file.write('</varDec>' + '\n')


    def compile_statements(self):
        '''  Compiles a sequence of statements, not including the enclosing "{}" '''
        # Compiles start of statements
        self.xml_file.write('<statements>' + '\n')
        if self.current_token not in self.statements:
            raise SyntaxError
        # Calls the appropriate compile statement method
        while self.current_token in self.statements:
            if self.current_token == 'let':
                self.compile_let()
            elif self.current_token == 'do':
                self.compile_do()
            elif self.current_token == 'while':
                self.compile_while()
            elif self.current_token == 'if':
                self.compile_if()
            else:
                self.compile_return()
        # Compiles end of statements
        self.xml_file.write('</statements>' + '\n')


    def compile_let(self):
        '''
        Compiles a let statement.
        letStatement structure:
            'let' varName ('[' expression ']')? '=' expression ';'
        '''
        # Compiles start of let statement
        self.xml_file.write('<letStatement>' + '\n')
        # Compiles let
        self.compile_keyword()
        # Compiles varName
        varname = self.current_token
        kind = self.symbol_tab.kind_of(varname)
        index = self.symbol_tab.index_of(varname)
        self.compile_var_name()

        self.isarray = (self.current_token == '[') # True if is 'let varname[exp]'
        # Compiles ('[' expression ']')?
        if self.current_token == '[':
            self.compile_symbol()
            self.compile_expression()
            self.vm_writer.write_push(kind, index) # push varname
            self.vm_writer.write_arithmetic('add')
            if self.current_token == ']':
                self.compile_symbol()
            else:
                raise SyntaxError
        # Compiles '='
        if self.current_token == '=':
            self.compile_symbol()
        else:
            raise SyntaxError
        # Compiles expression
        self.compile_expression()
        # Compiles semicolon
        self.compile_semicolon()

        if self.isarray == True:
            self.compile_array()
        # pop result to varname
        else:
            if kind == 'field':
                kind = 'this'
            self.vm_writer.write_pop(kind, index)

        # Compiles end of let statement
        self.xml_file.write('</letStatement>' + '\n')


    def compile_if(self):
        '''
        Compiles an if statement.
        ifStatement structure:
            'if' '(' expression ')' '{' statements '}'
            ('else' '{' statements '}')?
        '''
        # Compiles start of if statement
        self.xml_file.write('<ifStatement>' + '\n')
        # Compiles 'if'
        self.compile_keyword()
        # Compiles open rounded parenthesis
        self.compile_open_round_par()
        # Compiles expression
        self.compile_expression()
        # Compiles closed rounded parenthesis
        self.compile_closed_round_par()

        # Write flow control
        lab = self.if_label
        self.if_label += 1
        self.vm_writer.write_if(f'IF_TRUE{lab}')
        self.vm_writer.write_goto(f'IF_FALSE{lab}')
        self.vm_writer.write_label(f'IF_TRUE{lab}')
        # Compiles open curly bracket
        self.compile_open_curly_bracket()
        # Compiles statements
        self.compile_statements()
        # Compiles closed curly bracket
        self.compile_closed_curly_bracket()
        self.vm_writer.write_goto(f'IF_END{lab}')
        self.vm_writer.write_label(f'IF_FALSE{lab}')

        # Compiles ('else' '{' statements '}')?
        if self.current_token == 'else':
            self.compile_keyword()
            # Compiles open curly bracket
            self.compile_open_curly_bracket()
            # Compiles statements
            self.compile_statements()
            # Compiles closed curly bracket
            self.compile_closed_curly_bracket()
        self.vm_writer.write_label(f'IF_END{lab}')
        # Compiles end of if statement
        self.xml_file.write('</ifStatement>' + '\n')


    def compile_while(self):
        '''
        Compiles a while statement.
        whileStatement structure:
            'while' '(' expression ')' '{' statements '}'
        '''
        # Compiles start of while statement
        self.xml_file.write('<whileStatement>' + '\n')
        # Compiles 'while'
        self.compile_keyword()
        lab = self.while_label
        self.while_label += 1
        self.vm_writer.write_label(f'WHILE_EXP{lab}')
        # Compiles open rounded parenthesis
        self.compile_open_round_par()
        # Compiles expression
        self.compile_expression()
        # Compiles closed rounded parenthesis
        self.compile_closed_round_par()
        self.vm_writer.write_arithmetic('not')
        self.vm_writer.write_if(f'WHILE_END{lab}')
        # Compiles open curly bracket
        self.compile_open_curly_bracket()
        # Compiles statements
        self.compile_statements()
        # Compiles closed curly bracket
        self.compile_closed_curly_bracket()
        self.vm_writer.write_goto(f'WHILE_EXP{lab}')
        self.vm_writer.write_label(f'WHILE_END{lab}')
        # Compiles end of if statement
        self.xml_file.write('</whileStatement>' + '\n')


    def compile_return(self):
        '''
        Compiles a return statement.
        returnStatement structure:
            'return' expression? ';'
        '''
        # Compiles start of return statement
        self.xml_file.write('<returnStatement>' + '\n')
        # Compile return
        self.compile_keyword()
        # Compiles expression?
        if self.current_token != ';':
            self.compile_expression()
        # Compiles semicolon
        self.compile_semicolon()
        #Write return
        self.vm_writer.write_return(self.subroutine_type)
        # Compiles end of return statement
        self.xml_file.write('</returnStatement>' + '\n')


    def compile_subroutine_call(self):
        '''
        Compiles subroutineCall
        subroutineCall structure:
            subroutineName '(' expressionList ')' | (className |
            varName) '.' subroutineName '(' expressionList ')'
        '''
        # Compiles subroutineName | className | varName
        n_args = 0
        name = self.identifier()
        self.compile_identifier()

        # if subroutineCall structure is a method of the current class: subroutineName '(' expressionList ')'
        if self.current_token == '(':
            name = f'{self.tokens[1]}.{name}'
            self.compile_open_round_par()
            self.vm_writer.write_push('pointer', 0)
            n_args = self.compile_expression_list() + 1

        # if subroutineCall structure: (className | varName) '.' subroutineName '(' expressionList ')'
        elif self.current_token == '.':
            self.compile_symbol()
            # if varName is a data type symbol -> it's a method
            if name in self.symbol_tab.sub_symbol_table or name in self.symbol_tab.class_symbol_table:
                self.vm_writer.write_push(self.symbol_tab.kind_of(name), \
                self.symbol_tab.index_of(name))
                name = self.symbol_tab.type_of(name)
                n_args += 1
            name = f'{name}.{self.identifier()}'
            self.compile_identifier()
            self.compile_open_round_par()
            n_args += self.compile_expression_list()

        self.compile_closed_round_par()
        self.vm_writer.write_call(name, n_args)


    def compile_do(self):
        '''
        Compiles a do statement.
        doStatement structure:
            'do' subroutineCall ';'
        '''
        # Compiles start of do statement
        self.xml_file.write('<doStatement>' + '\n')
        # Compiles do
        self.compile_keyword()
        # Compiles subroutineCall
        self.compile_subroutine_call()
        self.vm_writer.write_pop('temp', 0)
        # Compiles semicolon
        self.compile_semicolon()
        # Compiles end of do statement
        self.xml_file.write('</doStatement>' + '\n')


    def compile_expression(self):
        '''
        Compiles an expression.
        expression structure:
            term (op term)*
        '''
        # Compiles start of expression
        self.xml_file.write('<expression>' + '\n')
        # writes term1
        self.compile_term()
        # Compiles (op term)*
        while self.current_token in self.op:
            operator = self.symbol()
            self.compile_symbol()
            self.compile_term()
            self.vm_writer.write_arithmetic(operator)
        # Compiles end of expression
        self.xml_file.write('</expression>' + '\n')


    def compile_expression_list(self):
        '''
        Compiles a (possibily empty) comma-separated list of expressions.
        expressionList structure:
            (expression (',' expression)*)?
        '''
        # Compiles start of expression list
        self.xml_file.write('<expressionList>' + '\n')
        # Compiles (expression (',' expression)*)?
        n_args = 0
        if self.current_token != ')':
            self.compile_expression()
            n_args += 1
            while self.current_token == ',':
                self.compile_symbol()
                self.compile_expression()
                n_args += 1
                # Compiles end of expression list
        self.xml_file.write('</expressionList>' + '\n')
        return n_args


    def compile_term(self):
        '''
        Compiles a term.
        term structure:
            integerCostant | stringCostant | keywordConstant | varName |
            varName '[' expression ']' | subroutineCall | '(' expression ')' |
            unaryOp term
        '''
        # Compiles start of term
        self.xml_file.write('<term>' + '\n')
        # If integerConstant
        if self.current_token.isdigit():
            if self.int_val() in range(0, 32767):
                self.compile_int_const()
            else:
                raise SyntaxError("Int value out of range. ")
        # If keywordConstant
        elif self.current_token in self.keyword_constant:
            self.compile_keyword_const()
            self.compile_symbol()
        # If stringConstant
        elif '"' in self.current_token:
            self.compile_string_const()
        # If varName | varName '[' expression ']' or subroutineCall
        elif self.is_identifier(self.current_token):
            # Compile varName '[' expression ']'
            if self.next_token == '[':
                self.vm_writer.write_push(self.symbol_tab.kind_of(self.identifier()), \
                self.symbol_tab.index_of(self.identifier()))
                self.compile_identifier()
                self.compile_symbol()
                self.compile_expression()
                self.compile_symbol()
                self.vm_writer.write_arithmetic('add')
                self.vm_writer.write_pop('pointer', 1)
                self.vm_writer.write_push('that', 0)
            # Compile subroutineCall
            elif self.next_token in ['(', '.']:
                self.compile_subroutine_call()
            # Compile varname
            else:
                self.vm_writer.write_push(self.symbol_tab.kind_of(self.identifier()), \
                self.symbol_tab.index_of(self.identifier()))
                self.compile_identifier()
        # If '(' expression ')'
        elif self.current_token == '(':
            self.compile_open_round_par()
            self.compile_expression()
            self.compile_closed_round_par()
        # If unaryOp term
        elif self.current_token in self.unary_op:
            unary_op = self.symbol()
            self.compile_symbol()
            self.compile_term()
            self.vm_writer.write_arithmetic(unary_op.replace('-', 'neg'))
        # Compiles end of term
        self.xml_file.write('</term>' + '\n')


    def run(self):
        ''' Initialize the Jack Analyzer and start running the parsing process '''
        self.remove_comments()
        self.split_tokens()
        self.create_strconst_list()
        # set current and next token
        for i in range(2):
            self.advance()
        self.compile_class()
        self.vm_writer.close()
