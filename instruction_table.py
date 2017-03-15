import os
from executor import Executor


class InstructionTable:
    _instruction_code = {
        'lit': 0, 'lod': 1, 'str': 2, 'cal': 3,
        'jmp': 4, 'jpc': 5, 'opr': 6,

        0: 'lit', 1: 'lod', 2: 'str', 3: 'cal',
        4: 'jmp', 5: 'jpc', 6: 'opr'
    }

    @property
    def table(self):
        return self._table

    @property
    def next_line_num(self):
        return self._curLineNum

    def __init__(self):
        self._table = []
        self._curLineNum = 0

    # Set 'ins' as a return value so that missing value in 'ins' can be filled later.
    def gen(self, ic, arg1, arg2):
        if ic not in ['lit', 'lod', 'str', 'cal', 'ini', 'jmp', 'jpc', 'opr']:
            raise Exception('Instruction code error.')
        ins = [self._instruction_code[ic], arg1, arg2]
        self._table.append(ins)
        self._curLineNum += 1
        return ins

    # Used when debugging. Print current instruction table.
    def print_ins_table(self, to_screen=False, file_name='instruction code.txt'):
        line_num = 0
        dir_name = 'instruction table'
        if not os.path.isdir(dir_name):
            os.mkdir(dir_name)
        output_file = open(dir_name + '\\' + file_name, 'w')
        for ins in self._table:
            line = self._instruction_code[ins[0]] + '\t' + str(ins[1]) + '\t' + str(ins[2])
            output_file.write(line + '\n')
            if to_screen:
                print(str(line_num) + '\t' + line)
                line_num += 1
        output_file.close()

    # Execute instructions in the table.
    def execute(self):
        executor = Executor(self._table)
        executor.execute()
