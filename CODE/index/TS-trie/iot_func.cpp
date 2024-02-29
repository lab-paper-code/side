#include "iot_func.h"
#include <bitset>
#include <map>

/* binary trie root */
ods::BinaryTrie1<unsigned long long, int> bt;
auto members = bsoncxx::builder::basic::array{};

bsoncxx::builder::stream::document document{};
mongocxx::instance inst{};
mongocxx::options::find opts;
const unsigned long long ADD = (unsigned long long)1 << 44;
const int temp_w = 20;
const int spat_w = 34;

ods::BinaryTrie1<unsigned long long, int> make_index_trie(map<string, string> config){	//connect to mongodb and find all documents, make index tree

	ods::BinaryTrie1<unsigned long long, int> ret;

	system_clock::time_point start, end;
	duration<double> sec;

	// connect to mongodb
	stringstream conn_addr;
	conn_addr << "mongodb://"<<config["ID"]<<":"<<config["PW"]<<"@"<<config["Index_IP"];
	string conn_addr_s = conn_addr.str();
	cout << conn_addr_s <<endl;

    mongocxx::client conn{mongocxx::uri{conn_addr_s}};

    bsoncxx::builder::stream::document document{};

    auto db = conn[config["DB_name"]];
    auto collection = db[config["Index_name"]];;

	mongocxx::options::find opts;
	/* TSC_ID */
	bsoncxx::document::value checker = document << "TSC_ID" << 1 << "_id" << 0 << finalize;
	opts.projection(checker.view());

	/* get all data from MongoDB */
	start = system_clock::now();
	auto cursor = collection.find({}, opts);
	end = system_clock::now();
	sec = end - start;
	cout << "Query to MongoDB elapsed time: " << sec.count() << endl;

	/* push to vector */
	start = system_clock::now();
	vector <unsigned long long> stpt_vector;
	unsigned long long stpt_temp;

	// get all TSC_ID from mongodb
	for(auto&& doc : cursor){
		/* old: ST_PT, new: TSC_ID */
		stpt_temp = doc["TSC_ID"].get_int64();
		stpt_vector.push_back(stpt_temp);
	}

	end = system_clock::now();
	sec = end - start;
	cout << "Push data to vector elapsed time: " << sec.count() << endl;
	cout << "	# of data: " << stpt_vector.size() << endl;

	sort(stpt_vector.begin(), stpt_vector.end());
	stpt_vector.resize( unique(stpt_vector.begin(), stpt_vector.end()) - stpt_vector.begin() );
	
	cout << "	# of Leaf nodes: " << stpt_vector.size() << endl;

	/* make index trie */
	start = system_clock::now();
	for (unsigned i = 0; i < stpt_vector.size(); i++) {
		// add node in trie
		ret.add(stpt_vector[i]);
	}
	end = system_clock::now();
	sec = end - start;

	cout << "	# of all nodes: " << ret.arr.size() << endl;

	cout << "Create binaryTrie elapsed time: " << sec.count() << endl;
	
	return ret;
}

// find answer node in trie
void myFind(map<int, vector<unsigned long long>> levelMap, unsigned long long pt_left, unsigned long long pt_right, ods::BinaryTrie1<unsigned long long, int> *btrie, map<int, vector<unsigned long long>>& ret) {
	long long temp_node, node;

	// find temporal bit find
	temp_node = btrie->temp_find(pt_left);
	while (temp_node != btrie->POINTER_NULL_INT && btrie->arr[temp_node].x < pt_right) {

    	for (const auto& level_s2_pair : levelMap) {
			int level = level_s2_pair.first;
			const vector<unsigned long long>& s2_values = level_s2_pair.second;

			for (unsigned j = 0; j < s2_values.size(); j++){
			// find spatial bit find

				node = btrie->spat_find(s2_values[j], level, temp_node);
				if (node != btrie->POINTER_NULL_INT)
				{
					if (ret.find(level) == ret.end()) {
						// If level doesn't exist, create a new entry -> make TS and add it
						ret[level] = vector<unsigned long long>{(btrie->arr[temp_node].x << 44) + (s2_values[j] >> 20)};
					} else {
						// If it exists, add the value to the existing vector
						ret[level].push_back((btrie->arr[temp_node].x << 44) + (s2_values[j] >> 20));
					}
				}
			}
    	}
		// jump to next temporal node
		temp_node = btrie->arr[temp_node].jump;
	}



	// eliminate redundant
    for (auto& pair : ret) {
        std::vector<unsigned long long>& vec = pair.second;

        std::sort(vec.begin(), vec.end()); // sort
        vec.erase(std::unique(vec.begin(), vec.end()), vec.end());
    }

}

