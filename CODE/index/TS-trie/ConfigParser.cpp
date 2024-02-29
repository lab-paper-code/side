#include "ConfigParser.h"
#include <fstream>
#include <iostream>
#include <stdexcept>
 
CConfigParser::CConfigParser(const std::string& path)
{
	// read File
	std::ifstream openFile(path);
	if (openFile.is_open()) {
		std::string line;
		while (getline(openFile, line)) {
			std::string delimiter = " = ";
			if (std::string::npos == line.find(delimiter)) delimiter = "=";
			std::string token1 = line.substr(0, line.find(delimiter)); // key
			std::string token2 = line.substr(line.find(delimiter) + delimiter.length(), line.length()); // value
			m_table[token1] = token2;
		}
		openFile.close();
	}
}

std::map<std::string, std::string> CConfigParser::GetConfig()
{
	return m_table;
}