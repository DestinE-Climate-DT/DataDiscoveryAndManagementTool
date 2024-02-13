"""
This module contains the core structural elements of the data discovery tool. 
The core structural elements consists of the names of applications, HPC centers, ESMs etc.
The names of the file types produced by each application and their extensions.
Apart from that certain data structures to hold these infos.
"""

#Standard modules
import os
import sys
from importlib import import_module
import importlib

appNamesList=['AQUA','EnergyOnShore','EnergyOffShore','FWI','HydroMet','HydroRiver','SPITFIRE','Urban','WISE']

#Local modules
for appName in appNamesList:
    try:
        spec = importlib.util.spec_from_file_location(appName,
                         os.path.join(os.path.dirname(__file__),f"{appName}.py"))
        module = importlib.util.module_from_spec(spec)
        sys.modules[appName] = module
        spec.loader.exec_module(module)
        eval(f'exec("from {appName} import *")')
    except:
        print(sys.exc_info())
    

class configDatadiscoverer():

    activeConfig = None # static to be set once the instance is created from JSON,
                        # that would be further used by other modules.
    def __init__(self):
        
        self.appNamesList=[]
        """list[str]: List of the application names.
        Names of the applications using the GSV data and producing respective application specific data. 
        """
        
        self.hpcCenters=[]
        """list[str]: List of the HPC centers.
        Names of the HPC centers producing the data.
        """

        self.esmNames=[]
        """list[str]: List of the ESMs.
        Names of the Earth System Models used performing the simulations and producing the GSV data.
        """

        self.appDataSrcNames=[]
        """list[str]: List of the file types.
        Names of the different types of data sources / files each application can produce. 
        """

        self.appDataSrcNameFileExt={}    
        """list[str]: List of the file extensions.
        """

        self.datadiscovererBasePath=""
        """str: Path to location of the data discovery and management tool on disk.
        """

        self.datadiscovererDataPath=""
        """str: Path to location of the data produced by the applications.
        """

        self.datadiscovererOutputPath=""
        """str: Path to location of the catalog prouced by data discovery and management tool.
        """
        
        self.appSrcFlags={}
        """dict[str]: Dictionary of the file types produced by all the apps.
        Data structure to store the availability of different dataSrcNames ['netcdf','image','text'] 
        corresponding to each app in that sequence.
        For example we are using the above specified data sources for each app and filling this data 
        structure.
        """

        self.appDataSrcNamesAPImap={}
        """dict[str]:Mapping the APIs for handling the different data sources (types) produced by the
        Apps.
        """
    
    def setConfigfromJSON(self,jsonDict):
        self.__dict__ = jsonDict
        
    def setappNamesList(self,appNamesList):
        self.appNamesList = appNamesList
        
    def getappNamesList(self):
        return self.appNamesList
    
    def setHPCCenters(self,hpcCenters):
        self.hpcCenters = hpcCenters
        
    def getHPCCenters(self):
        return self.hpcCenters
    
    def setESMs(self,esmNames):
        self.esmNames = esmNames
        
    def getESMs(self):
        return self.esmNames

    def setappDataSrcNames(self,appDataSrcNames):
        self.appDataSrcNames = appDataSrcNames
        
    def getappDataSrcNames(self):
        return self.appDataSrcNames
    
    def setappDataSrcNameFileExt(self,appDataSrcNameFileExt):
        self.appDataSrcNameFileExt = appDataSrcNameFileExt
        
    def getappDataSrcNameFileExt(self):
        return self.appDataSrcNameFileExt
    
    def setappDataSrcFlags(self,appDataSrcFlags):
        self.appDataSrcFlags = appDataSrcFlags

    def getappDataSrcFlags(self):
        return self.appDataSrcFlags
        
    def setdatadiscovererBasePath(self,path):
        self.datadiscovererBasePath = path
    
    def getdatadiscovererBasePath(self):
        return self.datadiscovererBasePath
    
    def setdatadiscovererDataPath(self,path):
        self.datadiscovererDataPath=path
        
    def getdatadiscovererDataPath(self):
        return self.datadiscovererDataPath
    
    def setdatadiscovererOutputPath(self,path):
        self.datadiscovererOutputPath = path
        
    def getdatadiscovererOutputPath(self):
        return self.datadiscovererOutputPath
    
    def setappDataSrcNamesAPImap(self):
        self.appDataSrcNamesAPImap = {}
        
    def getappDataSrcNamesAPImap(self):
        return self.appDataSrcNamesAPImap
        
'''
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
'''