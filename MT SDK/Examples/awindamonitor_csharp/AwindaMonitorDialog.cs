
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

﻿using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.IO;
using System.Threading;
using System.Windows.Threading;
using Xsens;
using XDA;

namespace AwindaMonitor
{
	public partial class AwindaMonitorDialog : Form
	{
		enum States {
			DETECTING,
			CONNECTING,
			CONNECTED,
			ENABLED,
			OPERATIONAL,
			AWAIT_MEASUREMENT_START,
			MEASURING,
			AWAIT_RECORDING_START,
			RECORDING,
			FLUSHING
		};

		States _state;

		XsDevice _MyWirelessMasterDevice;

		private System.Windows.Forms.Timer _portScanTimer;
		private System.Windows.Forms.Timer _batteryLevelRequestTimer;
		
		// Connected MTw's
		internal List<XsDevice> _mtws = new List<XsDevice>();

		private MyXda _myxda;
		// Callback handler to track connectivity and data
		private MyWirelessMasterCallback m_myWirelessMasterCallback;
		private Dictionary<XsDevice, MyMtwCallback> _measuringMtws;
		private Dictionary<XsDevice, MyMtwCallback>.Enumerator _nextBatteryRequest;
		private Dictionary<uint, ConnectedMTwData> _connectedMtwData;

        private Thread _scanThread;

		public AwindaMonitorDialog()
		{
			InitializeComponent();

			_measuringMtws = new Dictionary<XsDevice, MyMtwCallback>();
			_connectedMtwData = new Dictionary<uint, ConnectedMTwData>();

			// create xda instance and set up callback handling
			_myxda = new MyXda();
			_myxda.WirelessMasterDetected += new EventHandler<PortInfoArg>(_myxda_WirelessMasterDetected);
			_myxda.DockedMtwDetected += new EventHandler<PortInfoArg>(_myxda_DockedMtwDetected);
			_myxda.MtwUndocked += new EventHandler<PortInfoArg>(_myxda_MtwUndocked);
			_myxda.OpenPortSuccessful += new EventHandler<PortInfoArg>(_myxda_OpenPortSuccessful);
			_myxda.OpenPortFailed += new EventHandler<PortInfoArg>(_myxda_OpenPortFailed);
			
			m_myWirelessMasterCallback = new MyWirelessMasterCallback();
			m_myWirelessMasterCallback.MtwWireless += new EventHandler<DeviceIdArg>(_callbackHandler_MtwWireless);                 
			m_myWirelessMasterCallback.MtwDisconnected += new EventHandler<DeviceIdArg>(_callbackHandler_MtwDisconnected);      
			m_myWirelessMasterCallback.MeasurementStarted += new EventHandler<DeviceIdArg>(_callbackHandler_MeasurementStarted);      
			m_myWirelessMasterCallback.MeasurementStopped += new EventHandler<DeviceIdArg>(_callbackHandler_MeasurementStopped);      
			m_myWirelessMasterCallback.DeviceError += new EventHandler<DeviceErrorArgs>(_callbackHandler_DeviceError);      
			m_myWirelessMasterCallback.WaitingForRecordingStart += new EventHandler<DeviceIdArg>(_callbackHandler_WaitingForRecordingStart);      
			m_myWirelessMasterCallback.RecordingStarted += new EventHandler<DeviceIdArg>(_callbackHandler_RecordingStarted);      
			m_myWirelessMasterCallback.ProgressUpdate += new EventHandler<ProgressUpdateArgs>(_callbackHandler_ProgressUpdate);

			_portScanTimer = new System.Windows.Forms.Timer();
			_portScanTimer.Interval = 1000;
			_portScanTimer.Tick += new EventHandler(scanPorts);

			_batteryLevelRequestTimer = new System.Windows.Forms.Timer();
			_batteryLevelRequestTimer.Interval = 1000;
			_batteryLevelRequestTimer.Tick += new EventHandler(requestBatteryLevels);

			_state = States.DETECTING;
			log("Detecting...");
			setWidgetsStates();

			comboBoxChannel.SelectedIndex = 0;

			_portScanTimer.Enabled = true;
			_batteryLevelRequestTimer.Enabled = true;
		}

