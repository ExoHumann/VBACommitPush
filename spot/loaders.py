"""Data loaders for VBA files."""

from spot.logging import get_logger


def load_vba_data(filename: str) -> dict:
    """
    Load VBA data from file.
    
    Args:
        filename: Path to the VBA data file
        
    Returns:
        Dictionary containing parsed VBA data
    """
    logger = get_logger(__name__)
    
    logger.debug(f"Starting to load VBA data from: {filename}")
    
    try:
        # Simulate loading process
        logger.info(f"Loading VBA data file: {filename}")
        
        # Instead of print("Processing data...") we use:
        logger.debug("Processing data sections...")
        
        # Simulate some processing
        data = {
            'sections': ['CrossSection', 'DeckObject', 'BearingArticulation'],
            'variables': 150,
            'points': 50
        }
        
        logger.info(f"Successfully loaded {data['variables']} variables and {data['points']} points")
        logger.debug("VBA data loading completed")
        
        return data
        
    except FileNotFoundError:
        logger.error(f"VBA data file not found: {filename}")
        raise
    except Exception as e:
        logger.error(f"Failed to load VBA data from {filename}: {e}")
        raise


def load_excel_data(filename: str) -> dict:
    """
    Load Excel data files.
    
    Args:
        filename: Path to Excel data file
        
    Returns:
        Dictionary containing parsed Excel data
    """
    logger = get_logger(__name__)
    
    logger.debug(f"Loading Excel data from: {filename}")
    
    # Instead of print("Reading Excel file...") we use:
    logger.info(f"Reading Excel file: {filename}")
    
    # Simulate Excel processing
    logger.debug("Parsing Excel sheets and cells...")
    
    result = {
        'sheets': 3,
        'rows': 1000,
        'columns': 12
    }
    
    logger.info(f"Excel data loaded: {result['sheets']} sheets, {result['rows']} rows")
    
    return result