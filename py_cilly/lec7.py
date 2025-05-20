'''
cilly 语法

program : statement* EOF

statement
    : define_statement
    | assign_statement
    | print_statement
    | if_statement
    | while_statement
    | continue_statement
    | break_statement
    | return_statement
    | block_statement
    | expr_statement
    ;

define_statement
    : 'var' ID '=' expr ';'
    ;

assign_statement
    : ID '=' expr ';'
    ;

print_statement
    : 'print' '(' args? ')' ';'
    ;

args : expr (',' expr)* ;

if_statement
    : 'if' '(' expr ')' statement ('else' statement)?
    ;

while_statement
    : 'while' '(' expr ')' statement
    ;

continue_statement
    : 'continue' ';'
    ;

break_statement
    : 'break' ';'
    ;

return_statement
    : 'return' expr? ';'
    ;

block_statement
    : '{' statement* '}'
    ;

expr_statement:
    : expr ';'

expr
    : id | num | string | 'true' | 'false' | 'null'
    | '(' expr ')'
    | ('-' | '!') expr
    | expr ('+' | '-' | '*' | '/' | '==' | '!=' | '>' | '>=' | '<' | '<=' | '&&' | '||') expr
    | 'fun' '(' params? ')' block_statement
    | expr '(' args? ')'
    ;

表达式实现
方法1：改造文法

expr: logic_expr
logic_expr : rel_expr ('&&' rel_expr)*
rel_expr : add_expr ('>' add_expr)*
add_expr : mul_expr ('+' mul_expr)*
mul_expr : unary ('*' unary)*
unary : factor | '-' unary
factor : id | num | ....

方法2： pratt解析

   1     +    2
     30    40

   1     *    2
     50     60

   1  +   2   *  3
        40  50

   1  +   2  +   3
       40   30
comment : '#' 非换行符号 '\r'? '\n'

cilly 词法
program : token* 'eof'

token
    : id | num | string
    | 'true' | 'false' | 'null'
    | 'var' | 'if' | 'else' | 'while' | 'continue' | 'break' | 'return' | 'fun'
    | '(' | ')' | '{' | '}' | ','
    | '=' | '=='
    | '+' | '-' | '*' | '/'
    | '!' | '!='
    | '>' | '>='
    | '<' | '<='
    | '&&' | '||'
    ;

num : [0-9]+ ('.' [0-9]*)?
string : '"' char* '"'
char : 不是双引号的字符
ws : (' ' | '\r' | '\n' | '\t)+


'''

