
//  ==> COPYRIGHT (C) 2025 MOVELLA TECHNOLOGIES OR SUBSIDIARIES WORLDWIDE <==
//  WARNING: COPYRIGHT (C) 2025 MOVELLA TECHNOLOGIES OR SUBSIDIARIES WORLDWIDE. ALL RIGHTS RESERVED.
//  THIS FILE AND THE SOURCE CODE IT CONTAINS (AND/OR THE BINARY CODE FILES FOUND IN THE SAME
//  FOLDER THAT CONTAINS THIS FILE) AND ALL RELATED SOFTWARE (COLLECTIVELY, "CODE") ARE SUBJECT
//  TO AN END USER LICENSE AGREEMENT ("AGREEMENT") BETWEEN XSENS AS LICENSOR AND THE AUTHORIZED
//  LICENSEE UNDER THE AGREEMENT. THE CODE MUST BE USED SOLELY WITH XSENS PRODUCTS INCORPORATED
//  INTO LICENSEE PRODUCTS IN ACCORDANCE WITH THE AGREEMENT. ANY USE, MODIFICATION, COPYING OR
//  DISTRIBUTION OF THE CODE IS STRICTLY PROHIBITED UNLESS EXPRESSLY AUTHORIZED BY THE AGREEMENT.
//  IF YOU ARE NOT AN AUTHORIZED USER OF THE CODE IN ACCORDANCE WITH THE AGREEMENT, YOU MUST STOP
//  USING OR VIEWING THE CODE NOW, REMOVE ANY COPIES OF THE CODE FROM YOUR COMPUTER AND NOTIFY
//  XSENS IMMEDIATELY BY EMAIL TO INFO@XSENS.COM. ANY COPIES OR DERIVATIVES OF THE CODE (IN WHOLE
//  OR IN PART) IN SOURCE CODE FORM THAT ARE PERMITTED BY THE AGREEMENT MUST RETAIN THE ABOVE
//  COPYRIGHT NOTICE AND THIS PARAGRAPH IN ITS ENTIRETY, AS REQUIRED BY THE AGREEMENT.
//  
//  THIS SOFTWARE CAN CONTAIN OPEN SOURCE COMPONENTS WHICH CAN BE SUBJECT TO 
//  THE FOLLOWING GENERAL PUBLIC LICENSES:
//  ==> Qt GNU LGPL version 3: http://doc.qt.io/qt-5/lgpl.html <==
//  ==> LAPACK BSD License:  http://www.netlib.org/lapack/LICENSE.txt <==
//  ==> StackWalker 3-Clause BSD License: https://github.com/JochenKalmbach/StackWalker/blob/master/LICENSE <==
//  ==> Icon Creative Commons 3.0: https://creativecommons.org/licenses/by/3.0/legalcode <==
//  

#ifndef XSDEVICESTATE_ENUM_H
#define XSDEVICESTATE_ENUM_H

/*!	\addtogroup enums Global enumerations
	@{
*/

//AUTO namespace xscontroller {
/*! \brief XsDevice state identifiers */
enum XsDeviceState
{
	XDS_Initial,					/*!< Initial unknown state */
	XDS_Config = 1,					/*!< Configuration mode. */
	XDS_Idle = 1,					/*!< Idle state. */ /*lint !e849*/
	XDS_Measurement,				/*!< Measurement mode, devices are transmitting data. */
	XDS_WaitingForRecordingStart,	/*!< The device is in measurement mode and waiting for an external trigger to go to recording state. \note Awinda Station only */
	XDS_Recording,					/*!< Same as measurement mode, but on Awinda systems retransmissions now also occur. \note Only on an Awinda Station is this an actual state in the device. For other devices, the state exists only in XDA. */
	XDS_FlushingData,				/*!< The device has been notified that it should stop recording. It is still measuring data and may flush retransmitted data to XDA. When XDA decides that it will not receive any more data that should be recorded, the state will be switched to XDS_Measurement automatically */
	XDS_Destructing,				/*!< The device is being destructed. After this callback, the device and any references to it are invalid. */
	XDS_Exporting,					/*!< Device is in a recording export state. */
	XDS_Synchronizing				/*!< Synchronizing state, device is synchronizing with other device(s). */
};
/*! @} */
typedef enum XsDeviceState XsDeviceState;
//AUTO }

#endif
