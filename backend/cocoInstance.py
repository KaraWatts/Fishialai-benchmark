from cocoapi.PythonAPI.pycocotools.coco import COCO

coco = None

def set_coco_instance(file_path):
    '''
    Initializes COCO instance for the given file path
    
    Parameters:
    file_path: str
    '''
    global coco
    coco = COCO(file_path)


def get_coco_instance():
    '''
    Checks if COCO instance is initialized and returns it

    Parameters:
    None

    Returns:
    COCO: COCO instance

    Raises:
    Exception: If COCO instance is not initialized
    '''
    if not coco:
        raise Exception("COCO instance not initialized")
    return coco