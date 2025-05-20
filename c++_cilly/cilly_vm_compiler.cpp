#include"cilly_vm_compiler.h"

cilly_vm::cilly_vm(vector<int> CODE,vector<node> CONSTS):code(CODE),consts(CONSTS){
	pc = 0;
	vm();
}

void cilly_vm::vm(){
	while(pc<code.size()){
		int ins = code[pc];
		if (ins == 0)break;//HALT 0
		else if (ins == 1) {
			int index = code[pc + 1];
			push(consts[index]);
			pc += 2;
		}//LOAD_CONST 1							*
		else if (ins == 2) {
			push(node{ monostate{},"null" });
			pc += 1;
		}//LOAD_NULL 2							*
		else if (ins == 3) {
			push(node{ true,"bool" });
			pc += 1;
		}//LOAD_TRUE 3							*
		else if (ins == 4) {
			push(node{ false,"bool" });
			pc += 1;
		}//LOAD_FALSE 4							*
		else if (ins == 5) {
			int scope_i = code[pc + 1];
			int index = code[pc + 2];
			push((*scopes[scopes.size()-scope_i-1])[index]);
			pc += 3;
		}//LOAD_VAR 5							*
		else if (ins == 6) {
			int scope_i = code[pc + 1];
			int index = code[pc + 2];
			node v = pop();
			if (v.tag == "fun") {
				int entry = get<pair<int, int>>(v.val).first;
				v = node{ make_pair(entry,scopes),"fun" };
			}
			(*scopes[scopes.size() - scope_i - 1])[index] = v;
			pc += 3;
		}//STORE_VAR 6							*
		else if (ins == 7) {
			//cout << pop().val;
			visit([](auto&& arg) {
				using T = decay_t<decltype(arg)>;
				if constexpr (is_same_v<T, int>) {
					cout << "int: " << arg;
				}
				else if constexpr (is_same_v<T, double>) {
					cout << "double: " << arg ;
				}
				else if constexpr (is_same_v<T, std::string>) {
					cout << "string: " << arg ;
				}
				else if constexpr (is_same_v<T, bool>) {
					cout << "bool: " << arg ;
				}
				else if constexpr (is_same_v<T, pair<int, int>>) {
					cout << "pair: (" << arg.first << ", " << arg.second << ")" ;
				}
				else if constexpr (is_same_v<T, pair<int, vector<shared_ptr<vector<node>>>>>) {
					cout << "pair: (" << arg.first << ", " << ")";
				}
				else if constexpr (is_same_v<T, std::monostate>) {
					cout << "monostate (empty)" ;
				}
				}, pop().val);
			cout << ' ';
			pc++;
		}//PRINT_ITEM 7							*
		else if (ins == 8) {
			cout << endl;
			pc++;
		}//PRINT_NEWLINE 8						*
		else if (ins == 9) {
			pc = code[pc + 1];
		}//JMP 9
		else if (ins == 10) {
			if (get<bool>(pop().val))pc = code[pc + 1];
			else pc += 2;
		}//JMP_TRUE 10
		else if (ins == 11) {
			if (!get<bool>(pop().val))pc = code[pc + 1];
			else pc += 2;
		}//JMP_FALSE 11
		else if (ins == 12) {
			pop();
			pc += 1;
		}//POP 12
		else if (ins == 13) {
			int var_cnt = code[pc + 1];
			auto p=make_shared<vector<node>>();
			scopes.push_back(p);
			for (int i = 0; i < var_cnt; i++) {
				p->push_back(node());
			}
			pc += 2;
		}//ENTER_SCOPE
		else if (ins == 14) {
			scopes.pop_back();
			pc += 1;
		}//LEAVE_SCOPE
		else if (ins == 16) {
			int arg_count=code[pc+1];
			int return_addr=pc+2;
			call_st.push({ return_addr,scopes });
			auto new_scope = make_shared<vector<node>>();
			for(int i=0;i<arg_count;i++){
				new_scope->push_back(pop());
			}
			reverse(new_scope->begin(), new_scope->end());
			node v = pop();
			auto [i,j]=get<pair<int, vector<shared_ptr<vector<node>>>>>(v.val);
			scopes = move(j);
			scopes.push_back(new_scope);
			pc=i;
		}//CALL 16
		else if (ins == 17) {
			auto [i,j] = call_st.top();
			scopes = move(j);
			call_st.pop();
			pc=i;
		}//RETURN 17
		else if (ins == 101) {
			int v=get<int>(pop().val);
			push(node{ -v,"int"});
			pc+=1;
		}//UNARY_NEG 101
		else if (ins == 102) {
			int v=get<bool>(pop().val);
			push(node{!v,"bool"});
			pc+=1;
		}//UNARY_NOT 102
		else if (ins == 111) {
			int v2=get<int>(pop().val);
			int v1=get<int>(pop().val);
			push(node{ v1+v2,"int" });
			pc+=1;
		}//BINARY_ADD 111
		else if (ins == 112) {
			int v2=get<int>(pop().val);
			int v1=get<int>(pop().val);
			push(node{ v1-v2,"int" });
			pc += 1;
		}//BINARY_SUB 112
		else if (ins == 113) {
			int v2=get<int>(pop().val);
			int v1=get<int>(pop().val);
			push(node{ v1*v2,"int" });
			pc += 1;
		}//BINARY_MUL 113
		else if (ins == 114) {
			int v2=get<int>(pop().val);
			int v1=get<int>(pop().val);
			push(node{ v1/v2,"int" });
			pc += 1;
		}//BINARY_DIV 114
		else if (ins == 115) {
			int v2=get<int>(pop().val);
			int v1=get<int>(pop().val);
			push(node{ v1%v2,"int" });
			pc += 1;
		}//BINARY_MOD 115
		else if (ins == 116) {
			int v2=get<int>(pop().val);
			int v1=get<int>(pop().val);
			push(node{ (int)pow(v1,v2),"int" });
			pc += 1;
		}//BINARY_POW 116
		else if (ins == 117) {
			int v2=get<int>(pop().val);
			int v1=get<int>(pop().val);
			push(node{ v1==v2,"bool" });
			pc += 1;
		}//BINARY_EQ 117
		else if (ins == 118) {
			int v2=get<int>(pop().val);
			int v1=get<int>(pop().val);
			push(node{ v1!=v2,"bool" });
			pc += 1;
		}//BINARY_NEQ 118
		else if (ins == 119) {
			int v2=get<int>(pop().val);
			int v1=get<int>(pop().val);
			push(node{ v1<v2,"bool" });
			pc += 1;
		}//BINARY_LT 119
		else if (ins == 120) {
			int v2=get<int>(pop().val);
			int v1=get<int>(pop().val);
			push(node{ v1>=v2,"bool" });
			pc += 1;
		}//BINARY_GT 120
	}
}

