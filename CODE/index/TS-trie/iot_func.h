#ifndef IOT_FUNC_H
#define IOT_FUNC_H

#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
#include <chrono>
#include <sstream>
#include "bsoncxx/builder/stream/document.hpp"
#include <bsoncxx/json.hpp>
#include <mongocxx/client.hpp>
#include <mongocxx/instance.hpp>
#include <cpprest/http_listener.h>
#include <cpprest/json.h>
#include "BinaryTrie.h"
#include "iot_time.h"
#include "cover.h"

using namespace std;
using namespace chrono;
using namespace web;
using namespace web::http;
using namespace web::http::experimental::listener;
using bsoncxx::builder::stream::finalize;

ods::BinaryTrie1<unsigned long long, int> make_index_trie(map<string, string> config);
void myFind(map<int, vector<unsigned long long>> levelMap, unsigned long long pt_left, unsigned long long pt_right, ods::BinaryTrie1<unsigned long long, int> *btrie,  map<int, vector<unsigned long long>>& ret);
void display_json(json::value const & jvalue,string const & prefix);
void handle_request(http_request request,function<void(json::value const &, json::value &)> action);
void handle_post(http_request request);

#endif // #ifndef IOT_FUNC_H