# This module contains the APIs for updating the catalog for each app and each of it's file types.
# These APIs need to be called by the app data curator for maintaining the catalog.

#TODO: 
# Create temporary files for each app and check the APIs.
# Create catalog for each app as well as the master catalog.
# Update the files to github and share in the meeting.
# Demonstrate with intake GUI.
# Create docstrings for each api and generate the online documentation.
# Create the STAC catalog and demonstrate in browser.

import os
import subprocess
import yaml
import intake
import pathlib
import itertools

from masterStructure import *
from utils import getAppSrcFileList


def createAppDataSrcNamesIntakeAPImap():
    """Create a mapping between the file types and the associated API for handling it.

    Mapper to club the file types and the corresponding access methods for handling netcdf, jpeg etc.

    Args:
            None.

    Returns: 
            None
    """
    
    for src in appDataSrcNames:
        if src == 'netcdf':
            appDataSrcNamesAPImap[src]=createNetcdfSrcListForIntake
        elif src == 'image':
            appDataSrcNamesAPImap[src]=createImageSrcListForIntake
        elif src == 'text':
            appDataSrcNamesAPImap[src]=createTextSrcListForIntake
        else:
            raise f'Unknown source type {src} encountered!'


def createDDTMasterIntakeCatalog():
    """Create master catalog file for the HPC centers.

    Create the top level master catalog containing the links to the yaml files for the HPC centers.

    Args:
            None.
    Returns: 
            None
    """

    sources={}
    sources.setdefault("sources",{})
    
    for hpc in hpcCenters:
        sources["sources"].setdefault(hpc,{})
        argsdict={
              "description": f"{hpc} data catalog",
              "driver":"yaml_file_cat",
              "args":
                    {
                      "path":"{{CATALOG_DIR}}/"+f"{hpc}/"+f"{hpc}.yaml"
                    }
                }
        sources["sources"][hpc]=argsdict

    if os.path.isfile(f"{ddtBasePath}/DDTMasterIntakeCatalog.yaml"):
        pathlib.Path(f"{ddtBasePath}/DDTMasterIntakeCatalog.yaml").unlink(missing_ok=True)

    with open(f"{ddtBasePath}/DDTMasterIntakeCatalog.yaml", "w") as f:
        f.write(
            "description: 'DestinE data discovery tool master intake catalog for the data produced at various HPC centers.'\n")
        yaml.dump(sources,f,sort_keys=False)
        f.close()


def createHPCIntakeCatalog():
    """Create yaml files for the HPC centers.

    For each of the HPC centers, create the yaml files containing the links to the yaml files for the Apps .

    Args:
            None.
    Returns: 
            None
    """

    sources={}
    sources.setdefault("sources",{})

    for hpc, app  in itertools.product(hpcCenters,appNamesList):

        sources["sources"].setdefault(app,{})
        argsdict={
              "description": f"{app} application data catalog",
              "driver":"yaml_file_cat",
              "args":
                    {
                      "path":"{{CATALOG_DIR}}/"+f"{app}/"+f"{app}.yaml"
                    }
                }

        sources["sources"][app]=argsdict

        hpcCatalogPath = os.path.join(ddtBasePath,f"{hpc}")
        if not os.path.exists(hpcCatalogPath):
            os.makedirs(hpcCatalogPath,exist_ok=True)

        hpcCatalog = os.path.join(hpcCatalogPath,f"{hpc}.yaml")
        
        if os.path.isfile(hpcCatalog):
            pathlib.Path(hpcCatalog).unlink(missing_ok=True)

        with open(f"{hpcCatalog}", "w") as f:
            f.write(
                "description: "+ f"\'Catalog for application data produced by the desitnation earth twin engine simulations performed on {hpc}.\'\n")
            yaml.dump(sources,f,sort_keys=False)
            f.close()


