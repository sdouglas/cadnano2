/******************************************************************************

Copyright 2011 Autodesk, Inc.  All rights reserved.

The MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in 
the Software without restriction, including without limitation the rights to 
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do 
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
SOFTWARE.

******************************************************************************/

#include <Windows.h>
#include <stdio.h>
#include <string>
#include <iostream>
#include <fstream>
#include "shlobj.h"
#include <vector>

using std::string;
using std::endl;
using std::vector;
using std::cout;
using std::cerr;
using std::ifstream;

bool FileExists( string FileName )
{
    FILE* fp = NULL;

    fp = fopen( FileName.c_str(), "rb" );
    if( fp != NULL )
    {
        fclose( fp );
        return true;
    } 

    return false;
}

bool WriteFile( string FileName, string s, bool append = false )
{
	cout << "Attempting to write to file " << FileName << endl;

	char* mode = "w";
	if( append ){
		mode = "a";
	}

	FILE * pFile = fopen (FileName.c_str(), mode);
	if (pFile != NULL) {
		fputs (s.c_str(), pFile);
		fclose (pFile);
		cout << "success!" << endl;
		return true;
	}

	cerr << "Failed to write \"" << s << "\" to "  << FileName << endl;
	return false;
}

bool WriteFile( string FileName, vector<string> s, bool append = false )
{
	string out = "";
	for( unsigned int i = 0; i < s.size(); i++) {
		out += s[i] + "\n";
	}

	return WriteFile(FileName, out, append);
}

vector<string> ReadFile( string FileName )
{
	vector<string> lines;
	cout << "Attempting to read to file " << FileName << endl;

	ifstream myfile ( FileName );
	if (myfile.is_open()) {
		while ( myfile.good() ) {
			string line;
			getline (myfile,line);
			if( line != "" ) {
				lines.push_back(line);
			}
		}
		myfile.close();
		cout << "success!" << endl;
	}else{
		cerr << "Failed to read " << FileName << endl;
	}

	return lines;
}

bool CreateDirectories( string FilePath )
{
	cout << "Attempting to create file path " << FilePath << endl;
	int ret = SHCreateDirectoryEx(NULL, FilePath.c_str(), NULL);
	if(ret == ERROR_SUCCESS || ret == ERROR_ALREADY_EXISTS || ret == ERROR_FILE_EXISTS){
		cout << "success!" << endl;
		return true;
	}else{
		cerr << FilePath << " creation failed with error code " << ret << endl;
		return false;
	}
}

bool modifyMayaEnvironment( string mayaSettingsPath, string cadnanoPath, bool add = true )
{
	string mayaEnvironmentPath = mayaSettingsPath + "Maya.env";

	if( add ) {
		if( FileExists(mayaEnvironmentPath) ){

			vector<string> file = ReadFile( mayaEnvironmentPath );
			for (unsigned int i = 0; i < file.size(); i++){
				string line = file[i];
				size_t varfound = line.find("MAYA_PLUG_IN_PATH");
				if( varfound != string::npos ){
					size_t pathfound = line.find( cadnanoPath );
					if( pathfound != string::npos ){
						//cadnano already exists in Maya's MAYA_PLUG_IN_PATH
						return true;
					}else{
						//MAYA_PLUG_IN_PATH is defined, but cadnano is not in it
						file[i] = line + ";" + cadnanoPath;
						return WriteFile( mayaEnvironmentPath, file );
					}
				}
			}
		}

		//MAYA_PLUG_IN_PATH was not found, or the file does not exist
		return WriteFile( mayaEnvironmentPath, "\nMAYA_PLUG_IN_PATH=" + cadnanoPath + "\n", true );

	}else{

		if( FileExists(mayaEnvironmentPath) ){
			vector<string> file = ReadFile( mayaEnvironmentPath );
			for (unsigned int i = 0; i < file.size(); i++){
				string line = file[i];
				size_t varfound = line.find("MAYA_PLUG_IN_PATH");
				size_t pathfound = line.find( cadnanoPath );
				if( varfound != string::npos && pathfound != string::npos ){
					//remove from path
					file[i] = file[i].erase(pathfound, cadnanoPath.length());
					return WriteFile( mayaEnvironmentPath, file );
				}
			}
		}

	}

	return true;
}

