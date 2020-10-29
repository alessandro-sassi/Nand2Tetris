import sys
import os
import re

class Tokenizer:
    '''
    Removes all comments and white space from the input
    and breaks it into Jack-language tokens,
    as specified by the Jack grammar
    '''

    keywords = ['class', 'constructor', 'function', 'method', 'field','static',
                   'var', 'int', 'char', 'boolean', 'void', 'true','false',
                   'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']

    symbols = ['{', '}', '(', ')', '[', ']', '.', ',', ';','+',
                  '-', '*', '/', '&', '|', '<', '>', '=', '~']

    types = ['int', 'boolean', 'char']

    def __init__(self, input_file):
        '''
        Constructor: takes the input file as argument,
        opens it and gets ready to tokenize it
        '''
        self.lines = input_file.readlines()
        self.clean_file = ""
        self.current_token = None
        self.next_token = None
        self.line = 0
        self.i = 0
        self.str_list = []
        self.n_str = 0
        
    def remove_comments(self):
        ''' Remove every type of comment from the file '''
        n = 0
        while n < len(self.lines):
            if '//' in self.lines[n]:
                self.clean_file += self.lines[n][:self.lines[n].index('//')]
                n += 1
            elif '/*' in self.lines[n] or '/**' in self.lines[n]:
                while '*/' not in self.lines[n]:
                    n += 1
                n += 1
            else:
                self.clean_file += self.lines[n]
                n += 1
        
    def split_tokens(self):
        ''' Create a list with all the tokens of the input file '''
        self.tokens = re.findall("\w+|[{}()\[\].;\",+\-*/&|<>=~\n]", self.clean_file)
        self.iterator = self.__iter__()

    def create_strconst_list(self):
        ''' Create a list of all the string constants of the input file '''
        s = self.clean_file
        while '"' in s:
            i1 = s.find('"')
            i2 = s.find('"', i1+1)
            text = s[i1:i2+1]
            self.str_list.append(text)
            s = s[i2+1:]

    def __iter__(self):
        '''
        Iterates over tokens and yields them,
        skipping comments and new lines
        '''
        while self.i < len(self.tokens):
            # Skips new lines and updates the current line
            if self.tokens[self.i] == '\n':
                self.line += 1
                self.i += 1
            # Yields a string constant
            elif self.tokens[self.i] == '"':
                token = self.str_list[self.n_str]
                self.n_str += 1
                self.i += 2
                while self.tokens[self.i-1] != '"':
                   self.i += 1
                yield token
            # Yield every other token
            else:
                yield self.tokens[self.i]
                self.i += 1

    def advance(self):
        '''
        Gets the next token from the tokens's iterator
        and makes it the current token
        '''
        self.current_token = self.next_token
        try:
            self.next_token = next(self.iterator)
        except StopIteration:
            pass

    def is_identifier(self, token):
        return token.isidentifier()

    def is_type(self, token):
        ''' Returns true if the token is primitive type or className '''
        return self.is_identifier(token) or token in self.types

    def key_word(self):
        ''' Returns the keyword wich is the current token '''
        return self.current_token

    def symbol(self):
        ''' Returns the symbol wich is the current token '''
        return self.current_token

    def identifier(self):
        ''' Returns the identifier wich is the current token '''
        return self.current_token

    def int_val(self):
        ''' Returns the integer value of the current token '''
        return int(self.current_token)

    def string_val(self):
        ''' Returns the string value of the current token, without the double quotes '''
        return self.current_token.strip('"')



