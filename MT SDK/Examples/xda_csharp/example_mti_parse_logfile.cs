
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
using System.Diagnostics;
using System.Collections.Generic;
using XDA;
using System.Threading;

namespace ExampleMtiParseLogfile
{
    internal class CallbackHandler : XsCallback
    {
        private int _progress;
        private object _lockThis;

		private int Progress
		{
			get { return _progress; }
			set { _progress = value;  }
		}
        
        public CallbackHandler()
            : base()
        {
            Progress = 0;
            _lockThis = new object();
		}

		public int getProgress()
		{
			return Progress;
		}
		
        protected override void onProgressUpdated(XsDevice dev, int current, int total, XsString identifier)
        {
            lock (_lockThis)
            {
				Progress = current;
            }
        }
    }


	static class Program
	{
		static void Main()
		{
            Console.WriteLine("Creating XsControl object...");
            XsControl control = new XsControl();
            Debug.Assert(control != null);

            try
            {
                Console.WriteLine("Opening log file...");
				XsString logFileName = new XsString("logfile.mtb");
				if (!control.openLogFile(logFileName))
					throw new Exception("Failed to open log file. Aborting.");

                Console.WriteLine("Opened log file: {0}", logFileName.toString());

                // Get number of devices in the file
                XsDeviceIdArray deviceIdArray = control.mainDeviceIds();
				XsDeviceId mtDevice = new XsDeviceId();
				
				// Find an MTi device
				for (uint i = 0; i < deviceIdArray.size(); i++)
				{
					if (deviceIdArray.at(i).isMti() || deviceIdArray.at(i).isMtig())
					{
						mtDevice = deviceIdArray.at(i);
						break;
					}
				}
				
                if (!mtDevice.isValid())
                    throw new Exception("No MTi device found. Aborting.");

                // Get the device object
                XsDevice tempDevice = control.device(mtDevice);
                Debug.Assert(tempDevice != null);
                XsDevice device = new XsDevice(tempDevice);

                Console.WriteLine("Device: {0}, with ID: {1} found in file.", device.productCode().toString(), device.deviceId().toXsString().toString());

                // Create and attach callback handler to device
                CallbackHandler callback = new CallbackHandler();
                device.addCallbackHandler(callback);

				// By default XDA does not retain data for reading it back.
				// By enabling this option XDA keeps the buffered data in a cache so it can be accessed 
				// through XsDevice::getDataPacketByIndex or XsDevice::takeFirstDataPacketInQueue
				device.setOptions(XsOption.XSO_RetainBufferedData, XsOption.XSO_None);

				Console.WriteLine("Loading the file...");
				device.loadLogFile();
				while (callback.getProgress() != 100)
					Thread.Yield();
				Console.WriteLine("File is fully loaded");

                string exportFileName = "exportfile.txt";
                using (System.IO.StreamWriter file = new System.IO.StreamWriter(@exportFileName))
				{
                    // Get total number of samples
                    uint packetCount = device.getDataPacketCount();

                    Console.WriteLine("Exporting the data...");
                    for (uint i = 0; i < packetCount; i++)
					{
						// Retrieve a packet
						XsDataPacket packet = device.getDataPacketByIndex(i);

						if (packet.containsCalibratedData())
						{
							XsVector acc = packet.calibratedAcceleration();
							file.Write("Acc X:{0,-5:f2}, Acc Y:{1,-5:f2}, Acc Z:{2,-5:f2}", acc.value(0), acc.value(1), acc.value(2));

							XsVector gyr = packet.calibratedGyroscopeData();
							file.Write(" |Gyr X:{0,-5:f2}, Gyr Y:{1,-5:f2}, Gyr Z:{2,-5:f2}", gyr.value(0), gyr.value(1), gyr.value(2));

							XsVector mag = packet.calibratedMagneticField();
							file.Write(" |Mag X:{0,-5:f2}, Mag Y:{1,-5:f2}, Mag Z:{2,-5:f2}", mag.value(0), mag.value(1), mag.value(2));
						}

						if (packet.containsOrientation())
						{
							XsQuaternion quaternion = packet.orientationQuaternion();
							file.Write("q0:{0,-5:f2}, q1:{1,-5:f2}, q2:{2,-5:f2}, q3:{3,-5:f2}", quaternion.w(), quaternion.x(), quaternion.y(), quaternion.z());

							XsEuler euler = packet.orientationEuler();
							file.Write(" |Roll:{0,-5:f2}, Pitch:{1,-5:f2}, Yaw:{2,-5:f2}", euler.roll(), euler.pitch(), euler.yaw());
						}

						if (packet.containsLatitudeLongitude())
						{
							XsVector latLon = packet.latitudeLongitude();
							file.Write(" |Lat:{0,-5:f2}, Lon:{1,-5:f2}", latLon.value(0), latLon.value(1));
						}

						if (packet.containsAltitude())
							file.Write(" |Alt:{0,-5:f2}", packet.altitude());

						if (packet.containsVelocity())
						{
							XsVector vel = packet.velocity(XsDataIdentifier.XDI_CoordSysEnu);
							file.Write(" |E:{0,-5:f2}, N:{1,-5:f2}, U:{2,-5:f2}", vel.value(0), vel.value(1), vel.value(2));
						}
                        file.WriteLine("");
					}
				}
                Console.WriteLine("File is exported to: {0}", exportFileName);

                Console.WriteLine("Closing XsControl object...");
                control.close();

                Console.WriteLine("Successful exit.");
            }
            catch (Exception exc)
            {
                Console.WriteLine(exc.ToString());
            }

            Console.WriteLine("Press [ENTER] to continue.");
            Console.Read();
        }
	}
}