		private void requestBatteryLevels(object sender, EventArgs e)
		{
			if (_measuringMtws.Count == 0)
				return;
			// It is impossible to request battery status for all MTWs at once. So cycle between them
			if (!_nextBatteryRequest.MoveNext()) 
			{
				_nextBatteryRequest = _measuringMtws.GetEnumerator();
			}
			else
				_nextBatteryRequest.Current.Key.requestBatteryLevel();
		}

		private void scanPorts(object sender, EventArgs e)
		{
            if (_scanThread == null)
            {
                if (_state != States.MEASURING || _state != States.AWAIT_MEASUREMENT_START || _state != States.RECORDING || _state != States.FLUSHING)
                {
                    _scanThread = new Thread(_myxda.scanPorts);
                    _scanThread.Start();
                }
            }
		}

		void _myxda_WirelessMasterDetected(object sender, PortInfoArg e)
		{
            if (_myxda != null)
            {
                if (InvokeRequired)
                {
                    // Update UI, make sure this happens on the UI thread
                    BeginInvoke(new Action(delegate { _myxda_WirelessMasterDetected(sender, e); }));
                }
                else
                {
                    switch (_state)
                    {
                        case States.DETECTING:
                            log(String.Format("Master Detected. Port: {0}, ID: {1}", e.PortInfo.portName().toString(), e.PortInfo.deviceId().toXsString().toString()));
                            _state = States.CONNECTING;
                            _myxda.openPort(e.PortInfo);
                            setWidgetsStates();
                            break;
                        default:
                            break;
                    }
                }
            }

        }
		void _myxda_DockedMtwDetected(object sender, PortInfoArg e)
		{
			if (InvokeRequired)
			{
				// Update UI, make sure this happens on the UI thread
				BeginInvoke(new Action(delegate { _myxda_DockedMtwDetected(sender, e); }));
			}
			else
			{
				log(String.Format("MTw Docked. Port: {0}, ID: {1}", e.PortInfo.portName().toString(), e.PortInfo.deviceId().toXsString().toString()));

				String mtwId = e.PortInfo.deviceId().toXsString().toString();
				if (dockedMtwList.FindStringExact(mtwId) == ListBox.NoMatches)
				{
					dockedMtwList.Items.Add(mtwId);
				}
				dockedMtwListGroupBox.Text = String.Format("Docked MTw list ({0}):", dockedMtwList.Items.Count);
			}
		}
		void _myxda_MtwUndocked(object sender, PortInfoArg e)
		{
			if (InvokeRequired)
			{
				// Update UI, make sure this happens on the UI thread
				BeginInvoke(new Action(delegate { _myxda_MtwUndocked(sender, e); }));
			}
			else
			{
				log(String.Format("MTw Undocked. Port: {0}, ID: {1}", e.PortInfo.portName().toString(), e.PortInfo.deviceId().toXsString().toString()));

				String mtwId = e.PortInfo.deviceId().toXsString().toString();

				dockedMtwList.Items.Remove(mtwId);
				dockedMtwListGroupBox.Text = String.Format("Docked MTw list ({0}):", dockedMtwList.Items.Count);
			}
		}
		void _myxda_OpenPortSuccessful(object sender, PortInfoArg e)
		{
			if (InvokeRequired)
			{
				// Update UI, make sure this happens on the UI thread
				BeginInvoke(new Action(delegate { _myxda_OpenPortSuccessful(sender, e); }));
			}
			else
			{
				// Update the UI			
				switch (_state)
				{
				case States.CONNECTING:
					if (e.PortInfo.deviceId().isWirelessMaster())
					{
						// Set the label to indicate the ID of the station.
						labelStationId.Text = e.PortInfo.deviceId().toXsString().toString();
						_MyWirelessMasterDevice = _myxda.getDevice(e.PortInfo.deviceId());

						// Attach the callback handler. This causes events to arrive in m_myWirelessMasterCallback.
						_MyWirelessMasterDevice.addCallbackHandler(m_myWirelessMasterCallback);

						_state = States.CONNECTED;
						log(String.Format("Master Connected. Port: {0}, ID: {1}", e.PortInfo.portName().toString(), e.PortInfo.deviceId().toXsString().toString()));

						// Be sure to start with radio disabled
						if (_MyWirelessMasterDevice.isRadioEnabled())
						{
							SetRadioChannel(-1);
						}

						setWidgetsStates();
					}
					break;
				default:
					break;
				}
			}
		}
		void _myxda_OpenPortFailed(object sender, PortInfoArg e)
		{
			if (InvokeRequired)
			{
				// Update UI, make sure this happens on the UI thread
				BeginInvoke(new Action(delegate { _myxda_OpenPortFailed(sender, e); }));
			}
			else
			{
				if (e.PortInfo.deviceId().isWirelessMaster())
				{
					log(String.Format("Connect to wireless master failed. Port: {0}", e.PortInfo.portName().toString()));
				}
				else
				{
					log(String.Format("Connect to device failed. Port: {0}", e.PortInfo.portName().toString()));
				}

				switch (_state)
				{
					case States.CONNECTING:
						log("Closing XDA");
						_myxda.reset();
						_state = States.DETECTING;
						setWidgetsStates();
						break;
					default:
						break;
				}
			}
		}

