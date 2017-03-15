"""
Syntax analysis module.
"""
from map_info import MapInfo
from symbol_table import SymbolTable
from lexical_analysis import LexicalAnalyst
from instruction_table import InstructionTable


class SyntaxAnalyst:
    def __init__(self, input_file_name):
        self._seq_layer = -1
        self.la = LexicalAnalyst(input_file_name)
        self.it = InstructionTable()
        self.st = SymbolTable(self.it)
        self.has_return = False
        self._return_void = False
        self._main_ins = None

    # Main loop
    def execute(self):
        self.la.getsym()

        while self.la.sym_type == MapInfo.mmap['const']:
            self.la.getsym()
            self._const_asm()
            if self.la.sym_type != MapInfo.mmap[MapInfo.ssym[';']]:
                raise Exception('Semicolon missing. ')
            self.la.getsym()
        while self.la.sym_type == MapInfo.mmap['ident']:
            self._var_asm()
            if self.la.sym_type != MapInfo.mmap[MapInfo.ssym[';']]:
                raise Exception('Semicolon missing. ')
            self.la.getsym()
        self._main_ins = self.it.gen('cal', None, self.it.next_line_num + 1)
        end_ins = self.it.gen('jmp', 0, None)
        while self.la.sym_type == MapInfo.mmap['void'] or self.la.sym_type == MapInfo.mmap['int']:
            self._return_void = self.la.sym_type == MapInfo.mmap['void']
            self.la.getsym()
            self._func()
        if self.la.sym_type != MapInfo.mmap[None]:
            raise Exception('Fatal error in main analysis loop. ')
        if self._main_ins[1] is None:
            raise Exception('Function \'main\' missing.')
        self.st.clear()
        end_ins[2] = self.it.next_line_num

        self.la.close_input()
        self.it.print_ins_table(input('Print instruction table to screen?(Y / N):\n') == 'Y')
        print()
        self.it.execute()

    # Functions handler.
    def _func(self):
        """
        Function definition should be something  with return type, argument list, statement sequence or
        single line of statement and return statement(must return something if it's of 'int' type) as below samples:

        void foo([arg_a, arg_b])
            # Something to do

        or

        int bar([arg_a]) {
            '''
            Something to do
            '''
            return something
        }
        """
        # Format error. Should be a identifier
        if self.la.sym_type != MapInfo.mmap['ident']:
            raise Exception('Format error.')
        param = []
        name = self.la.cur_sym
        self.has_return = False
        self.la.getsym()
        # Format error. Should be a '('
        if self.la.sym_type != MapInfo.mmap[MapInfo.ssym['(']]:
            raise Exception('Format error.')
        self.la.getsym()

        # For none empty list.
        if self.la.sym_type != MapInfo.mmap[MapInfo.ssym[')']]:
            while True:
                # Format error. Should be a identifier
                if self.la.sym_type != MapInfo.mmap['ident']:
                    raise Exception('Format error.')
                param.append(self.la.cur_sym)
                self.la.getsym()
                if self.la.sym_type != MapInfo.mmap[MapInfo.ssym[',']]:
                    break
                self.la.getsym()

        # Format error. Should be a ')'
        if self.la.sym_type != MapInfo.mmap[MapInfo.ssym[')']]:
            raise Exception('Format error.')
        self.la.getsym()
        self.st.add_func(name, param, self._return_void)
        self.st.new_layer(param[::-1])
        if name == 'main':
            self._main_ins[1] = self.it.next_line_num
            if not self._return_void:
                raise Exception('Main function should not return anything.')
        self._stat_seq()
        if not self._return_void and not self.has_return:
            raise Exception('Return value is required in function \'' + name + '\'')
        # Error if no return

    # Statement sequences handler.
    def _stat_seq(self):
        """
        Statement sequence:
        ...
        {
            var_a = func foo(var_b)[;
            var_c = var_b;
            ...
            last_statement = 0
            ]
        }

        For statement sequences, a ';' must appear after every statement except for the last one.
        No ';' for the last statement of sequence.
        """
        # It may contains a statement sequence.
        if self.la.sym_type == MapInfo.mmap[MapInfo.ssym['{']]:
            self._seq_layer += 1
            if self._seq_layer:
                self.st.new_layer()
            self.la.getsym()
            while True:
                self._statement()
                # ';' Semicolon checking
                if self.la.sym_type != MapInfo.mmap[MapInfo.ssym[';']]:
                    break
                self.la.getsym()
            # Format error. Should be a '}'
            if self.la.sym_type != MapInfo.mmap[MapInfo.ssym['}']]:
                raise Exception('Format error.')
            self.st.pop()
            if not self._seq_layer:
                self.it.gen('opr', 0, 0)
            self._seq_layer -= 1

        # Format error. Should be a '{'
        else:
            raise Exception('Format error.')
        self.la.getsym()

    # Statement handler
    def _statement(self):
        """
        To recognize multiple kinds of statements.

        Constant definition:
        const A = 1[, B = 2, C = 3...]

        Variable definition:
        Edwin = 1[, name = Edwin...]

        Read statement:
        read name[, number, bla_bla_bla...]

        Write statement:
        write A[, B, C...]

        If statement:
        if expression1
            # Statement sequence 1
        [elif expression2
            # Statement sequence 2
        ...]
        [else
            # Statement sequence 3
        ]

        'For' loop statement:
        for ([ini_statement]; [end_condition]; [step_simple_exp])
            # Statement sequence

        While loop statement:
        while(continue_condition)
            # Statement sequence

        Do while loop statement:
        do {
            # Statement sequence
        } while(continue_condition)

        Return statement:
        return expression
        """
        # Const assignment.
        if self.la.sym_type == MapInfo.mmap['const']:
            self.la.getsym()
            self._const_asm()

        # Variable assignment or value giving.
        elif self.la.sym_type == MapInfo.mmap['ident']:
            var_idx = self.st.variable_idx(self.la.cur_sym, self._seq_layer)
            # new variable assignment
            if var_idx == -1:
                self._var_asm()
            # value giving
            else:
                self.la.getsym()
                # Format error. Should be a '='
                if self.la.sym_type != MapInfo.mmap[MapInfo.ssym['=']]:
                    raise Exception('Format error.')
                self.la.getsym()
                self._exp()
                self.it.gen('str', var_idx, 0)

        # Read statement.
        elif self.la.sym_type == MapInfo.mmap['read']:
            self.la.getsym()
            while True:
                # Format error. Should be a identifier
                if self.la.sym_type != MapInfo.mmap['ident']:
                    raise Exception('Format error.')
                name = self.la.cur_sym
                is_variable = self.st.variable_idx(name, self._seq_layer)
                is_constant = self.st.const_idx(name, self._seq_layer)
                if is_constant != -1:
                    raise Exception('Constant can\'t be reassigned.')
                if is_variable == -1:
                    raise Exception('Can\'t be used before defined.')
                self.it.gen('opr', 14, is_variable)
                self.la.getsym()
                # Read statement over.
                if self.la.sym_type != MapInfo.mmap[MapInfo.ssym[',']]:
                    break
                self.la.getsym()

        # Write statement.
        elif self.la.sym_type == MapInfo.mmap['write']:
            self.la.getsym()
            while True:
                self._exp()
                self.it.gen('opr', 15, 0)
                # Write statement over.
                if self.la.sym_type != MapInfo.mmap[MapInfo.ssym[',']]:
                    break
                self.la.getsym()

        # If statement.
        elif self.la.sym_type == MapInfo.mmap['if']:
            end_ins = []
            while True:
                self.la.getsym()
                self._exp()
                jmp_ins = self.it.gen('jpc', 0, None)
                self._stat_seq()
                end_ins.append(self.it.gen('jmp', 0, None))
                jmp_ins[2] = self.it.next_line_num
                if self.la.sym_type != MapInfo.mmap['elif']:
                    break

            if self.la.sym_type == MapInfo.mmap['else']:
                self.la.getsym()
                self._stat_seq()
            for i in range(len(end_ins)):
                end_ins[i][2] = self.it.next_line_num

        # While statement
        elif self.la.sym_type == MapInfo.mmap['while']:
            self.la.getsym()
            # Format error. Should be a '('
            if self.la.sym_type != MapInfo.mmap[MapInfo.ssym['(']]:
                raise Exception('Format error.')
            self.la.getsym()
            jmp_back_idx = self.it.next_line_num
            self._exp()
            jmp_out_ins = self.it.gen('jpc', 0, None)
            # Format error. Should be a ')'
            if self.la.sym_type != MapInfo.mmap[MapInfo.ssym[')']]:
                raise Exception('Format error.')
            self.la.getsym()
            self._stat_seq()
            self.it.gen('jmp', 0, jmp_back_idx)
            jmp_out_ins[2] = self.it.next_line_num

        # Repeat until statement
        elif self.la.sym_type == MapInfo.mmap['repeat']:
            self.la.getsym()
            jmp_back_idx = self.it.next_line_num
            self._stat_seq()
            # Format error. Should be a 'while'
            if self.la.sym_type != MapInfo.mmap['until']:
                raise Exception('Format error.')
            self.la.getsym()
            # Format error. Should be a '('
            if self.la.sym_type != MapInfo.mmap[MapInfo.ssym['(']]:
                raise Exception('Format error.')
            self.la.getsym()
            self._exp()
            # Format error. Should be a ')'
            if self.la.sym_type != MapInfo.mmap[MapInfo.ssym[')']]:
                raise Exception('Format error.')
            jmp_out_ins = self.it.gen('jpc', 1, None)
            self.it.gen('jmp', 0, jmp_back_idx)
            jmp_out_ins[2] = self.it.next_line_num
            self.la.getsym()

        # Do while statement
        elif self.la.sym_type == MapInfo.mmap['do']:
            self.la.getsym()
            jmp_back_idx = self.it.next_line_num
            self._stat_seq()
            # Format error. Should be a 'while'
            if self.la.sym_type != MapInfo.mmap['while']:
                raise Exception('Format error.')
            self.la.getsym()
            # Format error. Should be a '('
            if self.la.sym_type != MapInfo.mmap[MapInfo.ssym['(']]:
                raise Exception('Format error.')
            self.la.getsym()
            self._exp()
            # Format error. Should be a ')'
            if self.la.sym_type != MapInfo.mmap[MapInfo.ssym[')']]:
                raise Exception('Format error.')
            jmp_out_ins = self.it.gen('jpc', 0, None)
            self.it.gen('jmp', 0, jmp_back_idx)
            jmp_out_ins[2] = self.it.next_line_num
            self.la.getsym()

        # For statement
        elif self.la.sym_type == MapInfo.mmap['for']:
            self.la.getsym()
            # Format error. Should be a '('
            if self.la.sym_type != MapInfo.mmap[MapInfo.ssym['(']]:
                raise Exception('Format error.')
            self.la.getsym()
            self._statement()
            # Format error. Should be a ';'
            if self.la.sym_type != MapInfo.mmap[MapInfo.ssym[';']]:
                raise Exception('Format error.')
            self.la.getsym()
            back_to_judge = self.it.next_line_num
            self._exp()
            jmp_out_ins = self.it.gen('jpc', 0, None)
            jmp_to_loop = self.it.gen('jmp', 0, None)
            # Format error. Should be a ';'
            if self.la.sym_type != MapInfo.mmap[MapInfo.ssym[';']]:
                raise Exception('Format error.')
            self.la.getsym()
            step_stat = self.it.next_line_num
            self._statement()
            self.it.gen('jmp', 0, back_to_judge)
            # Format error. Should be a ')'
            if self.la.sym_type != MapInfo.mmap[MapInfo.ssym[')']]:
                raise Exception('Format error.')
            self.la.getsym()
            jmp_to_loop[2] = self.it.next_line_num
            self._stat_seq()
            self.it.gen('jmp', 0, step_stat)
            jmp_out_ins[2] = self.it.next_line_num

        # Return statement
        elif self.la.sym_type == MapInfo.mmap['return']:
            self.has_return = True
            self.la.getsym()
            if not self._return_void:
                self._sp_exp()
            self.st.ret(self._seq_layer + 1)
            if self.la.sym_type != MapInfo.mmap[MapInfo.ssym['}']]:
                raise Exception('Sequence should end after return.')

        # Function calling
        elif self.la.sym_type == MapInfo.mmap['func']:
            self._function_call_handler(True)

        # Empty statement
        elif self.la.sym_type == MapInfo.mmap[MapInfo.ssym['}']] or \
                self.la.sym_type == MapInfo.mmap[MapInfo.ssym[';']]:
                return

        # Format error. Should be a start of any kind of statement.
        else:
            raise Exception('Format error.')

        # # print symbol table. used in debugging.
        # print(self.st)

    # Expression
    def _exp(self):
        """
        Be consist of a simple expression or one single comparision operator between two simple expressions.
        Comparison operator: >|<|>=|<=|==|!=|ODD

        Examples:
        apple > boy; 1 + 1 >= 2; 2 ODD...
        """
        self._sp_exp()
        # Not just an identifier or a number
        if self.la.cur_sym in MapInfo.coopr:
            opr_num = 3
            for i in range(len(MapInfo.coopr)):
                if self.la.cur_sym == MapInfo.coopr[i]:
                    opr_num += i
                    break
            # 'ODD' operation
            if opr_num == 9:
                self.it.gen('opr', opr_num, 0)
                self.la.getsym()
                return
            self.la.getsym()
            self._sp_exp()
            self.it.gen('opr', opr_num, 0)

    # Simple expression
    def _sp_exp(self):
        """
        Be consist of a term expression or one single add or minus operator between two term expressions.
        Add operator: +|-

        Examples:
        1 + 1; 3 - 4...
        """
        self._term()
        # Not just an identifier or a number
        while self.la.cur_sym in MapInfo.amopr:
            opr_num = 1
            if self.la.cur_sym == '+':
                opr_num = 2
            self.la.getsym()
            self._term()
            self.it.gen('opr', opr_num, 0)

    # Term expression
    def _term(self):
        """
        Be consist of a factor or one single multiple-operation operator between two factors.
        Multiple-operation operator: *|/|%|XOR

        Examples:
        2 * 2; 3 XOR 1...
        """
        self._factor()
        # Not just an identifier or a number
        while self.la.cur_sym in MapInfo.mulopr:
            opr_num = 10
            for i in range(len(MapInfo.mulopr)):
                if self.la.cur_sym == MapInfo.mulopr[i]:
                    opr_num += i
                    break
            self.la.getsym()
            self._factor()
            self.it.gen('opr', opr_num, 0)

    # Factor expression
    def _factor(self):
        """
        Be consist of a number or a identifier,
        or a self-operator with one identifier,
        or a return value from a function,
        or a simple expression being bracketed.
        Self-operator: ++ | --

        Examples:
        a; ++b; c++; func foo(1[, 2, 3]); (2 * 5)
        """
        # (simple-exp)
        if self.la.sym_type == MapInfo.mmap[MapInfo.ssym['(']]:
            self.la.getsym()
            self._sp_exp()
            # Format error. Should be a ')'
            if self.la.sym_type != MapInfo.mmap[MapInfo.ssym[')']]:
                raise Exception('Format error.')
            self.la.getsym()

        # Function
        elif self.la.sym_type == MapInfo.mmap['func']:
            self._function_call_handler(False)

        # ident++ or ident-- or just an identifier
        elif self.la.sym_type == MapInfo.mmap['ident']:
            name = self.la.cur_sym
            is_constant = self.st.const_idx(name, self._seq_layer)
            is_variable = self.st.variable_idx(name, self._seq_layer)
            if is_variable != -1:
                self.it.gen('lod', is_variable, 0)
            elif is_constant != -1:
                self.it.gen('lit', 0, self.st.get_const_val(name))
            else:
                raise Exception('Identifier not defined.')
            self.la.getsym()
            if self.la.cur_sym in MapInfo.selfopr:
                if is_constant != -1:
                    raise Exception('Self-operator can\'t be used on constants.')
                self.it.gen('lod', is_variable, 0)
                if self.la.cur_sym == '++':
                    self.it.gen('lit', 0, 1)
                else:
                    self.it.gen('lit', 0, -1)
                self.it.gen('opr', 2, 0)
                self.it.gen('str', is_variable, 0)
                self.la.getsym()

        # number
        elif self.la.sym_type == MapInfo.mmap['number']:
            self.it.gen('lit', 0, self.la.cur_num)
            self.la.getsym()

        # -ident or +ident
        elif self.la.cur_sym in MapInfo.amopr:
            self_minus = self.la.cur_sym == '-'
            self.la.getsym()
            if self.la.sym_type not in [MapInfo.mmap['ident'], MapInfo.mmap['number'], MapInfo.mmap['func']]:
                raise Exception('Syntax Error.')
            self._factor()
            if self_minus:
                self.it.gen('lit', 0, -1)
                self.it.gen('opr', 4, 0)

        # ++ident or --ident
        elif self.la.cur_sym in MapInfo.selfopr:
            if self.la.cur_sym == '++':
                self_opr = True
            else:
                self_opr = False
            self.la.getsym()
            # Format error. Should be a identifier
            if self.la.sym_type != MapInfo.mmap['ident']:
                raise Exception('Format error.')
            name = self.la.cur_sym
            is_constant = self.st.const_idx(name, self._seq_layer)
            is_variable = self.st.variable_idx(name, self._seq_layer)
            if is_constant != -1 or is_variable == -1:
                raise Exception('Self-operator can only be used on variables.')
            self.it.gen('lod', is_variable, 0)
            if self_opr is not None:
                if self_opr:
                    self.it.gen('lit', 0, 1)
                else:
                    self.it.gen('lit', 0, -1)
                self.it.gen('opr', 2, 0)
                self.it.gen('str', is_variable, 0)
                self.it.gen('lod', is_variable, 0)
            self.la.getsym()

        else:
            raise Exception('Format error.')

    # Function call handler
    def _function_call_handler(self, return_void):
        self.la.getsym()
        # Format error. Should be a identifier
        if self.la.sym_type != MapInfo.mmap['ident']:
            raise Exception('Format error.')
        param_len = 0
        name = self.la.cur_sym
        if not self.st.has_func(name):
            raise Exception('Function not defined.')
        func_info = self.st.func_info(name)
        if func_info[1] != return_void:
            raise Exception('Function return type error.')
        self.la.getsym()
        # Format error. Should be a '('
        if self.la.sym_type != MapInfo.mmap[MapInfo.ssym['(']]:
            raise Exception('Format error.')
        self.la.getsym()
        # For none empty list.
        if self.la.sym_type != MapInfo.mmap[MapInfo.ssym[')']]:
            while True:
                self._sp_exp()
                param_len += 1
                if self.la.sym_type != MapInfo.mmap[MapInfo.ssym[',']]:
                    break
                self.la.getsym()
        if param_len != len(func_info[0]):
            raise Exception('Parameter number is not correct, ' + str(len(func_info[0]))
                            + 'needed, ' + str(param_len) + ' given.')
        # Format error. Should be a ')'
        if self.la.sym_type != MapInfo.mmap[MapInfo.ssym[')']]:
            raise Exception('Format error.')
        self.it.gen('cal', func_info[2], self.it.next_line_num + 1)
        self.la.getsym()

    # Variable assignment function
    def _var_asm(self):
        while True:
            # Format error. Should be a identifier
            if self.la.sym_type != MapInfo.mmap['ident']:
                raise Exception('Format error.')
            name = self.la.cur_sym
            self.la.getsym()

            # Initialize the variable
            if self.la.sym_type == MapInfo.mmap[MapInfo.ssym['=']]:
                self.la.getsym()
                self._sp_exp()
            elif self.la.sym_type == MapInfo.mmap[MapInfo.ssym[',']]\
                    or self.la.sym_type == MapInfo.mmap[MapInfo.ssym[';']]:
                # If the value is not given, make it 0.
                self.it.gen('lit', 0, 0)

            self.st.add_var(name, max(0, self._seq_layer))
            if self.la.sym_type != MapInfo.mmap[MapInfo.ssym[',']]:
                return
            self.la.getsym()

    # Constant assignment function
    def _const_asm(self):
        while True:
            # Format error. Should be a identifier
            if self.la.sym_type != MapInfo.mmap['ident']:
                raise Exception('Format error.')
            name = self.la.cur_sym
            self.la.getsym()
            # Format error. Should be a '='
            if self.la.sym_type != MapInfo.mmap[MapInfo.ssym['=']]:
                raise Exception('Format error.')
            self.la.getsym()
            # self.sp_exp()
            if self.la.sym_type != MapInfo.mmap['number']:
                raise Exception('Constants should be instant numbers.')
            self.st.add_const(name, self.la.cur_num, max(0, self._seq_layer))
            self.la.getsym()
            # Const assignment over.
            if self.la.sym_type != MapInfo.mmap[MapInfo.ssym[',']]:
                return
            self.la.getsym()
