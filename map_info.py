class MapInfo:
    # Map symbol with integers
    mmap = {
        # Symbols
        'number': 1, 'ident': 2, 'if': 3, 'elif': 4, 'else': 5,
        'do': 6, 'while': 7, 'for': 8, 'read': 9, 'write': 10,
        'until': 11, 'func': 12, 'repeat': 13, 'return': 14,
        # Operators
        'becomes': 15, 'ifEqual': 16, 'unEqual': 17, 'lgEqual': 18, 'slEqual': 19,
        'larger': 20, 'smaller': 21, 'comma': 22, 'semicol': 23, 'lParent': 24,
        'rParent': 25, 'oprPlus': 26, 'oprMin': 27, 'oprMult': 28, 'oprDevd': 29,
        'lBrace': 30, 'rBrace': 31,
        # Expanded operators
        'resRedu': 32, 'XOR': 33, 'ODD': 34, 'selfPls': 35, 'selfMin': 36,
        # Objects
        'const': 37, 'int': 38, 'void': 39,
        # VM code
        'lit': 40, 'sto': 41, 'lod': 42, 'cal': 43,
        'opr': 44, 'ini': 45, 'jmp': 46, 'jpc': 47,
        # Unknown symbols
        'unknown':48,
        # EOF
        None: -1
    }

    # Map on single symbol
    ssym = {
        '+': 'oprPlus', '-': 'oprMin', '*': 'oprMult', '/': 'oprDevd',
        '<': 'smaller', '>': 'larger', '(': 'lParent', ')': 'rParent',
        '%': 'resRedu', ';': 'semicol', '=': 'becomes', ',': 'comma',
        '{': 'lBrace', '}': 'rBrace'
    }

    # Comparision operator and ODD, which would return a boolean value after operation
    # Opr number: 3~9
    coopr = [
        '>', '<', '>=', '<=', '==', '!=', 'ODD'
    ]

    # Add or minus operator
    # Opr number: 1~2
    amopr = [
        '-', '+'
    ]

    # Self add or self minus
    selfopr = [
        '++', '--'
    ]

    # Multiply divide, '%' and 'XOR'
    # Opr number: 10~13
    mulopr = [
        '*', '/', '%', 'XOR'
    ]
