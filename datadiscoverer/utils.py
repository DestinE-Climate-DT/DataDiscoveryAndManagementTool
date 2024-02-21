"""
This module contains certain utitlity functions like for fetching the files from a given location on disk etc.
"""

#Standard modules
import os
import sys
import glob
from pathlib import Path
import importlib
    
#Local modules
try:
    from .config import configDatadiscoverer
except:
    print(sys.exc_info())
    print(f"Module 'config' import error in {__file__}")


def getAppSrcFileList(app,src,esm,srcExtList):
    """Create a list of files produced by the app, for a given file type.

    Search the app data directory and create a list of all the files of a given file type like netcdf, jpeg etc.

    Args:
            app : Application Name.
            src : Source or file type name like netcdf, image, text.
            esm : Earth system model Name.
            srcExtList: The file suffix like *.nc, *.jpg, *.pdf, *.txt, *.csv.
    Returns: 
            srcFileList - a list.
    """
    
    srcFileList = []
    
    localconfig = configDatadiscoverer.activeConfig
    appDataPath = localconfig.getDataPath()
    appDataSrcPath = Path(os.path.join(appDataPath,app))
    
    try:
        os.path.exists(appDataSrcPath)
    except:
        print(sys.exc_info())

    print(f"\t{appDataSrcPath} {src}")
    for srcExt in srcExtList:
        print(f"\t\t{srcExt}")
        globArg = os.path.join(appDataSrcPath,"**",f"{srcExt}")
        srcFileList += glob.glob(globArg,recursive=True)
    
    esmList = list(filter(lambda k: esm in k, srcFileList))
    
    return esmList