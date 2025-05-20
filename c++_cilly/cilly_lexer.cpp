#include"cilly_lexer.h"

cilly_tokens_operators tokens_operator;

cilly_lexer::cilly_lexer(string primative_code):code(primative_code) {
	code_to_tokens();
}
char cilly_lexer::peek(int p) {
	return code[pc + p];
}
char cilly_lexer::next() {
	pc++;
	return code[pc - 1];
}
char cilly_lexer::match(char c) {
	//if (c == peek())pc++;
	return next();
}
void cilly_lexer::code_to_tokens() {
	pc++;
	tokens.clear();
	while (true) {
		skip_ws();
		if (pc == code.size())break;
		tokens.push_back(get_token());
	}
}
void cilly_lexer::skip_ws() {
	while (isspace(peek())) {
		next();
	}
}
token cilly_lexer::get_token() {
	char cur_ch = peek();
	if (cur_ch == '_' || isalpha(cur_ch))
		return id_token();
	else if (cur_ch == '"')
		return string_token();
	else if (isdigit(cur_ch))
		return num_token();
	else if (tokens_operator.in_op1(peek())) {
		string op1(1, peek());
		next();
		return { op1,monostate{} };
	}
	else if (tokens_operator.in_op2(peek())) {
		string op1(1, peek());
		string op2 = tokens_operator.get_op2(peek());
		next();
		if (peek() == op2[1]) {
			next();
			return { op2,monostate{} };
		}
		return { op1,monostate{} };
	}
	return { "illegal_token",monostate{} };
};
token cilly_lexer::num_token() {
	string token_next;
	while (isdigit(peek()))token_next += next();
	if (peek() == '.') {
		token_next += next();
		while (isdigit(peek()))token_next += next();
		return { "double", stod(token_next) };
	}
	return { "int", stoi(token_next) };
};
token cilly_lexer::string_token() {
	match('"');
	string token_next;
	while (peek() != '"') { token_next += next(); 
	}
	match('"');
	return { "string",token_next };
}
token cilly_lexer::id_token() {
	string token_next;
	while (is_digit_alpha(peek()))token_next += next();
	if (tokens_operator.in_key_words(token_next))return { token_next,monostate{} };
	return { "id",token_next };
};

vector<token> cilly_lexer::get_tokens() {
	return tokens;
}

//¸¨Öúº¯Êý
bool is_digit_alpha(char c) {
	return c == '_' || isalnum(c);
}