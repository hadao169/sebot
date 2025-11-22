
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

namespace ExampleMtiReceiveData
{
    internal class CallbackHandler : XsCallback
    {
        private uint _maxNumberOfPacketsInBuffer;
        private uint _numberOfPacketsInBuffer;
        private Queue<XsDataPacket> _packetBuffer;
        private object _lockThis;

        private uint MaxNumberOfPacketsInBuffer
        {
            get { return _maxNumberOfPacketsInBuffer; }
            set { _maxNumberOfPacketsInBuffer = value; }
        }

        private uint NumberOfPacketsInBuffer
        {
            get { return _numberOfPacketsInBuffer; }
            set { _numberOfPacketsInBuffer = value; }
        }

        private Queue<XsDataPacket> PacketBuffer
        {
            get { return _packetBuffer; }
            set { _packetBuffer = value; }
        }

        public CallbackHandler(uint maxBufferSize = 5)
            : base()
        {
            MaxNumberOfPacketsInBuffer = maxBufferSize;
            NumberOfPacketsInBuffer = 0;
            PacketBuffer = new Queue<XsDataPacket>();
            _lockThis = new object();
        }

        public bool packetAvailable()
	    {
            lock (_lockThis)
                return NumberOfPacketsInBuffer > 0;
	    }

        public XsDataPacket getNextPacket()
        {
            Debug.Assert(packetAvailable());
            lock (_lockThis)
            {
                XsDataPacket oldestPacket = PacketBuffer.Peek();
                PacketBuffer.Dequeue();
                --NumberOfPacketsInBuffer;
                return oldestPacket;
            }
        }