class CompilationEngine(Tokenizer):
    '''
    Gets its input from the Tokenizer and
    emits its parsed structure into an output file/stream
    '''
    subroutine_dec = ['constructor', 'method', 'function']
    class_var_dec = ['field', 'static']
    statements = ['let', 'if', 'while', 'do', 'return']
    op = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
    unary_op = ['-', '~']
    keyword_constant = ['true', 'false', 'null', 'this']

    def __init__(self, input_file, xml_file):
        super().__init__(input_file)
        self.xml_file = xml_file

    def compile_symbol(self):
        self.xml_file.write(f'<symbol> {self.symbol()} </symbol>' + '\n')
        self.advance()

    def compile_keyword(self):
        self.xml_file.write(f'<keyword> {self.key_word()} </keyword>' + '\n')
        self.advance()

    def compile_identifier(self):
        self.xml_file.write(f'<identifier> {self.identifier()} </identifier>' + '\n')
        self.advance()

    def compile_int_const(self):
        self.xml_file.write(f'<integerConstant> {self.current_token} </integerConstant>' + '\n')
        self.advance()

    def compile_string_const(self):
        self.xml_file.write(f'<stringConstant> {self.string_val()} </stringConstant>' + '\n')
        self.advance()

    def compile_type(self):
        if self.current_token in self.types:
            self.compile_keyword()
        elif self.is_identifier(self.current_token):
            self.compile_identifier()
        else:
            raise SyntaxError(f"At line {self.line} expected primitive type or className")

    def compile_var_name(self):
        if self.is_identifier(self.current_token):
            self.compile_identifier()
        else:
            raise SyntaxError(f"At line {self.line} expected varName")

    def compile_semicolon(self):
        if self.current_token == ';':
            self.compile_symbol()
        else:
            raise SyntaxError(f"At line {self.line} expected ';'")

    def compile_open_round_par(self):
        if self.current_token == '(':
            self.compile_symbol()
        else:
            raise SyntaxError(f"At line {self.line} expected '('")

    def compile_closed_round_par(self):
        if self.current_token == ')':
            self.compile_symbol()
        else:
            raise SyntaxError(f"At line {self.line} expected ')'")

    def compile_open_curly_bracket(self):
        if self.current_token == '{':
            self.compile_symbol()
        else:
            raise SyntaxError(f"At line {self.line} expected open curly bracket")

    def compile_closed_curly_bracket(self):
        if self.current_token == '}':
            self.compile_symbol()
        else:
            raise SyntaxError(f"At line {self.line} expected closed curly bracket")

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
            raise SyntaxError(f"At line {self.line} expected 'class'")

        # Compiles className
        if self.is_identifier(self.current_token):
            self.compile_identifier()
        else:
            raise SyntaxError(f"At line {self.line} expected className")

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
            raise SyntaxError(f"At line {self.line} expected classVarDec")

        # Compiles type
        self.compile_type()

        # Compiles varName (',' varName)*
        while self.current_token != ';':
            self.compile_var_name()
            if self.current_token == ',' and self.is_identifier(self.next_token):
                 self.compile_symbol()
            elif self.current_token == ',' and not self.is_type(self.next_token):
                raise SyntaxError(f"At line {self.line} expected varName")

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
            self.compile_keyword()
        else:
            raise SyntaxError(f"At line {self.line} expected 'constructor', 'method' or 'function'")

        # Compiles ('void' | type)
        if self.current_token == 'void':
            self.compile_keyword()
        elif self.current_token in self.types:
            self.compile_keyword()
        elif self.is_identifier(self.current_token):
            self.compile_identifier()
        else:
            raise SyntaxError(f"At line {self.line} expected 'void', primitive type or className")

        # Compiles subroutineName
        if self.is_identifier(self.current_token):
            self.compile_identifier()
        else:
            raise SyntaxError(f"At line {self.line} expected subroutineName")

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
                raise SyntaxError(f"At line {self.line} expected primitive type or className")
            elif self.current_token != ')':
                raise SyntaxError(f"At line {self.line} expected ','")
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
            raise SyntaxError(f"At line {self.line} expected 'var'")

        # Compiles type
        self.compile_type()

        # Compiles varName (',' varName)*
        while self.current_token != ';':
            self.compile_var_name()
            if self.current_token == ',' and self.is_identifier(self.next_token):
                 self.compile_symbol()
            elif self.current_token == ',' and not self.is_type(self.next_token):
                raise SyntaxError(f"At line {self.line} expected varName")

        # Compiles semicolon
        self.compile_semicolon()

        # Compiles end of varDec
        self.xml_file.write('</varDec>' + '\n')


    def compile_statements(self):
        '''  Compiles a sequence of statements, not including the enclosing "{}" '''
        # Compiles start of statements
        self.xml_file.write('<statements>' + '\n')

        if self.current_token not in self.statements:
            raise SyntaxError(f"At line {self.line} expected statement's declaration")

        # Calls the appropriate compile's statement method
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
        self.compile_var_name()

        # Compiles ('[' expression ']')?
        if self.current_token == '[':
            self.compile_symbol()
            self.compile_expression()
            if self.current_token == ']':
                self.compile_symbol()
            else:
                raise SyntaxError(f"At line {self.line} expected ']'")

        # Compiles '='
        if self.current_token == '=':
            self.compile_symbol()
        else:
            raise SyntaxError(f"At line {self.line} expected '='")

        # Compiles expression
        self.compile_expression()

        # Compiles semicolon
        self.compile_semicolon()

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

        # Compiles open curly bracket
        self.compile_open_curly_bracket()

        # Compiles statements
        self.compile_statements()

        # Compiles closed curly bracket
        self.compile_closed_curly_bracket()

        # Compiles ('else' '{' statements '}')?
        if self.current_token == 'else':
            self.compile_keyword()
            # Compiles open curly bracket
            self.compile_open_curly_bracket()
            # Compiles statements
            self.compile_statements()
            # Compiles closed curly bracket
            self.compile_closed_curly_bracket()

        # Compiles end of if statement
        self.xml_file.write('</ifStatement>' + '\n')


    def compile_while(self):
        ''' Compiles a while statement.
        whileStatement structure:
            'while' '(' expression ')' '{' statements '}'
        '''
        # Compiles start of while statement
        self.xml_file.write('<whileStatement>' + '\n')

        # Compiles 'while'
        self.compile_keyword()

        # Compiles open rounded parenthesis
        self.compile_open_round_par()

        # Compiles expression
        self.compile_expression()

        # Compiles closed rounded parenthesis
        self.compile_closed_round_par()

        # Compiles open curly bracket
        self.compile_open_curly_bracket()

        # Compiles statements
        self.compile_statements()

        # Compiles closed curly bracket
        self.compile_closed_curly_bracket()

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
        self.compile_identifier()

        # if subroutineCall structure: is subroutineName '(' expressionList ')'
        if self.current_token == '(':
            self.compile_symbol()
            self.compile_expression_list()
            self.compile_closed_round_par()
        # if subroutineCall structure: (className | varName) '.' subroutineName '(' expressionList ')'
        elif self.current_token == '.':
            self.compile_symbol()
            self.compile_identifier()
            self.compile_open_round_par()
            self.compile_expression_list()
            self.compile_closed_round_par()
        else:
            raise SyntaxError(f"At line {self.line} expected '(' or '.'")


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

        # Compiles term
        self.compile_term()

        # Compiles (op term)*
        while self.current_token in self.op:
            self.compile_symbol()
            self.compile_term()

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
        if self.current_token != ')':
            self.compile_expression()
            while self.current_token == ',':
                self.compile_symbol()
                self.compile_expression()

        # Compiles end of expression list
        self.xml_file.write('</expressionList>' + '\n')


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
            self.compile_keyword()
        # If stringConstant
        elif '"' in self.current_token:
            self.compile_string_const()
        # If varName | varName '[' expression ']' or subroutineCall
        elif self.is_identifier(self.current_token):
            if self.next_token == '[':
                self.compile_identifier()
                self.compile_symbol()
                self.compile_expression()
                self.compile_symbol()
            elif self.next_token in ['(', '.']:
                self.compile_subroutine_call()
            else:
                self.compile_identifier()
        # If '(' expression ')'
        elif self.current_token == '(':
            self.compile_open_round_par()
            self.compile_expression()
            self.compile_closed_round_par()
        # If unaryOp term
        elif self.current_token in self.unary_op:
            self.compile_symbol()
            self.compile_term()

        # Compiles end of term
        self.xml_file.write('</term>' + '\n')


    def run(self):
        ''' Initialize the Jack Analyzer and start running the parsing process '''
        self.remove_comments()
        self.split_tokens()
        self.create_strconst_list()
        for i in range(2):
            self.advance()
        self.compile_class()



def main():
    if len(sys.argv) != 2:
        print("Usage: JackAnalyzer.py fileName.jack/directoryName")
        sys.exit(1)

    in_put = sys.argv[1]

    # Creates a list with all the jack files and
    # saves the path where xml files are going to be created
    if os.path.isfile(in_put):
        jack_files = [in_put]
        in_path = os.path.abspath(in_put)
        in_path = in_path[:in_path.rfind('/')]
    elif os.path.isdir(in_put):
        jack_files = [file for file in os.listdir(in_put) if '.jack' in file]
        in_path = os.path.abspath(in_put)

    # Creates a directory for the xml files
    out_path = os.path.join(in_path, 'xml')
    try:
        os.mkdir(out_path)
    except FileExistsError:
        pass

    # Runs the Jack Analyzer for every jack file, and create each corresponding xml file
    for jack_file in jack_files:
        out_filepath = os.path.join(out_path, jack_file.split('.')[0] + '.xml')
        # Opens each out file and writes xml code in it
        with open(os.path.join(in_path, jack_file), 'r') as in_file:
            out_file = open(out_filepath, 'w')
            CompilationEngine(in_file, out_file).run()
            out_file.close()

main()

