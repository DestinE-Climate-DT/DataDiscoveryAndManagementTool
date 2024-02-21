"""
This module contains the core structural elements of the data discovery tool. 
The core structural elements consists of the names of applications, HPC centers,
ESMs etc.The names of the file types produced by each application and their 
extensions.Apart from that certain data structures to hold these infos.
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
                                            "enum" : ['description','provider',
                                                      'datasources','metadata']
                                    },
                                    "required":['description','provider',
                                                'datasources','metadata']
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
        return None
    
    userConfig = None
    
    with open(f"{configFile}") as f:

        try:
            userConfig = json.load(f)
        
            try:
                # Input data - JSON format validation.
                validate(instance=userConfig, schema=configSchema)
            except exceptions.ValidationError as e:
                print(f"Invalid JSON schema found in configuration file : {configFile}")
                print(f"Error :{e}")
                return None
            
        except json.JSONDecodeError as e:
            print(f"Error :{e}")
            #print(f"{json.JSONDecodeError.msg}\n{json.JSONDecodeError.doc}\n \
            #        {json.JSONDecodeError.lineno}\n{json.JSONDecodeError.colno}\n")
            
            return None
    
    print("Input data format validation checks done!")
    
    curconfig = configDatadiscoverer()
    configDatadiscoverer.activeConfig = curconfig
    curconfig.setConfigfromJSON(userConfig)
    
    # TODO: Input data - additional checks for the input data.
    inputDataChecksPassed = True 
            
    print("Input data additional checks on-going")
    
    # 1.Check if all apps exist in appNames and appDescriptionInfo.
    appNames     = curconfig.getappNames()
    appDescInfo  = curconfig.getappDescriptionInfo()
    
    errorMessages = []
    if len(appNames) != len(appDescInfo.items()) :
        failedApps = []
        inputDataChecksPassed = False
        for app in appNames:
            if app not in appDescInfo.keys():
                failedApps.append(app)
        errorMessages.append(f"Mismatch in number of apps in 'appNames' and 'appDescriptionInfo'.The following apps failed:{failedApps}")
    
    if inputDataChecksPassed is False:
        curconfig = None
        for msg in errorMessages:
            print(f"{msg}\n")
        return None
    else:
        print("Input data additional checks done")

    return curconfig
        
        
class configDatadiscoverer():
    """Class to hold the various paramters to drive the datadiscoverer.
    """

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

        '''
        self.appDataSrcNamesAPImap={}
        """dict[str]:Mapping the APIs for handling the different data sources (types) produced by the
        Apps.
        """
        '''
    
    def setConfigfromJSON(self,jsonDict):
        """Set the datadiscoverer configuration to the input JSON dictionary.

        For setting the configuration parameters of the datadiscoverer from the input JSON dictionary.

        Args:
                jsonDict: A JSON dictionary.
        Returns:
                None.
        """

        self.__dict__ = jsonDict
        self.appDataSrcNamesAPImap = {}

    def setInstallationPath(self,path):
        """Set the datadiscoverer installation path.

        For setting the location where the datadiscoverer is intalled on the disk to the configuration.

        Args:
                path: Path to datadiscoverer.
        Returns:
                None.
        """

        self.installationPath = path
    
    def getInstallationPath(self):
        """Get the datadiscoverer installation path.

        For getting the location where the datadiscoverer is intalled on the disk.

        Args:
                None.
        Returns:
                str: Path to datadiscoverer.
        """

        return self.installationPath
    
    def setDataPath(self,path):
        """Set the application data path.

        For setting the location where the apps store the data that is to be cataloged by the datadiscoverer.

        Args:
                path: Path to location of the data produced by the apps.
        Returns:
                None.
        """

        self.dataPath=path
        
    def getDataPath(self):
        """Get the application data path.

        For setting the location where the apps store the data that is to be cataloged by the datadiscoverer.

        Args:
                None.
        Returns:
                path: Path to location of the data produced by the apps.
        """

        return self.dataPath
    
    def setOutputPath(self,path):
        """Set the output path.

        For setting the location where the catalogs produced by datadiscoverer will be stored.

        Args:
                path: Path to location of the catalogs produced by the datadiscoverer.
        Returns:
                None.
        """

        self.outputPath = path
        
    def getOutputPath(self):
        """Get the output path.

        For getting the location where the catalogs produced by datadiscoverer will be stored.

        Args:
                None.
        Returns:
                path: Path to location of the catalogs produced by the datadiscoverer.
        """

        return self.outputPath
        
    def setappNames(self,appNamesList):
        """Set the application names.

        For updating the configuration with the application names.

        Args:
                list[str]: List of the application names.
        Returns:
                None.
        """
        self.appNames = appNamesList
        
    def getappNames(self):
        """Get the application names.

        For getting the application names from the configuration.

        Args:
                None.
        Returns:
                list[str]: List of the application names.
        """

        return self.appNames
    
    def setHPCCenters(self,hpcCenters):
        """Set the HPC centers names.

        For updating the configuration with the HPC center names.

        Args:
                list[str]: List of the HPC center names.
        Returns:
                None.
        """

        self.hpcCenters = hpcCenters
        
    def getHPCCenters(self):
        """Get the HPC centers names.

        For getting the HPC center names from the configuration.

        Args:
                None.
        Returns:
                list[str]: List of the HPC center names.
        """

        return self.hpcCenters
    
    def setESMs(self,esmNames):
        """Set the ESM names.

        For updating the configuration with the ESM names.

        Args:
                list[str]: List of the ESM names.
        Returns:
                None.
        """

        self.esmNames = esmNames
        
    def getESMs(self):
        """Set the ESM names.

        For getting the ESM names from the configuration.

        Args:
                None.
        Returns:
                list[str]: List of the ESM names.
        """

        return self.esmNames
    
    def setappDataSrcNames(self,appDataSrcNames):
        """Set the data source names.

        For updating the configuration with the data source names like 'netcdf', 'image', 'text'.

        Args:
                list[str]: List of the data source names.
        Returns:
                None.
        """

        self.appDataSrcNames = appDataSrcNames
        
    def getappDataSrcNames(self):
        """Get the data source names.

        For getting the data source names like 'netcdf', 'image', 'text' from the configuration.

        Args:
                None.
        Returns:
                list[str]: List of the data source names.
        """

        return self.appDataSrcNames
    
    def setappDataSrcNameFileExt(self,appDataSrcNameFileExt):
        """Set the file name extension for the data sources.

        For updating the configuration with the file name extensions for the various types of data sources that the data produced by the apps belongs to.

        Args:
                appDataSrcNameFileExt: Dictionary of the data source names and the corresponding file name extensions.
        Returns:
                None.
        """

        self.appDataSrcNameFileExt = appDataSrcNameFileExt
        
    def getappDataSrcNameFileExt(self):
        """Get the file name extension for the data sources.

        For getting the file name extensions,for the various types of data sources that the data produced by the apps belongs to, from the the configuration.

        Args:
                None.
        Returns:
                appDataSrcNameFileExt: Dictionary of the data source names and the corresponding file name extensions.
        """

        return self.appDataSrcNameFileExt
    
    def setappDescriptionInfo(self,appDescInfo):
        """Set the application description info to the configuration.

        For updating the configuration with the application description info, provider etc.

        Args:
                appDescInfo: Dictionary of the various parameters that describe the various apps.
        Returns:
                None.
        """

        self.appDescriptionInfo = appDescInfo
        
    def getappDescriptionInfo(self):
        """Get the application description from the configuration.

        For getting the application description info, provider etc from the configuration.

        Args:
                None.
        Returns:
                appDescInfo: Dictionary of the various parameters that describe the various apps.
        """

        return self.appDescriptionInfo
    
    def getappDataSrcs(self,app):
        """Get the data sources produced by  a given application.

        For getting the data sources to which the data produced by a given application belongs to, from the configuration.

        Args:
                None.
        Returns:
                appDescInfo: List of data source names.
        """

        return self.appDescriptionInfo[app]['datasources']
    
    def getappDescription(self,app):
        """Get the description of a given application.

        For getting the description about a given application from the configuration.

        Args:
                app: Application name.
        Returns:
                str: Application description.
        """

        return self.appDescriptionInfo[app]['description']
    
    def getappProvider(self,app):
        """Get the provider of a given application.

        For getting the details about the provider of a given application from the configuration.

        Args:
                app: Application name.
        Returns:
                str: Details of the application provider.
        """

        return self.appDescriptionInfo[app]['provider']
    
    def getappMetadataKeys(self,app):
        """Get the metadata keys for a given application.

        For getting the metadata keys for the data produced by a given application from the configuration.

        Args:
                app: Application name.
        Returns:
                str: List of metadata keys.
        """

        return self.appDescriptionInfo[app]['metadata']    