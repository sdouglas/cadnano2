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
	NSAutoreleasePool* ar = [[NSAutoreleasePool alloc] init];
	NSString* resourceFolder = [[NSBundle mainBundle] resourcePath];
	NSString* cadnanoModuleFolder = [resourceFolder stringByAppendingPathComponent:@"cadnano2"];
	const char* d = [cadnanoModuleFolder UTF8String];
	chdir(d);
	
	Py_Initialize();
	PySys_SetArgv(argc, argv);
	
	PyObject* mainModule = PyImport_AddModule("__main__");
	PyObject* mainModuleDict = PyModule_GetDict(mainModule);
	
	FILE* mainFile = fopen("main.py", "r");
	if (mainFile != NULL)
		PyRun_File(mainFile, "main.py", Py_file_input, mainModuleDict, mainModuleDict);
	else
		fprintf(stderr, "Could not locate main.py in %s!\n", d);
	
	Py_Finalize();
	[ar release];
	return 0;
}
