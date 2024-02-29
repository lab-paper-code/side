#include "iot_time.h"

static short year_to_day[] = {366, 365, 365, 365, 366, 365, 365, 365, 366, 365,
					   365, 365, 366, 365, 365, 365, 366, 365, 365, 365, 
					   366, 365, 365, 365, 366, 365, 365, 365, 366, 365, 
					   365, 365, 366, 365, 365, 365, 366, 365, 365, 365, 
					   366, 365, 365, 365, 366, 365, 365, 365, 366, 365,
					   365, 365, 366, 365, 365, 365, 366, 365, 365, 365, 
					   366, 365, 365, 365};
					   
static short month_to_day[] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};

int get_minute_and_second(Time t){
	return (t.minute * 60 + t.second);
}

Time make_next_day(Time t){
	t.day++;
	if(month_to_day[t.month-1] < t.day){
		t.day = 1;
		t.month++;
	}
	if(t.month > 12){
		t.month = 1;
		t.year++;
	}
	return t;
}

int time_to_decimal(Time t) {
	int ret;
	
	int y = t.year << 14;
	int m = t.month << 10;
	int d = t.day << 5;
	int h = t.hour;

	ret = y + m + d + h;

	return ret;
}

Time make_time(int y, int m, int d, int h, int mi, int s){
	Time t;
	t.year = y;
	t.month = m;
	t.day = d;
	t.hour = h;
	t.minute = mi;
	t.second = s;
	
	return t;
}

Time string_to_time(string s){
	Time ret;
	
	ret.year = stoi(s.substr(0, 4)) - 2000;
	ret.month = stoi(s.substr(5, 2));
	ret.day = stoi(s.substr(8, 2));
	ret.hour = stoi(s.substr(s.length() - 8, 2));
	ret.minute = stoi(s.substr(s.length() - 5, 2));
	ret.second = stoi(s.substr(s.length() - 2, 2));
	
	return ret;
}

string time_to_string(Time t){
	string s;
	int temp_year = t.year + 2000;
	s += to_string(temp_year)+'-';
	
	if(t.month < 10) s += '0';
	s += to_string(t.month)+'-';
	
	if(t.day < 10) s += '0';
	s += to_string(t.day)+" ";
	
	if(t.hour < 10) s += '0';
	s += to_string(t.hour)+':';
	
	if(t.minute < 10) s += '0';
	s += to_string(t.minute)+':';
	
	if(t.second < 10) s += '0';
	s += to_string(t.second);
	
	return s;		
}

bool compare_time(Time a, Time b){
	if(a.year != b.year){
		return a.year < b.year;
	}
	else{
		if(a.month != b.month){
			return a.month < b.month;
		}
		else{
			if(a.day != b.day){
				return a.day < b.day;
			}
			else{
				if(a.hour != b.hour){
					return a.hour < b.hour;
				}
				else{
					if(a.minute != b.minute){
						return a.minute < b.minute;
					}
					else{
						return a.second < b.second;
					}
				}
			}
		}
	}
}

int calc_time_diff(Time a, Time b){
	int diff_day = 0;
	
	for(int i = b.year; i > a.year; i--){
		diff_day += year_to_day[i];
	}
	
	for(int i = 0; i < b.month; i++){
		if(i == 1 && year_to_day[b.year] == 366){
			diff_day++;
		}
		diff_day += month_to_day[i];
	}
	
	for(int i = 0; i < a.month; i++){
		if(i == 1 && year_to_day[a.year] == 366){
			diff_day--;
		}
		diff_day -= month_to_day[i];
	}
	
	diff_day += (b.day - a.day);
	b.hour += (diff_day*24);
	
	return (b.hour * 3600 + b.minute * 60 + b.second) - (a.hour * 3600 + a.minute * 60 + a.second);
}