		void _callbackHandler_MtwWireless(object sender, DeviceIdArg e)
		{
			if (InvokeRequired)
			{
				// Update UI, make sure this happens on the UI thread
				BeginInvoke(new Action(delegate { _callbackHandler_MtwWireless(sender, e); }));
			}
			else
			{
				log(String.Format("MTw Connected. ID: {0}", e.DeviceId.toXsString().toString()));

				String mtwIdStr = e.DeviceId.toXsString().toString();
				ConnectedMTwData connectedMtwData = new ConnectedMTwData();
				if (connectedMtwList.FindStringExact(mtwIdStr) == ListBox.NoMatches)
				{
					connectedMtwList.SelectedIndex = connectedMtwList.Items.Add(mtwIdStr);

					// This is a new MTw, add it.
					connectedMtwData._rssi = 0;
					connectedMtwData._frameSkipsList = new List<int>();
					_connectedMtwData[e.DeviceId.legacyDeviceId()] = connectedMtwData;

					connectedMtwListGroupBox.Text = String.Format("Connected MTw list ({0}):", connectedMtwList.Items.Count);
				}
				btnMeasure.Enabled = _state == States.ENABLED && connectedMtwList.Items.Count > 0;
			}
		}

		void _callbackHandler_MtwDisconnected(object sender, DeviceIdArg e)
		{
			if (InvokeRequired)
			{
				// Update UI, make sure this happens on the UI thread
				BeginInvoke(new Action(delegate { _callbackHandler_MtwDisconnected(sender, e); }));
			}
			else
			{
				String mtwIdStr = e.DeviceId.toXsString().toString();
				log(String.Format("MTw Disconnected. ID: {0}", mtwIdStr));

				Int32 index = connectedMtwList.FindStringExact(mtwIdStr);
				if (index != ListBox.NoMatches)
				{
					// Found --> delete
					connectedMtwList.Items.Remove(mtwIdStr);
					_connectedMtwData.Remove(e.DeviceId.legacyDeviceId());

					connectedMtwListGroupBox.Text = String.Format("Connected MTw list ({0}):", connectedMtwList.Items.Count);
					btnMeasure.Enabled = _state == States.ENABLED && connectedMtwList.Items.Count > 0;
				}
			}
		}
		void _callbackHandler_MeasurementStarted(object sender, DeviceIdArg e)
		{
            if (_scanThread != null)
            {
                _scanThread.Join(100);
                _scanThread = null;
            }

            if (InvokeRequired)
			{
				// Update UI, make sure this happens on the UI thread
				BeginInvoke(new Action(delegate { _callbackHandler_MeasurementStarted(sender, e); }));
			}
			else
			{
				log(String.Format("Measurement Started. ID: {0}", e.DeviceId.toXsString().toString()));

				if (_myxda.getDevice(e.DeviceId).deviceId().legacyDeviceId() == _MyWirelessMasterDevice.deviceId().legacyDeviceId())
				{
					switch (_state)
					{
					case States.AWAIT_MEASUREMENT_START:
						{
							// Get the MTws that are measuring and attach callback handlers
							clearMeasuringMtws();
							List<XsDeviceId> deviceIds = m_myWirelessMasterCallback.getConnectedMtws();
							foreach (XsDeviceId devId in deviceIds)
                            {
								XsDevice mtw = _myxda.getDevice(devId);
                                if (mtw != null)
                                {
                                    MyMtwCallback callback = new MyMtwCallback();

                                    // connect signals
                                    callback.DataAvailable += new EventHandler<DataAvailableArgs>(_callbackHandler_DataAvailable);
                                    callback.BatteryLevelChanged += new EventHandler<BatteryLevelChangedArgs>(_callbackHandler_BatteryLevelChanged);

                                    mtw.addCallbackHandler(callback);
                                    _measuringMtws[mtw] = callback;
                                }
							}
							_nextBatteryRequest = _measuringMtws.GetEnumerator();
							_state = States.MEASURING;
							setWidgetsStates();
						}
						break;

					case States.RECORDING:
					case States.FLUSHING:
						log(String.Format("Recording Finished. ID: {0}", e.DeviceId.toXsString().toString()));
						// Ready recording (flushing also ready), so file can be closed.
						_MyWirelessMasterDevice.closeLogFile();
						_state = States.MEASURING;
						setWidgetsStates();
						break;
					default:
						break;
					}
				}
			}
		}
		void _callbackHandler_MeasurementStopped(object sender, DeviceIdArg e)
		{
			if (InvokeRequired)
			{
				// Update UI, make sure this happens on the UI thread
				BeginInvoke(new Action(delegate { _callbackHandler_MeasurementStopped(sender, e); }));
			}
			else
			{
				log(String.Format("Measurement Stopped. ID: {0}", e.DeviceId.toXsString().toString()));
				if (e.DeviceId .toInt()== _MyWirelessMasterDevice.deviceId().legacyDeviceId())
				{
					clearMeasuringMtws();
					_state = States.OPERATIONAL;
					setWidgetsStates();
				}
			}
		}
		void _callbackHandler_DeviceError(object sender, DeviceErrorArgs e)
		{
			if (InvokeRequired)
			{
				// Update UI, make sure this happens on the UI thread
				BeginInvoke(new Action(delegate { _callbackHandler_DeviceError(sender, e); }));
			}
			else
			{
				log(String.Format("ERROR. ID: {0}", e.DeviceId.toXsString().toString()));
				switch (_state)
				{
					case States.AWAIT_MEASUREMENT_START:
						_state = States.ENABLED;
						setWidgetsStates();
						break;
					default:
						break;
				}
			}
		}
		void _callbackHandler_WaitingForRecordingStart(object sender, DeviceIdArg e)
		{
			if (InvokeRequired)
			{
				// Update UI, make sure this happens on the UI thread
				BeginInvoke(new Action(delegate { _callbackHandler_WaitingForRecordingStart(sender, e); }));
			}
			else
			{
				log(String.Format("Waiting for recording start. ID: {0}", _MyWirelessMasterDevice.deviceId().toXsString().toString()));
				_state = States.AWAIT_RECORDING_START;
				setWidgetsStates();
			}
		}
		void _callbackHandler_RecordingStarted(object sender, DeviceIdArg e)
		{
			if (InvokeRequired)
			{
				// Update UI, make sure this happens on the UI thread
				BeginInvoke(new Action(delegate { _callbackHandler_RecordingStarted(sender, e); }));
			}
			else
			{
				if (_state == States.AWAIT_RECORDING_START)
				{
					log(String.Format("Waiting for recording start. ID: {0}", _MyWirelessMasterDevice.deviceId().toXsString().toString()));
					_state = States.RECORDING;
					setWidgetsStates();
				}
			}
		}
		void _callbackHandler_ProgressUpdate(object sender, ProgressUpdateArgs e)
		{
			if (InvokeRequired)
			{
				// Update UI, make sure this happens on the UI thread
				BeginInvoke(new Action(delegate { _callbackHandler_ProgressUpdate(sender, e); }));
			}
			else
			{
				if (_state == States.FLUSHING && e.Identifier == "Flushing")
				{
					if (comboBoxUpdateRate.SelectedIndex == 0)
					{
						// Nothing to flush when at the highest update rate.
						_MyWirelessMasterDevice.abortFlushing();
						log(String.Format("Flushing aborted. ID: {0}", _MyWirelessMasterDevice.deviceId().toXsString().toString()));
					}

					if (e.Total != 0 && comboBoxUpdateRate.SelectedIndex != 0)
					{
						// Only do this when there is still data to be flushed
						// and not the highest update rate was selected.
						progressBarFlushing.Maximum = e.Total;
						progressBarFlushing.Value = e.Current;
					}
				}
			}
		}

