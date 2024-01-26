import os
import glob
from pathlib import Path

from masterStructure import *

def getAppSrcFileList(app,src,srcExt):
    """Create a list of files produced by the app, for a given file type.

    Search the app data directory and create a list of all the files of a given file type like netcdf, jpeg etc.

    Args:
            app : Application Name.
            src : Source or file type name like netcdf, image, text.
            srcExt: The file suffix like *.nc, *.jpg,*.txt.
    Returns: 
            srcFileList - a list.
    """
    
    srcFileList = []
    
    root=Path(os.path.join(appDataPath,app))
    print(f"{root} {src} {srcExt}")
    
    globArg = os.path.join(root,f"{srcExt}")
    print(globArg)
    
    srcFileList = glob.glob(globArg)
    
    print(srcFileList)
    return srcFileList