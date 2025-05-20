#include "PluginManager.h"
#include <stdio.h>
#include <stdlib.h>
#include "SpanFilterPlugin.h"

void SpanFilterPlugin::input(std::string file) {
 inputfile = file;
 std::ifstream ifile(inputfile.c_str(), std::ios::in);
 while (!ifile.eof()) {
   std::string key, value;
   ifile >> key;
   ifile >> value;
   parameters[key] = value;
 }
}

void SpanFilterPlugin::run() {

}

void SpanFilterPlugin::output(std::string file) {
   std::string command = "export OLDPATH=${PYTHONPATH}; ";
   command += "export PYTHONPATH=/usr/local/lib64/python3.9/site-packages/:${PYTHONPATH}; ";
   command += "python3.9 plugins/SpanFilter/runSpanFilter.py ";
   command += parameters["sqldatabase"] + " ";
   command += parameters["pdbinput"] + " ";
   command += PluginManager::addPrefix(parameters["csvfile"]) + " ";
   command += parameters["span"] + " ";
   command += file + "; ";
   command += "export PYTHONPATH=${OLDPATH}";
 std::cout << command << std::endl;

 system(command.c_str());
}

PluginProxy<SpanFilterPlugin> SpanFilterPluginProxy = PluginProxy<SpanFilterPlugin>("SpanFilter", PluginManager::getInstance());
