"""
This module contains the core structural elements of the data discovery tool. 
The core structural elements consists of the names of applications, HPC centers, ESMs etc.
The names of the file types produced by each application and their extensions.
Apart from that certain data structures to hold these infos.
"""

#Standard modules
import os
import sys
#from importlib import import_module
import importlib

global appNamesList


appNamesList=['AQUA','EnergyOnShore','EnergyOffShore','FWI','HydroMet','HydroRiver','SPITFIRE','Urban','WISE']
"""list[str]: List of the application names.
Names of the applications using the GSV data and producing respective application specific data. 
"""

#Local modules
for appName in appNamesList:
    #print(os.path.dirname(__file__))
    try:
        #appModule = import_module(appName,os.path.dirname(__file__))
        #appModule = import_module(appName,'ddTool')
        spec = importlib.util.spec_from_file_location(appName,os.path.join(os.path.dirname(__file__),f"{appName}.py"))
        module = importlib.util.module_from_spec(spec)
        sys.modules[appName] = module
        spec.loader.exec_module(module)
        eval(f'exec("from {appName} import *")')
    except:
        print(sys.exc_info())
    #else:
    #    globals()[appName]=appModule
    #    eval(f'exec("from {appName} import *")')


'''
for appName in appNamesList:
    try:
        from . import eval(f{"appName"})
    except:
        print(sys.exc_info())
'''

global hpcCenters

hpcCenters=['LUMI','MareNostrum']
"""list[str]: List of the HPC centers.
Names of the HPC centers producing the data.
"""


esmNames=['ICON','IFS']
"""list[str]: List of the ESMs.
Names of the Earth System Models used performing the simulations and producing the GSV data.
"""


global appDataSrcNames

appDataSrcNames=['netcdf','image','text']
"""list[str]: List of the file types.
Names of the different types of data sources / files each application can produce. 
"""

appDataSrcNameFileExt={
    'netcdf'   :['*.nc'],
    'image'   :['*.jpg','*.pdf','*.png','*.gif'],
    'text'     :['*.txt','*.csv']
}
"""list[str]: List of the file extensions.
"""


# NOTE: TO BE DISCUSSED!
# ----------------------
# Grouping of the different data sources for each application
# for example say 
#       'netcdf' files can be grouped as -- 'monthly', 'daily' etc. and an app can produce some
#                                           subset of this classification
appDataSrcNamesGrouping={
    'netcdf'   :['monthly','daily'],
    'images'   :[''],
    'text'     :['']
}


appSrcFlags={
    'AQUA'               :   [True,True,False],
    'EnergyOnShore'      :   [True,True,True],
    'EnergyOffShore'     :   [True,True,False],
    'FWI'                :   [True,True,False],
    'HydroMet'           :   [True,False,True],
    'HydroRiver'         :   [True,False,True],
    'SPITFIRE'           :   [True,False,False],
    'Urban'              :   [True,True,True],
    'WISE'               :   [False,True,False]
}
"""dict[str]: Dictionary of the file types produced by all the apps.
Data structure to store the availability of different dataSrcNames ['netcdf','image','text'] corresponding to each app in that sequence.
For example we are using the above specified data sources for each app and filling this data structure.
"""


#ddtBasePath="/work/bm0146/k204247/DestinE/destinE_DDTool"
ddtBasePath=".."
"""str: Path to location of the data discovery and management tool on disk.
"""


#appDataPath="/work/bm0146/k204247/DestinE/destinE_DDTool/destinE_AppData"
#appDataPath="/work/bm0146/k204247/DestinE/destinE_DDTool/destinEData"
appDataPath="../destinEData"
"""str: Path to location of the data produced by the applications.
"""


# Mapping the APIs for handling the different data sources (types) produced by the Apps.
global appDataSrcNamesAPImap
appDataSrcNamesAPImap={}

global outputPath
outputPath = ""