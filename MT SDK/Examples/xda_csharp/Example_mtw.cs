
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
using Xsens;
using XDA;

namespace MTwExample
{
	public partial class Form1 : Form
	{
		private MyXda _xda;
		private XsDevice _measuringDevice = null;
		private Dictionary<XsDevice, MyMtCallback> _measuringMts = new Dictionary<XsDevice, MyMtCallback>();
		private Dictionary<ulong, ConnectedMtData> _connectedMtwData = new Dictionary<ulong, ConnectedMtData>();

		public Form1()
		{
			InitializeComponent();
			_xda = new MyXda();
			cbxChannel.SelectedIndex = 0;
			step(1);
		}

		private void Form1_FormClosed(object sender, FormClosedEventArgs e)
		{
			timer1.Enabled = false;

			if (_measuringDevice != null)
				_measuringDevice.clearCallbackHandlers();

			_measuringMts.Clear();

			_xda.Dispose();
			_xda = null;
		}

		private void btnScan_Click(object sender, EventArgs e)
        {
            //reset the following two GUI elements just in case
            cbxStations.SelectedIndex = -1;
            cbxStations.Items.Clear();
            btnEnable.Enabled = false;

			_xda.scanPorts();
			if (_xda._DetectedDevices.Count > 0)
			{
				foreach (XsPortInfo portInfo in _xda._DetectedDevices)
				{
					if (portInfo.deviceId().isWirelessMaster())
					{
						_xda.openPort(portInfo);
						MasterInfo ai = new MasterInfo(portInfo.deviceId());
						ai.ComPort = portInfo.portName();
						ai.BaudRate = portInfo.baudrate();
						cbxStations.Items.Add(ai);
						break;
					}
				}

				if (cbxStations.Items.Count > 0)
				{
					cbxStations.SelectedIndex = 0;
					btnEnable.Enabled = true;
					step(2);
				}
				else
				{
					step(3);
				}
			}
		}

		private void btnEnable_Click(object sender, EventArgs e)
		{
            var selectedItem = (MasterInfo)cbxStations.SelectedItem;
            XsDevice device = null;
            if (selectedItem != null)
                device = _xda.getDevice(selectedItem.DeviceId);
            if (device != null)
            {
                if (device.isRadioEnabled())
                    device.disableRadio();
                if (device.enableRadio(Convert.ToInt32(cbxChannel.Text)))
                {
                    btnScan.Enabled = false;
                    btnEnable.Enabled = false;
                    btnMeasure.Enabled = true;
                    step(4);
                }
                else
                {
                    step(6);
                    btnScan.Enabled = true;
                    btnEnable.Enabled = false;
                }
            }
		}

		private void btnMeasure_Click(object sender, EventArgs e)
		{
            var selectedItem = (MasterInfo)cbxStations.SelectedItem;
            if (selectedItem == null)
                return;

            step(9);
			_connectedMtwData.Clear();
			_measuringDevice = _xda.getDevice(selectedItem.DeviceId);
            if (_measuringDevice != null)
            {
                _measuringDevice.gotoMeasurement();
                XsDevicePtrArray deviceIds = _measuringDevice.children();
                for (uint i = 0; i < deviceIds.size(); i++)
                {
                    XsDevice mtw = new XsDevice(deviceIds.at(i));
                    MyMtCallback callback = new MyMtCallback();

                    ConnectedMtData mtwData = new ConnectedMtData();
                    _connectedMtwData.Add(mtw.deviceId().toInt(), mtwData);

                    // connect signals
                    callback.DataAvailable += new EventHandler<DataAvailableArgs>(_callbackHandler_DataAvailable);

                    mtw.addCallbackHandler(callback);
                    _measuringMts.Add(mtw, callback);
                }
                lblDeviceCount.Text = string.Format("MTw's Connected: {0}", deviceIds.size());
                btnMeasure.Enabled = false;
                btnRecord.Enabled = true;
                btnStop.Enabled = true;
                timer1.Interval = 20;
                timer1.Enabled = true;
            }
            else
                step(6);
        }

		private void btnRecord_Click(object sender, EventArgs e)
		{
			_measuringDevice.createLogFile(new XsString(textBoxFilename.Text));
			_measuringDevice.startRecording();
			btnRecord.Enabled = false;
		}

		private void btnStop_Click(object sender, EventArgs e)
		{
			btnStop.Enabled = false;
			timer1.Enabled = false;

			if (_measuringDevice.isRecording())
				_measuringDevice.stopRecording();
			_measuringDevice.gotoConfig();
			_measuringDevice.disableRadio();
			_measuringDevice.clearCallbackHandlers();

			btnScan.Enabled = true;

			if (cbxStations.Items.Count > 0)
			{
				cbxStations.SelectedIndex = 0;
				btnEnable.Enabled = true;
				step(2);
			}
			else
			{
				step(1);
			}
		}

		private void timer1_Tick(object sender, EventArgs e)
		{
			string text = "";
			foreach (KeyValuePair<ulong, ConnectedMtData> data in _connectedMtwData)
			{
				if (data.Value._orientation != null)
				{
					text += string.Format("{3:X8} {0,-5:f2}, {1,-5:f2}, {2,-5:f2} [°]\n",
										   data.Value._orientation.x(),
										   data.Value._orientation.y(),
										   data.Value._orientation.z(), data.Key);
				}
			}
			rtbData.Text = text;
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
				//Getting Euler angles.
				XsEuler oriEuler = e.Packet.orientationEuler();

				_connectedMtwData[e.Device.deviceId().toInt()]._orientation = oriEuler;
			}
		}

		/// <summary>
		/// Some step by step info
		/// </summary>
		/// <param name="stepNumber"></param>
		private void step(int stepNumber)
		{
			switch (stepNumber)
			{
				case 1:
					rtbSteps.Text = "Connect the Awinda Station, dock the MTWs and click 'Scan'.";
					break;
				case 2:
					rtbSteps.Text = "Select a station from the combobox, select a channel and click 'Enable Radio'.";
					break;
				case 3:
					rtbSteps.Text = "No station was found, make sure the drivers were installed correctly.";
					break;
				case 4:
					rtbSteps.Text = "Undock the MTws from the station and wait for them to connect to the station. This is indicated by the MTw LEDs blinking in sync with the CONN LED on the station.\n\n" +
									"Then click 'Measure' and wait a bit.";
					break;
				case 6:
					rtbSteps.Text = "There was an unexpected failure enabling the station.";
					break;
				case 8:
					rtbSteps.Text = "There was an unexpected failure going to the operational mode.";
					break;
				case 9:
					rtbSteps.Text = "Enjoy the data... click 'Stop' when no further joy can be obtained from looking at the data.\nClick 'Record' when you want to feel the same joy again at a later moment";
					break;
				default:
					rtbSteps.Text = "No station was found, make sure the drivers were installed correctly.";
					break;
			}
		}
	}
}