p1 = '''
    var pi = 3.1415926;

    var area = fun(r) {
        return pi * r * r;
    } ;

    print(area(10), area(20));

    var abs = fun(x) {
        if(x < 0)
            return -x;
        else
            return x;
    } ;

    var sqrt = fun(x) {
        var iter = fun(guess) {
            if( abs(x - guess * guess) < 0.0001 )
                return guess;
            else
                return iter((guess + x / guess) / 2);
        };

        return iter(1);

    };

    print(sqrt(2), sqrt(2) * sqrt(2));

    var make_counter = fun(i) {
        return fun() {
            i = i + 1;
            return i;
        };
    };

    var c1 = make_counter(0);
    var c2 = make_counter(0);

    print(c1(), c1(), c2());

    var K = fun(a) {
        return fun(b) {
            return a;
        };
    };

    var KI = fun(a) {
        return fun(b) {
            return b;
        };
    };

    var pair = fun(a,b) {
        return fun(f) {
            return f(a)(b);
        };
    };

    var first = fun(p) {
        return p(K);
    };

    var second = fun(p) {
        return p(KI);
    };

    var p = pair(1,2);

    print(first(p), second(p));

    var fact = fun(n) {
        if(n == 0)
            return 1;
        else
            return n * fact(n-1);
   };

   var fact2 = fun(n) {
       var r = 1;
       var i = n;

       while(n > 0) {
           r = n * r;
           n = n - 1;
       }

       return r;

   };
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

        match(')')

        return e

    def brackets(bp=0):
        match('[')

        exprs = []

        if peek()!=']':
            exprs.append(expr())
        while peek()!=']':
            match(',')
            exprs.append(expr())

        match(']')

        return ['array', exprs]

    def brace(bp=0):
        match('{')

        exprs = {}
        if peek()!='}':
            key = expr()
            match(':')
            exprs[tk_val(key)] = expr()
        while peek()!='}':
            match(',')
            key = expr()
            match(':')
            exprs[tk_val(key)]=expr()
        match('}')

        return ['struct', exprs]

    op1 = {
        'id': (100, literal),
        'num': (100, literal),
        'str': (100, literal),
        'true': (100, literal),
        'false': (100, literal),
        'null': (100, literal),
        '-': (85, unary),
        '!': (85, unary),
        'fun': (98, fun_expr),
        '(': (100, parens),
        '[': (100, brackets),
        '{': (100, brace),
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

    def index(array, bp=0):
        match('[')
        ind = expr()
        match(']')
        return ['binary', '[]', array, ind]

    def member(struct, bp=0):
        match('.')
        return ['binary', '.', struct, expr()]

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
        '!=': (50, 51, binary),
        '&&': (40, 41, binary),
        '||': (30, 31, binary),
        '(': (90, 91, call),
        '[':(90, 91, index),
        '.':(90, 91, member),
    }

    def get_op2_parser(t):
        if t not in op2:
            return (0, 0, None)
        else:
            return op2[t]

    def expr(bp=0):
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
            if r[0]=='return':
                return tk_val(r[1])
        return r

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
        if tag =='array':
            return node
        if tag == 'struct':
            new_env=({},None)
            for key, value in val.items():
                new_env[0][key]=visit(value,new_env)
            return [tag, new_env[0]]
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
        if op == '!':
            return mk_bool(not (v))
        err(f'非法一元运算符{op}')

    def ev_binary(node, env):
        _, op, e1, e2 = node
        v1 = val(visit(e1, env))
        if op == '&&':
            if v1 == False:
                return FALSE
            else:
                return visit(e2, env)
        if op == '||':
            if v1 == True:
                return TRUE
            else:
                return visit(e2, env)

        if op == '.':
            v2 = visit(e2, (v1,None))
            return v2
        v2 = val(visit(e2, env))
        if op == '[]':
            return visit(v1[v2],env)

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

def cilly_simplify(ast:list)->list:
    ast_dict={}
    def err(msg):
        error('cilly simplify', msg)
    def analyze(ast):
        _, statements = ast
        new_statements=[]
        for statement in statements:
            new_statements.append(optimize(statement))
        return ['program', new_statements]
    def optimize(node):
        if node == None:
            return node
        _ = node[0]
        if _ in ['expr_stat','print']:
            return [_, optimize(node[1])]
        elif _ =='if':
            cond = optimize(node[1])
            if cond==['true', None]:
                return optimize(node[2])
            elif cond==['false', None]:
                return optimize(node[3])
            return [_, cond, optimize(node[2]), optimize(node[3])]
        elif _ =='while':
            return [_, optimize(node[1]), optimize(node[2])]
        elif _ == 'define':
            v2 = optimize(node[2])
            ast_dict[node[1]]=v2
            return [_,node[1],v2]
        elif _=='assign':
            return [_, node[1], optimize(node[2])]
        elif _=='block':
            statements = node[1]
            new_statements=[]
            for statement in statements:
                new_statements.append(optimize(statement))
            return [_, new_statements]
        elif _ =='unary':
            _, op, e = node
            v = optimize(e)
            if v[0] == 'num':
                if op == '-':
                    return mk_num(-v[1])
                if op == '!':
                    return mk_bool(not v[1])
            return node
        elif _== 'binary':
            _, op, e1, e2 = node
            e1 = optimize(e1)
            e2 = optimize(e2)
            if e1[0] in ['num','str','true','false'] and e2[0] in ['num','str','true','false']:
                return ev_binary([_, op, e1, e2])
            return [_, op, e1, e2]
        elif _ == 'id':
            return node
        elif _ == 'fun':
            _, params, body = node
            body = optimize(body)
            return [_,params, body]
        elif _ == 'return':
            _, e = node
            if e != None:
                return [_,optimize(e)]
            else:
                return [_]
        elif _ == 'call':
            _, f_expr, args = node
            if f_expr[1] in ast_dict:
                primi = ast_dict[f_expr[1]]
                p_args = primi[1]
                p_body = primi[2]
                return replace_vars(p_body,p_args,args)
            return node
        elif _ in ['num','str','array','struct','true','false','null','break','continue']:
            return node
        else:
            err(f'非法节点{node}')
        return node
    def ev_binary(node):
        _, op, e1, e2 = node
        v1, v2 = e1[1], e2[1]
        if op == '&&':
            if e1 == False:
                return FALSE
            else:
                return e2
        if op == '||':
            if e1 == True:
                return TRUE
            else:
                return e2
        if op == '+':
            if type(v1) == str:
                return mk_str(v1 + str(v2))
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
        return node
    def replace_vars(proc, list1, list2):
        name_mapping = dict(zip(list1, list2))
        def traverse(node):
            if isinstance(node, list):
                if len(node) >= 2 and node[0] == 'id' and isinstance(node[1], str):
                    old_name = node[1]
                    return name_mapping.get(old_name, ['id',old_name])
                else:
                    return [traverse(elem) for elem in node]
            else:
                return node
        return traverse(proc)
    new_ast=analyze(ast)
    return new_ast

def cilly_analyzer(ast):
    def err(msg):
        return error('cilly analyzer', msg)
    def analyze_program(node):
        _, statements = node
        p_s_s = [visit(statement) for statement in statements]
        def proc(env):
            p = NULL
            for p_s in p_s_s:
                p = p_s(env)
            return p
        return proc
    def analyze_expr_stat(node):
        _, e= node
        p_e = visit(e)
        def proc(env):
            return p_e(env)
        return proc
    def ev_print(node):
        _, args = node
        p_a_s=[visit(a) for a in args]
        def proc(env):
            for p_a in p_a_s:
                print(val(p_a(env)), end=' ')
            print('')
            return NULL
        return proc
    def ev_if(node):
        _, cond, true_stat, false_stat = node
        p_cond=visit(cond)
        p_true_stat = visit(true_stat)
        p_false_stat = visit(false_stat)
        def proc(env):
            if p_cond(env) == TRUE:
                return p_true_stat(env)
            if false_stat != None:
                return p_false_stat(env)
            return NULL
        return proc
    def ev_break(node):
        def proc(env):
            return ['break']
        return proc
    def ev_continue(node):
        def proc(env):
            return ['continue']
        return proc
    def ev_define(node):
        _, name, e = node
        p_e = visit(e)
        def proc(env):
            v = p_e(env)
            define_var(env, name, v)
            return NULL
        return proc
    def ev_assign(node):
        _, name, e = node
        p_e=visit(e)
        def proc(env):
            v = p_e(env)
            set_var(env, name, v)
            return NULL
        return proc
    def ev_block(node):
        _, statements = node
        p_r_s=[]
        for s in statements:
            p_r_s.append(visit(s))
        def proc(env):
            r=NULL
            block_env = extend_env({}, {}, env)
            for p_r in p_r_s:
                r = p_r(block_env)
                if r[0] in ['break', 'continue', 'return']:
                    return r
            return r
        return proc
    def ev_unary(node):
        _, op, e = node
        p_v = visit(e)
        def proc(env):
            _, op, e = node
            v = val(p_v(env))
            if op == '-':
                return mk_num(-v)
            if op == '!':
                return mk_bool(not (v))
            err(f'非法一元运算符{op}')
        return proc
    def ev_id(node):
        _, name = node
        def proc(env):
            return lookup_var(env, name)
        return proc
    def ev_fun(node):
        _, params, body = node
        def proc(env):
            return mk_proc(params, body, env)
        return proc
    def ev_return(node):
        _, e = node
        p_e=visit(e)
        def proc(env):
            if e != None:
                return ['return', p_e(env)]
            else:
                return ['return', NULL]
        return proc
    def ev_call(node):
        _, f_expr, args = node
        p_proc = visit(f_expr)
        p_args = [visit(a) for a in args]
        def proc(env):
            proc=p_proc(env)
            if proc[0] not in ['proc', 'primitive']:
                err(f'非法函数{proc}')
            if proc[0] == 'primitive':
                _, f = proc
                args = [val(p_a(env)) for p_a in p_args]
                return f(*args)
            _, params, body, saved_env = proc
            args = [p_a(env) for p_a in p_args]
            f_env = extend_env(params, args, saved_env)
            v = visit(body)(f_env)
            if v[0] == 'return':
                return v[1]
            return v
        return proc
    def analyze_literal(node):
        tag = node[0]

        if tag in ['num', 'str']:
            v = node
        elif tag =='array':
            v = node
        elif tag =='struct':
            def proc(env):
                new_env=({},None)
                for key, value in node[1].items():
                    new_env[0][key]=visit(value)(new_env)
                return [tag, new_env[0]]
            return proc
        elif tag == 'false':
            v = FALSE
        elif tag == 'true':
            v = TRUE
        elif tag == 'null':
            v = NULL
        else:
            err(f'非法字面量{tag}')

        def proc(env):
            return v

        return proc

    def analyz_binary(node):
        _, op, e1, e2 = node

        p1 = visit(e1)
        p2 = visit(e2)
        if op == '.':
            def proc(env):
                v1=p1(env)
                v2 = visit(e2)((val(v1), None))
                return v2
            return proc
        if op == '[]':
            def proc(env):
                return visit(val(p1(env))[val(p2(env))])(env)
            return proc
        if op == '+':
            def proc(env):
                v1 = val(p1(env))
                v2 = val(p2(env))
                if type(v1) == str or type(v2) == str:
                    return mk_str(str(v1) + str(v2))
                return mk_num(v1 + v2)
            return proc
        elif op == '-':
            op_proc = lambda v1, v2: mk_num(v1 - v2)
        elif op == '*':
            op_proc = lambda v1, v2: mk_num(v1 * v2)
        elif op == '/':
            op_proc = lambda v1, v2: mk_num(v1 / v2)
        elif op == '%':
            op_proc = lambda v1, v2: mk_num(v1 % v2)
        elif op == '>':
            op_proc = lambda v1, v2: mk_bool(v1 > v2)
        elif op == '>=':
            op_proc = lambda v1, v2: mk_bool(v1 >= v2)
        elif op == '<':
            op_proc = lambda v1, v2: mk_bool(v1 < v2)
        elif op == '<=':
            op_proc = lambda v1, v2: mk_bool(v1 <= v2)
        elif op == '==':
            op_proc = lambda v1, v2: mk_bool(v1 == v2)
        elif op == '!=':
            op_proc = lambda v1, v2: mk_bool(v1 != v2)
        else:
            err(f'非法二元运算符{op}')

        def proc(env):
            v1 = val(p1(env))
            v2 = val(p2(env))
            return op_proc(v1, v2)

        return proc

    def analyze_while(node):
        _, cond, body = node

        p_cond = visit(cond)
        p_body = visit(body)

        def proc(env):
            r = NULL
            prev_r = NULL
            while (p_cond(env) == TRUE):
                r = p_body(env)
                if r[0] == 'continue':
                    continue
                if r[0] == 'break':
                    r = prev_r
                    break
                prev_r = r
            return r
        return proc

    visitors = {
        'program': analyze_program,
        'expr_stat': analyze_expr_stat,
        'print': ev_print,
        'if': ev_if,
        'while': analyze_while,
        'break': ev_break,
        'continue': ev_continue,
        'define': ev_define,
        'assign': ev_assign,
        'block': ev_block,
        'unary': ev_unary,
        'binary': analyz_binary,
        'id': ev_id,
        'fun': ev_fun,
        'return': ev_return,
        'call': ev_call,
        'num': analyze_literal,
        'str': analyze_literal,
        'array': analyze_literal,
        'struct': analyze_literal,
        'true': analyze_literal,
        'false': analyze_literal,
        'null': analyze_literal,
    }

    def visit(node):
        if node is None:
            return NULL
        tag = node[0]
        if tag not in visitors:
            err(f'非法ast节点{tag}')

        return visitors[tag](node)

    return visit(ast)

p2 = '''
var fern = fun(len) {
    if(len > 5){
        forward(len);
        right(10);
        fern( len - 10);
        left( 40);
        fern( len - 10);
        right(30);
        backward(len);
    }
};
penground("red");
pencolor("green");
left(90);
penup();
backward(200);
pendown();
fern(100);
'''                                                          # 2

p3_1 = '''
var child = {
	name:"Al" + "ice",
	age:12 + 23,
	height:145,
	sing : fun(song) { print("sing: ",song);},
	toString : fun() { 
	    sing("Hello");
	    return "name:" +  name +  " age:" + age + " height:" + height;},
};
child.sing("123");
print(child.toString());                    
'''                                                        # 选做3 结构体

p3_2 = '''
var i=[
    [4,5,6,],
    2+3,
    fun(song) { print("sing: ",song);},
    ];
