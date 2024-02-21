"""
This module contains the APIs for updating the STAC catalog for each app and each of it's file types.
These APIs need to be called by the app data curator for maintaining the STAC catalog.
"""

#Standard modules
import os
import sys
import json
import itertools
from datetime import datetime, timezone
import importlib

#Non-standard modules
try:
    import rasterio
    import pystac
    from shapely.geometry import Polygon, mapping
except:
    print(sys.exc_info())
    print(f"Module 'raterio/pystac/shapely' import error in {__file__}")

#Local modules
try:
    from .config import configDatadiscoverer
except:
    print(sys.exc_info())
    print(f"Module 'config' import error in {__file__}")

try:
    from .utils import getAppSrcFileList
except:
    print(sys.exc_info())
    print(f"Module 'utils' import error in {__file__}")


sourceMediaTypeMap =  {
    'netcdf':{
                '.nc' : pystac.MediaType.HDF5,
    },
    'image':{
                '.pdf' : pystac.MediaType.PDF,
                '.jpg' : pystac.MediaType.JPEG,
                '.png' : pystac.MediaType.PNG,
                '.tiff': pystac.MediaType.TIFF
    },
    'text':{
                '.csv' : pystac.MediaType.TEXT, # to check if any other driver exists.
                '.txt' : pystac.MediaType.TEXT,
    }
}

    
def createMasterSTACCatalog():
    """Create master STAC catalog file for the HPC centers.

    Create the top level master STAC catalog containing the links to the STAC catalogs for the HPC centers.

    Args:
            None.
    Returns: 
            None.
    """

    localconfig = configDatadiscoverer.activeConfig
    outputPath = localconfig.getOutputPath()

    catalog = pystac.Catalog(id='datadiscovererSTACCatalog', 
                         description='DestinE data discovery tool master STAC catalog for the data produced at various HPC centers.')
    
    for hpc in localconfig.getHPCCenters():
    
        hpcCatalog = pystac.Catalog(id=f'{hpc}', 
                         description=f"{hpc} data catalog")
        catalog.add_child(hpcCatalog,f'{hpc}')
    
    try:
        os.path.exists(outputPath)
    except:
        print(sys.exc_info())
        return
        
    catalog.normalize_and_save(root_href = outputPath, 
                         catalog_type=pystac.CatalogType.SELF_CONTAINED)
    
    createHPCSTACCatalog()


def createHPCSTACCatalog():
    """Create STAC catalog for the HPC centers.

    For each of the HPC centers, create the STAC catalog containing the links to the STAC catalogs for the Apps.

    Args:
            None.
    Returns: 
            None.
    """
    localconfig = configDatadiscoverer.activeConfig
    outputPath = localconfig.getOutputPath()

    for hpc, app  in itertools.product(localconfig.getHPCCenters(),
                                       localconfig.getappNames()):
        
        hpcCatalogPath = os.path.join(outputPath,f"{hpc}")
        hpcCatalogFile = os.path.join(hpcCatalogPath,"catalog.json")
        hpcCatalog=pystac.Catalog.from_file(hpcCatalogFile)
        
        appDescription = localconfig.getappDescription(app)
        
        appCatalog = pystac.Catalog( id=f'{app}', 
                        description = appDescription
                        #,providers = appInfoDict['provider']
                        )
        hpcCatalog.add_child(appCatalog,f'{app}')
        hpcCatalog.normalize_and_save(root_href = hpcCatalogPath, 
                         catalog_type=pystac.CatalogType.SELF_CONTAINED)
    createAppSTACCatalog()


def createAppSTACCatalog():
    """Create STAC catalog for the Apps.

    For each of the Apps, create the STAC catalog containing the links to the STAC catalogs for the ESMs.

    Args:
            None.
    Returns: 
            None.
    """
    localconfig = configDatadiscoverer.activeConfig
    outputPath = localconfig.getOutputPath()

    for hpc, app, esm  in itertools.product(localconfig.getHPCCenters(),
                                        localconfig.getappNames(),
                                        localconfig.getESMs()):

        appCatalogPath = os.path.join(outputPath,f"{hpc}",f"{app}")
        appCatalogFile = os.path.join(outputPath,f"{hpc}",f"{app}","catalog.json")
        appCatalog=pystac.Catalog.from_file(appCatalogFile)
        
        esmCatalog = pystac.Catalog(id=f'{esm}', 
                    description=f"{esm} GSV data catalog")
        appCatalog.add_child(esmCatalog,f'{esm}')
        appCatalog.normalize_and_save(root_href = appCatalogPath, 
                catalog_type=pystac.CatalogType.SELF_CONTAINED)
    
    createESMSTACCatalog()