		void _callbackHandler_DataAvailable(object sender, DataAvailableArgs e)
		{
			if (InvokeRequired)
			{
				// Update UI, make sure this happens on the UI thread
				BeginInvoke(new Action(delegate { _callbackHandler_DataAvailable(sender, e); }));
			}
			else
			{
				String mtwIdStr = e.Device.deviceId().toXsString().toString();
				Int32 index = connectedMtwList.FindStringExact(mtwIdStr);

				if (index == ListBox.NoMatches)
				{
					log(String.Format("Obsolete data received of an MTw {0} that's no longer in the list.", mtwIdStr));
					return;
				}

				if (!e.Packet.containsSdiData())
				{
					log(String.Format("Packet received of an MTw {0} not containing data.", mtwIdStr));
					return;
				}

				// Getting SDI data.
				XsSdiData sdiData = e.Packet.sdiData();

                _connectedMtwData[e.Device.deviceId().legacyDeviceId()]._rssi = e.Packet.rssi();

                if (e.Packet.containsOrientation())
                {
                    //Getting Euler angles.
                    XsEuler oriEuler = e.Packet.orientationEuler();
                    
                    // Just for fun: pitch to select.
                    // (you only want to select this in the GUI after the XKF-3w filters stabilized though)
                    if (checkBoxPitchToSelect.Checked == true && Math.Abs(oriEuler.y()) > 30)
                    {
                        connectedMtwList.SelectedItem = mtwIdStr;
                    }
                    _connectedMtwData[e.Device.deviceId().legacyDeviceId()]._orientation = oriEuler;
                }
                
				// -- Determine effective update rate percentage --

				// Determine the number of frames over which the SDI data in this
				// packet was determined.
				int frameSkips;


				if (e.Packet.frameRange().last() > e.Packet.frameRange().first())
				{
					frameSkips = e.Packet.frameRange().last() - e.Packet.frameRange().first() - 1;
				}
				else
				{
					// Rollover (internal framecounter is unsigned 16 bits integer)
					frameSkips = 65535 + e.Packet.frameRange().last() - e.Packet.frameRange().first() - 1;
				}

				_connectedMtwData[e.Device.deviceId().legacyDeviceId()]._frameSkipsList.Add(frameSkips);
				_connectedMtwData[e.Device.deviceId().legacyDeviceId()]._sumFrameSkips = _connectedMtwData[e.Device.deviceId().legacyDeviceId()]._sumFrameSkips + (uint)frameSkips;
				_connectedMtwData[e.Device.deviceId().legacyDeviceId()]._effectiveUpdateRate = (int)(100 * (1 - (float)_connectedMtwData[e.Device.deviceId().legacyDeviceId()]._sumFrameSkips / (float)(_connectedMtwData[e.Device.deviceId().legacyDeviceId()]._frameSkipsList.Count() + _connectedMtwData[e.Device.deviceId().legacyDeviceId()]._sumFrameSkips)));

				while (_connectedMtwData[e.Device.deviceId().legacyDeviceId()]._frameSkipsList.Count() + _connectedMtwData[e.Device.deviceId().legacyDeviceId()]._sumFrameSkips > 99 && _connectedMtwData[e.Device.deviceId().legacyDeviceId()]._frameSkipsList.Count() > 0)
				{
					_connectedMtwData[e.Device.deviceId().legacyDeviceId()]._sumFrameSkips = _connectedMtwData[e.Device.deviceId().legacyDeviceId()]._sumFrameSkips - (uint)_connectedMtwData[e.Device.deviceId().legacyDeviceId()]._frameSkipsList[0];
					_connectedMtwData[e.Device.deviceId().legacyDeviceId()]._frameSkipsList.RemoveAt(0);
				}

				if (connectedMtwList.Text == mtwIdStr)
				{
					// Display data when MTw selected.
					displayMtwData(_connectedMtwData[e.Device.deviceId().legacyDeviceId()]);
				}
			}
		}

