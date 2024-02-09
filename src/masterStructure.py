"""
This module contains the core structural elements of the data discovery tool. 
The core structural elements consists of the names of applications, HPC centers, ESMs etc.
The names of the file types produced by each application and their extensions.
Apart from that certain data structures to hold these infos.
"""

#Standard modules
import sys
from importlib import import_module

#Local modules
appNamesList=['AQUA','EnergyOnShore','EnergyOffShore','FWI','HydroMet','HydroRiver','SPITFIRE','Urban','WISE']
"""list[str]: List of the application names.
"""

for appName in appNamesList:
    try:
        appModule = import_module(appName)
    except:
        print(sys.exc_info())
    else:
        globals()[appName]=appModule
        eval(f'exec("from {appName} import *")')
        
        
# Names of the HPC centers producing the data.
hpcCenters=['LUMI','MareNostrum']
"""list[str]: List of the HPC centers.
"""


# Names of the Earth System Models used performing the simulations and producing the GSV data.
esmNames=['ICON','IFS']
"""list[str]: List of the ESMs.
"""

# Names of the applications using the GSV data and producing respective application specific data. 
#appNamesList=['AQUA','EnergyOnShore','EnergyOffShore','FWI','HydroMet','HydroRiver','SPITFIRE','Urban','WISE']

#Names of the different types of data sources / files each application can produce
# for example say 
#       'mHM' app produces - netcdf files, image files and  text files.
#       'AQUA' app produces - netcdf files only.
#       'WildFire' app produces - image files only.
#       'Energy'   app produces - netcdf and text files
#       'Urban' app produces -  text files
appDataSrcNames=['netcdf','image','text']
"""list[str]: List of the file types.
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


# Data structure to store the availability of different dataSrcNames ['netcdf','image','text']
# corresponding to each app in that sequence.
# For example we are using the above specified data sources for each app and filling this data structure.
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
"""


#Path to the data discovery tool installation location.
ddtBasePath="/work/bm0146/k204247/DestinE/destinE_DDTool"
"""str: Path to location of the data discovery and management tool on disk.
"""


#Path to the app data location.
#appDataPath="/work/bm0146/k204247/DestinE/destinE_DDTool/destinE_AppData"
appDataPath="/work/bm0146/k204247/DestinE/destinE_DDTool/destinEData"
"""str: Path to location of the data produced by the applications.
"""


# Mapping the APIs for handling the different data sources (types) produced by the Apps.
appDataSrcNamesAPImap={}
