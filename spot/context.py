"""Context building utilities for VBA data processing."""

from spot.logging import get_logger
from spot.loaders import load_vba_data, load_excel_data


def build_processing_context(data_files: list) -> dict:
    """
    Build processing context from multiple data files.
    
    Args:
        data_files: List of file paths to process
        
    Returns:
        Dictionary containing the processing context
    """
    logger = get_logger(__name__)
    
    logger.debug("Starting context building process")
    
    context = {
        'files': [],
        'total_variables': 0,
        'total_points': 0,
        'sections': []
    }
    
    # Instead of print(f"Processing {len(data_files)} files...") we use:
    logger.info(f"Building context from {len(data_files)} data files")
    
    for i, filename in enumerate(data_files):
        logger.debug(f"Processing file {i+1}/{len(data_files)}: {filename}")
        
        try:
            if filename.endswith('.txt'):
                data = load_vba_data(filename)
            else:
                data = load_excel_data(filename)
            
            context['files'].append({
                'filename': filename,
                'data': data
            })
            
            # Instead of print(f"Processed {filename}") we use:
            logger.debug(f"Successfully processed: {filename}")
            
        except Exception as e:
            # Instead of print(f"Error processing {filename}: {e}") we use:
            logger.warning(f"Skipping file due to error in {filename}: {e}")
            continue
    
    # Calculate totals
    for file_data in context['files']:
        data = file_data['data']
        if 'variables' in data:
            context['total_variables'] += data['variables']
        if 'points' in data:
            context['total_points'] += data['points']
        if 'sections' in data:
            context['sections'].extend(data['sections'])
    
    # Remove duplicates from sections
    context['sections'] = list(set(context['sections']))
    
    logger.info(f"Context built successfully: {len(context['files'])} files processed")
    logger.info(f"Total variables: {context['total_variables']}, total points: {context['total_points']}")
    logger.debug(f"Available sections: {', '.join(context['sections'])}")
    
    return context


def validate_context(context: dict) -> bool:
    """
    Validate the processing context.
    
    Args:
        context: Processing context dictionary
        
    Returns:
        True if context is valid, False otherwise
    """
    logger = get_logger(__name__)
    
    logger.debug("Starting context validation")
    
    # Instead of print("Validating context...") we use:
    logger.info("Validating processing context")
    
    if not context.get('files'):
        logger.error("Context validation failed: No files processed")
        return False
    
    if context.get('total_variables', 0) == 0:
        logger.warning("No variables found in context")
    
    if context.get('total_points', 0) == 0:
        logger.warning("No points found in context")
    
    if not context.get('sections'):
        logger.error("Context validation failed: No sections found")
        return False
    
    logger.info("Context validation passed")
    logger.debug(f"Validated context with {len(context['files'])} files and {len(context['sections'])} sections")
    
    return True