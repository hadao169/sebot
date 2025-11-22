
//  Copyright (c) 2003-2025 Movella Technologies B.V. or subsidiaries worldwide.
//  All rights reserved.
//  
//  Redistribution and use in source and binary forms, with or without modification,
//  are permitted provided that the following conditions are met:
//  
//  1.	Redistributions of source code must retain the above copyright notice,
//  	this list of conditions, and the following disclaimer.
//  
//  2.	Redistributions in binary form must reproduce the above copyright notice,
//  	this list of conditions, and the following disclaimer in the documentation
//  	and/or other materials provided with the distribution.
//  
//  3.	Neither the names of the copyright holders nor the names of their contributors
//  	may be used to endorse or promote products derived from this software without
//  	specific prior written permission.
//  
//  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
//  EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
//  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
//  THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
//  SPECIAL, EXEMPLARY OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT 
//  OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
//  HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY OR
//  TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
//  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.THE LAWS OF THE NETHERLANDS 
//  SHALL BE EXCLUSIVELY APPLICABLE AND ANY DISPUTES SHALL BE FINALLY SETTLED UNDER THE RULES 
//  OF ARBITRATION OF THE INTERNATIONAL CHAMBER OF COMMERCE IN THE HAGUE BY ONE OR MORE 
//  ARBITRATORS APPOINTED IN ACCORDANCE WITH SAID RULES.
//  

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.Windows.Threading;
using System.Threading;
using XDA;

namespace Xsens
{
	internal class MyXda : IDisposable
	{
		// Xda interface instance
		private bool _disposed = false;
		private XsControl _xda = null;
		public List<XsPortInfo> _DetectedDevices = new List<XsPortInfo>();

		public event EventHandler<PortInfoArg> WirelessMasterDetected;
		public event EventHandler<PortInfoArg> DockedMtwDetected;
		public event EventHandler<PortInfoArg> MtwUndocked;
		public event EventHandler<PortInfoArg> OpenPortSuccessful;
		public event EventHandler<PortInfoArg> OpenPortFailed;

		public MyXda()
		{
			_xda = new XsControl();
		}

		~MyXda()
		{
			if (_xda != null)
				_xda = null;
		}

		public void Dispose()
		{
			Dispose(false);
			// This object will be cleaned up by the Dispose method.
			// Therefore, you should call GC.SupressFinalize to
			// take this object off the finalization queue
			// and prevent finalization code for this object
			// from executing a second time.
			GC.SuppressFinalize(this);
		}

		private void Dispose(bool disposing)
		{
			if (!_disposed)
			{
				if (_xda != null)
				{
					_xda.close();
					_xda.Dispose();
					_xda = null;
				}
				_disposed = true;
			}
		}

        //checks if the device ID is known before returning the device
		public XsDevice getDevice(XsDeviceId deviceId)
		{
            bool knownID = false;
            for (uint i = 0; i < _xda.deviceIds().size(); ++i)
            {
                if (_xda.deviceIds().at(i).toXsString().toString() == deviceId.toXsString().toString())
                {
                    knownID = true;
                    break;
                }
            }
            if (knownID)
            {
                XsDevice p = _xda.device(deviceId);
                if (p == null)
                    return null;
                return new XsDevice(p);
            }
            else
                return null;
        }

		public void reset()
		{
			_DetectedDevices.Clear();
			_xda.close();
		}

		public bool openPort(XsPortInfo portInfo)
		{
			if (_xda.openPort(portInfo))
			{
				if (OpenPortSuccessful != null)
				{
					OpenPortSuccessful(this, new PortInfoArg(portInfo));
				}
				return true;
			}
			else
			{
				if (OpenPortFailed != null)
				{
					OpenPortFailed(this, new PortInfoArg(portInfo));
				}
				return false;
			}
		}

