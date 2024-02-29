/*
*		Config File Parsing Class
*/
 
#include <string>
#include <map>
 
class CConfigParser {
public:
	CConfigParser(const std::string& path);
	std::map<std::string, std::string> GetConfig();
 
private:
	std::map<std::string, std::string> m_table;
};