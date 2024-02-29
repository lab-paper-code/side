#include "cover.h"
#include <bitset>

const int S2_LEVEL = 20;
const int MAXCELL = 10000;
const int VECTOR_RESERVE = 100000000;

/* binary trie root */
extern ods::BinaryTrie1<unsigned long long, int> bt;



// get s2 cells in query region
void get_cells_from_cover(S2CellUnion covering, int start_date, int end_date, map<int, vector<unsigned long long>> *result){	
	
	map<int, vector<unsigned long long>> temp;

	unsigned long long start = start_date;
	unsigned long long end = end_date;

	unsigned long long number_of_cells = covering.size();

	cout << "number_of_cells: " << number_of_cells << endl;
	map<int, vector<unsigned long long>> levelMap; // S2 Cell level map

	// Make Searching map
	for(unsigned long long i = 0; i < number_of_cells; i++){
		
		unsigned long long s2_search_id = covering.cell_id(i).id();
		int level = covering.cell_id(i).level();

		if (levelMap.find(level) == levelMap.end()) {
			// If level doesn't exist, create a new entry
			levelMap[level] = std::vector<unsigned long long>{s2_search_id};
		} else {
			// If it exists, add the value to the existing vector
			levelMap[level].push_back(s2_search_id);
		}
	}


	// find answer node
	myFind(levelMap, start, end, &bt, temp);


	// Access and copy the content
    for (const auto& pair : temp) {
        int level = pair.first;
        const std::vector<unsigned long long>& temp_tsc = pair.second;

		(*result)[level] = temp_tsc;
    }

	// CLEAR the map
	temp.clear();
}

/* type 0: circle */
void get_radius_to_s2_list(double* ca, double rad, int start_date, int end_date, map<int, vector<unsigned long long>> *ret){
	system_clock::time_point start, end;
	duration<double> sec;
	S2Point center;
	S1Angle radius;

	center = S2CellId(S2LatLng::FromDegrees(ca[0], ca[1])).ToPoint();
	radius = S2Earth::ToAngle(util::units::Kilometers(rad));

	S2RegionCoverer::Options options;
	options.set_max_level(S2_LEVEL);
	options.set_max_cells(MAXCELL);
	S2RegionCoverer coverer(options);

	S2Cap cap(center, radius);
	S2CellUnion covering = coverer.GetCovering(cap);

	start = system_clock::now();
	get_cells_from_cover(covering, start_date, end_date, ret);
	end = system_clock::now();
	sec = end - start;
	cout << "Search on Index elapsed time: " << sec.count() << " (s)" << endl;
}

/* type 1: rectangle */
void get_rect_to_s2_list(double* ca, int start_date, int end_date, map<int, vector<unsigned long long>> *ret){	//make rectangle that include two points in web paremeter
	system_clock::time_point start, end;
	duration<double> sec;

	S2RegionCoverer::Options options;
	options.set_max_level(S2_LEVEL);
	options.set_max_cells(MAXCELL);
	S2RegionCoverer coverer(options);

	S2LatLngRect rect = S2LatLngRect::FromPointPair(S2LatLng::FromDegrees(ca[0], ca[1]),S2LatLng::FromDegrees(ca[2], ca[3]));

	// clock start
	start = system_clock::now();
	S2CellUnion covering = coverer.GetCovering(rect);
	get_cells_from_cover(covering, start_date, end_date, ret);
	// clock end
	end = system_clock::now();
	sec = end - start;

	cout << "Search on Index elapsed time: " << sec.count() << " (s)" << endl;
}

/* type 2: polygon*/
void get_polygon_to_s2_list(double* ca, int ca_size, int start_date, int end_date, map<int, vector<unsigned long long>> *ret){
	system_clock::time_point start, end;
	duration<double> sec;
	vector <S2Point> polygon_point;
	
	for(auto i=0; i<ca_size; i+=2){
		polygon_point.push_back(S2CellId(S2LatLng::FromDegrees(ca[i], ca[i+1])).ToPoint());
	}
	S2RegionCoverer::Options options;
	options.set_max_level(S2_LEVEL);
	options.set_max_cells(MAXCELL);
	S2RegionCoverer coverer(options);

	S2Loop* loops = new S2Loop(polygon_point, S2Debug::DISABLE);
    loops->Normalize();

	S2CellUnion covering = coverer.GetCovering(*loops);
	polygon_point.clear();

	start = system_clock::now();
	get_cells_from_cover(covering, start_date, end_date, ret);
	end = system_clock::now();
	sec = end - start;
	cout << "Search on Index elapsed time: " << sec.count() << " (s)" << endl;
}