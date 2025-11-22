
%  Copyright (c) 2003-2025 Movella Technologies B.V. or subsidiaries worldwide.
%  All rights reserved.
%  
%  Redistribution and use in source and binary forms, with or without modification,
%  are permitted provided that the following conditions are met:
%  
%  1.	Redistributions of source code must retain the above copyright notice,
%  	this list of conditions, and the following disclaimer.
%  
%  2.	Redistributions in binary form must reproduce the above copyright notice,
%  	this list of conditions, and the following disclaimer in the documentation
%  	and/or other materials provided with the distribution.
%  
%  3.	Neither the names of the copyright holders nor the names of their contributors
%  	may be used to endorse or promote products derived from this software without
%  	specific prior written permission.
%  
%  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
%  EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
%  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
%  THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
%  SPECIAL, EXEMPLARY OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT 
%  OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
%  HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY OR
%  TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
%  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.THE LAWS OF THE NETHERLANDS 
%  SHALL BE EXCLUSIVELY APPLICABLE AND ANY DISPUTES SHALL BE FINALLY SETTLED UNDER THE RULES 
%  OF ARBITRATION OF THE INTERNATIONAL CHAMBER OF COMMERCE IN THE HAGUE BY ONE OR MORE 
%  ARBITRATORS APPOINTED IN ACCORDANCE WITH SAID RULES.
%  

function example_mti_receive_data()
%%------- HELP
%
% This script allows the user to understand the step-wise procedure to receive data from MTi devices.
%
% The code is divided into two parts:
%
% 1) Set-up of the system
%
% 2) Event handler of the MT.
%
%%-------- IMPORTANT NOTES
%
% - For the code to work properly, make sure the code folder is your current directory in Matlab.
%
% - This code supports both 32 and 64 bits Matlab version.
%
% - The code requires xsensdeviceapi_com.dll to be registered in the Windows
%   register (this is done automatically during the Xsens MT SDK installation)
%

%% Launch activex server
try
    switch computer
        case 'PCWIN'
            h = actxserver('xsensdeviceapi_com32.IXsensDeviceApi');
        case 'PCWIN64'
            h = actxserver('xsensdeviceapi_com64.IXsensDeviceApi');
        otherwise
            error('XDA:os','Unsupported OS');
    end
catch e
    fprintf('\nPlease reinstall MT SDK or check manual,\n Xsens Device Api is not found.')
    rethrow(e);
end
fprintf('\nActiveXsens server - activated \n');

version = h.xdaVersion;
fprintf('Using XDA version: %.0f.%.0f.%.0f\n',version{1:3})
if length(version)>3
    fprintf('XDA build: %.0f%s\n',version{4:5})
end

%% Scan for devices
fprintf('Scanning for devices... \n')
ports = h.XsScanner_scanPorts(0,100,true,true);

% Find an MTi device
numPorts = size(ports,1);
for port = 1:numPorts
    if (h.XsDeviceId_isMti(ports{port,1}) || h.XsDeviceId_isMtig(ports{port,1}))
        mtPort = ports(port,:);
        break
    end
end

if isempty(mtPort)
    fprintf('No MTi device found. Aborting. \n');
    return
end

deviceId = mtPort{1};
portName = mtPort{3};
baudrate = mtPort{4};

fprintf('Found a device with: \n');
fprintf(' Device ID: %s \n', h.XsDeviceId_toDeviceTypeString(deviceId, false));
fprintf(' Baudrate: %d \n', baudrate);
fprintf(' Port name: %s \n', portName);

%% Open port
fprintf('Opening port... \n')
if ~h.XsControl_openPort(portName, baudrate, 0, true)
    fprintf('Could not open port. Aborting. \n');
    return
end

% Get the device object
device = h.XsControl_device(deviceId);
fprintf('Device: %s, with ID: %s opened. \n', h.XsDevice_productCode(device), h.XsDeviceId_toString(h.XsDevice_deviceId(device)));

%% Register eventhandler
h.registerevent({'onLiveDataAvailable',@eventhandlerXsens});
h.setCallbackOption(h.XsComCallbackOptions_XSC_LivePacket, h.XsComCallbackOptions_XSC_None);
% show events using h.events and h.eventlisteners too see which are registerd;

%% Put device into configuration mode
fprintf('Putting device into configuration mode... \n')
if ~h.XsDevice_gotoConfig(device)
    fprintf('Could not put device into configuration mode. Aborting. \n');
    return
end

%% Configure the device
fprintf('Configuring the device... \n')
if (h.XsDeviceId_isImu(deviceId))
    outputConfig = {h.XsDataIdentifier_XDI_PacketCounter,0;
        h.XsDataIdentifier_XDI_SampleTimeFine,0;
        h.XsDataIdentifier_XDI_Acceleration,100;
        h.XsDataIdentifier_XDI_RateOfTurn,100;
        h.XsDataIdentifier_XDI_MagneticField,100};
