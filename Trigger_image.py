import PySpin
import sys

def init_camera()->tuple:
    '''
    Initialize FLIR camera
    '''
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
        
def configure_trigger(cam)->bool:
    """
    This function configures the camera to use a trigger. First, trigger mode is
    ensured to be off in order to select the trigger source. Trigger mode is
    then enabled, which has the camera capture only a single image upon the
    execution of the chosen trigger.

     :param cam: Camera to configure trigger for.
     :type cam: CameraPtr
     :return: True if successful, False otherwise.
     :rtype: bool
    """

    print('*** CONFIGURING TRIGGER ***\n')

    try:
        result = True

        # Ensure trigger mode off
        # The trigger must be disabled in order to configure whether the source
        # is software or hardware.
        if cam.TriggerMode.GetAccessMode() != PySpin.RW:
            print('Unable to disable trigger mode (node retrieval). Aborting...')
            return False

        cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)

        print('Trigger mode disabled...')

        # Set TriggerSelector to FrameStart
        # For this example, the trigger selector should be set to frame start.
        # This is the default for most cameras.
        if cam.TriggerSelector.GetAccessMode() != PySpin.RW:
            print('Unable to get trigger selector (node retrieval). Aborting...')
            return False

        cam.TriggerSource.SetValue(PySpin.TriggerSelector_FrameStart)

        print('Trigger selector set to frame start...')

        # Select trigger source
        # The trigger source must be set to hardware or software while trigger
        # mode is off.
        if cam.TriggerSource.GetAccessMode() != PySpin.RW:
            print('Unable to get trigger source (node retrieval). Aborting...')
            return False

        cam.TriggerSource.SetValue(PySpin.TriggerSource_Line0)
        print('Trigger source set to hardware...')

        # Turn trigger mode on
        # Once the appropriate trigger source has been set, turn trigger mode
        # on in order to retrieve images using the trigger.
        cam.TriggerSelector.SetValue(PySpin.TriggerSelector_FrameStart)
        cam.TriggerActivation.SetValue(PySpin.TriggerActivation_RisingEdge)
        cam.TriggerMode.SetValue(PySpin.TriggerMode_On)
        print('Trigger mode turned back on...')

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result


def acquire_image(cam)->bool:
    """
    This function acquires and saves 10 images from a device.
    Please see Acquisition example for more in-depth comments on acquiring images.

    :param cam: Camera to acquire images from.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    print('*** IMAGE ACQUISITION ***\n')
    
    image_result = None
    
    try:
        # Set acquisition mode to continuous
        if cam.AcquisitionMode.GetAccessMode() != PySpin.RW:
            print('Unable to set acquisition mode to continuous. Aborting...')
            return False

        cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
        print('Acquisition mode set to continuous...')

        #  Begin acquiring images
        cam.BeginAcquisition()
        print('Acquiring images: waiting for external trigger')

        # Get device serial number for filename
        device_serial_number = ''
        if cam.TLDevice.DeviceSerialNumber.GetAccessMode() == PySpin.RO:
            device_serial_number = cam.TLDevice.DeviceSerialNumber.GetValue()

            print('Device serial number retrieved as %s...' % device_serial_number)

        #  Retrieve next received image
        image_result = cam.GetNextImage()

        # End acquisition
        cam.EndAcquisition()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)

    #  Ensure image completion
    if image_result.IsIncomplete():
        print('Image incomplete with image status %d ...' % image_result.GetImageStatus())
        image_result = None
    else:
        print('Image acquired correcly')
    
    return image_result

def save_image(image_result, filename='Triggered_image.jpg'):
    # Create ImageProcessor instance for post processing images
    print('*** SAVING IMAGE ***\n')
    
    try:
        processor = PySpin.ImageProcessor()

        # Set image processor color processing method
        processor.SetColorProcessing(PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_HQ_LINEAR)
        
        
        #  Print image information
        width = image_result.GetWidth()
        height = image_result.GetHeight()
        
        print('Processing image, width = %d, height = %d' % (width, height))

        #  Convert image to mono 8
        image_converted = processor.Convert(image_result, PySpin.PixelFormat_Mono8)
        # Save image
        image_converted.Save(filename)

        print('Image saved at %s\n' % filename)

        #  Release image
        image_result.Release()
        
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)

def reset_trigger(cam)->bool:
    """
    This function returns the camera to a normal state by turning off trigger mode.

    :param cam: Camera to acquire images from.
    :type cam: CameraPtr
    :returns: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True
        # Ensure trigger mode off
        # The trigger must be disabled in order to configure whether the source
        # is software or hardware.
        if cam.TriggerMode.GetAccessMode() != PySpin.RW:
            print('Unable to disable trigger mode (node retrieval). Aborting...')
            return False

        cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)

        print('Trigger mode disabled...')

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result
    
def close_camera(cam, cam_list:list, system: PySpin.SystemPtr):
    '''
    End acquisition and deinitialize FLIR camera
    '''
    try:
        cam.DeInit()
        cam_list.Clear()
        system.ReleaseInstance()
        print('Camera correcly closed.')
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)