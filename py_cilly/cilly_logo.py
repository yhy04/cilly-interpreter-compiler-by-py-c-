'''
grammar logo;

prog
    : (line? EOL)+ line? EOF
    ;

line
    : cmd+ comment?
    | comment
    | print_ comment?
    | procedureDeclaration
    ;

cmd
    : repeat_   *
    | fd    *
    | bk    *
    | rt    *
    | lt    *
    | cs    *
    | pu    *
    | pd    *
    | ht    *
    | st    *
    | home  *
    | label *
    | setxy *
    | make  *
    | procedureInvocation   *
    | ife   *
    | stop  *
    | fore  *
    ;

procedureInvocation
    : name expression*
    ;

procedureDeclaration
    : 'to' name parameterDeclarations* EOL? (line? EOL)+ 'end'
    ;

parameterDeclarations
    : ':' name (',' parameterDeclarations)*
    ;

func_
    : random
    ;

repeat_
    : 'repeat' number block
    ;

block
    : '[' cmd+ ']'
    ;

ife
    : 'if' comparison block
    ;

comparison
    : expression comparisonOperator expression
    ;

comparisonOperator
    : '<'
    | '>'
    | '='
    ;

make
    : 'make' STRINGLITERAL value
    ;

print_
    : 'print' (value | quotedstring)
    ;

quotedstring
    : '[' (quotedstring | ~ ']')* ']'
    ;

name
    : STRING
    ;

value
    : STRINGLITERAL
    | expression
    | deref
    ;

signExpression
    : (('+' | '-'))* (number | deref | func_)
    ;

multiplyingExpression
    : signExpression (('*' | '/') signExpression)*
    ;

expression
    : multiplyingExpression (('+' | '-') multiplyingExpression)*
    ;

deref
    : ':' name
    ;

fd
    : ('fd' | 'forward') expression
    ;

bk
    : ('bk' | 'backward') expression
    ;

rt
    : ('rt' | 'right') expression
    ;

lt
    : ('lt' | 'left') expression
    ;

cs
    : 'cs'
    | 'clearscreen'
    ;

pu
    : 'pu'
    | 'penup'
    ;

pd
    : 'pd'
    | 'pendown'
    ;

ht
    : 'ht'
    | 'hideturtle'
    ;

st
    : 'st'
    | 'showturtle'
    ;

home
    : 'home'
    ;

stop
    : 'stop'
    ;

label
    : 'label'
    ;

setxy
    : 'setxy' expression expression
    ;

random
    : 'random' expression
    ;

fore
    : 'for' '[' name expression expression expression ']' block
    ;

number
    : NUMBER
    ;

comment
    : COMMENT
    ;

STRINGLITERAL
    : '"' STRING
    ;

STRING
    : [a-zA-Z] [a-zA-Z0-9_]*
    ;

NUMBER
    : [0-9]+
    ;

COMMENT
    : ';' ~ [\r\n]*
    ;

EOL
    : '\r'? '\n'
    ;

WS
    : [ \t\r\n] -> skip
    ;

'''
import random


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
    '+','-','*','/','^','(',')',',',
    '=','[',']',':','"',';','`'
]

cilly_op2 = {
    '>': '>=',
    '<': '<=',
}

cilly_keywords = [
    # 'forward','fd','back','bk','right','rt','left','lt','home',
    'setxy', # goto()
    # 'penup','pu','pendown','pd','showturtle','st','hideturtle','ht','setheading','seth',
    'setpencolor','setpc', # pencolor()
    'setbackground','setbg', # bgcolor()
    'setpensize', # pensize()
    'label', # write()

    'and','or','not',
    'make',
    'if','ifelse',
    'repeat','for','while','stop',
    'to','end',
    'true','false',
    'print',
    # 'random','pick',
]