def createESMSTACCatalog():
    """Create STAC catalog for the ESMs.

    For each of the ESMs, create the STAC catalog containing the links to the STAC catalogs for the available sources.

    Args:
            None.
    Returns: 
            None.
    """

    localconfig = configDatadiscoverer.activeConfig
    outputPath = localconfig.getOutputPath()

    
    appDataSrcNames = localconfig.getappDataSrcNames()
    appDataSrcNameFileExt = localconfig.getappDataSrcNameFileExt()
    
    for hpc, app, esm  in itertools.product(localconfig.getHPCCenters(),
                                            localconfig.getappNames(),
                                            localconfig.getESMs()):
    
        currentAppDataSrcs = localconfig.getappDataSrcs(app)
        
        esmCatalogPath = os.path.join(outputPath,f"{hpc}",f"{app}",f"{esm}")
        esmCatalogFile = os.path.join(outputPath,f"{hpc}",f"{app}",f"{esm}","catalog.json")
        esmCatalog = pystac.Catalog.from_file(esmCatalogFile)
        
        print(f"Ingesting '{app}' data produced using GSV from {esm} simulations performed on {hpc}")
        
        for src in currentAppDataSrcs:
            
            srcCatalog = pystac.Catalog(id=f'{src}', 
                        description=f"{src} files data catalog")

            srcExt=appDataSrcNameFileExt[src]
            
            #  Fetch the 'metadata' keys for this 'app' from 'appDescInfo'.
            appMetadataKeys = localconfig.getappMetadataKeys(app)
            
            createSTACSourcesForFileList(app,src,srcCatalog,getAppSrcFileList(app,src,esm,srcExt))

            esmCatalog.add_child(srcCatalog,f'{src}')
                    
        esmCatalog.normalize_and_save(root_href = esmCatalogPath, 
                catalog_type=pystac.CatalogType.SELF_CONTAINED)
    return


def createSTACSourcesForFileList(app,src,srcCatalog,srcFileList):
    """Create STAC items for the netcdf files in the input
       file list of files.

    For each of the netcdf files in the input file list, create the STAC item and save in the input catalog file.

    Args:
            app : Application Name.
            src : Source Name.
            catFile : Catalog File Name.
            srcFileList : List of netcdf files.
    Returns: 
            None
    """
    global sourceMediaTypeMap
    
    localconfig = configDatadiscoverer.activeConfig
    #  Fetch the 'metadata' keys for this 'app' from 'appDescInfo'.
    appMetadataKeys = localconfig.getappMetadataKeys(app)
    
    if appMetadataKeys is None or len(appMetadataKeys) == 0:
        print(f'Application  {app} does not have metadata! Ignoring {app}.')
        return

    if src not in sourceMediaTypeMap.keys():
        print(f'Source type {src} not handled! \n Ignoring {srcFile} in createSTACSourcesForFileList.')
        return

    stacItemList = []
    count = 1
    
    stacItemList = map(stacItemCreator, itertools.repeat(app,len(srcFileList)), itertools.repeat(src,len(srcFileList)),
                       srcFileList, itertools.repeat(appMetadataKeys,len(srcFileList)), range(1,len(srcFileList)+1))
    
    # Add the items to the catalog.
    for stacItem in stacItemList:
        #intakeSrc.name = f"{src}{count}"
        srcCatalog.add_item(stacItem)
    
    return


def stacItemCreator(app,src,srcFile,appMetadataKeys,itemId):
    """Create stac item for the input source file.

    For the input file of given source and app and metadata keys, prepare the STAC item.

    Args:
            app : application Name
            src : source Name
            catFile : Catalog File Name.
            srcFileList : List of netcdf files.
    Returns:
            intakeSrc : intake catalog object.
    """
    global sourceMediaTypeMap
    
    if src not in sourceMediaTypeMap.keys():
        print(f'Source type {src} not handled! \n Ignoring {srcFile} in stacItemCreator.')
        return None

    
    if not os.path.isfile(srcFile):
        print(f"File {srcFile} doesn't exist!")
        return None

    datetime_utc = datetime.now(tz=timezone.utc)
    bbox_global=[-180,-90,180,90]

    footprint_polygon = Polygon([ [-180, -90],  [-180, 90],
                                  [180, 90],    [180, -90] ])
    footprint=mapping(footprint_polygon)

    #create metadata for item
    itemMetadata = {}

    #  Fetch the 'metadata' values from the 'srcFile' by removing file suffix and splitting with '_'.
    fileName,fileExt = os.path.splitext( os.path.basename(srcFile) )
    metadataValues = fileName.split('_')

    # NOTE: The metadata keys have fixed order as the file name parts seperated by '_'
    if len(metadataValues) < len(appMetadataKeys) :
        for i in range(len(metadataValues),len(appMetadataKeys)):
            metadataValues.append('-')

    for key in appMetadataKeys:
        if app == 'AQUA':
            itemMetadata[key] =  metadataValues[appMetadataKeys.index(key)]
        # TODO for other apps
        else:
            print('Metadata not available')

    item = pystac.Item(id=f'{src}{itemId}',
             geometry=footprint,
             bbox=bbox_global,
             datetime=datetime_utc,
             properties=itemMetadata)

    item.add_asset(key=f'{src}file{itemId}',
                   asset=pystac.Asset(href=srcFile,media_type=sourceMediaTypeMap[src][fileExt]))
    
    return item