import PySpin
import sys

def init_camera() -> tuple:
    """
    Initialize the FLIR camera system and retrieve the first available camera.

    Returns
    -------
    tuple
        A tuple containing:
        - cam (PySpin.CameraPtr): The initialized camera object.
        - cam_list (PySpin.CameraList): List of connected cameras.
        - system (PySpin.SystemPtr): PySpin system instance.
    """
    cam = None
    print('*** INITIALIZING CAMERA ***\n')
    try:
        system = PySpin.System.GetInstance()
        cam_list = system.GetCameras()
        cam = cam_list.GetByIndex(0)
        cam.Init()
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
    
    return cam, cam_list, system

def configure_trigger(cam) -> bool:
    """
    Configure the camera to use a hardware or software trigger.

    Ensures the trigger mode is off before setting the trigger source and activation type. 
    Finally, enables the trigger mode for the camera to capture a single image upon trigger.

    Parameters
    ----------
    cam : PySpin.CameraPtr
        The camera to configure the trigger for.

    Returns
    -------
    bool
        True if the configuration is successful, False otherwise.
    """
    print('*** CONFIGURING TRIGGER ***\n')
    try:
        result = True

        if cam.TriggerMode.GetAccessMode() != PySpin.RW:
            print('Unable to disable trigger mode (node retrieval). Aborting...')
            return False
        
        cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
        print('Trigger mode disabled...')

        cam.TriggerSource.SetValue(PySpin.TriggerSelector_FrameStart)
        print('Trigger selector set to frame start...')

        cam.TriggerSource.SetValue(PySpin.TriggerSource_Line0)
        print('Trigger source set to Line 0...')

        cam.TriggerActivation.SetValue(PySpin.TriggerActivation_RisingEdge)
        print('Trigger activation set to RisingEdge...')
        
        cam.TriggerMode.SetValue(PySpin.TriggerMode_On)
        print('Trigger mode turned back on...')
        
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result

def Start_acquisition(cam) -> bool:
    """
    Start image acquisition on the camera in continuous mode.

    Sets the camera acquisition mode to continuous and begins acquisition. 
    This function assumes an external trigger will control the capture timing.

    Parameters
    ----------
    cam : PySpin.CameraPtr
        The camera to acquire images from.

    Returns
    -------
    bool
        True if the acquisition is started successfully, False otherwise.
    """
    print('*** IMAGE ACQUISITION ***\n')
    try:
        if cam.AcquisitionMode.GetAccessMode() != PySpin.RW:
            print('Unable to set acquisition mode to continuous. Aborting...')
            return False
        
        cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
        print('Acquisition mode set to continuous...')

        cam.BeginAcquisition()
        print('Acquiring images: waiting for external trigger')
        
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False
    
    return True

def GetImage(cam):
    """
    Retrieve the next image from the camera.

    Blocks until an image is received or the timeout expires.

    Parameters
    ----------
    cam : PySpin.CameraPtr
        The camera to retrieve an image from.

    Returns
    -------
    PySpin.ImagePtr or None
        The retrieved image object, or None if an error occurs.
    """
    image_result = None
    try:
        image_result = cam.GetNextImage(500)
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
    return image_result

def save_image(image_result, filename='Triggered_image.jpg'):
    """
    Save a captured image to a file after converting its format.

    The image is converted to mono8 format and saved with the specified filename. 
    Basic image information such as width and height is also printed.

    Parameters
    ----------
    image_result : PySpin.ImagePtr
        The captured image to process and save.
    filename : str, optional
        The filename to save the image as. Default is 'Triggered_image.jpg'.
    """
    print('*** SAVING IMAGE ***\n')
    try:
        processor = PySpin.ImageProcessor()
        processor.SetColorProcessing(PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_HQ_LINEAR)
        
        width = image_result.GetWidth()
        height = image_result.GetHeight()
        print('Processing image, width = %d, height = %d' % (width, height))

        image_converted = processor.Convert(image_result, PySpin.PixelFormat_Mono8)
        image_converted.Save(filename)
        print('Image saved at %s\n' % filename)

        image_result.Release()
        print('Got image. Acquisition ended.')
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)

def reset_trigger(cam) -> bool:
    """
    Reset the camera by disabling the trigger mode.

    Parameters
    ----------
    cam : PySpin.CameraPtr
        The camera to reset the trigger mode for.

    Returns
    -------
    bool
        True if the trigger is successfully disabled, False otherwise.
    """
    try:
        result = True

        if cam.TriggerMode.GetAccessMode() != PySpin.RW:
            print('Unable to disable trigger mode (node retrieval). Aborting...')
            return False
        
        cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
        print('Trigger mode disabled...')
        
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result

def close_camera(cam, cam_list: list, system: PySpin.SystemPtr):
    """
    End image acquisition, deinitialize the camera, and release system resources.

    Cleans up by stopping acquisition, deinitializing the camera, clearing the camera list, 
    and releasing the PySpin system instance.

    Parameters
    ----------
    cam : PySpin.CameraPtr
        The camera to close.
    cam_list : list
        The list of connected cameras.
    system : PySpin.SystemPtr
        The PySpin system instance to release.
    """
    try:
        cam.EndAcquisition()
        cam.DeInit()
        cam_list.Clear()
        system.ReleaseInstance()
        print('Camera correctly closed.')
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)