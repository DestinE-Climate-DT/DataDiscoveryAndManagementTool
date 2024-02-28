"""
This module contains the APIs for updating the intake catalog for each app and each of it's file types.
These APIs need to be called by the app data curator for maintaining the intake catalog.
"""

#Standard modules
import os
import sys
import subprocess
import itertools
import importlib
from pathlib import Path

#Non-standard modules
try:
    import intake
    import yaml
except:
    print( sys.exc_info() )
    print( f"Module 'intake/yaml' import error in {__file__}" )

#Local modules
try:
    from .config import configAppdataexplorer
except:
    print( sys.exc_info() )
    print( f"Module 'config' import error in {__file__}" )

try:
    from .utils import getAppSrcFileList
except:
    print( sys.exc_info() )
    print( f"Module 'utils' import error in {__file__}" )


def createMasterIntakeCatalog( catalogFileName ):
    """Create master catalog file for the HPC centers.

    Create the top level master catalog containing the links to the yaml files for the HPC centers.

    Args:
            catalogFileName : String to hold the name of top level catalog file that would be created.
    Returns: 
            None
    """
    localconfig = configAppdataexplorer.activeConfig
    outputPath = localconfig.getOutputPath()
    
    sources={}
    sources.setdefault( "sources", {} )
    
    for hpc in localconfig.getHPCCenters():
        sources[ "sources" ].setdefault( hpc, {} )
        argsdict={
              "description": f"{hpc} data catalog",
              "driver":"yaml_file_cat",
              "args":
                    {
                        "path":os.path.join( "{{CATALOG_DIR}}", f"{hpc}", f"{hpc}.yaml" )
                    }
                }
        sources[ "sources" ][ hpc ]=argsdict
        
    if not os.path.exists( f"{outputPath}" ):
        Path( f"{outputPath}" ).mkdir( parents=True, exist_ok=True ) 
    else:
        if os.path.isfile( os.path.join( f"{outputPath}", f"{catalogFileName}.yaml" ) ):
            # TODO: If update then read the exisitng yaml file and compare with the 'sources'
            #       created above based on the 'config.json' parameters. Update if any missing 
            #       items into the existing yaml tree and dump this updated 'sources' to file.
            # If update is 'false' , i.e., create fresh catalog, then delete the existing yaml
            #       file and create a new one.
            Path( os.path.join( f"{outputPath}", f"{catalogFileName}.yaml" ) ).unlink( missing_ok = True ) 

    try:
        with open( os.path.join( f"{outputPath}", f"{catalogFileName}.yaml" ), "w"  ) as f:
            f.write(
                "description: 'DestinE data discovery tool-appdataexplorer, intake catalog for the data produced at various HPC centers.'\n")
            yaml.dump( sources, f, sort_keys=False )
            f.close()
    except OSError as err:
        print( f"Error {err} while writing {os.path.join( {outputPath}, {catalogFileName}.yaml )}!" )
        return
        
    createHPCIntakeCatalog()


def createHPCIntakeCatalog():
    """Create yaml files for the HPC centers.

    For each of the HPC centers, create the yaml files containing the links to the yaml files for the Apps .

    Args:
            None
    Returns: 
            None
    """
    localconfig = configAppdataexplorer.activeConfig
    outputPath = localconfig.getOutputPath()

    sources={}
    sources.setdefault("sources",{})

    for hpc, app  in itertools.product( localconfig.getHPCCenters(),
                                        localconfig.getappNames() ):

        sources["sources"].setdefault( app, {} )
        pathValue = os.path.join( r"{{CATALOG_DIR}}", f"{app}", f"{app}.yaml" )
        argsdict={
              "description": f"{app} application data catalog",
              "driver":"yaml_file_cat",
              "args":
                    {
                      "path": os.path.join(  r"{{CATALOG_DIR}}", f"{app}", f"{app}.yaml" )
                        
                    }
                }

        sources["sources"][app]=argsdict

        hpcCatalogPath = os.path.join( outputPath, f"{hpc}" )
        if not os.path.exists( hpcCatalogPath ):
            os.makedirs( hpcCatalogPath, exist_ok=True )

        hpcCatalog = os.path.join(hpcCatalogPath,f"{hpc}.yaml")
        
        if os.path.isfile( hpcCatalog ):
            # TODO: If update then read the exisitng yaml file and compare with the 'sources'
            #       created above based on the 'config.json' parameters. Update if any missing 
            #       items into the existing yaml tree and dump this updated 'sources' to file.
            # If update is 'false' , i.e., create fresh catalog, then delete the existing yaml
            #       file and create a new one.
            Path( hpcCatalog ).unlink( missing_ok=True )

        try:
            with open( f"{hpcCatalog}", "w" ) as f:
                f.write("description: "+ f"\'Catalog for application data produced by the desitnation earth twin engine simulations performed on {hpc}.\'\n" )
                yaml.dump( sources, f, sort_keys=False )
                f.close()
        except OSError as err:
            print( f"Error {err} while writing {hpcCatalog}!" )
            return

    createAppIntakeCatalog()


