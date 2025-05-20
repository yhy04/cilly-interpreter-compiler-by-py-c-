'''
sql 语法

program : statement* EOF

statement
    : create_table_statement
    | alter_table_statement
    | drop_table_statement
    | insert_into_statement
    | query_statement

    | update_statement
    | delete_statement
    ;

create_table_statement
    : 'create' 'table' ID '('
        column1 data_type constraint
        (','
        column1 data_type constraint
        )*
        ')' ';'
    ;

insert_into_statement
    : 'insert' 'into' ID 'values' (column_list) ';'
    ;

alter_table_statement
    : 'alter' 'table' ID alter_action ';'
        alter_action :
            `'add' 'column' column1 data_type
            `'drop' 'column' column1
    ;

query_statement
    : 'select' select_list | * 'from' table_references
        ('where' cond)?
        ('order' 'by' 'asc'|'desc')? ';'
    ;

update_statement
    : 'update' table_name 'set' column1=v1 (,column_i=v_i)*
        'where' conditions ';'

'''

def error(src, msg):
    raise Exception(f'{src} : {msg}')

def mk_tk(tag, val=None):
    return [tag, val]

def tk_tag(t):
    return t[0]

def tk_val(t):
    return t[1]

def make_str_reader(s, err):
    cur = None
    pos = -1

    def peek(p=0):
        if pos + p >= len(s):
            return 'eof'
        else:
            return s[pos + p]

    def match(c):
        if c != peek():
            err(f'期望{c}, 实际{peek()}')

        return next()

    def next():
        nonlocal pos, cur

        old = cur
        pos = pos + 1
        if pos >= len(s):
            cur = 'eof'
        else:
            cur = s[pos]

        return old

    next()
    return peek, match, next

cilly_op1 = [
    '(', ')', '{', '}', ',', ';','[',']',
    '+', '-', '*', '/', '%', ':','.',
]

cilly_op2 = {
    '>': '>=',
    '<': '<=',
    '=': '==',
    '!': '!=',
    '&': '&&',
    '|': '||',
}

cilly_keywords = [
    'var', 'print', 'if', 'else', 'while', 'break', 'continue', 'return', 'fun',
    'true', 'false', 'null',

    'select','from','where','order','by',
    'distinct','limit','and','or','not','asc','desc','in',
    'create','alter','drop','table','add','column',
    'inner','left','right','full','subquery',
    'insert','into','update','delete','values','set',
    'int','char','null',
    'not',
]