bool modifyMayaPluginPrefs( string mayaSettingsPath, bool add = true )
{
	string mayaPrefsPath = mayaSettingsPath + "prefs\\";
	string mayaPluginsPath = mayaPrefsPath + "pluginPrefs.mel";

	if( add ) {

		if ( !CreateDirectories( mayaPrefsPath ) ){
			return false;
		}

		if( !FileExists( mayaPluginsPath ) ){
			//The header is very important, Maya will not load this file unless the header is there
			return WriteFile( mayaPluginsPath, "//Maya Preference 2012 (Release 1)\n//\n//\nevalDeferred(\"autoLoadPlugin(\\\"\\\", \\\"spCadNano.py\\\", \\\"spCadNano\\\")\");\n" );
		}else{
			vector<string> file = ReadFile( mayaPluginsPath );
			for (unsigned int i = 0; i < file.size(); i++){
				string line = file[i];
				size_t cmdfound = line.find("autoLoadPlugin");
				size_t pluginfound = line.find( "spCadNano" );
				if( cmdfound != string::npos && pluginfound != string::npos ){
					return true;
				}
			}
			return WriteFile( mayaPluginsPath, "\nevalDeferred(\"autoLoadPlugin(\\\"\\\", \\\"spCadNano.py\\\", \\\"spCadNano\\\")\"); \n", true );		
		}

	}else{

		if( FileExists( mayaPluginsPath ) ){
			vector<string> file = ReadFile( mayaPluginsPath );
			for (unsigned int i = 0; i < file.size(); i++){
				string line = file[i];
				size_t cmdfound = line.find("autoLoadPlugin");
				size_t pluginfound = line.find( "spCadNano" );
				if( cmdfound != string::npos && pluginfound != string::npos ){
					file[i] = "";
				}
			}
			return WriteFile( mayaPluginsPath, file );
		}

	}

	return true;
}

string upperCase(string strToConvert)
{
	for(unsigned int i=0;i<strToConvert.length();i++)
	{
		strToConvert[i] = toupper(strToConvert[i]);
	}
	return strToConvert;
}

int main(int argc, char* argv[])
{
	if( argc != 5 ){
		cerr << "Incorrect number of arguments" << endl;
		cerr << "usage: configuremaya /INSTALL <maya_path> <cadnano dir> <(x64|x86)>" << endl;
		MessageBox(NULL, "Incorrect number of arguments", NULL, NULL);
		return -1;
	}

	string appMode(argv[1]);
	appMode = upperCase(appMode);
	string mayaPath(argv[2]);
	string cadnanoPath(argv[3]);
	string platform(argv[4]);

	cout << "Configure Mode: " << appMode << endl;
	cout << "Maya Path: " << mayaPath << endl;
	cout << "CadNano2 Path: " << cadnanoPath << endl;
	cout << "Platform: " << platform << endl;

	bool res = true;

	//Maya Settings by default are stored in
	//x86: %FOLDERID_Documents%\maya\2012
	//x64: %FOLDERID_Documents%\maya\2012-x64
	char szPath[MAX_PATH*2];
	bool success = SHGetSpecialFolderPath( NULL, (LPSTR)szPath, CSIDL_PERSONAL, FALSE );
	if (success) {
		
		string userProfile( szPath );

		cout << "My Documents folder found at " << userProfile << endl;

		string mayaSettingsPath = userProfile + "\\maya\\2012";

		if( platform.compare("x64") == 0 )
		{
			mayaSettingsPath += "-x64\\";
		}else{
			mayaSettingsPath += "\\";
		}

		cout << "Settings folder at: " << mayaSettingsPath << endl;

		if( appMode == "/INSTALL" ) {
			res &= CreateDirectories( mayaSettingsPath );
			res &= modifyMayaEnvironment(mayaSettingsPath, cadnanoPath);
			res &= modifyMayaPluginPrefs(mayaSettingsPath);
		}else if( appMode == "/UNINSTALL" || appMode == "/ROLLBACK" ){
			res &= modifyMayaEnvironment(mayaSettingsPath, cadnanoPath, false);
			res &= modifyMayaPluginPrefs(mayaSettingsPath, false);
		}else{
			cout << "Invalid Configure Mode." << endl;
			res &= false;
		}
	}else{
		cerr << "My Documents folder could not be retrieved." << endl;
		res = false;
	}

	cout << "Updating Environment." << endl;

	//Declare environment variable change, since the installer doesn't do this for us
	LRESULT r = SendMessageTimeout(HWND_BROADCAST, WM_SETTINGCHANGE, 0, (LPARAM) "Environment", SMTO_ABORTIFHUNG, 5000, 0);
	if(r == 0){
		MessageBox( NULL, "Updating Environment failed, please restart Windows after installation completes.", NULL, NULL);
	}

	if( res ){
		//MessageBox( NULL, "cadnano plugin for Autodesk Maya configurations succeeded.", NULL, NULL);
		return 0;
	}else{
		MessageBox( NULL, "cadnano plugin for Autodesk Maya configurations failed.", NULL, NULL);
		return -1;
	}
}