		void displayMtwData(ConnectedMTwData mtwData)
		{
			// Last known battery level.
			batteryLevelLabel.Text = String.Format("{0} [%]", mtwData._batteryLevel);

			// RSSI (received signals strenght indicator) of this packet.
			rssiLabel.Text = String.Format("{0} [dBm]", mtwData._rssi);

			// Display Euler angles (if available).
            if (mtwData._containsOrientation)
            {
                rollLabel.Text = String.Format("{0,-5:f2} [deg]", mtwData._orientation.x());
                rollLabel.TextAlign = ContentAlignment.MiddleRight;
                pitchLabel.Text = String.Format("{0,-5:f2} [deg]", mtwData._orientation.y());
                yawLabel.Text = String.Format("{0,-5:f2} [deg]", mtwData._orientation.z());
            }

			// Display effective update rate.
			effUpdateRateLabel.Text = String.Format("{0} [%]", mtwData._effectiveUpdateRate);
		}

		void _callbackHandler_BatteryLevelChanged(object sender, BatteryLevelChangedArgs e)
		{
			if (InvokeRequired)
			{
				// Update UI, make sure this happens on the UI thread
				BeginInvoke(new Action(delegate { _callbackHandler_BatteryLevelChanged(sender, e); }));
			}
			else
			{
				String mtwIdStr = e.DeviceId.toXsString().toString();
				Int32 index = connectedMtwList.FindStringExact(mtwIdStr);
				if (index == ListBox.NoMatches)
				{
					log(String.Format("Obsolete data received of an MTw {0} that's no longer in the list.", mtwIdStr));
					return;
				}

				_connectedMtwData[e.DeviceId.legacyDeviceId()]._batteryLevel = e.Level;
			}
		}

