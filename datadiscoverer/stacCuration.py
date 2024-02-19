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


def createAppDataSrcNamesSTACAPImap():
    """Create a mapping between the file types and the associated STAC API for handling it.

    Mapper to club the file types and the corresponding access methods for handling netcdf, jpeg etc.

    Args:
            None.

    Returns: 
            None
    """
    localconfig = configDatadiscoverer.activeConfig
    appDataSrcNames = localconfig.getappDataSrcNames()
    appDataSrcNamesAPImap = localconfig.getappDataSrcNamesAPImap()
    
    for src in appDataSrcNames:
        if src == 'netcdf':
            appDataSrcNamesAPImap[src]=createNetcdfSrcListForSTAC
        elif src == 'image':
            appDataSrcNamesAPImap[src]=createImageSrcListForSTAC
        elif src == 'text':
            appDataSrcNamesAPImap[src]=createTextSrcListForSTAC
        else:
            raise f'Unknown source type {src} encountered!'
    return


def createDDTMasterSTACCatalog():
    """Create master STAC catalog file for the HPC centers.

    Create the top level master STAC catalog containing the links to the STAC catalogs for the HPC centers.

    Args:
            None.
    Returns: 
            None.
    """

    createAppDataSrcNamesSTACAPImap()
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
        
    catalog.normalize_and_save(root_href = outputPath, 
                         catalog_type=pystac.CatalogType.SELF_CONTAINED)
    return


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
    return


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
    return


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
    appDataSrcNamesAPImap = localconfig.getappDataSrcNamesAPImap()
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

            (appDataSrcNamesAPImap[src])(srcCatalog,getAppSrcFileList(app,src,esm,srcExt))

            esmCatalog.add_child(srcCatalog,f'{src}')
                    
        esmCatalog.normalize_and_save(root_href = esmCatalogPath, 
                catalog_type=pystac.CatalogType.SELF_CONTAINED)
    return


def createNetcdfSrcListForSTAC(srcCatalog,srcFileList):
    """Create STAC items for the netcdf files in the input
       file list of files.

    For each of the netcdf files in the input file list, create the STAC item and save in the input catalog file.

    Args:
            catFile : Catalog File Name.
            srcFileList : List of netcdf files.
    Returns: 
            None
    """

    count=1
    for srcFile in srcFileList:
        if not os.path.isfile(srcFile):
            print(f"File {srcFile} doesn't exist!")
            return
        
        datetime_utc = datetime.now(tz=timezone.utc)
        bbox_global=[-180,-90,180,90]
        
        footprint_polygon = Polygon([ [-180, -90],  [-180, 90],
                                      [180, 90],    [180, -90] ])
        footprint=mapping(footprint_polygon)
        
        item = pystac.Item(id=f'netcdf{count}',
                 geometry=footprint,
                 bbox=bbox_global,
                 datetime=datetime_utc,
                 properties={})
        
        item.add_asset(key=f'netcdffile{count}',
                       asset=pystac.Asset(href=srcFile,media_type=pystac.MediaType.HDF5))
        
        srcCatalog.add_item(item)
        count += 1
    return


def createImageSrcListForSTAC(srcCatalog,srcFileList):
    """Create STAC items for the image files in the input
       file list of files.

    For each of the image files in the input file list, create the STAC item and save in the input catalog file.

    Args:
            catFile : Catalog File Name.
            srcFileList : List of image files.
    Returns: 
            None
    """
    
    count=1
    for srcFile in srcFileList:
        if not os.path.isfile(srcFile):
            print(f"File {srcFile} doesn't exist!")
            return

        datetime_utc = datetime.now(tz=timezone.utc)
        bbox_global=[-180,-90,180,90]
        
        footprint_polygon = Polygon([ [-180, -90],  [-180, 90],
                                      [180, 90],    [180, -90] ])
        footprint=mapping(footprint_polygon)
        
        item = pystac.Item(id=f'image{count}',
                 geometry=footprint,
                 bbox=bbox_global,
                 datetime=datetime_utc,
                 properties={})
        
        item.add_asset(key=f'imagefile{count}',
                       asset=pystac.Asset(href=srcFile,media_type=pystac.MediaType.TEXT))
        
        srcCatalog.add_item(item)
        count += 1
    return


def createTextSrcListForSTAC(srcCatalog,srcFileList):
    """Create STAC items for the text files in the input
       file list of files.

    For each of the text files in the input file list, create the STAC item and save in the input catalog file.

    Args:
            catFile : Catalog File Name.
            srcFileList : List of text files.
    Returns:
            None
    """
    count=1
    for srcFile in srcFileList:
        if not os.path.isfile(srcFile):
            print(f"File {srcFile} doesn't exist!")
            return

        datetime_utc = datetime.now(tz=timezone.utc)
        bbox_global=[-180,-90,180,90]
        
        footprint_polygon = Polygon([ [-180, -90],  [-180, 90],
                                      [180, 90],    [180, -90] ])
        footprint=mapping(footprint_polygon)
        
        item = pystac.Item(id=f'text{count}',
                 geometry=footprint,
                 bbox=bbox_global,
                 datetime=datetime_utc,
                 properties={})
        
        item.add_asset(key=f'textfile{count}',
                       asset=pystac.Asset(href=srcFile,media_type=pystac.MediaType.TEXT))
        
        srcCatalog.add_item(item)
        count += 1
    return
