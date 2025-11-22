
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

#include "application.h"
#include "init_gpio.h"
#include "board.h"
#include "mtssp_interface.h"
#include "xbusmessageid.h"
#include "wait.h"
#include "xbus.h"
#include <string>
#include "xbustostring.h"
#include "fwupdate.h"
#include "xffdata.h"


/*!	\class Application
	The main application class of 'example_mti1_i2c_spi_firmware_updater'
*/

Application* g_thisPtr;

/*!	\brief Returns the value of the DataReady line
*/
bool checkDataReadyLine()
{
	return HAL_GPIO_ReadPin(DATA_READY_PORT, DATA_READY_PIN) == GPIO_PIN_SET;
}

/*!	\brief Callback function for FwUpdate which provides firmware-file (xff) data
*/
uint32_t readXffData(uint8_t* buffer, uint32_t offset, uint32_t length)
{
	uint32_t n;
	for (n = 0; n < length; n++)
	{
		if (offset + n == g_xffData_length)
			break;
		buffer[n] = g_xffData[offset + n];
	}
	return n;
}

/*!	\brief Callback function for FwUpdate for sending Xbus messages to the device
*/
void sendXbusMessageWrapper(uint8_t const* xbusMessage)
{
	g_thisPtr->sendXbusMessage(xbusMessage);
}

/*!	\brief Callback function for FwUpdate for signaling that a firmware update is finished
*/
void readyHandler(FWU_Result result)
{
	if (result == FWU_Success)
	{
		LOG("Firmware update finished\n");
	}
	else if (result == FWU_Failed)
	{
		LOG("Firmware update failed\n");
	}
}

/*!	\brief Constructs the Application
	\param[in] device The MtsspInterface for communicating with the MTi
*/
Application::Application(HostInterface* hostInterface, MtsspInterface* device)
	: m_host(hostInterface)
	, m_state(STATE_App_Idle)
	, m_device(device)
{
	g_thisPtr = this;
	m_fwUpdate.m_readXffData = readXffData;
	m_fwUpdate.m_sendXbusMessage = sendXbusMessageWrapper;
	m_fwUpdate.m_readyHandler = readyHandler;
	m_fwUpdate.m_txBuffer = m_fwuTxBuffer;
}


/*!	\brief Defines the main loop of the program which handles user commands
*/
void Application::run()
{
	handleEvent(EVT_Start);

	while (true)
	{
		if (checkDataReadyLine())
		{
			readDataFromDevice();
		}

		if (m_host->kbhit())
		{
			char c = m_host->getch();
			m_host->printf("\n");

			if (c == 'h')
			{
				printHelpText();
			}

			if (c == 'R')
			{
				resetDevice();
			}

			if (c == 'r')
			{
				Xbus_message(m_xbusTxBuffer, 0xFF, XMID_Reset, 0);
				m_device->sendXbusMessage(m_xbusTxBuffer);
			}

			if (c == 'v')
			{
				Xbus_message(m_xbusTxBuffer, 0xFF, XMID_ReqFirmwareRevision, 0);
				m_device->sendXbusMessage(m_xbusTxBuffer);
			}

			if (c == 'b')
			{
				Xbus_message(m_xbusTxBuffer, 0xFF, XMID_GotoBootLoader, 0);
				m_device->sendXbusMessage(m_xbusTxBuffer);
			}

			if (c == 'u')
			{
				FwUpdate_init(&m_fwUpdate);
				FwUpdate_start(&m_fwUpdate);
			}
		}
	}
}


/*!	\brief Send an Xbus message to the device
*/
void Application::sendXbusMessage(uint8_t const* xbusMessage)
{
	m_device->sendXbusMessage(xbusMessage);
}


/*!	\brief Prints the help text to the console
*/
void Application::printHelpText()
{
	m_host->printf("\n");
	m_host->printf("I2C/SPI Firmware updater example\n");
	m_host->printf("Press one of the following keys to execute a command:\n");
	m_host->printf("(h) help:       Print this help text\n");
	m_host->printf("(R) Reset:      Hard reset the device\n");
	m_host->printf("(r) reset:      Soft reset the device\n");
	m_host->printf("(v) version:    Request firmware version\n");
	m_host->printf("(b) bootloader: Goto bootloader mode\n");
	m_host->printf("(u) update:     Start firmware update\n");
	m_host->printf("\n");
}


/*!	\brief Implements the state machine which defines the program
*/
void Application::handleEvent(Event event, const uint8_t* data)
{
	switch (m_state)
	{
		case STATE_App_Idle:
		{
			if (event == EVT_Start)
			{
				printHelpText();
			}

			if (event == EVT_XbusMessage)
			{
				m_host->printf("Got Xbus message: %s\n", xbusToString(data));

				if (Xbus_getMessageId(data) == XMID_FirmwareUpdate)
				{
					FwUpdate_handleXbus(&m_fwUpdate, data);
				}
			}
		} break;
	}
}


/*!	\brief Resets the MTi
*/
void Application::resetDevice()
{
	HAL_GPIO_WritePin(RESET_PORT, RESET_PIN, GPIO_PIN_SET);
	wait_us(1000);
	HAL_GPIO_WritePin(RESET_PORT, RESET_PIN, GPIO_PIN_RESET);
}


/*!	\brief Read data from the Notification and Control pipes of the device
*/
void Application::readDataFromDevice()
{
	uint16_t notificationMessageSize;
	uint16_t measurementMessageSize;
	m_device->readPipeStatus(notificationMessageSize, measurementMessageSize);

	m_xbusRxBuffer[0] = XBUS_PREAMBLE;
	m_xbusRxBuffer[1] = XBUS_MASTERDEVICE;

	if (notificationMessageSize && notificationMessageSize < sizeof(m_xbusRxBuffer))
	{
		m_device->readFromPipe(&m_xbusRxBuffer[2], notificationMessageSize, XBUS_NOTIFICATION_PIPE);
		handleEvent(EVT_XbusMessage, m_xbusRxBuffer);
	}

	if (measurementMessageSize && measurementMessageSize < sizeof(m_xbusRxBuffer))
	{
		m_device->readFromPipe(&m_xbusRxBuffer[2], measurementMessageSize, XBUS_MEASUREMENT_PIPE);
		handleEvent(EVT_XbusMessage, m_xbusRxBuffer);
	}
}


