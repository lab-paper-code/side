#ifndef COVER_H
#define COVER_H

#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>
#include <cmath>
#include <queue>
#include <cstdlib>
#include <math.h>

#include "s2/base/commandlineflags.h"
#include "s2/s2earth.h"
#include "s2/s1chord_angle.h"
#include "s2/s2closest_point_query.h"
#include "s2/s2point_index.h"
#include "s2/s2cap.h"
#include "s2/s2loop.h"
#include "s2/s2region_term_indexer.h"
#include "iot_func.h"

using namespace std;
using namespace chrono;

typedef struct dot{
	double la, lo;
	dot(double _la, double _lo){
		la = _la;
		lo = _lo;
	}
}dot;

const unsigned long long prefix_s2_id = (unsigned long long)427 << 33; // for 40 bit value
const unsigned long long prefix_stpt = (unsigned long long)427 << 53; // for 64 bit value
void check_chunk(unsigned long long, int, vector <unsigned long long> *);
void get_cells_from_cover(S2CellUnion, int, int, map<int, vector<unsigned long long>> *);
void get_radius_to_s2_list(double*, double, int, int, map<int, vector<unsigned long long>> *);
void get_rect_to_s2_list(double*, int, int, map<int, vector<unsigned long long>> *);
void get_polygon_to_s2_list(double*, int, int, int, map<int, vector<unsigned long long>> *);
#endif // #ifndef COVER_H