keywords_to_ins={
    'setxy':'goto',
    'setpencolor':'pencolor',
    'setpc':'pencolor',
    'setbackground':'bgcolor',
    'setbg':'bgcolor',
    'setpensize':'pensize',
    'label':'write',
}

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
        if c=='<' and peek(1)=='>':
            next()
            next()
            return mk_tk('<>')
        if c == '"':
            return string()
        if c==':':
            next()
            return id()
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
        while peek() not in [' ', '\t', '\r', '\n'] and peek() != 'eof':
            r = r + next()
        return mk_tk('str', r)

    def is_alpha(c):
        return len(c)==1 and ((c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z'))

    def is_digit_alpha__(c):
        return c == '_' or is_digit(c) or is_alpha(c)

    def id():
        r = '' + next()

        while is_digit_alpha__(peek()):
            r = r + next()

        if r in cilly_keywords:
            if r in keywords_to_ins:
                return mk_tk('id',keywords_to_ins[r])
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

instructions={
        'forward': 1,
        'fd': 1,
        'back': 1,
        'bk': 1,
        'right': 1,
        'rt': 1,
        'left': 1,
        'lt': 1,
        'home': 0,
        'goto': 2,
        'penup': 0,
        'pu': 0,
        'pendown': 0,
        'pd': 0,
        'showturtle': 0,
        'st': 0,
        'hideturtle': 0,
        'ht': 0,
        'setheading': 1,
        'seth': 1,
        'pencolor': 1,
        'bgcolor': 1,
        'pensize': 1,
        'write': 1,
        'random': 1,
        'pick':1,
    }

def cilly_parser(tokens):
    def err(msg):
        error('cilly parser', msg)
    peek, match, next = make_token_reader(tokens, err)
    def program():
        r = []
        while peek() != 'eof':
            if peek()==',':
                next()
                continue
            r.append(statement())
        return ['program', r]

    def statement():
        t = peek()
        if t=='make':
            return assign_stat()
        if t=='if':
            return if_stat()
        if t=='ifelse':
            return ifelse_stat()
        if t=='repeat':
            return repeat_stat()
        if t=='for':
            return for_stat()
        if t=='while':
            return while_stat()
        if t=='stop':
            return stop_stat()
        if t=='to':
            return fun_stat()
        if t=='[':
            return block_stat()
        if t=='print':
            return print_stat()
        if t==',':
            return next()
        return expr_stat()

    def assign_stat():
        match('make')
        id = tk_val(match('str'))
        e = expr()
        return ['make', id, e]
    def if_stat():
        match('if')
        cond=expr()
        true_stat=block_stat()
        return ['if',cond,true_stat]
    def ifelse_stat():
        match('if')
        cond=expr()
        true_stat=block_stat()
        false_stat=block_stat()
        return ['ifelse',cond,true_stat,false_stat]
    def repeat_stat():
        match('repeat')
        cnt=expr()
        action=block_stat()
        return ['repeat',cnt,action]
    def for_stat():
        match('for')
        for_list=args()
        body=block_stat()
        return ['for',for_list,body]
    def while_stat():
        match('while')
        match('[')
        cond=expr()
        match(']')
        body=block_stat()
        return ['while',cond,body]
    def stop_stat():
        match('stop')
        return ['stop',None]
    def fun_stat():
        match('to')
        id=tk_val(match('id'))
        params=[]
        while peek()!='[':
            params.append(tk_val(match('id')))
        instructions[id]=len(params)
        body=block_stat()
        match('end')
        return ['make',id,['to',params,body]]
    def block_stat():
        match('[')
        e=[]
        while peek()!=']':
            e.append(statement())
        match(']')
        return ['block',e]
    def call(t,bp=0):
        cnt=instructions[t[1]]
        params=[]
        for _ in range(cnt):
            if peek()==',':
                next()
            params.append(expr())
        return ['call',t,params]
    def print_stat():
        match('print')
        if peek()=='[':
            match('[')
            alist=[]
            while peek()!=']':
                if peek()==',':
                    next()
                    continue
                alist.append(expr())
            match(']')
            return ['print',alist]
        return ['print', [expr()]]
    def args():
        r = []
        match('[')
        while peek() != ']':
            if peek()==',':
                next()
                continue
            r.append(expr())
        match(']')
        return r

    def expr_stat():
        e = expr()
        return ['expr_stat', e]

    def literal(bp=0):
        return next()

    def unary(bp):
        op = tk_tag(next())
        e = expr(bp)
        return ['unary', op, e]

    def parens(bp=0):
        match('[')
        v=[]
        while peek()!=']':
            v.append(expr())
        match(']')
        return ['list',v]

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
        '[': (100,parens),
    }

    def get_op1_parser(t):
        if t not in op1:
            err(f'非法token: {t}')
        return op1[t]

    def binary(left, bp):
        op = tk_tag(next())
        right = expr(bp)
        return ['binary', op, left, right]

    op2 = {
        '*': (80, 81, binary),
        '/': (80, 81, binary),
        '%': (80, 81, binary),
        '+': (70, 71, binary),
        '-': (70, 71, binary),
        '^':(90,91,binary),
        '>': (60, 61, binary),
        '>=': (60, 61, binary),
        '<': (60, 61, binary),
        '<=': (60, 61, binary),
        '==': (50, 51, binary),
        '!=': (50, 51, binary),
        '<>':(50, 51, binary),
        '&&': (40, 41, binary),
        'and': (40, 41, binary),
        '||': (30, 31, binary),
        'or': (30, 31, binary),
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
            if type(left[1])==str and left[1] in instructions:
                l_bp, r_bp, parser=90, 91, call
            else:
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

    def make(node,env):
        _,name,e=node
        v=visit(e,env)
        env[0][name]=v
        return NULL

    def if_proc(node,env):
        _,cond,true_stat=node
        if visit(cond,env)==TRUE:
            visit(true_stat,env)
        return NULL
    def ifelse_proc(node,env):
        _,cond,true_stat,false_stat=node
        if visit(cond,env)==TRUE:
            visit(true_stat,env)
        else:
            visit(false_stat,env)
        return NULL

    def block(node,env):
        _, statements = node
        r = NULL
        # block_env = extend_env({}, {}, env)
        for s in statements:
            # r = visit(s, block_env)
            r=visit(s,env)
            if r[0] in ['break', 'continue', 'return']:
                return r
        return r

    def repeat(node,env):
        _,cnt,action=node
        for _ in range(val(visit(cnt,env))):
            r=visit(action,env)
            if r[0]=='stop':
                break
        return NULL

    def to(node,env):
        _,id,body=node
        return mk_proc(id, body, env)

    def for_proc(node,env):
        _,for_list,body=node
        r0,r1,r2=for_list
        for _ in range(val(visit(r0,env)),val(visit(r1,env)),val(visit(r2,env))):
            r=visit(body,env)
            if r[0] == 'stop':
                break
        return NULL

    def while_proc(node,env):
        _,cond,body=node
        r = NULL
        prev_r = NULL
        while visit(cond, env) == TRUE:
            r = visit(body, env)
            if r[0] == 'stop':
                r = prev_r
                break
            prev_r = r
        return r

    def stop(node,env):
        return ['stop']

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
        if tag =='list':
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
        if op == '!'or op == 'not':
            return mk_bool(not (v))
        err(f'非法一元运算符{op}')

    def ev_binary(node, env):
        _, op, e1, e2 = node
        v1 = val(visit(e1, env))
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
        if op=='^':
            return mk_num(v1**v2)
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
        if op == '!=' or op=='<>':
            return mk_bool(v1 != v2)

        err(f'非法二元运算符{op}')


    def ev_break(node, env):
        return ['break']

    def ev_continue(node, env):
        return ['continue']

    def ev_id(node, env):
        _, name = node
        return lookup_var(env, name)

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
            v=tuple(args)
            return f(*args)
        _, params, body, saved_env = proc
        args = [visit(a, env) for a in args]
        f_env = extend_env(params, args, saved_env)
        v = visit(body, f_env)
        if v[0]=='return':
            return v[1]
        return v

    visitors = {
        'make':make,
        'if':if_proc,
        'ifesle':ifelse_proc,
        'block':block,
        'repeat':repeat,
        'to':to,
        'for':for_proc,
        'while':while_proc,
        'stop':stop,

        'program': ev_program,
        'expr_stat': ev_expr_stat,
        'print': ev_print,
        'break': ev_break,
        'continue': ev_continue,

        'unary': ev_unary,
        'binary': ev_binary,

        'id': ev_id,

        'fun': ev_fun,
        'return': ev_return,
        'call': ev_call,

        'num': ev_literal,
        'str': ev_literal,
        'list': ev_literal,
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
star = '''
to star [repeat 5 [ fd 100 rt 144 ]] end
clearscreen
star
'''

fern = '''
to fern :len [
    if :len>5 [
        fd :len rt 10 
        fern :len-10 
        lt 40 
        fern :len-10
        rt 30
        bk :len
    ]
] end
setpencolor "green
lt 90
pu
bk 200
pd
fern 100
'''

square = '''
to square :length [
  repeat 4 [ fd :length rt 90 ]
] end
to randomcolor [
  setpencolor pick [ "red "orange "yellow "green "blue "violet ]
] end
clearscreen
repeat 36 [ randomcolor square random 200 rt 10 ]
'''

david_star = '''
to staple [
    fd 100 rt 90 fd 204 rt 90 fd 100
    bk 100 lt 90 bk 204 lt 90 bk 100
] end
setpencolor "green
lt 90
for [0 6 1] [staple 
fd 100 rt 90 fd 24 lt 60 staple
rt 60 bk 24 lt 90 bk 100
fd 50 rt 60]
'''
name_ = '''
to Y_print [
    fd 10 
    lt 30 
    fd 8 bk 8 
    rt 60 
    fd 8 bk 8 
    lt 30
    bk 10
] end
to H_print [
    fd 17 bk 8.5 
    rt 90 
    fd 8 
    lt 90 
    fd 8.5 bk 17
] end
to W_print [   
    rt 165
    fd 17 
    lt 150
    fd 17
    rt 150
    fd 17 
    lt 150
    fd 17
    seth 90
] end
setpencolor "green
pu
bk 360
lt 90 bk 360
lt 90 fd 12 rt 90 pd
Y_print
pu rt 90 fd 8 lt 90 pd
H_print
pu rt 90 fd 8 lt 90 pd
Y_print
pu fd 17 rt 90 fd 20 lt 90 pd
W_print
pu bk 17 rt 90 fd 8 lt 90 pd
Y_print
pu rt 90 fd 12 lt 90 fd 4 pd
label "yhy_wy
'''
import inspect
import turtle
def f1(i):
    return mk_tk('variant',random.randrange(i))
def f2(items):
    return random.choice(items)
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
            'random':mk_primitive_proc(f1),
            'pick':mk_primitive_proc(f2),
        }
        | Function
        ,
        None
    )
    return env

def cilly_interp(prog, env):
    tokens = cilly_lexer(prog)
    # print(tokens)
    ast = cilly_parser(tokens)
    # print(ast)
    v = cilly_eval(ast, env)
    # return v

def cilly_repl():
    # init_env = ({}, None)
    init_env=env_create([turtle])
    while True:
        i = input('> ')
        if i=='break':
            break
        v = cilly_interp(i, init_env)

def main():
    cilly_interp(fern,env_create([turtle]))                    # 2
    cilly_repl()                                            # 1
    turtle.done()

if __name__ =='__main__':
    main()

'''
proc='
make "a 1+2
make "a "abc
if true [make "a 3]
ifelse false [] [make "a 4]
for [0 6 1] []
while :i<6 [make "i :i+1]
to A :a [:a+1] end
to star [repeat 5 [ fd 100 rt 144 ]] end
clearscreen
star
["a "b "c ]
[1 ,-2  4]
'
'''