		private bool findPortInfo(XsPortInfo portInfo)
		{
			bool retval = false;
			foreach (XsPortInfo port in _DetectedDevices)
			{
				String did1 = port.deviceId().toXsString().toString();
				String did2 = portInfo.deviceId().toXsString().toString();
				if (port.deviceId().toXsString().toString() == portInfo.deviceId().toXsString().toString())
				{
					retval = true;
					break;
				}
			}
			return retval;
		}

		public void scanPorts()
		{
			List<XsPortInfo> scannedDevicesSet = new List<XsPortInfo>();
			XsPortInfoArray scannedDevices = XsScanner.scanPorts();

			// Check if we found new devices.
			for (uint i = 0; i < scannedDevices.size(); i++)
			{
				XsPortInfo port = scannedDevices.at(i);
				scannedDevicesSet.Add(port);
				if (!findPortInfo(port))
				{
					if (port.deviceId().isWirelessMaster())
					{
						if (WirelessMasterDetected != null)
							WirelessMasterDetected(this, new PortInfoArg(port));
					}
					else if (port.deviceId().isMtw())
					{
						if (DockedMtwDetected != null)
							DockedMtwDetected(this, new PortInfoArg(port));
					}
				}
			}

			// Check if we have lost devices (that are not opened already).
			foreach (XsPortInfo portD in _DetectedDevices)
			{
				bool found = false;
				String did = portD.deviceId().toXsString().toString();
				foreach (XsPortInfo portS in scannedDevicesSet)
				{
					if (portS.deviceId().toXsString().toString() == portD.deviceId().toXsString().toString())
						found = true;
				}
				if (!found)
				{
					if (portD.deviceId().isMtw() && MtwUndocked != null)
						MtwUndocked(this, new PortInfoArg(portD));
				}
			}

			_DetectedDevices = scannedDevicesSet;
		}
	}

	internal class MyMtCallback : XsCallback
	{
		// private RichTextBox _log;

		public event EventHandler<DataAvailableArgs> DataAvailable;
		public event EventHandler<BatteryLevelChangedArgs> BatteryLevelChanged;

		public MyMtCallback()
			: base()
		{
		}

		protected override void onLiveDataAvailable(XsDevice dev, XsDataPacket packet)
		{
			XsDevice device = new XsDevice(dev);
			XsDataPacket pack = new XsDataPacket(packet);
			if (DataAvailable != null)
			{
				DataAvailable(this, new DataAvailableArgs(device, pack));
			}
		}

		protected override void onInfoResponse(XsDevice dev, XsInfoRequest request)
		{
			XsDevice device = new XsDevice(dev);
			if (request == XsInfoRequest.XIR_BatteryLevel)
			{
				int batteryLevel = device.batteryLevel();
				if (BatteryLevelChanged != null)
				{
					BatteryLevelChanged(this, new BatteryLevelChangedArgs(device.deviceId(), batteryLevel));
				}
			}
		}
	}

	internal class MyWirelessMasterCallback : XsCallback
	{
		List<XsDeviceId> _ConnectedMtws = new List<XsDeviceId>();

		public event EventHandler<DeviceErrorArgs> DeviceError;
		public event EventHandler<DeviceIdArg> MeasurementStarted;
		public event EventHandler<DeviceIdArg> MeasurementStopped;
		public event EventHandler<DeviceIdArg> WaitingForRecordingStart;
		public event EventHandler<DeviceIdArg> RecordingStarted;
		public event EventHandler<DeviceIdArg> MtwDisconnected;
		public event EventHandler<DeviceIdArg> MtwRejected;
		public event EventHandler<DeviceIdArg> MtwPluggedIn;
		public event EventHandler<DeviceIdArg> MtwWireless;
		public event EventHandler<DeviceIdArg> MtwFile;
		public event EventHandler<DeviceIdArg> MtwUnknown;
		public event EventHandler<DeviceIdArg> MtwError;
		public event EventHandler<ProgressUpdateArgs> ProgressUpdate;

		public List<XsDeviceId> getConnectedMtws()
		{
			return _ConnectedMtws;
		}

