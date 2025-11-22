
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

function example_mti_parse_logfile()
%%------- HELP
%
% This script allows the user to understand the step-wise procedure to load and parse a file
%
% The code is divided into two parts:
%
% 1) Set-up of the system and read some data
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

logFileName = 'logfile.mtb';
%% Open the log file
fprintf('Opening log file... \n')
if ~h.XsControl_openLogFile(logFileName)
    fprintf('Failed to open log file. Aborting. \n')
    return
end
fprintf('Opened log file: %s \n', logFileName)

% Get number of devices in the file
deviceIdArray = h.XsControl_mainDeviceIds()';
if ~h.XsDeviceId_isMti(deviceIdArray) && ~h.XsDeviceId_isMtig(deviceIdArray)
    fprintf('No valid devices found in file. Aborting. \n')
    return
end
mtDevice = deviceIdArray;

if ~h.XsDeviceId_isValid(mtDevice)
    fprintf('No Mti device found. Aborting. \n')
    return
end

device = h.XsControl_device(mtDevice);

fprintf('Device: %s, with ID: %s found in file. \n', h.XsDevice_productCode(device), h.XsDeviceId_toString(h.XsDevice_deviceId(device)));

% By default XDA does not retain data for reading it back.
% By enabling this option XDA keeps the buffered data in a cache so it can be accessed 
% through XsDevice::getDataPacketByIndex or XsDevice::takeFirstDataPacketInQueue
h.XsDevice_setOptions(device, h.XsOption_XSO_RetainBufferedData, 0);

%% Load the log file and wait until it is loaded
% Wait for logfile to be fully loaded, there are three ways to do this:
% - callback: Demonstrated here, which has loading progress information
% - waitForLoadLogFileDone: Blocking function, returning when file is loaded
% - isLoadLogFileInProgress: Query function, used to query the device if the loading is done
%
% The callback option is used here.

h.registerevent({'onProgressUpdated', @eventhandlerXsens});
fileLoaded = 0;
currentProgress = 0;

h.XsDevice_loadLogFile(device);

w = waitbar(0, 'Loading the file...');
while fileLoaded == 0
    % Wait until file is loaded
    waitbar(currentProgress/100, w)
    pause(.2)
end
close(w);
fprintf('File is fully loaded\n')

%% Get total number of samples
packetCount = h.XsDevice_getDataPacketCount(device);


%% Export the data
fprintf('Exporting the data...\n')
s = '';
for index = 1:packetCount
    % Get data packet
    dataPacket =  h.XsDevice_getDataPacketByIndex(device,index);
    % Check if dataPacket is a data packet
    if dataPacket
        if h.XsDataPacket_containsCalibratedData(dataPacket)
            acc = cell2mat(h.XsDataPacket_calibratedAcceleration(dataPacket));
            s = strcat(s, sprintf('Acc X: %.2f, Acc Y: %.2f, Acc Z: %.2f', acc(1), acc(2), acc(3)));

            gyr = cell2mat(h.XsDataPacket_calibratedGyroscopeData(dataPacket));
            s = strcat(s, sprintf(' |Gyr X: %.2f, Gyr Y: %.2f, Gyr Z: %.2f', gyr(1), gyr(2), gyr(3)));

            mag = cell2mat(h.XsDataPacket_calibratedMagneticField(dataPacket));
            s = strcat(s, sprintf(' |Mag X: %.2f, Mag Y: %.2f, Mag Z: %.2f', mag(1), mag(2), mag(3)));
        end

        if h.XsDataPacket_containsOrientation(dataPacket)
            quaternion = cell2mat(h.XsDataPacket_orientationQuaternion(dataPacket,h.XsDataIdentifier_XDI_CoordSysEnu));
            s = strcat(s, sprintf('q0: %.2f, q1: %.2f, q2: %.2f, q3: %.2f ', quaternion(1), quaternion(2), quaternion(3), quaternion(4)));

            euler = cell2mat(h.XsDataPacket_orientationEuler(dataPacket,h.XsDataIdentifier_XDI_CoordSysEnu));
            s = strcat(s, sprintf(' |Roll: %.2f, Pitch: %.2f, Yaw: %.2f ', euler(1), euler(2), euler(3)));
        end

        if h.XsDataPacket_containsLatitudeLongitude(dataPacket)
            latlon = cell2mat(h.XsDataPacket_latitudeLongitude(dataPacket));
            s = strcat(s, sprintf(' |Lat: %7.2f, Lon: %7.2f ', latlon(1), latlon(2)));
        end

        if h.XsDataPacket_containsAltitude(dataPacket)
            s = strcat(s, sprintf(' |Alt: %7.2f ', h.XsDataPacket_altitude(dataPacket)));
        end

        if h.XsDataPacket_containsVelocity(dataPacket)
            vel = cell2mat(h.XsDataPacket_velocity(dataPacket,h.XsDataIdentifier_XDI_CoordSysEnu));
            s = strcat(s, sprintf(' |E: %7.2f, N: %7.2f, U: %7.2f ', vel(1), vel(2), vel(3)));
        end

        s = strcat(s,'\n');
    end
end

exportFileName = 'exportfile.txt';
outfile = fopen(exportFileName, 'w');
fprintf(outfile, s);
fclose(outfile);
fprintf('File is exported to: %s \n', exportFileName);


%% Close XsControl object
fprintf('Closing XsControl object... \n');
h.XsControl_close();

%% Release COM-object
fprintf('Releasing COM-object... \n');
delete(h);
clear h;
fprintf('Successful exit. \n');

%% Event handler
    function eventhandlerXsens(varargin)
        % Device pointer is zero for progressUpdated
        devicePtr = varargin{3}{1};
        % The current progress
        currentProgress = varargin{3}{2};
        % The total work to be done
        total = varargin{3}{3};
        % Identifier, in the case the file name which is loaded
        identifier = varargin{3}{4};
        if currentProgress == 100
            fileLoaded = 1;
        end
    end
end
