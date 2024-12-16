# FLIR Camera Control Library

A Python library for controlling FLIR cameras using the PySpin SDK. This library includes functions for initializing the camera, configuring triggers, starting acquisitions, retrieving and saving images, and shutting down the camera system.

## Features
- Initialize and configure FLIR cameras.
- Set up hardware or software triggers.
- Capture images continuously or using external triggers.
- Save images in `mono8` format.
- Reset and safely shut down the camera system.

## Installation

### Prerequisites
Before using this library, ensure you have:
1. A FLIR camera supported by the [Spinnaker SDK](https://www.flir.com/products/spinnaker-sdk/).
2. The PySpin SDK installed on your system. Refer to FLIR's [PySpin Installation Guide](https://www.flir.com/support-center/iis/machine-vision/downloads/spinnaker-sdk-and-firmware-download/) for detailed instructions.
3. Python 3.6+ installed.

### Installing the Library
1. Clone the repository from GitHub:
  ```
  git clone https://github.com/yourusername/flir-camera-control.git
  ```
2. Navigate to the cloned directory:
  ```
  cd flir-camera-control
  ```
3. Install the required dependencies (if any) using `pip`:
  ```
  pip install -r requirements.txt
  ```