		protected override void onConnectivityChanged(XsDevice dev, XsConnectivityState state)
		{
			XsDevice device = new XsDevice(dev);
			if (state == XsConnectivityState.XCS_Wireless)
			{
				lock (_ConnectedMtws)
				{
					_ConnectedMtws.Add(device.deviceId());
				}

			}
			else
			{
				lock (_ConnectedMtws)
				{
					_ConnectedMtws.Remove(device.deviceId());
				}
			}

			switch (state)
			{
				case XsConnectivityState.XCS_Disconnected:      /*!< Device has disconnected, only limited informational functionality is available. */
					if (MtwDisconnected != null)
						MtwDisconnected(this, new DeviceIdArg(device.deviceId()));
					break;
				case XsConnectivityState.XCS_Rejected:          /*!< Device has been rejected and is disconnected, only limited informational functionality is available. */
					if (MtwRejected != null)
						MtwRejected(this, new DeviceIdArg(device.deviceId()));
					break;
				case XsConnectivityState.XCS_PluggedIn:         /*!< Device is connected through a cable. */
					if (MtwPluggedIn != null)
						MtwPluggedIn(this, new DeviceIdArg(device.deviceId()));
					break;
				case XsConnectivityState.XCS_Wireless:          /*!< Device is connected wirelessly. */
					if (MtwWireless != null)
						MtwWireless(this, new DeviceIdArg(device.deviceId()));
					break;
				case XsConnectivityState.XCS_File:              /*!< Device is reading from a file. */
					if (MtwFile != null)
						MtwFile(this, new DeviceIdArg(device.deviceId()));
					break;
				case XsConnectivityState.XCS_Unknown:           /*!< Device is in an unknown state. */
					if (MtwUnknown != null)
						MtwUnknown(this, new DeviceIdArg(device.deviceId()));
					break;
				default:
					if (MtwError != null)
						MtwError(this, new DeviceIdArg(device.deviceId()));
					break;
			}
		}

		protected override void onDeviceStateChanged(XsDevice dev, XsDeviceState newState, XsDeviceState oldState)
		{
			XsDevice device = new XsDevice(dev);

			switch (newState)
			{
				case XsDeviceState.XDS_Config:
					if (oldState != XsDeviceState.XDS_Initial)
					{
						if (MeasurementStopped != null)
							MeasurementStopped(this, new DeviceIdArg(device.deviceId()));
					}
					break;

				case XsDeviceState.XDS_Measurement:
					if (MeasurementStarted != null)
						MeasurementStarted(this, new DeviceIdArg(device.deviceId()));
					break;

				case XsDeviceState.XDS_WaitingForRecordingStart:
					if (WaitingForRecordingStart != null)
						WaitingForRecordingStart(this, new DeviceIdArg(device.deviceId()));
					break;

				case XsDeviceState.XDS_Recording:
					if (RecordingStarted != null)
						RecordingStarted(this, new DeviceIdArg(device.deviceId()));
					break;
				default:
					break;
			}
		}

		protected override void onError(XsDevice dev, XsResultValue error)
		{
			XsDevice device = new XsDevice(dev);
			if (DeviceError != null)
				DeviceError(this, new DeviceErrorArgs(device.deviceId(), error));
		}

		protected override void onProgressUpdated(XsDevice dev, int current, int total, XsString identifier)
		{
			XsDevice device = new XsDevice(dev);
			if (ProgressUpdate != null)
				ProgressUpdate(this, new ProgressUpdateArgs(device.deviceId(), current, total, identifier.toString()));
		}
	}

	internal class ConnectedMtData
	{
		public int _batteryLevel { get; set; }
		public int _rssi { get; set; }
		public int _effectiveUpdateRate { get; set; }
		public XsEuler _orientation { get; set; }
		public XsCalibratedData _calibratedData { get; set; }
		public List<int> _frameSkipsList { get; set; }
		public uint _sumFrameSkips { get; set; }

		public ConnectedMtData()
		{
			_sumFrameSkips = 0;
			_batteryLevel = 0;
			_rssi = 0;
			_effectiveUpdateRate = 0;
		}
	}
}