print(i[0][0]);
print(i[1+0]);
i[2]("array");
'''                                                        # 选做3 数组

p4_1 = '''
var i=0;
while(i<10000){
i=i+1;
}
print(i);
'''

p4_2 = '''
var f=fun(k){
if(k==0)return 1;
if(k==1)return 1;
return f(k-1)+f(k-2);
};
print(f(22));
print("end");
'''

p4_3 = '''
var f=fun(k){
if(k==1)return 1;
return f(k-1);
};
print(f(80));
print("end");
'''

p4_4 = '''
var f=fun(k){
if(k==0)return 1;
if(k==1)return 1;
if(k==2)return 1;
return f(k-1)+f(k-2)+f(k-3);
};
print(f(20));
print("end");
'''

import inspect
import turtle
def env_create(modules:list):
    Function = {}
    for module in modules:
        funs = {
            name: getattr(module, name)
            for name in dir(module)
            if callable(getattr(module, name)) and not name.startswith('_')
        }
        for key, value in funs.items():
            try:
                sig = inspect.signature(value)
            except ValueError:
                continue
            params = str(sig)[1:-1]
            code = f"""
def {key}({params}):
    module.{key}({params})
    return ['null', None]
"""
            exec_env = {'module': module, 'mk_primitive_proc': mk_primitive_proc}
            exec(code, exec_env)
            Function[key] = exec_env['mk_primitive_proc'](exec_env[key])

    env = (
        {
            'cilly_greet': mk_primitive_proc(greet)
        }
        | Function
        ,
        None
    )
    return env
def greet(name):
    print("Hello " + name)
    return NULL
def forward(distance):
    turtle.forward(distance)
    return NULL
def backward(distance):
    turtle.backward(distance)
    return NULL
def right(angle):
    turtle.right(angle)
    return NULL
def left(angle):
    turtle.left(angle)
    return NULL
def pencolor(color):
    turtle.pencolor(color)
    return NULL
def penup():
    turtle.penup()
    return NULL
def pendown():
    turtle.pendown()
    return NULL

def cilly_interp(prog, env):
    tokens = cilly_lexer(prog)
    ast = cilly_parser(tokens)
    print(ast)
    v = cilly_eval(ast, env)
    return v

def cilly_analyze_proc(prog, env):
    tokens = cilly_lexer(prog)
    ast = cilly_parser(tokens)
    print(ast)
    proc = cilly_analyzer(ast)
    result = proc(env)
    return result

def cilly_repl():
    init_env = ({}, None)
    while True:
        i = input('> ')
        v = cilly_interp(i, init_env)

import time
def runtime(p, *args):
    start = time.time()
    v = p(*args)
    elapsed = time.time() - start
    return elapsed

def main():

    # cilly_repl()                                            # 1

    # cilly_interp(p2,env_create([turtle]))                    # 2

    env = ({
               'cilly_greet': mk_primitive_proc(greet),
               'forward': mk_primitive_proc(forward),
               'backward': mk_primitive_proc(backward),
               'right': mk_primitive_proc(right),
               'left': mk_primitive_proc(left),
               'pencolor': mk_primitive_proc(pencolor),
               'penup': mk_primitive_proc(penup),
               'pendown': mk_primitive_proc(pendown),
           }, None)
    from lec10 import p1
    cilly_interp(p1,env)

    # cilly_interp(p3_1, env_create([]))                   # 3
    # cilly_interp(p3_2,env_create([]))                    # 3

    # print(runtime(cilly_interp, p4_4, ({}, None)))
    # print(runtime(cilly_analyze_proc, p4_4, ({}, None)))  # 选做4

if __name__ =='__main__':
    main()