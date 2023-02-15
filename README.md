# optitrack_data_capture
This repo is to use the Optitrack Trio camera to record 3D pos data of markers.
Maintainers: Mark Lee, Sarvesh Patil

# installation
Install Optitrack Motive 2.3.2 from [this Windows installer](https://optitrack.com/support/downloads/)
Trio is only supported by 2.3.2 software NOT 3.0.2.

Install the NatNet SDK 4.0.0 from [this Windows installer](https://optitrack.com/support/downloads/developer-tools.html#natnet-sdk)
This SDK includes samples, which we will be using the Python Client to interface with Motive Data Stream.

Clone this repository which includes the modified NatNetClient.py and IAM_mocap_server.py files. Replace the NatNetClient.py with the one from this repo.

# usage
Modify the NUM_MARKERS and SAVE_PATH in the IAM_mocap_server.py files.
```
cd `directory_to_\Users\Mark\Desktop\NatNetSDK\Samples\PythonClient\optitrack_data_capture`
python IAM_mocap_server.py
```
