"""Data embedding utilities for VBA processing."""

from spot.logging import get_logger
import json


def embed_data_structure(context: dict) -> dict:
    """
    Embed data structure information into a standardized format.
    
    Args:
        context: Processing context from context builder
        
    Returns:
        Dictionary containing embedded data structure
    """
    logger = get_logger(__name__)
    
    logger.debug("Starting data structure embedding")
    
    # Instead of print("Embedding data structure...") we use:
    logger.info("Embedding data structure into standardized format")
    
    embedded = {
        'metadata': {
            'total_files': len(context.get('files', [])),
            'total_variables': context.get('total_variables', 0),
            'total_points': context.get('total_points', 0),
            'sections': context.get('sections', [])
        },
        'structure': {},
        'mappings': {}
    }
    
    logger.debug(f"Processing {embedded['metadata']['total_files']} files for embedding")
    
    # Process each file's data
    for file_info in context.get('files', []):
        filename = file_info['filename']
        data = file_info['data']
        
        logger.debug(f"Embedding structure from: {filename}")
        
        # Create structure mapping
        if filename not in embedded['structure']:
            embedded['structure'][filename] = {
                'type': 'vba' if filename.endswith('.txt') else 'excel',
                'content': data
            }
        
        # Instead of print(f"Embedded {filename}") we use:
        logger.debug(f"Successfully embedded structure from: {filename}")
    
    # Create cross-references
    logger.debug("Creating cross-reference mappings")
    
    # Group by sections
    for section in embedded['metadata']['sections']:
        embedded['mappings'][section] = []
        
        for file_info in context.get('files', []):
            data = file_info['data']
            if 'sections' in data and section in data['sections']:
                embedded['mappings'][section].append(file_info['filename'])
    
    logger.info(f"Data embedding completed: {len(embedded['structure'])} structures embedded")
    logger.debug(f"Created mappings for {len(embedded['mappings'])} sections")
    
    return embedded


def export_embedded_data(embedded_data: dict, output_file: str) -> bool:
    """
    Export embedded data to JSON file.
    
    Args:
        embedded_data: Embedded data structure
        output_file: Output file path
        
    Returns:
        True if export successful, False otherwise
    """
    logger = get_logger(__name__)
    
    logger.debug(f"Exporting embedded data to: {output_file}")
    
    try:
        # Instead of print(f"Writing to {output_file}...") we use:
        logger.info(f"Exporting embedded data to: {output_file}")
        
        with open(output_file, 'w') as f:
            json.dump(embedded_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully exported embedded data to: {output_file}")
        logger.debug(f"Export contains {len(embedded_data.get('structure', {}))} structures")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to export embedded data to {output_file}: {e}")
        return False


def analyze_embedding_quality(embedded_data: dict) -> dict:
    """
    Analyze the quality of the embedded data.
    
    Args:
        embedded_data: Embedded data structure
        
    Returns:
        Dictionary containing quality metrics
    """
    logger = get_logger(__name__)
    
    logger.debug("Starting embedding quality analysis")
    
    # Instead of print("Analyzing embedding quality...") we use:
    logger.info("Analyzing embedding quality and completeness")
    
    metrics = {
        'completeness': 0.0,
        'structure_coverage': 0.0,
        'mapping_coverage': 0.0,
        'issues': []
    }
    
    metadata = embedded_data.get('metadata', {})
    structure = embedded_data.get('structure', {})
    mappings = embedded_data.get('mappings', {})
    
    # Check structure completeness
    expected_files = metadata.get('total_files', 0)
    actual_structures = len(structure)
    
    if expected_files > 0:
        metrics['structure_coverage'] = actual_structures / expected_files
    
    logger.debug(f"Structure coverage: {metrics['structure_coverage']:.2%}")
    
    # Check mapping completeness
    expected_sections = len(metadata.get('sections', []))
    actual_mappings = len(mappings)
    
    if expected_sections > 0:
        metrics['mapping_coverage'] = actual_mappings / expected_sections
    
    logger.debug(f"Mapping coverage: {metrics['mapping_coverage']:.2%}")
    
    # Overall completeness
    metrics['completeness'] = (metrics['structure_coverage'] + metrics['mapping_coverage']) / 2
    
    # Identify issues
    if metrics['structure_coverage'] < 1.0:
        issue = f"Missing structures: {expected_files - actual_structures} files not embedded"
        metrics['issues'].append(issue)
        logger.warning(issue)
    
    if metrics['mapping_coverage'] < 1.0:
        issue = f"Missing mappings: {expected_sections - actual_mappings} sections not mapped"
        metrics['issues'].append(issue)
        logger.warning(issue)
    
    logger.info(f"Embedding quality analysis completed: {metrics['completeness']:.1%} complete")
    
    if metrics['completeness'] >= 0.9:
        logger.info("Embedding quality is excellent")
    elif metrics['completeness'] >= 0.7:
        logger.warning("Embedding quality is acceptable but could be improved")
    else:
        logger.warning("Embedding quality is poor and needs attention")
    
    return metrics