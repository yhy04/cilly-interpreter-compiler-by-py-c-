#include<iostream>
#include"cilly_lexer.h"
#include<memory>
#include"cilly_parser.h"
#include"cilly_vm_compiler.h"
using namespace std;

ostream& operator<<(ostream& os, const token& tk) {
	os << tk.first << ": ";  // 先输出 key
	visit([&os](auto&& arg) {  // 再根据 variant 类型输出 value
		using T = decay_t<decltype(arg)>;
		if constexpr (is_same_v<T, monostate>) {
			os << "None" << '\t';
		}
		else if constexpr (is_same_v<T, int>) {
			os << arg << '\t';
		}
		else if constexpr (is_same_v<T, double>) {
			os << arg << '\t';
		}
		else if constexpr (is_same_v<T, std::string>) {
			os << '\"' << arg << "\"" << '\t';
		}
		}, tk.second);
	return os;
}
ostream& operator<<(ostream& os, const ast_node& node) {
    visit([&os](const auto& arg) {
        using T = decay_t<decltype(arg)>;
        if constexpr (is_same_v<T, monostate>) {
            os << "null";
        }
        else if constexpr (is_same_v<T, int>) {
            os << arg;
        }
        else if constexpr (is_same_v<T, double>) {
            os << arg;
        }
        else if constexpr (is_same_v<T, string>) {
            os << "\"" << arg << "\"";
        }
        else if constexpr (is_same_v<T, vector<ast_node>>) {
            cout << "[";
            for (const auto node : arg) {
                cout << node << ",";
            }
            cout << "]";
        }
        }, node.val);
    return os;
}
ostream& operator<<(ostream& os, const node& nd) {
    os << nd.tag<<' ';
    visit([&os](const auto& arg) {
        using T = decay_t<decltype(arg)>;
        if constexpr (is_same_v<T, monostate>) {
            os << "null";
        }
        else if constexpr (is_same_v<T, int>) {
            os << arg;
        }
        else if constexpr (is_same_v<T, double>) {
            os << arg;
        }
        else if constexpr (is_same_v<T, string>) {
            os << "\"" << arg << "\"";
        }
        else if constexpr (is_same_v<T, bool>) {
            os << "\"" << arg << "\"";
        }
        else if constexpr (is_same_v<T, pair<int,int>>) {
            os << "\"" << arg.first << ", " << arg.second << "\"";
        }
        else if constexpr (is_same_v<T, pair<int, vector<shared_ptr<vector<node>>>>>) {
            cout << "[";
            cout << arg.first<<", ";
            for (const auto node : arg.second) {
                cout << node << ",";
            }
            cout << "]";
        }
        }, nd.val);
    return os;
}
int main() {
	string code = "var odd = fun(n){if (n == 0)return false;else return even(n - 1); }; var even = fun(n) {if (n == 0) return true;else return odd(n - 1);};print(even(3), odd(3)); ";
     //code = "var f=fun(n){print(n);};f(10);";
     //code = "print(\"abc\");print(3);3;";
    //code = "var i=1;var j = 2;if (i == 2)print(3); else print(4); ";

    cilly_lexer lexer(code);  
    for (auto& i : lexer.get_tokens())
        cout << i<<' ';
    cout << "\n\n";
	
    cilly_parser parser(lexer.get_tokens());
    cout << parser.get_ast() << "\n\n";
    
    cilly_compiler compiler(parser.get_ast());
    //for (auto _ : compiler.get_code())cout << _<<' ';
    //cout << "\n\n";
    for(auto _:compiler.get_consts())cout << _<<' ';
    cout << "\n\n";

    //vector<int> cd{ 13, 2, 1, 0, 6, 0, 0, 1, 1, 6, 0, 1, 5, 0, 1, 1, 2, 16, 1, 7, 5, 0, 0, 1, 2, 16, 1, 7, 8, 14, 0, 13, 0, 5, 1, 0, 1, 3, 117, 11, 46, 3, 14, 17, 9, 59, 5, 2, 0, 5, 1, 0, 1, 4, 112, 16, 1, 14, 17, 14, 2, 17, 13, 0, 5, 1, 0, 1, 3, 117, 11, 77, 4, 14, 17, 9, 90, 5, 2, 1, 5, 1, 0, 1, 4, 112, 16, 1, 14, 17, 14, 2, 17 };
    ////cd = { 13, 1, 1, 0, 6, 0, 0, 5, 0, 0, 1, 1, 16, 1, 12, 14, 0, 13, 0, 5, 1, 0, 7, 8, 14, 2, 17
    ////};
    //vector<node> cts{ {make_pair(62,1),"fun"},{make_pair(31,1),"fun"}, {3,"int"},{0,"int"},{1,"int"}};
    cilly_vm vm(compiler.get_code(), compiler.get_consts());
}