def createAppIntakeCatalog():
    """Create yaml files for the Apps.

    For each of the Apps, create the yaml files containing the links to the yaml files for the ESMs .

    Args:
            None.
    Returns: 
            None
    """
    
    sources={}
    sources.setdefault("sources",{})
    
    for hpc, app, esm  in itertools.product(hpcCenters,appNamesList,esmNames):

        sources["sources"].setdefault(esm,{})
        argsdict={
              "description": f" \'{esm} GSV data catalog \' ",
              "driver":"yaml_file_cat",
              "args":
                    {
                      "path":"{{CATALOG_DIR}}/"+f"{esm}/"+f"{esm}.yaml"
                    }
                }
        sources["sources"][esm]=argsdict
            
        appCatalogPath = os.path.join(ddtBasePath,f"{hpc}",f"{app}")
        if not os.path.exists(appCatalogPath):
            os.makedirs(appCatalogPath,exist_ok=True)

        appCatalog = os.path.join(appCatalogPath,f"{app}.yaml")

        if os.path.isfile(appCatalog):
            pathlib.Path(appCatalog).unlink(missing_ok=True)

        with open( appCatalog, "w" ) as f:
            f.write(f"description: {app} application data catalog\n")
            yaml.dump(sources,f,sort_keys=False)
            f.close()


def createESMIntakeCatalog():
    """Create yaml files for the ESMs.

    For each of the ESMs, create the yaml files containing the links to the yaml files for the available sources .

    Args:
            None.
    Returns: 
            None
    """
       
    sources={}
    sources.setdefault("sources",{})
    
    for hpc, app, esm in itertools.product(hpcCenters, appNamesList, esmNames):
        currentAppSrcDict = {}
        currentAppSrcFlags = appSrcFlags[app]

        sources={}
        sources.setdefault("sources",{})

        for src in appDataSrcNames:
            if currentAppSrcFlags[appDataSrcNames.index(src)] == True:

                sources["sources"].setdefault(src,{})
                argsdict={
                      "description": f"{src} files data catalog",
                      "driver":"yaml_file_cat",
                      "args":
                            {
                              "path":"{{CATALOG_DIR}}/"+f"{src}/"+f"{src}.yaml"
                            }
                        }

                sources["sources"][src]=argsdict

        esmCatalogPath = os.path.join(ddtBasePath,f"{hpc}",f"{app}",f"{esm}")
                
        if not os.path.exists(esmCatalogPath):
            os.makedirs(esmCatalogPath,exist_ok=True)

        esmCatalog = os.path.join(esmCatalogPath,f"{esm}.yaml")

        if os.path.isfile(esmCatalog):
            pathlib.Path(esmCatalog).unlink(missing_ok=True)

        with open( esmCatalog, "w" ) as f:
            f.write(f"description: 'Catalog for files generated from {esm} GSV.  '\n")
            yaml.dump(sources,f,sort_keys=False)
            f.close()            


def createSrcIntakeCatalog():
    """Create yaml files for the sources.

    For each of the app, check the available sources (file types) and  create the corresponding yaml files.

    Args:
            None.
    Returns: 
            None
    """

    for hpc, app, esm, src in itertools.product(hpcCenters, appNamesList, esmNames, appDataSrcNames):
        currentAppSrcDict = {}
        currentAppSrcFlags = appSrcFlags[app]
                
        print(f"current HPC : {hpc} App: {app} ESM : {esm}  Source : {src} Flag: {currentAppSrcFlags[appDataSrcNames.index(src)]}")

        if currentAppSrcFlags[appDataSrcNames.index(src)] == True:

            srcCatalogPath = os.path.join(ddtBasePath,f"{hpc}",f"{app}",f"{esm}",f"{src}")

            if not os.path.exists(srcCatalogPath):
                os.makedirs(srcCatalogPath,exist_ok=True)
            srcCatalog = os.path.join(ddtBasePath,f"{hpc}",f"{app}",f"{esm}",f"{src}",f"{src}.yaml")

            srcExtList=appDataSrcNameFileExt[src]
            (appDataSrcNamesAPImap[src])(srcCatalog,getAppSrcFileList(app,src,srcExtList))
        else:
            continue


