# This module contains the core structural elements of the data discovery tool. The core structural elements
# consists of the application names, the names of the file types produced by each application.

import os

# Names of the HPC centers producing the data.
hpcCenters=['LUMI','MareNostrum']

# Names of the Earth System Models used performing the simulations and producing the GSV data.
esmNames=['ICON','IFS']

# Names of the applications using the GSV data and producing respective application specific data. 
appNamesList=['Aqua','Energy','HydroMet','HydroRiver','Urban','Wildfires']

#Names of the different types of data sources / files each application can produce
# for example say 
#       'mHM' app produces - netcdf files, image files and  text files.
#       'Aqua' app produces - netcdf files only.
#       'WildFire' app produces - image files only.
#       'Energy'   app produces - netcdf and text files
#       'Urban' app produces -  text files
appDataSrcNames=['netcdf','image','text']

appDataSrcNameFileExt={
    'netcdf'   :'*.nc',
    'image'   :'*.jpg',
    'text'     :'*.txt'
}

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


# Data structure to store the availability of different dataSrcNames corresponding to each app.
# For example we are using the above specified data sources for each app and filling this data structure.
appSrcFlags={
    'Aqua'        :   [True,True,True],
    'Energy'      :   [False,False,True],
    'HydroMet'    :   [True,False,False],
    'HydroRiver'  :   [True,False,False],
    'Urban'       :   [False,False,True],
    'Wildfires'   :   [True,True,False]
}

#Path to the data discovery tool installation location.
ddtBasePath="/work/bm0146/k204247/DestinE/destinE_DDTool"

#Path to the app data location.
appDataPath="/work/bm0146/k204247/DestinE/destinE_DDTool/destinEData"

# Mapping the APIs for handling the different data sources (types) produced by the Apps.
appDataSrcNamesAPImap={}