Before running the MT SDK Python example, the XDA (xsensdeviceapi)
Python interface needs to be installed using the included XDA wheel file.
Make sure to have the correct version of python and pip are installed on your machine.

Supported Python versions: 3.7.x up to 3.9.x

1. Make sure to have "wheel" installed on your machine:

pip install wheel

2. Install xsensdeviceapi wheel:

Located in 
Windows: <INSTALL_FOLDER>\MTSDK\Python\x64 or Win32
Linux: <INSTALL_FOLDER>/xsens/python

pip install xsensdeviceapi-<xda version>-cp<Python version>-none-<os type>.whl

For example (MTSDK 2021.0.0 wheel for Python 3.9 on Linux):
pip install xsensdeviceapi-2021.0.0-cp39-none-linux_x86_64.whl or

For example (MTSDK 2021.0.0 wheel for Python 3.9 on Windows):
pip install xsensdeviceapi-2021.0.0-cp39-none-win_amd64.whl

3. Now you are ready to run the MT SDK in Python

------------------------------------------------------------------------------------

Important:
On Windows, run examples from command prompt as Administrator to prevent permission issues (some examples use file operations).

------------------------------------------------------------------------------------

In case your Python IDE is unable to find the xsensdeviceapi module or if the
auto-completion does not work, try using:

import xsensdeviceapi.xsensdeviceapi_py<Python version>_64 as xda
instead of:
import xsensdeviceapi as xda

For example for Python 3.9:
import xsensdeviceapi.xsensdeviceapi_py39_64 as xda
