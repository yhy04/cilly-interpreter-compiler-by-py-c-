#pragma once
#include"cilly_parser.h"
#include<stack>
#include<math.h>

struct node{
	string tag;
    variant<monostate, int, double, string, bool, pair<int, int>,
    pair<int, vector<shared_ptr<vector<node>>>>> val;
    node() : tag("null"), val(monostate{}){}
    node(monostate v, string t="null") :tag(t), val(v) {}
    node(int v,string t="int") : tag(t), val(v) {}
    node(double v, string t= "double") : tag(t), val(v) {}
    node(string v, string t= "string") : tag(t), val(v) {}
    node(bool v,string t= "bool") :tag(t), val(v) {}
    node(pair<int,int> v, string t= "fun") :tag(t), val(v) {}
    node(pair<int, vector<shared_ptr<vector<node>>>> v, string t = "fun") :tag(t), val(v) {}
    node(const node& other) {
        tag = other.tag;
        if (holds_alternative<monostate>(other.val)) {
            val = monostate{};
        }
        else if (holds_alternative<int>(other.val)) {
            val = get<int>(other.val);
        }
        else if (holds_alternative<double>(other.val)) {
            val = get<double>(other.val);
        }
        else if (holds_alternative<string>(other.val)) {
            val = get<string>(other.val);
        }
        else if (holds_alternative<bool>(other.val)) {
            val = get<bool>(other.val);
        }
        else if (holds_alternative<pair<int,int>>(other.val)) {
            val = get<pair<int, int>>(other.val);
        }
        else if (holds_alternative<pair<int, vector<shared_ptr<vector<node>>>>>(other.val)) {
            val = get<pair<int, vector<shared_ptr<vector<node>>>>>(other.val);
        }
    }
};
class cilly_vm {
public:
	cilly_vm(vector<int>,vector<node>);
	void vm();
    void push(node v) { st.push(v); };
    node pop() { 
        node v = st.top();
        st.pop();
        return v; }

private:
	vector<int> code;
	int pc;
    stack<node> st;
    vector<shared_ptr<vector<node>>> scopes;
    vector<node> consts;
    stack<pair<int, vector<shared_ptr<vector<node>>>>> call_st;
};

class cilly_compiler
{
public:
    cilly_compiler(ast_node);
    int add_const(ast_node);
    int emit(int);
    int emit(int, int);
    int emit(int, int,int);
    void backpatch(int,int);
    void backpatch(int, int,int);
    void compile_program();
    void visit(ast_node&);
    int define_name(ast_node&);
    pair<int,int> look_var_name(ast_node&);
    vector<int>& get_code() { return code; }
    vector<node>& get_consts() { return consts; }
private:
    vector<int> code;
    vector<node> consts;

    vector<shared_ptr<vector<string>>> scopes;
    
    ast_node ast;
    stack<pair<int, int>> while_st_addrdep;
    stack<pair<vector<int>,vector<int>>> while_s;
    stack<pair<ast_node, ast_node>> fun_define_s;
    stack<pair<int, vector<shared_ptr<vector<string>>>>> fun_define_scope;
    stack<int> fun_depth;
    int HALT = 0,
        LOAD_CONST = 1,

        LOAD_NULL = 2,
        LOAD_TRUE = 3,
        LOAD_FALSE = 4,

        LOAD_VAR = 5,
        STORE_VAR = 6,

        PRINT_ITEM = 7,
        PRINT_NEWLINE = 8,
        JMP = 9,
        JMP_TRUE = 10,
        JMP_FALSE = 11,

        POP = 12,

        ENTER_SCOPE = 13,
        LEAVE_SCOPE = 14,
        CALL = 16,
        RETURN = 17,

        UNARY_NEG = 101,
        UNARY_NOT = 102,

        BINARY_ADD = 111,
        BINARY_SUB = 112,
        BINARY_MUL = 113,
        BINARY_DIV = 114,
        BINARY_MOD = 115,
        BINARY_POW = 116,

        BINARY_EQ = 117,
        BINARY_NE = 118,
        BINARY_LT = 119,
        BINARY_GE = 120;

};