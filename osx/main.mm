//
//  main.m
//  cadnano2
//
//  Created by Jonathan deWerd on 7/2/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <Cocoa/Cocoa.h>
#import "Python.h"
#import <stdio.h>

int main(int argc, char *argv[]) {
	chdir("/l/c");
	Py_Initialize();
	PySys_SetArgv(argc, argv);
	
	PyObject* mainModule = PyImport_AddModule("__main__");
	PyObject* mainModuleDict = PyModule_GetDict(mainModule);
	
	FILE* mainFile = fopen("main.py", "r");
	PyRun_File(mainFile, "main.py", Py_file_input, mainModuleDict, mainModuleDict);
	
	Py_Finalize();
	return 0;
}
