#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
#include <chrono>
#include <math.h>
#include <map>
#include "iot_func.h"
#include "ConfigParser.h"

using namespace std;
using namespace chrono;

/* binary trie root */
extern ods::BinaryTrie1<unsigned long long, int> bt;


int main(int argc, char* argv[]) {

	if(argc != 1)
		cout << "Execute Index File : ./Index" << endl;

	CConfigParser config_path("../config.txt");
	map<string, string> config =  config_path.GetConfig();

	system_clock::time_point start, end;
	duration<double> sec;

	start = system_clock::now();
		
	bt = make_index_trie(config);

	end = system_clock::now();
	sec = end - start;
	cout << "Total make_trie time: " << sec.count() << endl;
	
	/* index to binary file */
	start = system_clock::now();
	bt.IdxToFile();
	end = system_clock::now();
	sec = end - start;
	cout << "Index to file elapsed time: " << sec.count() << endl;

	//REST Server
	http_listener listener(U(config["Web_IP"]));

	listener.support(methods::POST, handle_post);
	try{
		listener
			.open()
			.then([&listener]() {cout << "Index Server On\n\n"; })
			.wait();
		while (true);
	} catch (exception const &e){
		wcout << e.what() << endl;
	}
}
