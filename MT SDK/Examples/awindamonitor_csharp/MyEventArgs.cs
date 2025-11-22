
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
using System.Linq;
using System.Text;
using XDA;

namespace Xsens
{
    public class MtwEventArgs : EventArgs
    {
        public XsDevice Mtw { get; private set; }
        public bool Connected { get; private set; }
        public MtwEventArgs(XsDevice mtw, bool connected)
        {
            Mtw = mtw;
            Connected = connected;
        }
    }

    public class DataAvailableArgs : EventArgs
    {
        public XsDevice Device { get; private set; }
        public XsDataPacket Packet { get; private set; }
        public DataAvailableArgs(XsDevice device, XsDataPacket packet)
        {
            Device = device;
            Packet = packet;
        }
    }

    public class BatteryLevelChangedArgs : EventArgs
    {
        public XsDeviceId DeviceId { get; private set; }
        public int Level { get; private set; }
        public BatteryLevelChangedArgs(XsDeviceId deviceId, int level)
        {
            DeviceId = deviceId;
            Level = level;
        }
    }

    public class ProgressUpdateArgs : EventArgs
    {
        public XsDeviceId DeviceId { get; private set; }
		public int Current { get; private set; }
        public int Total { get; private set; }
        public string Identifier { get; private set; }
        public ProgressUpdateArgs(XsDeviceId deviceId, int current, int total, string identifier)
        {
            DeviceId = deviceId;
			Current = current;
            Total = total;
			Identifier = identifier;
        }
    }

    public class DeviceErrorArgs : EventArgs
    {
        public XsDeviceId DeviceId { get; private set; }
        public XsResultValue Result { get; private set; }
        public DeviceErrorArgs(XsDeviceId deviceId, XsResultValue result)
        {
            DeviceId = deviceId;
            Result = result;
        }
    }

    public class DeviceIdArg : EventArgs
    {
        public XsDeviceId DeviceId { get; private set; }
        public DeviceIdArg(XsDeviceId deviceId)
        {
            DeviceId = deviceId;
			string bla = DeviceId.toXsString().toString();
			string bla2 = deviceId.toXsString().toString();
        }	
    }

    public class PortInfoArg : EventArgs
    {
        public XsPortInfo PortInfo { get; private set; }
        public PortInfoArg(XsPortInfo portInfo)
        {
            PortInfo = portInfo;
        }
    }
}
