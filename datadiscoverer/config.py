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
import json

#Non-standard modules
try:
    from jsonschema import validate
    from jsonschema import exceptions
except:
    print(sys.exc_info())
    print(f"Module 'jsonschema' import error in {__file__}")

        
configSchema = {
                    "type" : "object",
                    "properties" : {
                            "installationPath":{ "type" : "string"},
                            "dataPath":{ "type" : "string"},
                            "outputPath":{ "type" : "string"},

                            "appNames":{
                                "type" : "array",
                                "items": {"type": "string","enum" : ['AQUA','EnergyOnShore','EnergyOffShore','FWI',
                                                                     'HydroMet','HydroRiver','SPITFIRE','Urban','WISE']},
                                "uniqueItems": True
                                 },

                            "hpcCenters":{
                                "type" : "array",
                                "items": {"type": "string","enum" : ["LUMI","MareNostrum"]},
                                "uniqueItems": True
                                 },

                            "esmNames":{
                                "type" : "array",
                                "items": {"type": "string","enum" : ["ICON","IFS"]},
                                "uniqueItems": True
                                 },

                            "appDataSrcNames":{
                                "type" : "array",
                                "items": {
                                    "type": "string",
                                    "enum" : ["netcdf","image","text"]
                                },
                                "uniqueItems": True
                            },

                            "appDataSrcNameFileExt":{

                                "type" : "object",
                                "propertyNames": {
                                    "enum": ["netcdf","image","text"]
                                },
                                "additionalProperties": {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    }
                                }
                            },
                        
                            "appDescriptionInfo":{
                               
                                "type" : "object",
                                "propertyNames": {
                                    "enum" : ["AQUA","EnergyOnShore","EnergyOffShore","FWI",
                                                      "HydroMet","HydroRiver","SPITFIRE","Urban","WISE"]
                                },
                                
                                "additionalProperties": {
                                    
                                    "type": "object",
                                    "propertyNames": {
                                            "enum" : ['description','provider','datasources']
                                    },
                                    "required":['description','provider','datasources']
                                }
                            }
                    },
    
                    "required":["installationPath","dataPath","outputPath","appNames","hpcCenters","esmNames","appDataSrcNames","appDataSrcNameFileExt","appDescriptionInfo"]                       
               }


def initializeDataDiscoverer(configFile):
    """Initializing the datadiscoverer.

    Initialize the datadiscoverer library configuration with the parameters provided in 
    the input json file.

    Args:
            configFile : JSON file with configuration parameters.
     Returns: 
            curconfig - current configuration object.
    """
    
    global configSchema
    
    if not os.path.exists(configFile):
        print(f"Configuration File {configFile} doesn't exist !!!")
        return 
    
    userConfig = None
    with open(f"{configFile}") as f:
        userConfig = json.load(f)
        
        try:
            validate(instance=userConfig, schema=configSchema)
        except exceptions.ValidationError:
            print(f"Invalid JSON schema found in configuration file : {configFile}")
            print(f"Message:{exceptions.ValidationError.message}\n \
                    Failed key :{exceptions.ValidationError.validator}\n \
                    Value :{exceptions.ValidationError.validator_value}")
            return 
    
    curconfig = configDatadiscoverer()
    configDatadiscoverer.activeConfig = curconfig
    curconfig.setConfigfromJSON(userConfig)
    
    return curconfig
        
        
class configDatadiscoverer():

    activeConfig = None # static to be set once the instance is created from JSON,
                        # that would be further used by other modules.
    def __init__(self):
        
        self.appNames=[]
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
        Names of the different types of data sources / files the applications can produce. 
        """

        self.appDataSrcNameFileExt={}    
        """list[str]: List of the file extensions.
        """
        
        self.appDescriptionInfo={}
        """dict[str]: Dictionary of the description for each of the apps.
        Data structure to store the description, provider etc corresponding to each app.
        """


        self.installationPath=""
        """str: Path to location of the data discovery and management tool on disk.
        """

        self.dataPath=""
        """str: Path to location of the data produced by the applications.
        """

        self.outputPath=""
        """str: Path to location of the catalog prouced by data discovery and management tool.
        """

        self.appDataSrcNamesAPImap={}
        """dict[str]:Mapping the APIs for handling the different data sources (types) produced by the
        Apps.
        """
    
    def setConfigfromJSON(self,jsonDict):
        self.__dict__ = jsonDict
        self.appDataSrcNamesAPImap = {}

    def setInstallationPath(self,path):
        self.installationPath = path
    
    def getInstallationPath(self):
        return self.installationPath
    
    def setDataPath(self,path):
        self.dataPath=path
        
    def getDataPath(self):
        return self.dataPath
    
    def setOutputPath(self,path):
        self.outputPath = path
        
    def getOutputPath(self):
        return self.outputPath
        
    def setappNames(self,appNamesList):
        self.appNames = appNamesList
        
    def getappNames(self):
        return self.appNames
    
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
    
    def setappDescriptionInfo(self,appDescInfo):
        self.appDescriptionInfo = appDescInfo
        
    def getappDescriptionInfo(self):
        return self.appDescriptionInfo

    def getappDataSrcs(self,app):
        return self.appDescriptionInfo[app]['datasources']
    
    def getappDescription(self,app):
        return self.appDescriptionInfo[app]['description']

    def getappProvider(self,app):
        return self.appDescriptionInfo[app]['provider']
    
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