def cilly_lexer(prog):
    def err(msg):
        error('cilly lexer', msg)

    peek, match, next = make_str_reader(prog, err)

    def program():
        r = []
        while True:
            skip_ws()
            if peek() == 'eof':
                break
            r.append(token())
        return r

    def skip_ws():
        while peek() in [' ', '\t', '\r', '\n']:
            next()

    def token():

        c = peek()

        if is_digit(c):
            return num()

        if c == '"':
            return string()
        if c == "'":
            return _string()

        if c == '_' or is_alpha(c):
            return id()

        if c in cilly_op1:
            next()
            return mk_tk(c)

        if c in cilly_op2:
            next()
            if peek() == cilly_op2[c][1]:
                next()
                return mk_tk(cilly_op2[c])
            else:
                return mk_tk(c)

        err(f'非法字符{c}')

    def is_digit(c):
        return c >= '0' and c <= '9'

    def num():
        r = ''
        while is_digit(peek()):
            r = r + next()

        if peek() == '.':
            r = r + next()

            while is_digit(peek()):
                r = r + next()

        return mk_tk('num', float(r) if '.' in r else int(r))

    def string():
        match('"')
        r = ''
        while peek() != '"' and peek() != 'eof':
            r = r + next()
        match('"')
        return mk_tk('str', r)

    def _string():
        match("'")
        r = ''
        while peek() != "'" and peek() != 'eof':
            r = r + next()
        match("'")
        return mk_tk('str', r)

    def is_alpha(c):
        return (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z')

    def is_digit_alpha__(c):
        return c == '_' or is_digit(c) or is_alpha(c)

    def id():
        r = '' + next()

        while is_digit_alpha__(peek()):
            r = r + next()

        if r in cilly_keywords:
            return mk_tk(r)

        return mk_tk('id', r)

    return program()

EOF = mk_tk('eof')

def make_token_reader(ts, err):
    pos = -1
    cur = None

    def peek(p=0):
        if pos + p >= len(ts):
            return 'eof'
        else:
            return tk_tag(ts[pos + p])

    def match(t):
        if peek() != t:
            err(f'期望{t},实际为{cur}')

        return next()

    def next():
        nonlocal pos, cur

        old = cur
        pos = pos + 1

        if pos >= len(ts):
            cur = EOF
        else:
            cur = ts[pos]

        return old

    next()

    return peek, match, next

def cilly_parser(tokens):
    def err(msg):
        error('cilly parser', msg)
    peek, match, next = make_token_reader(tokens, err)
    def program():
        r = []
        while peek() != 'eof':
            if peek()==';':
                match(';')
                continue
            r.append(statement())
        return ['program', r]

    def statement():
        t = peek()
        if t == 'create' and peek(1) == 'table':
            return create_stat()
        if t == 'insert' and peek(1) == 'into':
            return insert_stat()
        if t == 'select':
            return query_stat()
        if t == 'drop':
            return drop_table()
        if t=='update':
            return update_stat()
        if t=='delete':
            return delete_stat()
        if t=='alter':
            return alter_stat()

        if t == 'var':
            return define_stat()
        if t == 'id' and peek(1) == '=':
            return assign_stat()
        if t == 'print':
            return print_stat()
        if t == 'if':
            return if_stat()
        if t == 'while':
            return while_stat()
        if t == 'break':
            return break_stat()
        if t == 'continue':
            return continue_stat()
        if t == 'return':
            return return_stat()
        if t == '{':
            return block_stat()
        return expr_stat()

    def create_stat():
        match('create')
        match('table')
        id=tk_val(match('id'))
        match('(')
        column_list=[column_definition()]
        while peek()!=')':
            match(',')
            column_list.append(column_definition())
        match(')')
        return ['create_table',id,column_list]

    def column_definition():
        column_id = tk_val(match('id'))
        data_type = tk_tag(next())
        if data_type=='char':
            match('(')
            t=tk_val(match('num'))
            match(')')
        else :
            t=0
        return [column_id,[data_type,t]]

    def insert_stat():
        match('insert')
        match('into')
        id=tk_val(match('id'))
        match('values')
        match('(')
        if peek() == ')':
            alist = []
        else:
            alist = args()
        match(')')
        match(';')
        return ['insert_into',id,alist]

    def query_stat():
        match('select')
        if peek()=='*':
            match('*')
            column_list = '*'
        else:
            column_list=[tk_val(match('id'))]
            while peek()==',':
                match(',')
                column_list.append(tk_val(match('id')))
        match('from')
        id = tk_val(match('id'))
        if peek()==';':
            match(';')
            return ['query',column_list, id,None,None]
        if peek()=='where':
            match('where')
            cond=expr()
            if peek() == ';':
                match(';')
                return ['query', column_list, id, cond,None]
        else:
            cond=None
        if peek()=='order':
            match('order')
            match('by')
            f_column=tk_val(match('id'))
            if peek()!=';':
                f_sort=tk_tag(next())
            else:
                f_sort='asc'
            match(';')
            return ['query', column_list, id, cond, [f_column,f_sort]]

    def drop_table():
        match('drop')
        if peek()=='table':
            match('table')
        id=tk_val(match('id'))
        return ['drop',id]

    def update_stat():
        match('update')
        id = tk_val(match('id'))
        match('set')
        k=[tk_val(match('id'))]
        match('=')
        v=[tk_val(next())]
        while peek()==',':
            match(',')
            k.append(tk_val(match('id')))
            match('=')
            v.append(tk_val(next()))
        match('where')
        cond=expr()
        match(';')
        return ['update',id,cond,k,v]

    def delete_stat():
        match('delete')
        match('from')
        id=tk_val(match('id'))
        match('where')
        cond=expr()
        match(';')
        return ['delete',id,cond]

    def alter_stat():
        match('alter')
        match('table')
        id = tk_val(match('id'))
        action=[alter_action()]
        while peek()==',':
            match(',')
            action.append(alter_action())
        match(';')
        return ['alter',id,action]

    def alter_action():
        if peek()=='add':
            match('add')
            match('column')
            return column_definition()
        if peek()=='drop':
            match('drop')
            match('column')
            return tk_val(match('id'))




    def define_stat():
        match('var')
        id = tk_val(match('id'))
        match('=')
        e = expr()
        match(';')
        return ['define', id, e]

    def assign_stat():
        id = tk_val(match('id'))
        match('=')
        e = expr()
        match(';')
        return ['assign', id, e]

    def print_stat():
        match('print')
        match('(')
        if peek() == ')':
            alist = []
        else:
            alist = args()
        match(')')
        match(';')

        return ['print', alist]

    def args():
        r = [expr()]
        while peek() == ',':
            match(',')
            r.append(expr())
        return r

    def if_stat():  # if ( expr ) statement (else statment)?
        match('if')
        match('(')
        cond = expr()
        match(')')

        true_stat = statement()

        if peek() == 'else':
            match('else')
            false_stat = statement()
        else:
            false_stat = None
        return ['if', cond, true_stat, false_stat]

    def while_stat():
        match('while')
        match('(')
        cond = expr()
        match(')')
        body = statement()

        return ['while', cond, body]

    def continue_stat():
        match('continue')
        match(';')
        return ['continue']

    def break_stat():
        match('break')
        match(';')
        return ['break']

    def return_stat():
        match('return')
        if peek() != ';':
            e = expr()
        else:
            e = None
        match(';')

        return ['return', e]

    def block_stat():
        match('{')

        r = []

        while peek() != '}':
            r.append(statement())

        match('}')
        return ['block', r]

    def expr_stat():
        e = expr()
        match(';')

        return ['expr_stat', e]

    def literal(bp=0):
        return next()

    def unary(bp):
        op = tk_tag(next())
        e = expr(bp)

        return ['unary', op, e]

    def fun_expr(bp=0):
        match('fun')
        match('(')
        if peek() == ')':
            plist = []
        else:
            plist = params()
        match(')')
        body = block_stat()
        return ['fun', plist, body]

    def params():
        r = [tk_val(match('id'))]
        while peek() == ',':
            match(',')
            r.append(tk_val(match('id')))
        return r

    def parens(bp=0):
        match('(')
        e = expr()
        if peek()==')':
            match(')')
            return e
        v=[e]
        while peek()!=')':
            match(',')
            v.append(expr())
        match(')')
        return v

    op1 = {
        'id': (100, literal),
        'num': (100, literal),
        'str': (100, literal),
        'true': (100, literal),
        'false': (100, literal),
        'null': (100, literal),
        '-': (85, unary),
        '!': (85, unary),
        'not': (85, unary),
        'fun': (98, fun_expr),
        '(': (100, parens),
    }

    def get_op1_parser(t):
        if t not in op1:
            err(f'非法token: {t}')

        return op1[t]

    def binary(left, bp):

        op = tk_tag(next())

        right = expr(bp)

        return ['binary', op, left, right]

    def call(fun_expr, bp=0):
        match('(')
        if peek() != ')':
            alist = args()
        else:
            alist = []
        match(')')
        return ['call', fun_expr, alist]

    op2 = {
        '*': (80, 81, binary),
        '/': (80, 81, binary),
        '%': (80, 81, binary),
        '+': (70, 71, binary),
        '-': (70, 71, binary),
        '>': (60, 61, binary),
        '>=': (60, 61, binary),
        '<': (60, 61, binary),
        '<=': (60, 61, binary),
        '==': (50, 51, binary),
        'in': (50, 51, binary),
        '!=': (50, 51, binary),
        '&&': (40, 41, binary),
        'and': (40, 41, binary),
        '||': (30, 31, binary),
        'or': (30, 31, binary),
        '(': (90, 91, call),
    }

    def get_op2_parser(t):
        if t not in op2:
            return (0, 0, None)
        else:
            return op2[t]

    def expr(bp=0):
        if peek()=='select':
            return query_stat()
        r_bp, parser = get_op1_parser(peek())
        left = parser(r_bp)
        while True:
            l_bp, r_bp, parser = get_op2_parser(peek())
            if parser == None or l_bp <= bp:
                break
            left = parser(left, r_bp)
        return left
    return program()

def mk_num(i):
    return ['num', i]
def mk_str(s):
    return ['str', s]
def mk_proc(params, body, env):
    return ['proc', params, body, env]
def mk_primitive_proc(f):
    return ['primitive', f]
TRUE = ['bool', True]
FALSE = ['bool', False]
def mk_bool(b):
    return TRUE if b else FALSE
NULL = ['null', None]

def val(v):
    return v[1]
# 环境: ({x:1, y:2},parent_env)
def lookup_var(env, name):
    while env:
        e, env = env

        if name in e:
            return e[name]

    error('lookup var', f'变量未定义{name}')

def set_var(env, name, val):
    while env:
        e, env = env
        if name in e:
            e[name] = val
            return

    error('set var', f'变量未定义{name}')

def define_var(env, name, val):
    e, env = env

    if name in e:
        error('define var', f'变量已定义{name}')

    e[name] = val

def extend_env(vars, vals, env):
    e = {var: val for (var, val) in zip(vars, vals)}
    return (e, env)

env = ({}, None)

def cilly_eval(ast, env):
    def err(msg):
        return error('cilly eval', msg)

    def ev_program(node, env):
        _, statements = node
        r = NULL
        for s in statements:
            r = visit(s, env)
        return r

    def create_table(node,env):
        _, table_name,column_list=node
        v={}
        for _ in column_list:
            column_id,data_type=_
            v[column_id]=data_type
        define_var(env,table_name,[v])

    def insert_into(node,env):
        _,table_name,column_list=node
        e=lookup_var(env,table_name)
        data_model=e[0]
        if len(data_model)!=len(column_list):
            err(f'非法插入value,长度不匹配 {column_list}')
        index = 0
        data_e = []
        for _,v in data_model.items():
            obj,ins=column_list[index]
            if v[0]=='int':
                if type(ins)!=int:
                    err('类型不匹配,需要类型为int')
            elif v[0]=='char':
                if type(ins)!=str:
                    err('类型不匹配,需要类型为str')
                elif len(ins)>v[1]:
                    err(f'字符串长度超出限制,错误的字符串{ins}')
            data_e.append(ins)
            index+=1
        e.append(data_e)
        print(e[1:])

    def query(node,env):
        _,column_list,id,cond,f_=node
        if cond==None:
            e=lookup_var(env,id)
        else:
            dfs(cond,env)
            e=choose_rows(lookup_var(env,id),cond,env)
        v=e[1:]
        if f_!=None:
            table_keys = list(e[0].keys())
            f_c, f_f = f_
            t=table_keys.index(f_c)
            if f_f=='asc':
                v=sorted(v, key=lambda x: x[t])
            elif f_f=='desc':
                v=sorted(v, key=lambda x: x[t], reverse=True)
            else:
                err(f'illegal sort:{f_f}')
        if column_list=='*':
            print(v)
            return v
        else:
            table_keys = list(e[0].keys())
            index_list = [table_keys.index(key) for key in column_list]
            v=[[row[i] for i in index_list] for row in v]
            print(v)
            return v

    def dfs(cond,env):
        if cond[0]=='unary':
            dfs(cond[2],env)
        elif cond[0]=='binary' and cond[1]=='in':
            dfs(cond[2], env)
            if cond[3][0]=='query':
                cond[3] = [_[-1] for _ in visit(cond[3], env)]
            elif type(cond[3][0])==list:
                c3=[]
                for _ in cond[3]:
                    if _[0]=='query':
                        for __ in visit(_,env):
                            c3.append(__[-1])
                    else:
                        c3.append(visit(_,env)[-1])
                cond[3] = c3
            elif len(cond[3])==2:
                cond[3] = [cond[3][-1]]
        elif cond[0]=='binary':
            dfs(cond[2],env)
            dfs(cond[3],env)

    def choose_rows(table,cond,env):
        table_keys = list(table[0].keys())
        v=[table[0]]
        for i in table[1:]:
            row_env=({table_keys[index]:['variant',i[index]] for index in range(len(table_keys))},env)
            if visit(cond,row_env)==TRUE:
                v.append(i)
        return v

    def drop(node,env):
        _,id=node
        env[0].pop(id)

    def update(node,env):
        _,id,cond,k,v=node
        e=choose_rows(lookup_var(env,id),cond,env)
        table_keys = list(e[0].keys())
        index_list = [table_keys.index(key) for key in k]
        for _ in e[1:]:
            for i in range(len(index_list)):
                _[index_list[i]]=v[i]
        print(e[1:])

    def delete(node,env):
        _,id_table,cond=node
        e1=lookup_var(env, id_table)
        e2=choose_rows(lookup_var(env, id_table), cond, env)
        e2_id=[id(_) for _ in e2[1:]]
        v=[_ for _ in e1 if id(_) not in e2_id]
        set_var(env,id_table,v)

    def alter(node,env):
        _,id,action=node
        e=lookup_var(env, id)
        for _ in action:
            if type(_)==list:
                column_id, data_type = _
                e[0][column_id] = data_type
                for __ in e[1:]:
                    __.append(None)
            else:
                table_keys = list(e[0].keys())
                i = table_keys.index(_)
                for __ in e[1:]:
                    __.pop(i)
                e[0].pop(table_keys[i])
        print(e[1:])


    def ev_expr_stat(node, env):
        _, e = node
        return visit(e, env)

    def ev_print(node, env):
        _, args = node
        for a in args:
            print(val(visit(a, env)), end=' ')
        print('')
        return NULL

    def ev_literal(node, env):
        tag, val = node
        if tag in ['num', 'str']:
            return node
        if tag in ['true', 'false']:
            return TRUE if tag == 'true' else FALSE
        if tag == 'null':
            return NULL
        err(f'非法字面量{node}')

    def ev_unary(node, env):
        _, op, e = node
        v = val(visit(e, env))
        if op == '-':
            return mk_num(-v)
        if op == '!' or op == 'not':
            return mk_bool(not (v))
        err(f'非法一元运算符{op}')

    def ev_binary(node, env):
        _, op, e1, e2 = node
        v1 = val(visit(e1, env))
        if op=='in':
            if v1 in e2:
                return TRUE
            return FALSE
        if op == '&&' or op=='and':
            if v1 == False:
                return FALSE
            else:
                return visit(e2, env)
        if op == '||' or op=='or':
            if v1 == True:
                return TRUE
            else:
                return visit(e2, env)
        v2 = val(visit(e2, env))
        if op == '+':
            if type(v1) == str or type(v2) == str:
                return mk_str(str(v1) + str(v2))
            return mk_num(v1 + v2)
        if op == '-':
            return mk_num(v1 - v2)
        if op == '*':
            return mk_num(v1 * v2)
        if op == '/':
            return mk_num(v1 / v2)
        if op == '%':
            return mk_num(v1 % v2)

        if op == '>':
            return mk_bool(v1 > v2)
        if op == '>=':
            return mk_bool(v1 >= v2)
        if op == '<':
            return mk_bool(v1 < v2)
        if op == '<=':
            return mk_bool(v1 <= v2)
        if op == '==':
            return mk_bool(v1 == v2)
        if op == '!=':
            return mk_bool(v1 != v2)

        err(f'非法二元运算符{op}')

    def ev_if(node, env):
        _, cond, true_stat, false_stat = node
        if visit(cond, env) == TRUE:
            return visit(true_stat, env)
        if false_stat != None:
            return visit(false_stat, env)
        return NULL

    def ev_while(node, env):
        _, cond, body = node
        r = NULL
        prev_r = NULL
        while visit(cond, env) == TRUE:
            r = visit(body, env)
            if r[0] == 'continue':
                continue
            if r[0] == 'break':
                r = prev_r
                break
            prev_r = r
        return r

    def ev_break(node, env):
        return ['break']

    def ev_continue(node, env):
        return ['continue']

    def ev_block(node, env):
        _, statements = node
        r = NULL
        block_env = extend_env({}, {}, env)
        for s in statements:
            r = visit(s, block_env)
            if r[0] in ['break', 'continue', 'return']:
                return r
        return r

    def ev_id(node, env):
        _, name = node
        return lookup_var(env, name)

    def ev_define(node, env):
        _, name, e = node
        v = visit(e, env)
        define_var(env, name, v)
        return NULL

    def ev_assign(node, env):
        _, name, e = node
        v = visit(e, env)
        set_var(env, name, v)
        return NULL

    def ev_fun(node, env):
        _, params, body = node
        return mk_proc(params, body, env)

    def ev_return(node, env):
        _, e = node
        if e != None:
            return ['return', visit(e, env)]
        else:
            return ['return', NULL]

    def ev_call(node, env):
        _, f_expr, args = node
        proc = visit(f_expr, env)
        if proc[0] not in ['proc', 'primitive']:
            err(f'非法函数{proc}')

        if proc[0] == 'primitive':
            _, f = proc
            args = [val(visit(a, env)) for a in args]
            return f(*args)
        _, params, body, saved_env = proc
        args = [visit(a, env) for a in args]
        f_env = extend_env(params, args, saved_env)
        v = visit(body, f_env)
        if v[0]=='return':
            return v[1]
        return v

    visitors = {
        'program': ev_program,
        'create_table':create_table,
        'insert_into':insert_into,
        'query':query,
        'drop':drop,
        'update':update,
        'delete':delete,
        'alter':alter,


        'expr_stat': ev_expr_stat,
        'print': ev_print,
        'if': ev_if,
        'while': ev_while,
        'break': ev_break,
        'continue': ev_continue,
        'define': ev_define,
        'assign': ev_assign,
        'block': ev_block,
        'unary': ev_unary,
        'binary': ev_binary,
        'id': ev_id,
        'fun': ev_fun,
        'return': ev_return,
        'call': ev_call,
        'num': ev_literal,
        'str': ev_literal,
        'array': ev_literal,
        'struct': ev_literal,
        'true': ev_literal,
        'false': ev_literal,
        'null': ev_literal,
    }

    def visit(node, env):
        t = node[0]
        if t not in visitors:
            err(f'非法节点{node}')
        return visitors[t](node, env)
    return visit(ast, env)

def cilly_interp(prog, env):
    tokens = cilly_lexer(prog)
    # print(tokens)
    ast = cilly_parser(tokens)
    # print(ast)
    v = cilly_eval(ast, env)
    # print(env)
    # return v

def cilly_repl():
    import pickle
    with open('env.pkl', 'rb') as f:
        env = pickle.load(f)
    print(env)
    while True:
        i = input('> ')
        if i=='HALT':
            break
        elif i=='clear':
            env=({}, None)
            continue
        v = cilly_interp(i, env)
    print(env)
    with open('env.pkl', 'wb') as f:
        pickle.dump(env, f)


def main():
    cilly_repl()                                            # 1

if __name__ =='__main__':
    main()

'''
proc='
create table stu(name char(20),age int,grade int);

insert into stu values("Alice",12,6);
insert into stu values("Bob",14,8);
insert into stu values("Gretchen",16,10);

select * from stu;
select name,grade from stu where age>13 or name=="_";
select * from stu where not(age>12);
select * from stu order by age asc;
select * from stu order by age desc;
select * from stu where name in ("Alice");
select * from stu where name in ("Alice") or age in (14);
select * from stu where name in (select name from stu;);
select * from stu where age in (14,select age from stu where name in ('Alice'););
select * from stu where age in (select age from stu where name in (select name from stu;););

update stu set name="Gretel",age=16,grade=10 where name=="Gretchen";
update stu set name="Gretchen" where name=="Gretel";

delete from stu where name=="Gretchen";

alter table stu add column height int;
alter table stu drop column height;
alter table stu drop column grade;

drop table stu;
'
'''