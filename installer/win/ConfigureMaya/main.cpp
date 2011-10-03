#include <Windows.h>
#include <stdio.h>
#include <string>
#include <iostream>
#include <fstream>
#include "shlobj.h"

bool FileExists( std::string FileName )
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

bool AppendFile( std::string FileName, std::string s )
{
	std::cout << "Attempting to append to file " << FileName;

	FILE * pFile;
	pFile = fopen (FileName.c_str(), "a");
	if (pFile != NULL) {
		fputs (s.c_str(), pFile);
		fclose (pFile);
		return true;
	}

	std::cout << "Failed to append \"" << s << "\" to"  << FileName;
	return false;
}

bool CreateDirectories( std::string FilePath )
{
	std::cout << "Attempting to create file path" << FilePath;
	int ret = SHCreateDirectoryEx(NULL, FilePath.c_str(), NULL);
	if(ret == ERROR_SUCCESS || ret == ERROR_ALREADY_EXISTS || ret == ERROR_FILE_EXISTS){
		return true;
	}else{
		std::cout << FilePath << " creation failed with error code " << ret;
		return false;
	}
}

bool modifyMayaEnvironment( std::string mayaSettingsPath, std::string cadnanoPath, bool add = true )
{
	std::string mayaEnvironmentPath = mayaSettingsPath + "Maya.env";
	return AppendFile( mayaEnvironmentPath, "\nMAYA_PLUG_IN_PATH=" + cadnanoPath + "\n" );
}

bool modifyMayaPluginPrefs( std::string mayaSettingsPath, bool add = true )
{
	std::string mayaPluginsPath = mayaSettingsPath + "prefs\\";

	if ( !CreateDirectories( mayaPluginsPath ) ){
		return false;
	}

	mayaPluginsPath = mayaPluginsPath + "pluginPrefs.mel";

	if( FileExists( mayaPluginsPath ) ){
		return AppendFile( mayaPluginsPath, "\nevalDeferred(\"autoLoadPlugin(\\\"\\\", \\\"spCadNano.py\\\", \\\"spCadNano\\\")\"); \n" );
	}else{
		return AppendFile( mayaPluginsPath, "//Maya Preference 2012 (Release 1)\n//\n//\nevalDeferred(\"autoLoadPlugin(\\\"\\\", \\\"spCadNano.py\\\", \\\"spCadNano\\\")\");\n" );
	}

}

int main(int argc, char* argv[])
{
	if( argc != 4 ){
		std::cout << "Incorrect number of arguments";
		MessageBox(NULL, "Incorrect number of arguments", NULL, NULL);
		return -1;
	}

	std::string mayaPath(argv[1]);
	std::string cadnanoPath(argv[2]);
	std::string platform(argv[3]);

	char buffer[250];
	ExpandEnvironmentStrings("%USERPROFILE%",buffer,250);
	std::string userProfile = buffer;
	std::string mayaSettingsPath = userProfile + "\\Documents\\maya\\2012";

	if( platform.compare("x64") == 0 )
	{
		mayaSettingsPath += "-x64\\";
	}else{
		mayaSettingsPath += "\\";
	}

	bool res = true;

	res &= CreateDirectories( mayaSettingsPath );
	res &= modifyMayaEnvironment(mayaSettingsPath, cadnanoPath);
	res &= modifyMayaPluginPrefs(mayaSettingsPath);

	SendMessageTimeout( HWND_BROADCAST, WM_SETTINGCHANGE, NULL, (LPARAM)"Environment", NULL, NULL, NULL);

	if( !res ){
		MessageBox( NULL, "CadNano plugin for Autodesk Maya configurations failed", NULL, NULL);
		return -1;
	}else{
		return 0;
	}
}
