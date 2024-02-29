#ifndef IOT_TIME_H
#define IOT_TIME_H

#include <string>

using namespace std;

typedef struct Time{
	int year, month, day;
	int hour, minute, second;
} Time;

int get_minute_and_second(Time t);
Time make_next_day(Time t);
Time make_time(int y, int m, int d, int h, int mi, int s);
int calc_time_diff(Time a, Time b);
Time string_to_time(string s);
bool compare_time(Time a, Time b);
string time_to_string(Time t);
int time_to_decimal(Time t);

#endif // #ifndef IOT_TIME_H