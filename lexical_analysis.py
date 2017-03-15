"""
Lexical analysis module.
"""
from map_info import MapInfo


class LexicalAnalyst:
    # String of preserved words.
    _preserved = [
        'if', 'elif', 'else', 'XOR', 'ODD', 'until', 'const', 'repeat', 'for',
        'do', 'while', 'read', 'write', 'int', 'void', 'func', 'return'
    ]

    @property
    def cur_num(self):
        return self._cur_num

    @property
    def cur_sym(self):
        return self._cur_sym

    @property
    def sym_type(self):
        return self._sym_type

    @property
    def line_num(self):
        return self._cur_line_num

    # Initialize a new file reader.
    def __init__(self, filename):
        self.src = open(filename)

        # character cache.
        self._cur_line_num = 0
        self.cur_line = []
        self._cur_num = 0
        self.cur_char = ' '
        self._cur_sym = None
        self._sym_type = None
        self.eof = False

    # Read single line of code from source file.
    def _readline(self):
        self._cur_line_num += 1
        return list(self.src.readline())[::-1]

    # Read single char from line.
    # Flush: to skip a line before reading or not.
    def _getch(self, flush=False):
        if self.cur_line == [] or flush:
            self.cur_line = self._readline()
            # EOF.
            if not self.cur_line:
                self.eof = True
                self.cur_char = None
                return

        self.cur_char = self.cur_line.pop()

    # Get a symbol.
    def getsym(self):
        if self.eof:
            self._cur_sym = None
            self._sym_type = MapInfo.mmap[self._cur_sym]
            return

        # Skip over empty symbols. Return if meet end of file.
        while not self.eof and (self.cur_char == ' ' or self.cur_char == '\t' or self.cur_char == '\n'):
            self._getch()

        # Current char is an integer.
        if self.cur_char.isdigit():
            self._sym_type = MapInfo.mmap['number']
            self._cur_num = 0
            while self.cur_char.isdigit():
                self._cur_num = 10 * self._cur_num + int(self.cur_char)
                self._getch()

        # Current char is a letter(Identifier or preserved words).
        elif self.cur_char.isalnum():
            self._cur_sym = ''
            while self.cur_char.isalnum() or self.cur_char == '_':
                self._cur_sym += self.cur_char
                self._getch()
            # Find and judge if _cur_sym is a preserved word.
            if self._cur_sym in self._preserved:
                self._sym_type = MapInfo.mmap[self._cur_sym]
            else:
                self._sym_type = MapInfo.mmap['ident']

        # Current char is a symbol like ';' or '*' and so on.
        else:
            # Comments.
            if self.cur_char == '/':
                self._getch()
                # Jump over single line comment and get symbol again.
                if self.cur_char == '/':
                    self._getch(True)
                    self.getsym()
                # Jump over multiple line comment and get symbol again.
                elif self.cur_char == '*':
                    self._getch()
                    l = self.cur_char
                    while True:
                        f = l
                        self._getch()
                        l = self.cur_char
                        if f == '*' and l == '/':
                            break
                    self._getch()
                    self.getsym()
                # Single symbol '/'
                else:
                    self._cur_sym = '/'
                    self._sym_type = MapInfo.mmap[MapInfo.ssym['/']]

            # Equal or to judge if equal.
            elif self.cur_char == '=':
                self._getch()
                # Next char is '=' so that we get '=='
                if self.cur_char == '=':
                    self._cur_sym = '=='
                    self._sym_type = MapInfo.mmap['ifEqual']
                    self._getch()
                # Single symbol '='
                else:
                    self._cur_sym = '='
                    self._sym_type = MapInfo.mmap[MapInfo.ssym['=']]

            # Unequal
            elif self.cur_char == '!':
                self._getch()
                # Next char is '=' so that we get '!='
                if self.cur_char == '=':
                    self._cur_sym = '!='
                    self._sym_type = MapInfo.mmap['unEqual']
                    self._getch()

            # '>' or '>='
            elif self.cur_char == '>':
                self._getch()
                # Next char is '=' so that we get '>='
                if self.cur_char == '=':
                    self._cur_sym = '>='
                    self._sym_type = MapInfo.mmap['lgEqual']
                    self._getch()
                # Else '>'
                else:
                    self._cur_sym = '>'
                    self._sym_type = MapInfo.mmap[MapInfo.ssym['>']]

            # '<' or '<='
            elif self.cur_char == '<':
                self._getch()
                # Next char is '=' so that we get '<='
                if self.cur_char == '=':
                    self._cur_sym = '<='
                    self._sym_type = MapInfo.mmap['slEqual']
                    self._getch()
                # Else '<'
                else:
                    self._cur_sym = '<'
                    self._sym_type = MapInfo.mmap[MapInfo.ssym['<']]

            # '+' or '++'
            elif self.cur_char == '+':
                self._getch()
                # '++'
                if self.cur_char == '+':
                    self._cur_sym = '++'
                    self._sym_type = MapInfo.mmap['selfPls']
                    self._getch()
                # Single symbol '+'
                else:
                    self._cur_sym = '+'
                    self._sym_type = MapInfo.mmap[MapInfo.ssym['+']]

            # '-' or '--'
            elif self.cur_char == '-':
                self._getch()
                # '--'
                if self.cur_char == '-':
                    self._cur_sym = '--'
                    self._sym_type = MapInfo.mmap['selfMin']
                    self._getch()
                # Single symbol '-'
                else:
                    self._cur_sym = '-'
                    self._sym_type = MapInfo.mmap[MapInfo.ssym['-']]

            # Other single symbol, like ';', ',', '*', '(', ')' and others on map ssym.
            elif self.cur_char in MapInfo.ssym:
                self._cur_sym = self.cur_char
                self._sym_type = MapInfo.mmap[MapInfo.ssym[self.cur_char]]
                self._getch()

            # Other undefined char.
            else:
                self._sym_type = MapInfo.mmap['unknown']
                self._getch()

    # Used when finish reading the file.
    def close_input(self):
        self.src.close()