def createAppIntakeCatalog():
    """Create yaml files for the Apps.

    For each of the Apps, create the yaml files containing the links to the yaml files for the ESMs .

    Args:
            None
    Returns: 
            None
    """
    localconfig = configAppdataexplorer.activeConfig
    outputPath = localconfig.getOutputPath()
    
    sources={}
    sources.setdefault("sources",{})

    for hpc, app, esm  in itertools.product( localconfig.getHPCCenters(),
                                             localconfig.getappNames(),
                                             localconfig.getESMs() ):

        sources["sources"].setdefault( esm, {}) 
        argsdict={
              "description": f" \'{esm} GSV data catalog \' ",
              "driver":"yaml_file_cat",
              "args":
                    {
                      "path":os.path.join( "{{CATALOG_DIR}}", f"{esm}", f"{esm}.yaml" )
                    }
                }
        sources["sources"][esm]=argsdict
            
        appCatalogPath = os.path.join( outputPath, f"{hpc}", f"{app}")
        if not os.path.exists( appCatalogPath ):
            os.makedirs( appCatalogPath, exist_ok=True )

        appCatalog = os.path.join( appCatalogPath, f"{app}.yaml" )

        if os.path.isfile( appCatalog ):
            # TODO: If update then read the exisitng yaml file and compare with the 'sources'
            #       created above based on the 'config.json' parameters. Update if any missing 
            #       items into the existing yaml tree and dump this updated 'sources' to file.
            # If update is 'false' , i.e., create fresh catalog, then delete the existing yaml
            #       file and create a new one.
            Path( appCatalog ).unlink( missing_ok=True )

        try:
            with open( appCatalog, "w" ) as f:
                f.write( f"description: {app} application data catalog\n" )
                yaml.dump( sources, f, sort_keys=False )
                f.close()
        except OSError as err:
            print( f" Error {err} while writing {appCatalog}!" )
            return

        
    print('calling createESMIntakeCatalog()')        
    createESMIntakeCatalog()
    

def createESMIntakeCatalog():
    """Create yaml files for the ESMs.

    For each of the ESMs, create the yaml files containing the links to the yaml files for the available sources .

    Args:
            None
    Returns: 
            None
    """
    localconfig = configAppdataexplorer.activeConfig
    outputPath = localconfig.getOutputPath()
       
    sources={}
    sources.setdefault( "sources", {} )
    
    
    for hpc, app, esm  in itertools.product( localconfig.getHPCCenters(),
                                             localconfig.getappNames(),
                                             localconfig.getESMs() ):
        currentAppSrcDict = {}
        currentAppDataSrcs = localconfig.getappDataSrcs( app )

        sources={}
        sources.setdefault( "sources", {} )
    
        for src in currentAppDataSrcs:

            sources["sources"].setdefault( src, {} )
            argsdict={
                  "description": f"{src} files data catalog",
                  "driver":"yaml_file_cat",
                  "args":
                        {
                          "path":os.path.join( "{{CATALOG_DIR}}", f"{src}", f"{src}.yaml")
                        }
                    }

            sources["sources"][src]=argsdict

        esmCatalogPath = os.path.join( outputPath, f"{hpc}", f"{app}", f"{esm}" )
                
        if not os.path.exists( esmCatalogPath ):
            os.makedirs( esmCatalogPath, exist_ok=True )

        esmCatalog = os.path.join( esmCatalogPath, f"{esm}.yaml" )

        if os.path.isfile( esmCatalog ):
            # TODO: If update then read the exisitng yaml file and compare with the 'sources'
            #       created above based on the 'config.json' parameters. Update if any missing 
            #       items into the existing yaml tree and dump this updated 'sources' to file.
            # If update is 'false' , i.e., create fresh catalog, then delete the existing yaml
            #       file and create a new one.
            Path( esmCatalog ).unlink( missing_ok=True )
        
        try:
            with open( esmCatalog, "w" ) as f:
                f.write(f"description: 'Catalog for files generated from {esm} GSV.  '\n")
                yaml.dump( sources, f, sort_keys=False )
                f.close()
        except OSError as err:
            print( f"Error {err} while writing {esmCatalog}!" )
            return

    print('calling createESMIntakeCatalog()')        
    createSrcIntakeCatalog()

            