cilly_compiler::cilly_compiler(ast_node AST) :ast(AST) {
	compile_program();
}

int cilly_compiler::add_const(ast_node c) {
	vector<ast_node> e = get<vector<ast_node>>(c.val);
	string tag = get<string>(e[0].val);
	if (tag == "fun") {
		consts.push_back(node{ make_pair(-1,-1),"fun" });
		return consts.size() - 1;
	}
	for (int i = 0; i < consts.size(); i++) {
		node& a = consts[i];
		if (a.tag == tag) {
			if (tag == "int" && get<int>(a.val) == get<int>(e[1].val))
				return i;
			if (tag == "double" && get<double>(a.val) == get<double>(e[1].val))
				return i;
			if (tag == "string" && get<string>(a.val) == get<string>(e[1].val))
				return i;
		}
	}
	if (tag == "int")
		consts.push_back(node{ get<int>(e[1].val),tag });
	if (tag == "double")
		consts.push_back(node{ get<double>(e[1].val),tag });
	if (tag == "string")
		consts.push_back(node{ get<string>(e[1].val),tag });
	return consts.size() - 1;
	
}

int cilly_compiler::emit(int a){
	code.push_back(a);
	return code.size() - 1;
}
int cilly_compiler::emit(int a,int b) {
	code.push_back(a);
	code.push_back(b);
	return code.size() - 2;
}
int cilly_compiler::emit(int a,int b,int c) {
	code.push_back(a);
	code.push_back(b);
	code.push_back(c);
	return code.size() - 3;
}

