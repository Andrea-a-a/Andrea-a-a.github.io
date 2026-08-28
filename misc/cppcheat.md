# cpp cheatsheet

### general

` ? : `

### vector

` vector<int> test(n) `

` vector<int> test(n, a) `

` sort(a.begin(), a.end(), greater<int>()) ` or ` sort(a.begin(), a.end(), greater<>()) `

sort(a.begin(), a.end(), greater<long long>());

开了同步的情况下，
cout << ans << '\n';

去重：
sort(vec.begin(), vec.end());
vec.erase(unique(vec.begin(), vec.end()), vec.end());

pair咋用：
vec<pair<int, int>> a;

注意用int进行过程量计算可能会爆

用Point p = {1, 2}初始化结构体

读入一整行：
string line;
    // 当成功读取到一行时，循环继续；遇到 EOF（文件结束）或流错误时，循环退出
    while (getline(cin, line)) {
        // 处理当前读到的 line
        cout << "读取到: " << line << endl;
}

注意\n！cin会把\n留下，请cin >> n; cin.ignore();

一整行，然后用空格分开:
string s = "hello world cpp";
stringstream ss(s);
string token;
vector<string> tokens;

while (ss >> token) {          // 以 string 类型读取
    tokens.push_back(token);
}