def createSrcIntakeCatalog():
    """Create yaml files for the sources.

    For each of the app, check the available sources (file types) and  create the corresponding yaml files.

    Args:
            None
    Returns: 
            None
    """
    localconfig = configAppdataexplorer.activeConfig
    outputPath = localconfig.getOutputPath()

    appDataSrcNameFileExt = localconfig.getappDataSrcNameFileExt()

    for hpc, app, esm  in itertools.product( localconfig.getHPCCenters(),
                                             localconfig.getappNames(),
                                             localconfig.getESMs()):

        currentAppDataSrcs = localconfig.getappDataSrcs(app)
        print( f"Ingesting '{app}' data produced using GSV from {esm} simulations performed on {hpc}" )
        
        for src in currentAppDataSrcs:
            srcCatalogPath = os.path.join( outputPath, f"{hpc}", f"{app}", f"{esm}", f"{src}" )

            if not os.path.exists( srcCatalogPath ):
                os.makedirs( srcCatalogPath, exist_ok=True )
            srcCatalog = os.path.join( outputPath, f"{hpc}", f"{app}", f"{esm}", f"{src}", f"{src}.yaml" )

            srcExtList = appDataSrcNameFileExt[src]
            createIntakeCatalogSourcesForFileList( app, src, srcCatalog, getAppSrcFileList( app, src, esm, srcExtList ) )

            
def createIntakeCatalogSourcesForFileList( app, src, catFile, srcFileList ):
    """Create catalog for the sources for the inout file list.

    For all the source files, create the intake counterparts and write out to the catalog file.

    Args:
            app : application Name
            src : source Name
            catFile : Catalog File Name.
            srcFileList : List of netcdf files.
    Returns:
            None
    """
    
    localconfig = configAppdataexplorer.activeConfig
    #  Fetch the 'metadata' keys for this 'app' from 'appDescInfo'.
    appMetadataKeys = localconfig.getappMetadataKeys(app)
    
    #intakeSrcList = map(intakeSrcCreator,srcFileList)
    if os.path.isfile( catFile ):
    # TODO: If update then read the exisitng yaml file and compare with the 'sources'
    #       created above based on the 'config.json' parameters. Update if any missing 
    #       items into the existing yaml tree and dump this updated 'sources' to file.
    # If update is 'false' , i.e., create fresh catalog, then delete the existing yaml
    #       file and create a new one.
        Path( catFile ).unlink( missing_ok = True )
        
    sources={}
    sources.setdefault( "sources", {} )

    try:
        srcCatalogFile = open( catFile, "w" )
    except OSError as err:
        print(f"Error {err} while opening {catFile}!")
        return
    
    srcCatalogFile.write( f"description: 'Catalog for {src} files.'\n" )
    yaml.dump( sources, srcCatalogFile, sort_keys = False )
    srcCatalogFile.close()
    
    srcCatalog = intake.open_catalog( catFile )

    intakeSrcList = []
    count = 1
    
    intakeSrcList = map( intakeSrcCreator, itertools.repeat( app,len( srcFileList ) ),
                    itertools.repeat( src, len(srcFileList)), srcFileList,
                    itertools.repeat( appMetadataKeys, len( srcFileList ) ) )
    
    
    # Add the sources to the catalog.
    for intakeSrc in intakeSrcList:
        if intakeSrc is not None:
            intakeSrc.name = f"{src}{count}"
            srcCatalog = srcCatalog.add( intakeSrc )
            count += 1

    srcCatalog.save( catFile )
        
    return


def intakeSrcCreator( app, src, srcFile, appMetadataKeys ):
    """Create yaml resource for the input source file.

    For the input file of given source and app and metadata keys, prepare the intake object.

    Args:
            app : application Name
            src : source Name
            catFile : Catalog File Name.
            srcFileList : List of netcdf files.
    Returns:
            intakeSrc : intake catalog object.
    """
    
    if not os.path.isfile( srcFile ):
        print( f"File {srcFile} doesn't exist!" )
        return None

    # Create source.
    if src == 'netcdf':
        intakeSrc = intake.open_netcdf( srcFile )
    elif src == 'image':
        intakeSrc = intake.open_rasterio( srcFile )
    elif src == 'text':
        intakeSrc = intake.open_textfiles( srcFile )
    else:
        print( f'Source type {src} not handled! \n Ignoring {srcFile} in intakeSrcCreator.' )

    #create metadata for source.
    intakeSrc.metadata = {}

    #  Fetch the 'metadata' values from the 'srcFile' by removing file suffix and splitting with '_'.
    metadataValues = os.path.basename( srcFile ).split('.')[0].split('_')

    # NOTE: The metadata keys have fixed order as the file name parts seperated by '_'.
    if len( metadataValues ) < len( appMetadataKeys ) :
        for i in range( len( metadataValues ),len( appMetadataKeys ) ):
            metadataValues.append('-')

    for key in appMetadataKeys:
        if app == 'AQUA':
            intakeSrc.metadata[key] =  metadataValues[ appMetadataKeys.index( key ) ]
        # TODO for other apps once the data is available.
        else:
            print('Metadata not available')
    
    return intakeSrc