def createNetcdfSrcListForIntake(catFile,srcFileList):
    """Create yaml sources for the netcdf files in the input
       file list of files.

    For each of the netcdf files in the input file list, create the yaml source and save in the input catalog file.

    Args:
            catFile : Catalog File Name.
            srcFileList : List of netcdf files.
    Returns: 
            None
    """

    if os.path.isfile(catFile):
        pathlib.Path(catFile).unlink(missing_ok=True)

    sources={}
    sources.setdefault("sources",{})

    srcCatalogFile = open( catFile, "w" )
    srcCatalogFile.write("description: 'Catalog for netcdf files.'\n")
    yaml.dump(sources,srcCatalogFile,sort_keys=False)
    srcCatalogFile.close()
    
    srcCatalog = intake.open_catalog(catFile)

    netcdfSrcs=[]
    count=1
    for srcFile in srcFileList:
        if not os.path.isfile(srcFile):
            print(f"File {srcFile} doesn't exist!")
            return
        netcdfSrc = intake.open_netcdf(srcFile)
        netcdfSrc.name = f"netcdf{count}"
        
        # Add the sources to the catalog
        srcCatalog = srcCatalog.add(netcdfSrc)
        count += 1
        
    srcCatalog.save(catFile)
    return


def createImageSrcListForIntake(catFile,srcFileList):
    """Create yaml sources for the image files in the input
       file list of files.

    For each of the image files in the input file list, create the yaml source and save in the input catalog file.

    Args:
            catFile : Catalog File Name.
            srcFileList : List of image files.
    Returns: 
            None
    """
    
    if os.path.isfile(catFile):
        pathlib.Path(catFile).unlink(missing_ok=True)

    sources={}
    sources.setdefault("sources",{})

    srcCatalogFile = open( catFile, "w" )
    srcCatalogFile.write(
        "description: 'Catalog for image files.'\n")
    yaml.dump(sources,srcCatalogFile,sort_keys=False)
    srcCatalogFile.close()
    
    srcCatalog = intake.open_catalog(catFile)

    imageSrcs=[]
    count=1
    for srcFile in srcFileList:
        if not os.path.isfile(srcFile):
            print(f"File {srcFile} doesn't exist!")
            return
        imageSrc = intake.open_rasterio(srcFile)
        imageSrc.name = f"image{count}"
        
        # Add the sources to the catalog
        srcCatalog = srcCatalog.add(imageSrc)
        count += 1
        
    srcCatalog.save(catFile)
    return


def createTextSrcListForIntake(catFile,srcFileList):
    """Create yaml sources for the text files in the input
       file list of files.

    For each of the text files in the input file list, create the yaml source and save in the input catalog file.

    Args:
            catFile : Catalog File Name.
            srcFileList : List of text files.
    Returns: 
            None
    """

    if os.path.isfile(catFile):
        pathlib.Path(catFile).unlink(missing_ok=True)
        
    sources={}
    sources.setdefault("sources",{})

    srcCatalogFile = open( catFile, "w" )
    srcCatalogFile.write(
            "description: 'Catalog for text files.'\n")
    yaml.dump(sources,srcCatalogFile,sort_keys=False)
    srcCatalogFile.close()
    
    srcCatalog = intake.open_catalog(catFile)

    textSrcs=[]
    count=1
    for srcFile in srcFileList:
        if not os.path.isfile(srcFile):
            print(f"File {srcFile} doesn't exist!")
            return
        textSrc = intake.open_textfiles(srcFile)
        textSrc.name = f"text{count}"
        count += 1
        
        # Add the sources to the catalog
        srcCatalog = srcCatalog.add(textSrc)
        
    srcCatalog.save(catFile)
    return