        protected override void onLiveDataAvailable(XsDevice dev, XsDataPacket packet)
        {
            lock (_lockThis)
            {
                Debug.Assert(packet != null);
                while (NumberOfPacketsInBuffer >= MaxNumberOfPacketsInBuffer)
                    getNextPacket();

                PacketBuffer.Enqueue(new XsDataPacket(packet));
                ++NumberOfPacketsInBuffer;
                Debug.Assert(NumberOfPacketsInBuffer <= MaxNumberOfPacketsInBuffer);
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
                Console.WriteLine("Scanning for devices...");
                XsPortInfoArray portInfoArray = XsScanner.scanPorts();

                // Find an MTi device
                XsPortInfo mtPort = new XsPortInfo();
                for (uint i = 0; i < portInfoArray.size(); i++)
                {
                    if (portInfoArray.at(i).deviceId().isMti() || portInfoArray.at(i).deviceId().isMtig())
                    {
                        mtPort = portInfoArray.at(i);
                        break;
                    }
                }

                if (mtPort.empty())
                    throw new Exception("No MTi device found. Aborting.");

                Console.WriteLine("Found a device with ID: {0}", mtPort.deviceId().toXsString().toString());
                Console.WriteLine("At port: {0}", mtPort.portName().toString());
                Console.WriteLine("Baudrate: {0}", (int)mtPort.baudrate());

                Console.WriteLine("Opening port...");
                if (!control.openPort(mtPort.portName(), mtPort.baudrate()))
                    throw new Exception("Could not open port. Aborting.");

                // Get the device object
                XsDevice tempDevice = control.device(mtPort.deviceId());
                Debug.Assert(tempDevice != null);
                XsDevice device = new XsDevice(tempDevice);

                Console.WriteLine("Device: {0}, with ID: {1} opened.", device.productCode().toString(), device.deviceId().toXsString().toString());

                // Create and attach callback handler to device
                CallbackHandler callback = new CallbackHandler();
                device.addCallbackHandler(callback);

                // Put the device into configuration mode before configuring the device
                Console.WriteLine("Putting device into configuration mode...");
                if (!device.gotoConfig())
                    throw new Exception("Could not put device into configuration mode. Aborting.");

                Console.WriteLine("Configuring the device...");
                XsOutputConfigurationArray configArray = new XsOutputConfigurationArray();
                configArray.push_back(new XsOutputConfiguration(XsDataIdentifier.XDI_PacketCounter, 0));
                configArray.push_back(new XsOutputConfiguration(XsDataIdentifier.XDI_SampleTimeFine, 0));

                if (device.deviceId().isImu())
                {
                    configArray.push_back(new XsOutputConfiguration(XsDataIdentifier.XDI_Acceleration, 100));
                    configArray.push_back(new XsOutputConfiguration(XsDataIdentifier.XDI_RateOfTurn, 100));
                    configArray.push_back(new XsOutputConfiguration(XsDataIdentifier.XDI_MagneticField, 100));
                }
                else if (device.deviceId().isVru() || device.deviceId().isAhrs())
                {
                    configArray.push_back(new XsOutputConfiguration(XsDataIdentifier.XDI_Quaternion, 100));
                }
                else if (device.deviceId().isGnss())
                {
                    configArray.push_back(new XsOutputConfiguration(XsDataIdentifier.XDI_Quaternion, 100));
                    configArray.push_back(new XsOutputConfiguration(XsDataIdentifier.XDI_LatLon, 100));
                    configArray.push_back(new XsOutputConfiguration(XsDataIdentifier.XDI_AltitudeEllipsoid, 100));
                    configArray.push_back(new XsOutputConfiguration(XsDataIdentifier.XDI_VelocityXYZ, 100));
                }
                else
                {
                    throw new Exception("Unknown device while configuring. Aborting.");
                }

                if (!device.setOutputConfiguration(configArray))
                    throw new Exception("Could not configure MTi device. Aborting.");

                Console.WriteLine("Creating a log file...");
                XsString logFileName = new XsString("logfile.mtb");
                if (device.createLogFile(logFileName) != XsResultValue.XRV_OK)
                    throw new Exception("Failed to create a log file. Aborting.");
                else
                    Console.WriteLine("Created a log file: {0}", logFileName.c_str());

                Console.WriteLine("Putting device into measurement mode...");
                if (!device.gotoMeasurement())
                    throw new Exception("Could not put device into measurement mode. Aborting.");

                Console.WriteLine("Starting recording...");
                if (!device.startRecording())
                    throw new Exception("Failed to start recording. Aborting.");

                Console.WriteLine("Main loop. Recording data for 10 seconds.");
                Console.WriteLine("-----------------------------------------");

                long startTime = XsTimeStamp.nowMs();
                while (XsTimeStamp.nowMs() - startTime <= 10000)
                {
                    if (callback.packetAvailable())
                    {
                        // Retrieve a packet
                        XsDataPacket packet = callback.getNextPacket();

                        if (packet.containsCalibratedData())
                        {
                            XsVector acc = packet.calibratedAcceleration();
                            Console.Write("\rAcc X:{0,-5:f2}, Acc Y:{1,-5:f2}, Acc Z:{2,-5:f2}", acc.value(0), acc.value(1), acc.value(2));

                            XsVector gyr = packet.calibratedGyroscopeData();
                            Console.Write(" |Gyr X:{0,-5:f2}, Gyr Y:{1,-5:f2}, Gyr Z:{2,-5:f2}", gyr.value(0), gyr.value(1), gyr.value(2));

                            XsVector mag = packet.calibratedMagneticField();
                            Console.Write(" |Mag X:{0,-5:f2}, Mag Y:{1,-5:f2}, Mag Z:{2,-5:f2}", mag.value(0), mag.value(1), mag.value(2));
                        }

                        if (packet.containsOrientation())
                        {
                            XsQuaternion quaternion = packet.orientationQuaternion();
                            Console.Write("\rq0:{0,-5:f2}, q1:{1,-5:f2}, q2:{2,-5:f2}, q3:{3,-5:f2}", quaternion.w(), quaternion.x(), quaternion.y(), quaternion.z());

                            XsEuler euler = packet.orientationEuler();
                            Console.Write(" |Roll:{0,-5:f2}, Pitch:{1,-5:f2}, Yaw:{2,-5:f2}", euler.roll(), euler.pitch(), euler.yaw());
                        }

                        if (packet.containsLatitudeLongitude())
                        {
                            XsVector latLon = packet.latitudeLongitude();
                            Console.Write(" |Lat:{0,-5:f2}, Lon:{1,-5:f2}", latLon.value(0), latLon.value(1));
                        }

                        if (packet.containsAltitude())
                            Console.Write(" |Alt:{0,-5:f2}", packet.altitude());

                        if (packet.containsVelocity())
                        {
                            XsVector vel = packet.velocity(XsDataIdentifier.XDI_CoordSysEnu);
                            Console.Write(" |E:{0,-5:f2}, N:{1,-5:f2}, U:{2,-5:f2}", vel.value(0), vel.value(1), vel.value(2));
                        }

                        packet.Dispose();
                    }
                }
                Console.WriteLine("\n-----------------------------------------");

                Console.WriteLine("Stopping recording...");
                if (!device.stopRecording())
                    throw new Exception("Failed to stop recording. Aborting.");

                Console.WriteLine("Closing log file...");
                if (!device.closeLogFile())
                    throw new Exception("Failed to close log file. Aborting.");

                Console.WriteLine("Closing port...");
                control.closePort(mtPort.portName());

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