		// Track connection changes
		void _callbackHandler_MtwConnectionChanged(object sender, MtwEventArgs e)
		{
			if (InvokeRequired)
			{
				// Update UI, make sure this happens on the UI thread
				BeginInvoke(new Action(delegate { _callbackHandler_MtwConnectionChanged(sender, e); }));
			}
			else
			{
				if (e.Connected)
				{
					_mtws.Add(e.Mtw);
				}
				else if (_mtws.Contains(e.Mtw))
				{
					_mtws.Remove(e.Mtw);
				}

				updateMTws();
			}
		}

		void log(String message)
		{
			lock (logWindow)
			{
                if (!logWindow.IsDisposed)
                {
                    if (logWindow.InvokeRequired)
                    {
                        logWindow.BeginInvoke(new Action(delegate { logWindow.AppendText(message + "\n"); }));
                    }
                    else
                    {
                        logWindow.AppendText(message + "\n");
                        logWindow.ScrollToCaret();
                    }
                }		
			}
		}

		private void updateMTws()
		{
			btnMeasure.Enabled = _mtws.Count > 0;
		}

		private void clearMeasuringMtws()
		{
			lock(_measuringMtws)
			{
				foreach (KeyValuePair<XsDevice, MyMtwCallback> item in _measuringMtws)
				{
					 item.Key.clearCallbackHandlers();
				}
			}
			_measuringMtws.Clear();
			_nextBatteryRequest.Dispose();
		}

		private void AwindaMonitorDialog_FormClosed(object sender, FormClosedEventArgs e)
		{
			_portScanTimer.Enabled = false;
			_batteryLevelRequestTimer.Enabled = false;

			clearMeasuringMtws();

			if (_MyWirelessMasterDevice != null)
				_MyWirelessMasterDevice.clearCallbackHandlers();
			m_myWirelessMasterCallback.Dispose();

			_myxda.Dispose();
			_myxda = null;
		}

		private void btnEnable_Click(object sender, EventArgs e)
		{
			SetRadioChannel(_state == States.CONNECTED ? Convert.ToInt16(comboBoxChannel.Text) : -1);
		}

		private void SetRadioChannel(int channel)
		{
			if (_MyWirelessMasterDevice.enableRadio(channel))
			{
				if (channel != -1)
                {
					log(String.Format("Master Enabled. ID: {0}, Channel: {1}",_MyWirelessMasterDevice.deviceId().toXsString().toString(),channel));

					// Supported update rates and maximum available from xda
					XsIntArray supportedRates = _MyWirelessMasterDevice.supportedUpdateRates();
					int maxUpdateRate = _MyWirelessMasterDevice.maximumUpdateRate();

					// -- Put the allowed update rates in the combobox for the user to choose from --
					comboBoxUpdateRate.Items.Clear();
					for (uint i = 0; i < supportedRates.size() && supportedRates.at(i) <= maxUpdateRate; ++i)
					{
						// This is an allowed update rate, so add it to the list.
						comboBoxUpdateRate.Items.Add(Convert.ToString(supportedRates.at(i)));
					}

					// Select the current update rate of the station.
					int updateRateIndex = comboBoxUpdateRate.FindString(Convert.ToString(_MyWirelessMasterDevice.updateRate()));
					comboBoxUpdateRate.SelectedIndex = updateRateIndex;

					_state = States.ENABLED;

					// Set a default update rate of 75 (if available) when we set the radio channel
					updateRateIndex = comboBoxUpdateRate.FindString(Convert.ToString(75));

                    if (updateRateIndex != -1)
                    {
                        comboBoxUpdateRate.SelectedIndex = updateRateIndex;
                    }
				}
				else 
				{
					log(String.Format("Master Disabled. ID: {0}",_MyWirelessMasterDevice.deviceId().toXsString().toString()));
					connectedMtwList.Items.Clear();
					_state = States.CONNECTED;
				}
				setWidgetsStates();
			}
			else
			{
				if (channel != -1)
                {
					log(String.Format("Failed to enable wireless master. ID: {0}, Channel: {1}",_MyWirelessMasterDevice.deviceId().toXsString().toString(), channel));
				}
				else 
				{
					log(String.Format("Failed to disable wireless master. ID: {0}", _MyWirelessMasterDevice.deviceId().toXsString().toString()));
				}
			}
		}

