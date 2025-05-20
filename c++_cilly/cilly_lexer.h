#pragma once
#include<iostream>
#include<vector>
#include<unordered_set>
#include<unordered_map>
#include<variant>
#include<string>
using namespace std;

class cilly_tokens_operators {
public:
    cilly_tokens_operators() = default;
    bool in_void_word(char target) {
        return void_word.find(target) != void_word.end();
    };
    bool in_op1(char target) {
        return tokens_operators1.find(target) != tokens_operators1.end();
    };
    bool in_op2(char target) {
        return tokens_operators2.find(target) != tokens_operators2.end();
    };
    string get_op2(char target) {
        return tokens_operators2[target];
    };
    bool in_key_words(string target) {
        return keywords.find(target) != keywords.end();
    };
private:
    unordered_set<char> void_word = { ' ','\t','\r','\n' };
    unordered_set<char> tokens_operators1 = {
            '(', ')', '{', '}', '[', ']', ',', ';',
            '+', '-', '*', '/', '%', ':', '.'
    };
    unordered_map<char, string> tokens_operators2 = {
            {'>' , ">="},
            {'<' , "<="},
            {'=' , "=="},
            {'!' , "!="},
            {'&' , "&&"},
            {'|' , "||"}
    };
    unordered_set<string> keywords = {
        "var", "print", "if", "else", "while","break",
        "continue", "return", "fun", "true", "false",
        "null"
    };
};
extern cilly_tokens_operators tokens_operator;

using token = pair<string, variant<monostate, int, double, string>>;
class cilly_lexer
{
public:
    cilly_lexer(string code);
    char peek(int = 0);
    char next();
    char match(char);
    void code_to_tokens();
    void skip_ws();
    token get_token();
    token num_token();
    token string_token();
    token id_token();
    vector<token> get_tokens();
private:
    int pc = -1;
    string code;
    vector<token> tokens;
};

bool is_digit_alpha(char);