void cilly_compiler::backpatch(int addr,int operand){
	code[addr + 1] = operand;
}

void cilly_compiler::backpatch(int addr, int operand1,int operand2) {
	code[addr + 1] = operand1;
	code[addr + 2] = operand2;
}

void cilly_compiler::compile_program() {
	visit(ast);
	emit(HALT);
	while(!fun_define_scope.empty()){
		auto [params, body] = fun_define_s.top();
		auto [index, saved_scopes] = fun_define_scope.top();
		vector<ast_node> e = get<vector<ast_node>>(params.val);
		auto new_scope = make_shared<vector<string>>();
		for(auto &i:e){
			string name_id = get<string>(i.val);
			new_scope->push_back(name_id);
		}
		auto static_scopes = scopes;
		scopes = saved_scopes;
		scopes.push_back(new_scope);
		consts[index] = node{ make_pair(code.size(),e.size()),"fun" };
		fun_depth.push(scopes.size());
		visit(body);
		emit(LOAD_NULL);
		emit(RETURN);
		fun_depth.pop();
		scopes.pop_back();
		scopes = static_scopes;
		fun_define_s.pop();
		fun_define_scope.pop();
	}
}

void cilly_compiler::visit(ast_node& t) {
	vector<ast_node> e = get<vector<ast_node>>(t.val);
	ast_node& tag = e[0];
	string tag_stat = get<string>(tag.val);
	if(tag_stat=="expr_stat"){
		visit(e[1]);
		emit(POP);
	}
	else if (tag_stat == "print") {
		for(auto &_: get<vector<ast_node>>(e[1].val)) {
			visit(_);
			emit(PRINT_ITEM);
		}
		emit(PRINT_NEWLINE);
	}
	else if (tag_stat == "if") {
		visit(e[1]);
		int addr1 = emit(JMP_FALSE, -1);
		visit(e[2]);
		if(e.size() == 4){
			int addr2 = emit(JMP, -1);
			backpatch(addr1, code.size());
			visit(e[3]);
			backpatch(addr2, code.size());
		}
		else {
			backpatch(addr1, code.size());
		}
	}
	else if (tag_stat == "while") {
		int loop_start = code.size();
		while_s.push({ vector<int>{},vector<int>{} });
		while_st_addrdep.push({loop_start,scopes.size()});
		visit(e[1]);
		int addr = emit(JMP_FALSE, -1);
		visit(e[2]);
		int before_jmp = code.size();
		emit(JMP, loop_start);
		int after_while = code.size();
		backpatch(addr, after_while);
		auto &p = while_s.top();
		for (int _ : p.first) {
			backpatch(_, after_while);
		}
		for (int _ : p.second) {
			backpatch(_, before_jmp);
		}
		while_s.pop();
		while_st_addrdep.pop();
	}
	else if (tag_stat == "break") {
		auto & p = while_s.top();
		int q = while_st_addrdep.top().second;
		for (int i = scopes.size(); i > q; i--) {
			emit(LEAVE_SCOPE);
		}
		int addr = emit(JMP, -1);
		p.first.push_back(addr);
	}
	else if (tag_stat == "continue") {
		auto& p = while_s.top();
		int q = while_st_addrdep.top().second;
		for (int i = scopes.size(); i > q; i--) {
			emit(LEAVE_SCOPE);
		}
		int addr = emit(JMP, -1);
		p.second.push_back(addr);
	}
	else if (tag_stat == "define") {
		int index = define_name(e[1]);
		visit(e[2]);
		emit(STORE_VAR, 0, index);
	}
	else if (tag_stat == "assign") {
		auto [i, j] = look_var_name(e[1]);
		visit(e[2]);
		emit(STORE_VAR, i, j);
	}
	else if (tag_stat == "block" || tag_stat=="program") {
		auto p = make_shared<vector<string>>();
		scopes.push_back(p);
		int addr = emit(ENTER_SCOPE, -1);
		for (auto& _ : get<vector<ast_node>>(e[1].val)) {
			visit(_);
		}
		emit(LEAVE_SCOPE);
		backpatch(addr,p->size());
		scopes.pop_back();
	}
	else if (tag_stat == "unary") {
		visit(e[2]);
		string c = get<string>(e[1].val);
		if (c == "-")emit(UNARY_NEG);
		if (c == "!")emit(UNARY_NOT);
	}
	else if (tag_stat == "binary") {
		string op = get<string>(e[1].val);
		if (op == "&&") {
			visit(e[2]);
			int addr1 = emit(JMP_FALSE, -1);
			visit(e[3]);
			int addr2 = emit(JMP, -1);
			backpatch(addr1, code.size());
			emit(LOAD_FALSE);
			backpatch(addr2, code.size());
			return;
		}
		else if (op == "||") {
			visit(e[2]);
			int addr1 = emit(JMP_TRUE, -1);
			visit(e[3]);
			int addr2 = emit(JMP, -1);
			backpatch(addr1, code.size());
			emit(LOAD_TRUE);
			backpatch(addr2, code.size());
			return;
		}
		else if (op == ">" || op=="<=") {
			visit(e[3]);
			visit(e[2]);
			if (op == ">")emit(BINARY_LT);
			else emit(BINARY_GE);
			return;
		}
		visit(e[2]);
		visit(e[3]);
		if (op == "+")emit(BINARY_ADD);
		else if (op == "-")emit(BINARY_SUB);
		else if (op == "*")emit(BINARY_MUL);
		else if (op == "/")emit(BINARY_DIV);
		else if (op == "%")emit(BINARY_MOD);
		else if (op == "^")emit(BINARY_POW);
		else if (op == "==")emit(BINARY_EQ);
		else if (op == "!=")emit(BINARY_NE);
		else if (op == "<")emit(BINARY_LT);
		else if (op == ">=")emit(BINARY_GE);
	}
	else if (tag_stat == "id") {
		auto [i, j] = look_var_name(e[1]);
		emit(LOAD_VAR, i, j);
	}
	else if (tag_stat == "fun") {
		int addr1=emit(LOAD_CONST, -1);
		int index = add_const(t);
		fun_define_s.push({e[1],e[2]});
		fun_define_scope.push({index,scopes});

		backpatch(addr1, index);
	}
	else if (tag_stat == "return") {
		int dep = fun_depth.top();
		if (e.size() == 1) {
			emit(LOAD_NULL);
		}
		else visit(e[1]);
		for (int i = scopes.size(); i > dep; i--) {
			emit(LEAVE_SCOPE);
		}
		emit(RETURN);
	}
	else if (tag_stat == "call") {
		visit(e[1]);
		for (auto& _ : get<vector<ast_node>>(e[2].val)) {
			visit(_);
		}
		emit(CALL, get<vector<ast_node>>(e[2].val).size());
	}
	else if (tag_stat == "int") {
		int index = add_const(t);
		emit(LOAD_CONST, index);
	}
	else if (tag_stat == "double") {
		int index = add_const(t);
		emit(LOAD_CONST, index);
	}
	else if (tag_stat == "string") {
		int index = add_const(t);
		emit(LOAD_CONST, index);
	}
	else if (tag_stat == "true") {
		emit(LOAD_TRUE);
	}
	else if (tag_stat == "false") {
		emit(LOAD_FALSE);
	}
	else if (tag_stat == "null") {
		emit(LOAD_NULL);
	}
}

int cilly_compiler::define_name(ast_node& t){
	string c = get<string>(t.val);
	auto& scope = scopes.back();
	scope->push_back(c);
	return scope->size() - 1;
}

pair<int,int> cilly_compiler::look_var_name(ast_node& t) {
	string c = get<string>(t.val);
	for (int i = scopes.size() - 1; i >= 0; i--) {
		for (int j = 0; j < scopes[i]->size(); j++) {
			if ((*scopes[i])[j] == c)return { scopes.size() - i - 1,j };
		}
	}
}