		private void btnMeasure_Click(object sender, EventArgs e)
		{
			switch (_state)
            {
			case States.ENABLED:
			case States.OPERATIONAL:
			{
				// First set the update rate
				int desiredUpdateRate = Convert.ToInt32(comboBoxUpdateRate.Text);
				if (desiredUpdateRate != -1 && desiredUpdateRate != _MyWirelessMasterDevice.updateRate()) {
					if (_MyWirelessMasterDevice.setUpdateRate(desiredUpdateRate))
                    {
						log(String.Format("Update rate set. ID: {0}, Rate: {1}",_MyWirelessMasterDevice.deviceId().toXsString().toString(), desiredUpdateRate));
					}
					else
                    {
						log(String.Format("Failed to set update rate. ID: {0}, Rate: {1}", _MyWirelessMasterDevice.deviceId().toXsString().toString(), desiredUpdateRate));
					}
				}

				if (comboBoxUpdateRate.SelectedIndex == 0)
				{
					MessageBox.Show("Note: at the highest update rate\nrecording will be at effective update rate.");
				}

                States bkpState = _state;
                // Set the state to AWAIT_MEASUREMENT_START and go to measurement
                _state = States.AWAIT_MEASUREMENT_START;

                if (_MyWirelessMasterDevice.gotoMeasurement())
                {
                    log(String.Format("Waiting for measurement start. ID: {0}", _MyWirelessMasterDevice.deviceId().toXsString().toString()));
                }
                else
                {
                    // If gotoMeasurement fails revert the state
                    _state = bkpState;
                }
				
			}
			break;

			case States.MEASURING:
			{
				if (_MyWirelessMasterDevice.gotoConfig())
                {
					log(String.Format("Stopping measurement. ID: {0}", _MyWirelessMasterDevice.deviceId().toXsString().toString()));
				}
				else
                {
					log(String.Format("Failed to stop measurement. ID: {0}", _MyWirelessMasterDevice.deviceId().toXsString().toString()));
				}
			}
			break;
			default:
				break;

			}
			setWidgetsStates();     
		}

		private void btnRecord_Click(object sender, EventArgs e)
		{
			switch (_state)
			{
			case States.MEASURING:
				{
					// -- Start the recording --

					// Get the filename from the input and creating a log file.
					String logFilename = textBoxFilename.Text;
					if (_MyWirelessMasterDevice.createLogFile(new XsString(logFilename)) == XsResultValue.XRV_OK)
					{
						if (_MyWirelessMasterDevice.startRecording())
						{

						}
						else
						{
							log(String.Format("Failed to start recording. ID: {0}", _MyWirelessMasterDevice.deviceId().toXsString().toString()));
						}
					}
					else
					{
						log(String.Format("Failed to create log file: {0}", logFilename));
					}
				} break;

			case States.RECORDING:
				{
					// -- Stop the recording --
					_state = States.FLUSHING;
					_MyWirelessMasterDevice.stopRecording();
					log(String.Format("Stopping recording. ID: {0}", _MyWirelessMasterDevice.deviceId().toXsString().toString()));

				} break;

			default:
				break;
			}

			setWidgetsStates();
		}

