import re


class Tokenizer:
    '''
    Removes all comments and white space from the input
    and breaks it into Jack-language tokens,
    as specified by the Jack grammar


    keywords = ['class', 'constructor', 'function', 'method', 'field','static',
                   'var', 'int', 'char', 'boolean', 'void', 'true','false',
                   'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']

    symbols = ['{', '}', '(', ')', '[', ']', '.', ',', ';','+',
                  '-', '*', '/', '&', '|', '<', '>', '=', '~']
    '''

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
        self.i = 0
        self.str_list = []
        self.n_str = 0


    def remove_comments(self):
        '''
        Ignore every type of comment in the file
        and paste the clean code in clean_file
        '''
        n = 0
        while n < len(self.lines):
            # Ignore '//' comments
            if '//' in self.lines[n]:
                self.clean_file += self.lines[n][:self.lines[n].index('//')]
                n += 1
            # Ignore '/*...*/' and '/**...*/' comments
            elif '/*' in self.lines[n] or '/**' in self.lines[n]:
                while '*/' not in self.lines[n]:
                    n += 1
                n += 1
            # Append normal line of code to clean file
            else:
                self.clean_file += self.lines[n]
                n += 1


    def split_tokens(self):
        '''
        Create a list with all the tokens of the input file
        and an iterator for the tokens
        '''
        self.tokens = re.findall("\w+|[{}()\[\].;\",+\-*/&|<>=~]", self.clean_file)
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
        ''' Iterate over tokens and yields them '''
        while self.i < len(self.tokens):
            # Yield a string constant
            if self.tokens[self.i] == '"':
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
        Get the next token from the tokens's iterator
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
        return self.current_token.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


    def identifier(self):
        ''' Returns the identifier wich is the current token '''
        return self.current_token


    def int_val(self):
        ''' Returns the integer value of the current token '''
        return int(self.current_token)


    def string_val(self):
        ''' Returns the string value of the current token, without the double quotes '''
        return self.current_token.strip('"')
