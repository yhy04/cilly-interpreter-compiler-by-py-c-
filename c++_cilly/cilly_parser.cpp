#include "cilly_parser.h"

cilly_parser::cilly_parser(vector<token> primative_tokens) :tokens(primative_tokens) {
	token_to_ast();
}
string cilly_parser::peek(int p) {
	return tokens[pc + p].first;
}
token cilly_parser::peek_tk() {
	return tokens[pc];
}
string cilly_parser::next() {
	pc++;
	return tokens[pc - 1].first;
}
token cilly_parser::next_tk() {
	pc++;
	return tokens[pc - 1];
}
string cilly_parser::match(string tag) {
	if (tag != peek())return "err_tk";
	return next();
}
token cilly_parser::match_tk(string tag) {
	if (tag != peek())return { "tag","err_tk" };
	return next_tk();
}
void cilly_parser::token_to_ast() {
	pc++;
	ast = vector<ast_node >{};
	auto& vec = get<vector<ast_node>>(ast.val);
	vec.push_back(ast_node("program"));
	ast_node block_es = vector<ast_node >{};
	auto& e = get<vector<ast_node>>(block_es.val);
	while (true) {
		if (pc == tokens.size())break;
		e.push_back(get_statement());
	}
	vec.push_back(block_es);
}
ast_node cilly_parser::get_statement() {
	string tag = peek();
	if (tag == "var")
		return define_stat();
	else if (tag == "id" && peek(1) == "=")
		return assign_stat();
	else if(tag == "print")
		return print_stat();
	else if (tag == "if")
		return if_stat();
	else if (tag == "while")
		return while_stat();
	else if (tag == "break")
		return break_stat();
	else if (tag == "continue")
		return continue_stat();
	else if (tag == "return")
		return return_stat();
	else if (tag == "{")
		return block_stat();
	return expr_stat();
}
ast_node cilly_parser::define_stat() {
	ast_node define_n = vector<ast_node >{};
	auto& vec = get<vector<ast_node>>(define_n.val);
	match("var");
	string id = get<string>(peek_tk().second);
	match("id");
	match("=");
	ast_node e = expr();
	match(";");
	vec.push_back(ast_node("define"));
	vec.push_back(ast_node(id));
	vec.push_back(ast_node(e));
	return define_n;
}
ast_node cilly_parser::assign_stat() {
	ast_node assign_n = vector<ast_node >{};
	auto& vec = get<vector<ast_node>>(assign_n.val);
	string id = get<string>(peek_tk().second);
	match("id");
	match("=");
	ast_node e = expr();
	match(";");
	vec.push_back(ast_node("assign"));
	vec.push_back(ast_node(id));
	vec.push_back(ast_node(e));
	return assign_n;
}
ast_node cilly_parser::print_stat() {
	ast_node print_n = vector<ast_node >{};
	auto& vec = get<vector<ast_node>>(print_n.val);
	match("print");
	match("(");
	ast_node alist = vector<ast_node >{};
	if (peek() != ")")alist = args();
	match(")");
	match(";");
	vec.push_back(ast_node("print"));
	vec.push_back(ast_node(alist));
	return print_n;
}
ast_node cilly_parser::if_stat() {
	ast_node if_n = vector<ast_node >{};
	auto& vec = get<vector<ast_node>>(if_n.val);
	match("if");
	match("(");
	ast_node cond_stat = expr();
	match(")");
	ast_node true_stat = get_statement();
	ast_node false_stat = monostate{};
	if (peek() == "else") {
		match("else");
		false_stat = get_statement();
	}
	vec.push_back(ast_node("if"));
	vec.push_back(ast_node(cond_stat));
	vec.push_back(ast_node(true_stat));
	vec.push_back(ast_node(false_stat));
	return if_n;
}
ast_node cilly_parser::while_stat() {
	ast_node while_n = vector<ast_node >{};
	auto& vec = get<vector<ast_node>>(while_n.val);
	match("while");
	match("(");
	ast_node cond_stat = expr();
	match(")");
	ast_node body_stat = expr();
	vec.push_back(ast_node("if"));
	vec.push_back(ast_node(cond_stat));
	vec.push_back(ast_node(body_stat));
	return while_n;
}
ast_node cilly_parser::continue_stat() {
	ast_node continue_n = vector<ast_node >{};
	auto& vec = get<vector<ast_node>>(continue_n.val);
	match("continue");
	match(";");
	vec.push_back(ast_node("continue"));
	return continue_n;
}
ast_node cilly_parser::break_stat() {
	ast_node break_n = vector<ast_node >{};
	auto& vec = get<vector<ast_node>>(break_n.val);
	match("break");
	match(";");
	vec.push_back(ast_node("break"));
	return break_n;
}
ast_node cilly_parser::return_stat() {
	ast_node return_n = vector<ast_node >{};
	auto& vec = get<vector<ast_node>>(return_n.val);
	match("return");
	ast_node e = monostate{};
	if (peek() != ";")e = expr();
	match(";");
	vec.push_back(ast_node("return"));
	vec.push_back(ast_node(e));
	return return_n;
}
ast_node cilly_parser::block_stat() {
	ast_node block_n = vector<ast_node >{};
	auto& vec = get<vector<ast_node>>(block_n.val);
	ast_node block_es = vector<ast_node >{};
	auto& e = get<vector<ast_node>>(block_es.val);
	match("{");
	while (peek() != "}") {
		e.push_back(get_statement());
	}
	match("}");
	vec.push_back(ast_node("block"));
	vec.push_back(block_es);
	return block_n;
}
ast_node cilly_parser::expr_stat() {
	ast_node expr_n = vector<ast_node >{};
	auto& vec = get<vector<ast_node>>(expr_n.val);
	ast_node e = expr();
	match(";");
	vec.push_back(ast_node("expr_stat"));
	vec.push_back(ast_node(e));
	return expr_n;
}
ast_node cilly_parser::expr(int bp) {
	ast_node left_expr = vector<ast_node >{};
	auto& vec = get<vector<ast_node>>(left_expr.val);
	string cur_str = peek();
	int r_bp;
	if (cur_str == "id" || cur_str == "int" || cur_str == "double" || cur_str == "string" || cur_str == "true" || cur_str == "false" || cur_str == "null") {
		r_bp = 100;
		left_expr = literal_f();
	}
	else if (cur_str == "-" || cur_str == "!") {
		r_bp = 85;
		left_expr = unary(bp);
	}
	else if (cur_str == "fun") {
		r_bp = 98;
		left_expr = fun_expr(bp);
	}
	else if (cur_str == "(" || cur_str == "[" || cur_str == "{") {
		r_bp = 100;
		left_expr = parens_brakets_brace(bp);
	}
	else r_bp=-1;
	while (r_bp!=-1) {
		string r_str = peek();
		int l_bp;
		if (r_str == "*" || r_str == "/" || r_str == "%") {
			l_bp = 80;
			r_bp = 81;
			if (l_bp <= bp)break;
			left_expr = binary_cy(left_expr, r_bp);
		}
		else if (r_str == "+" || r_str == "-") {
			l_bp = 70;
			r_bp = 71;
			if (l_bp <= bp)break;
			left_expr = binary_cy(left_expr, r_bp);
		}
		else if (r_str == ">" || r_str == ">=" || r_str == "<" || r_str == "<=") {
			l_bp = 60;
			r_bp = 61;
			if (l_bp <= bp)break;
			left_expr = binary_cy(left_expr, r_bp);
		}
		else if (r_str == "==" || r_str == "!=") {
			l_bp = 50;
			r_bp = 51;
			if (l_bp <= bp)break;
			left_expr = binary_cy(left_expr, r_bp);
		}
		else if (r_str == "&&") {
			l_bp = 40;
			r_bp = 41;
			if (l_bp <= bp)break;
			left_expr = binary_cy(left_expr, r_bp);
		}
		else if (r_str == "||") {
			l_bp = 30;
			r_bp = 31;
			if (l_bp <= bp)break;
			left_expr = binary_cy(left_expr, r_bp);
		}
		else if (r_str == "(") {
			l_bp = 90;
			r_bp = 91;
			if (l_bp <= bp)break;
			left_expr = call(left_expr, r_bp);
		}
		else if (r_str == "[") {
			l_bp = 90;
			r_bp = 91;
			if (l_bp <= bp)break;
			left_expr = call(left_expr, r_bp);// index
		}
		else if (r_str == ".") {
			l_bp = 90;
			r_bp = 91;
			if (l_bp <= bp)break;
			left_expr = call(left_expr, r_bp);// member
		}
		else break;
	}
	return left_expr;
}