		//------------------------------------------------------------------------------
		// Set the states of widgets (labels, buttons and images) depending on the m_state.
		// This is basically a m_state machine with only 'm_state entry code'.
		//------------------------------------------------------------------------------
		private void setWidgetsStates()
		{
			switch (_state)
			{
				case AwindaMonitorDialog.States.DETECTING:
				{
					pictureBoxStateDiagram.Image = global::awindamonitor.Properties.Resources.connected;
				} break;

				case AwindaMonitorDialog.States.CONNECTING:
				{
					btnEnable.Enabled = false;
					pictureBoxStateDiagram.Image = global::awindamonitor.Properties.Resources.connecting;
					log("Scanning for station.");
					btnRecord.Enabled = false;
				} break;

				case AwindaMonitorDialog.States.CONNECTED:
				{
					btnMeasure.Enabled = false;
					labelChannel.Enabled = true;
					comboBoxChannel.Enabled = true;
					btnEnable.Enabled = true;
					btnEnable.Text = "Enable";
					labelUpdateRate.Enabled = false;
					comboBoxUpdateRate.Enabled = false;
					pictureBoxStateDiagram.Image = global::awindamonitor.Properties.Resources.connected;
					btnRecord.Enabled = false;
				} break;

				case AwindaMonitorDialog.States.ENABLED:
				{
					btnMeasure.Enabled = connectedMtwList.Items.Count > 0;
					btnMeasure.Text = "Start Measurement";
					btnEnable.Text = "Disable";
					btnEnable.Enabled = true;
					labelChannel.Enabled = false;
					comboBoxChannel.Enabled = false;
					labelUpdateRate.Enabled = true;
					comboBoxUpdateRate.Enabled = true;
					pictureBoxStateDiagram.Image = global::awindamonitor.Properties.Resources.enabled;
					btnRecord.Enabled = false;
				} break;

				case AwindaMonitorDialog.States.OPERATIONAL:
				{
					btnMeasure.Enabled = connectedMtwList.Items.Count > 0;
					btnMeasure.Text = "Start Measurement";
					btnEnable.Text = "Disable";
					btnEnable.Enabled = true;
					labelChannel.Enabled = false;
					comboBoxChannel.Enabled = false;
					labelUpdateRate.Enabled = true;
					comboBoxUpdateRate.Enabled = true;
					pictureBoxStateDiagram.Image = global::awindamonitor.Properties.Resources.operational;
					btnRecord.Enabled = false;
				} break;

				case AwindaMonitorDialog.States.AWAIT_MEASUREMENT_START:
				case AwindaMonitorDialog.States.AWAIT_RECORDING_START:
				{
					btnEnable.Enabled = false;
					btnMeasure.Text = "Waiting for start...";
					btnMeasure.Enabled = false;
					labelUpdateRate.Enabled = false;
					comboBoxUpdateRate.Enabled = false;
					pictureBoxStateDiagram.Image = global::awindamonitor.Properties.Resources.await_measurement_start;
					btnRecord.Enabled = false;
				} break;

				case AwindaMonitorDialog.States.MEASURING:
				{
					btnEnable.Enabled = false;
					btnMeasure.Text = "Stop measuring";
					btnMeasure.Enabled = true;
					labelUpdateRate.Enabled = false;
					comboBoxUpdateRate.Enabled = false;
					btnRecord.Text = "Start recording";
					btnRecord.Enabled = true;
					labelFilename.Enabled = true;
					textBoxFilename.Enabled = true;
					labelFlushing.Enabled = false;
					progressBarFlushing.Enabled = false;
					progressBarFlushing.Value = 0;
					pictureBoxStateDiagram.Image = global::awindamonitor.Properties.Resources.measuring;
				} break;

				case AwindaMonitorDialog.States.RECORDING:
				{
					btnRecord.Enabled = true;
					btnRecord.Text = "Stop recording";
					labelFilename.Enabled = false;
					textBoxFilename.Enabled = false;
					btnMeasure.Enabled = false;
					pictureBoxStateDiagram.Image = global::awindamonitor.Properties.Resources.recording;
				} break;

				case AwindaMonitorDialog.States.FLUSHING:
				{
					btnRecord.Enabled = false;
					btnRecord.Text = "Flushing";
					labelFlushing.Enabled = true;
					progressBarFlushing.Enabled = true;
					pictureBoxStateDiagram.Image = global::awindamonitor.Properties.Resources.flushing;
				} break;

				default:
						break;
			}
		}
	}
}
