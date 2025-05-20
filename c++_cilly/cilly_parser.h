#pragma once
#include"cilly_lexer.h"
#include<functional>

struct ast_node
{
    variant<monostate, int, double, string, vector<ast_node>> val;
    ast_node() : val(monostate{}) {} 
    ast_node(monostate v) : val(v) {}
    ast_node(int v) : val(v) {}
    ast_node(double v) : val(v) {}
    ast_node(string v) : val(v) {}
    ast_node(vector<ast_node> v) : val(v) {}
    ast_node(const ast_node& other) {
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
        else if (holds_alternative<vector<ast_node>>(other.val)) {
            vector<ast_node> new_vec;
            for (const auto& node : get<vector<ast_node>>(other.val)) {
                new_vec.push_back(node);
            }
            val = move(new_vec);
        }
    }
};

class cilly_parser
{
public:
    cilly_parser(vector<token>);
    string peek(int = 0);
    token peek_tk();
    string next();
    token next_tk();
    string match(string);
    token match_tk(string);
    void token_to_ast();
    ast_node get_statement();
    ast_node define_stat();
    ast_node assign_stat();
    ast_node print_stat();
    ast_node if_stat();
    ast_node while_stat();
    ast_node break_stat();
    ast_node continue_stat();
    ast_node return_stat();
    ast_node block_stat();
    ast_node expr_stat();
    ast_node expr(int=0);
    ast_node args();
    ast_node literal_f(int=0);
    ast_node unary(int);
    ast_node fun_expr(int=0);
    ast_node params();
    ast_node parens_brakets_brace(int=0);
    ast_node binary_cy(ast_node, int = 0);
    ast_node call(ast_node, int = 0);
    //ast_node index_member(ast_node, int = 0);
    ast_node& get_ast() {
        return ast;
    };
private:
    int pc = -1;
    vector<token> tokens;
    ast_node ast;
};