ast_node cilly_parser::args() {
	ast_node alist = vector<ast_node >{};
	auto& avec = get<vector<ast_node>>(alist.val);
	avec.push_back(expr());
	while (peek() == ",") {
		match(",");
		avec.push_back(expr());
	}
	return alist;
}
ast_node cilly_parser::literal_f(int bp) {
	ast_node literal_n = vector<ast_node >{};
	auto& vec = get<vector<ast_node>>(literal_n.val);
	token t = next_tk();
	vec.push_back(ast_node(t.first));
	if (t.first == "int")vec.push_back(get<int>(t.second));
	else if (t.first == "double")vec.push_back(get<double>(t.second));
	else if (t.first == "string")vec.push_back(get<string>(t.second));
	else if (t.first == "id")vec.push_back(get<string>(t.second));
	else vec.push_back(monostate{});
	return literal_n;
}
ast_node cilly_parser::unary(int bp) {
	ast_node unary_n = vector<ast_node >{};
	auto& vec = get<vector<ast_node>>(unary_n.val);
	string op = next();
	ast_node e = expr(bp);
	vec.push_back(ast_node("unary"));
	vec.push_back(ast_node(op));
	vec.push_back(ast_node(e));
	return unary_n;
}
ast_node cilly_parser::fun_expr(int bp) {
	ast_node fun_n = vector<ast_node >{};
	auto& vec = get<vector<ast_node>>(fun_n.val);
	ast_node fun_list = vector<ast_node >{};
	auto& list_vec = get<vector<ast_node>>(fun_list.val);
	match("fun");
	match("(");
	if (peek() != ")")fun_list = params();
	match(")");
	ast_node body = block_stat();
	vec.push_back(ast_node("fun"));
	vec.push_back(ast_node(fun_list));
	vec.push_back(ast_node(body));
	return fun_n;
}
ast_node cilly_parser::params() {
	ast_node params_n = vector<ast_node >{};
	auto& vec = get<vector<ast_node>>(params_n.val);
	string tk_v = get<string>(match_tk("id").second);
	vec.push_back(tk_v);
	while (peek() == ",") {
		match(",");
		string tk_v = get<string>(match_tk("id").second);
		vec.push_back(tk_v);
	}
	return params_n;
}
ast_node cilly_parser::parens_brakets_brace(int bp) {
	string cur_ch = peek();
	if (cur_ch == "(") {
		match("(");
		ast_node e = expr();
		match(")");
		return e;
	}
	else if(cur_ch=="["){
		ast_node arr= vector<ast_node >{};
		auto& vec = get<vector<ast_node>>(arr.val);
		match("[");
		if (peek() != "]")vec.push_back(expr());
		while (peek() != "]") {
			match(",");
			vec.push_back(ast_node(expr()));
		}
		match("]");
		return arr;
	}
	else if(cur_ch=="{"){
		ast_node dict = vector<ast_node >{};
		auto& vec = get<vector<ast_node>>(dict.val);
		match("{");
		//code
		match("}");
		return dict;
	}
	return monostate{ };
}
ast_node cilly_parser::binary_cy(ast_node left, int bp) {
	ast_node bina = vector<ast_node >{};
	auto& vec = get<vector<ast_node>>(bina.val);
	string op = next();
	ast_node right = expr(bp);
	vec.push_back(ast_node("binary"));
	vec.push_back(ast_node(op));
	vec.push_back(ast_node(left));
	vec.push_back(ast_node(right));
	return bina;
}
ast_node cilly_parser::call(ast_node fun_expr, int bp) {
	ast_node cal = vector<ast_node >{};
	auto& vec = get<vector<ast_node>>(cal.val);
	ast_node alist = vector<ast_node >{};
	auto& list_vec = get<vector<ast_node>>(alist.val);
	match("(");
	if (peek() != ")")alist = args();
	match(")");
	vec.push_back(ast_node("call"));
	vec.push_back(ast_node(fun_expr));
	vec.push_back(ast_node(alist));
	return cal;
}