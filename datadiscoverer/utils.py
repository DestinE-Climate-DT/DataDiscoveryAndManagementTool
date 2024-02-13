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

    
def getAppSrcFileList(app,src,srcExtList):
    """Create a list of files produced by the app, for a given file type.

    Search the app data directory and create a list of all the files of a given file type like netcdf, jpeg etc.

    Args:
            app : Application Name.
            src : Source or file type name like netcdf, image, text.
            srcExt: The file suffix like *.nc, *.jpg, *.pdf, *.txt, *.csv.
    Returns: 
            srcFileList - a list.
    """
    
    srcFileList = []
    
    localconfig = configDatadiscoverer.activeConfig
    appDataPath = localconfig.getdatadiscovererDataPath()
    root=Path(os.path.join(appDataPath,app))
    
    try:
        os.path.exists(root)
    except:
        print(sys.exc_info())

    for srcExt in srcExtList:
        print(f"{root} {src} {srcExt}")
        globArg = os.path.join(root,f"{srcExt}")
        print(globArg)

        srcFileList += glob.glob(globArg)
    
    return srcFileList