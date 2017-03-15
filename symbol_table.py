class SymbolTable:
    def __init__(self, it):
        self._funcDict = {}
        self._insTable = it
        self._varNum = [0]
        self._varTable = []
        self._consTable = []
        self._funcTable = []
        self._curLayerNum = 0

    def __str__(self):
        res = 'constant table:\n'
        for i in self._consTable:
            res += str(i) + '\n'
        res += '\nvariable table:\n'
        for i in self._varTable:
            res += str(i) + '\n'
        res += '\nfunc table:\n'
        for i in self._funcDict:
            res += i + str(self._funcTable[self._funcDict[i]]) + '\n'
        return res

    def has_func(self, name):
        """ Tell if a function is in function table. """
        return name in self._funcDict

    def func_info(self, name):
        return self._funcTable[self._funcDict[name]]

    def const_idx(self, name, search_range):
        """ Tell if a constant is in constant table within specific range. Return index if true. """
        cnt = 0
        idx = len(self._consTable)
        if idx == 0:
            return -1
        while idx > 0:
            idx -= 1
            if self._consTable[idx][0] == name \
                    and (self._curLayerNum - self._consTable[idx][1] <= search_range or self._consTable[idx][1] == 0):
                return cnt
            cnt += 1
        return -1

    def variable_idx(self, name, search_range):
        """ Tell if a variable is in variable table within specific range. Return index if true."""
        cnt = 0
        idx = len(self._varTable)
        if idx == 0:
            return -1
        while idx > 0:
            idx -= 1
            # if self._varTable[idx][0] == name \
            #         and (self._curLayerNum - self._varTable[idx][1] <= search_range or self._varTable[idx][1] == 0):
            #     return cnt
            if self._varTable[idx][0] == name:
                if self._curLayerNum - self._varTable[idx][1] <= search_range:
                    return cnt
                elif self._varTable[idx][1] == 0:
                    return -1 - self._varTable[idx][2]
            cnt += 1
        return -1

    def get_const_val(self, name):
        """ Get the value of a constant. """
        idx = len(self._consTable)
        while idx > 0:
            idx -= 1
            if self._consTable[idx][0] == name:
                return self._consTable[idx][2]

    def add_func(self, name, param_list=list(), return_void=True):
        """
        Add a function into function table and function dictionary
        Function dictionary:
                Key:    Function name
                Value:  Function number
        Function table(index number is function number):
                parameter list | have return value or not | entrance instruction line number
        """
        # Search all the constants and variable to ensure no identifier shares name with this new function.
        if self.has_func(name) or self.const_idx(name, 10086) != -1 or self.variable_idx(name, 10086) != -1:
            raise Exception("Identifier name already used before.")
        self._funcDict[name] = len(self._funcTable)
        self._funcTable.append([param_list, return_void, self._insTable.next_line_num])

    def add_const(self, name, val, search_range):
        """
        Add a constant into constant table.
        Constant table:
                constant name | defined on which layer | value
        """
        if self.has_func(name) or self.const_idx(name, search_range) != -1 \
                or self.variable_idx(name, search_range) != -1:
            raise Exception("Identifier name already used before.")
        self._consTable.append([name, self._curLayerNum, val])

    def add_var(self, name, search_range):
        """
        Add a variable into variable table.
        Variable table:
                variable name | defined on which layer | variable number
        """
        if self.has_func(name) or self.const_idx(name, search_range) != -1 \
                or self.variable_idx(name, search_range) != -1:
            raise Exception("Identifier name already used before.")
        self._varNum[self._curLayerNum] += 1
        self._varTable.append([name, self._curLayerNum, self._varNum[self._curLayerNum]])
        self._insTable.gen('str', -1, 0)

    def new_layer(self, predefined_var=None):
        """
        Add a new layer
        """
        self._curLayerNum += 1
        self._varNum.append(0)
        if predefined_var is not None:
            for i in predefined_var:
                self.add_var(i, 0)

    def pop(self):
        """
        Pop a layer. Also pop all the constants and variables of that layer.
        """
        len_c = len(self._consTable) - 1
        len_v = len(self._varTable) - 1
        self._insTable.gen('opr', -1, self._varNum[self._curLayerNum])
        while self._consTable and self._consTable[len_c][1] == self._curLayerNum:
            self._consTable.pop()
            len_c -= 1
        while self._varTable and self._varTable[len_v][1] == self._curLayerNum:
            self._varTable.pop()
            len_v -= 1
        self._varNum.pop()
        self._curLayerNum -= 1

    def ret(self, num_layer_being_pop):
        """
        Quit current function and dump all local variable and constants.
        Called when a 'return' is found.
        """
        for i in range(num_layer_being_pop):
            self._insTable.gen('opr', -1, self._varNum[self._curLayerNum - i])
        self._insTable.gen('opr', 0, 0)

    def clear(self):
        """
        Dump all the global variables and constants.
        Called when analysis over.
        """
        if self._curLayerNum:
            raise Exception('Symbol table error. Local variables and constants had not been pop completely.')
        while self._consTable:
            self._consTable.pop()
        while self._varTable:
            self._varTable.pop()
        self._varNum.pop()
