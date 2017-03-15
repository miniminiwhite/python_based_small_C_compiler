class Executor:
    def __init__(self, instruction_table):
        self._instructionTable = instruction_table
        self._dataStack = []
        self._variableStack = []
        self._funcCallStack = []

    def execute(self):
        """
        Instruction code:
        0: lit, put an instant number to the top of the data stack
        1: lod, load a number from a specific position to stack top
        2: str, store the number of stack-top to a specific position
        3: cal, call a function
        4: jmp, jump to and execute a specific instruction without any condition
        5: jpc, jump to and execute a specific instruction if condition is satisfied
        6: opr, operation
        """
        cur_ins_num = 0
        len_it = len(self._instructionTable)
        while cur_ins_num != len_it:
            ins = self._instructionTable[cur_ins_num]
            ins_code = ins[0]
            arg1 = ins[1]
            arg2 = ins[2]
            # print(ins)
            if ins_code == 0:
                # usage: lit 0 value
                self._dataStack.append(arg2)
                cur_ins_num += 1
            elif ins_code == 1:
                # usage: lod distance_from_top 0
                if arg1 >= 0:
                    offset = len(self._variableStack) - 1 - arg1
                else:
                    # global variables
                    offset = arg1 * -1 - 2
                self._dataStack.append(self._variableStack[offset])
                cur_ins_num += 1
            elif ins_code == 2:
                # usage: str distance_from_top 0
                offset = len(self._variableStack) - 1 - arg1
                if arg1 == -1:
                    self._variableStack.append(0)
                elif arg1 < 0:
                    offset = arg1 * -1 - 2
                self._variableStack[offset] = self._dataStack.pop()
                cur_ins_num += 1
            elif ins_code == 3:
                # usage: cal function_start_instruction_index return_instruction_index
                self._funcCallStack.append(arg2)
                cur_ins_num = arg1
            elif ins_code == 4:
                # usage: jmp 0 destination_instruction_index
                cur_ins_num = arg2
            elif ins_code == 5:
                # usage: jpc jump_condition destination_instruction_index
                res = self._dataStack.pop()
                if res == arg1:
                    cur_ins_num = arg2
                else:
                    cur_ins_num += 1
            elif ins_code == 6:
                # usage: opr operation_code parameter
                # Operation code:
                # -1: pop values from stack. parameter: time of popping
                #  0: return from a function
                #  1: minus, -
                #  2: add, +
                #  3: bigger than, >
                #  4: smaller than, <
                #  5: bigger equal, >=
                #  6: smaller equal, <=
                #  7: if equal, ==
                #  8: not equal, !=
                #  9: is odd, ODD
                # 10: multiply, *
                # 11: divide, /
                # 12: reduction, %
                # 13: xor, XOR
                # 14: read. parameter: variable distance from the top of the stack.
                # 15: write.
                cur_ins_num += 1
                if arg1 == -1:
                    for i in range(arg2):
                        self._variableStack.pop()
                elif arg1 == 0:
                    cur_ins_num = self._funcCallStack.pop()
                elif arg1 == 1:
                    a = self._dataStack.pop()
                    b = self._dataStack.pop()
                    self._dataStack.append(b - a)
                elif arg1 == 2:
                    a = self._dataStack.pop()
                    b = self._dataStack.pop()
                    self._dataStack.append(b + a)
                elif arg1 == 3:
                    a = self._dataStack.pop()
                    b = self._dataStack.pop()
                    if b > a:
                        self._dataStack.append(1)
                    else:
                        self._dataStack.append(0)
                elif arg1 == 4:
                    a = self._dataStack.pop()
                    b = self._dataStack.pop()
                    if b < a:
                        self._dataStack.append(1)
                    else:
                        self._dataStack.append(0)
                elif arg1 == 5:
                    a = self._dataStack.pop()
                    b = self._dataStack.pop()
                    if b >= a:
                        self._dataStack.append(1)
                    else:
                        self._dataStack.append(0)
                elif arg1 == 6:
                    a = self._dataStack.pop()
                    b = self._dataStack.pop()
                    if b <= a:
                        self._dataStack.append(1)
                    else:
                        self._dataStack.append(0)
                elif arg1 == 7:
                    a = self._dataStack.pop()
                    b = self._dataStack.pop()
                    if b == a:
                        self._dataStack.append(1)
                    else:
                        self._dataStack.append(0)
                elif arg1 == 8:
                    a = self._dataStack.pop()
                    b = self._dataStack.pop()
                    if b != a:
                        self._dataStack.append(1)
                    else:
                        self._dataStack.append(0)
                elif arg1 == 9:
                    a = self._dataStack.pop()
                    self._dataStack.append(a & 1)
                elif arg1 == 10:
                    a = self._dataStack.pop()
                    b = self._dataStack.pop()
                    self._dataStack.append(b * a)
                elif arg1 == 11:
                    a = self._dataStack.pop()
                    b = self._dataStack.pop()
                    self._dataStack.append(b / a)
                elif arg1 == 12:
                    a = self._dataStack.pop()
                    b = self._dataStack.pop()
                    self._dataStack.append(b % a)
                elif arg1 == 13:
                    a = self._dataStack.pop()
                    b = self._dataStack.pop()
                    self._dataStack.append(b ^ a)
                elif arg1 == 14:
                    offset = len(self._variableStack) - 1 - arg2
                    if arg2 < 0:
                        offset = arg2 * -1 - 2
                    self._variableStack[offset] = int(input())
                elif arg1 == 15:
                    print(self._dataStack.pop())
            # print(self._dataStack)