elseif (h.XsDeviceId_isVru(deviceId) || h.XsDeviceId_isAhrs(deviceId))
    outputConfig = {h.XsDataIdentifier_XDI_PacketCounter,0;
        h.XsDataIdentifier_XDI_SampleTimeFine,0;
        h.XsDataIdentifier_XDI_Quaternion,100};
elseif (h.XsDeviceId_isGnss(deviceId))
    outputConfig = {h.XsDataIdentifier_XDI_PacketCounter,0;
        h.XsDataIdentifier_XDI_SampleTimeFine,0;
        h.XsDataIdentifier_XDI_Quaternion,100;
        h.XsDataIdentifier_XDI_LatLon,100;
        h.XsDataIdentifier_XDI_AltitudeEllipsoid,100;
        h.XsDataIdentifier_XDI_VelocityXYZ,100};
else
    fprintf('Unknown device while configuring. Aborting. \n');
    return
end

if ~h.XsDevice_setOutputConfiguration(device,outputConfig)
    fprintf('Could not configure the device. Aborting. \n');
    return
end

%% Create a log file
fprintf('Creating a log file... \n')
filename = [cd '\logfile.mtb'];
if h.XsDevice_createLogFile(device,filename) ~= 0 % XRV_OK
    fprintf('Failed to create a log file. Aborting. \n');
    return
end

fprintf('Created a log file: %s \n',filename);

%% Put device into measurement mode
fprintf('Putting device into measurement mode... \n')
if ~h.XsDevice_gotoMeasurement(device)
    fprintf('Could not put device into measurement mode. Aborting. \n');
    return
end

%% Start recording
fprintf('Starting recording... \n')
if ~h.XsDevice_startRecording(device)
    fprintf('Failed to start recording. Aborting. \n');
    return
end

%% Record data
fprintf('Recording data for 10 seconds. \n');
tic;
while toc < 10
    pause(.01);
end

%% Stop recording
fprintf('\nStopping recording... \n');
if ~h.XsDevice_stopRecording(device)
    fprintf('Failed to stop recording. Aborting. \n');
    return
end

%% Close log file
fprintf('Closing log file... \n');
if ~h.XsDevice_closeLogFile(device)
    fprintf('Failed to close log file. Aborting. \n');
    return
end

%% Close port and XsControl object
fprintf('Closing port and XsControl object... \n');
h.XsControl_closePort(portName);
h.XsControl_close();

%% Release COM-object
fprintf('Releasing COM-object... \n');
delete(h);
clear h;
fprintf('Successful exit. \n');

%% Event handler
    function eventhandlerXsens(varargin)
        % only action when new datapacket arrived
        dataPacket = varargin{3}{2};

        if h.XsDataPacket_containsCalibratedData(dataPacket)
            acc = cell2mat(h.XsDataPacket_calibratedAcceleration(dataPacket));
            fprintf('\rAcc X: %.2f, Acc Y: %.2f, Acc Z: %.2f', acc(1), acc(2), acc(3));

            gyr = cell2mat(h.XsDataPacket_calibratedGyroscopeData(dataPacket));
            fprintf(' |Gyr X: %.2f, Gyr Y: %.2f, Gyr Z: %.2f', gyr(1), gyr(2), gyr(3));

            mag = cell2mat(h.XsDataPacket_calibratedMagneticField(dataPacket));
            fprintf(' |Mag X: %.2f, Mag Y: %.2f, Mag Z: %.2f', mag(1), mag(2), mag(3));
        end

        if h.XsDataPacket_containsOrientation(dataPacket)
            quaternion = cell2mat(h.XsDataPacket_orientationQuaternion(dataPacket,h.XsDataIdentifier_XDI_CoordSysEnu));
            fprintf('\rq0: %.2f, q1: %.2f, q2: %.2f, q3: %.2f', quaternion(1), quaternion(2), quaternion(3), quaternion(4));

            euler = cell2mat(h.XsDataPacket_orientationEuler(dataPacket,h.XsDataIdentifier_XDI_CoordSysEnu));
            fprintf(' |Roll: %.2f, Pitch: %.2f, Yaw: %.2f', euler(1), euler(2), euler(3));
        end

        if h.XsDataPacket_containsLatitudeLongitude(dataPacket)
            latlon = cell2mat(h.XsDataPacket_latitudeLongitude(dataPacket));
            fprintf(' |Lat: %7.2f, Lon: %7.2f', latlon(1), latlon(2));
        end

        if h.XsDataPacket_containsAltitude(dataPacket)
            alt = h.XsDataPacket_altitude(dataPacket);
            fprintf(' |Alt: %7.2f', alt);
        end

        if h.XsDataPacket_containsVelocity(dataPacket)
            vel = cell2mat(h.XsDataPacket_velocity(dataPacket,h.XsDataIdentifier_XDI_CoordSysEnu));
            fprintf(' |E: %.2f, N: %.2f, U: %.2f', vel(1), vel(2), vel(3));
        end

        h.dataPacketHandled(varargin{3}{1}, dataPacket);
    end
end