void display_json(
   json::value const & jvalue,
   string const & prefix){
   cout << prefix << jvalue.serialize() << endl;
}

void handle_request(
   http_request request,
   function<void(json::value const &, json::value &)> action)
{
   auto answer = json::value::object();
   request
      .extract_json()
      .then([&answer, &action](pplx::task<json::value> task) {
         try
         {
            auto const & jvalue = task.get();
            display_json(jvalue, "Received json: ");
 
            if (!jvalue.is_null())
            {
               action(jvalue, answer);
            }
         }
         catch (http_exception const & e)
         {
            cout << e.what() << endl;
         }
      })
      .wait();
 
   //display_json(answer, "S: ");
   request.reply(status_codes::OK, answer);
}

void handle_post(http_request request)	//get parameter from web, 
{
	handle_request(request,[](json::value const & jvalue, json::value & answer){
		map<int, vector<unsigned long long>> Range_S2id;

		json::value type = jvalue.at(U("type"));
		json::value radius;
		json::value coordinates = jvalue.at(U("coordinates"));
		json::value time = jvalue.at(U("time"));

		int tp = type.as_integer();

		double rad;

		auto c = coordinates.as_array();
		double ca[c.size()];
		for(unsigned i=0; i<c.size(); i++){
			ca[i] = c[i].as_double();
		}

		auto tm = time.as_array();
		int tma[tm.size()];
		for(unsigned i=0; i<tm.size(); i++){
			tma[i] = tm[i].as_integer();
		}
		unsigned long long start_date = time_to_decimal(make_time(tma[0], tma[1], tma[2], tma[3], 0, 0));
		unsigned long long end_date = time_to_decimal(make_time(tma[4], tma[5], tma[6], tma[7], 0, 0));
	
		//search part with query type checking 
		if(tp == 0){ // circle
			radius = jvalue.at(U("radius"));
			rad = radius.as_double();
			get_radius_to_s2_list(ca, rad, start_date, end_date, &Range_S2id);
		}else if(tp == 1){ // rectangle
			get_rect_to_s2_list(ca, start_date, end_date, &Range_S2id);
		}else if(tp == 2){ // polygon
			get_polygon_to_s2_list(ca, c.size(), start_date, end_date, &Range_S2id);
		}



		// Separate the keys and values into separate vectors
		vector<int> level_ts;
		vector<int> length_ts;
		vector<unsigned long long> ts_val;

		int sum_of_length = 0;
		vector<vector<unsigned long long>> values;
		for (const auto& pair : Range_S2id) {
			level_ts.push_back(pair.first);
			values.push_back(pair.second);
			length_ts.push_back((pair.second).size());
			sum_of_length += (pair.second).size();
		}

		// Combine all values into a single vector
		for (const auto& valueVector : values) {
			ts_val.insert(ts_val.end(), valueVector.begin(), valueVector.end());
		}


		// print the cell count
		cout << "	# of results: " << sum_of_length << endl;


		json::value level = json::value::array(level_ts.size());
		json::value length = json::value::array(length_ts.size());
		json::value tsc_id = json::value::array(ts_val.size());

		for(unsigned i=0; i<level_ts.size(); i++)
			level.as_array()[i] = json::value(json::value::number(level_ts[i]));
		for(unsigned i=0; i<length_ts.size(); i++)
			length.as_array()[i] = json::value(json::value::number(length_ts[i]));
		for(unsigned i=0; i<ts_val.size(); i++)
			tsc_id.as_array()[i] = json::value(uint64_t(ts_val[i]));


		// Make a answer array
		answer[U("TSC_ID")] = tsc_id;
		answer[U("length")] = length;
		answer[U("level")] = level;
	
	});
}