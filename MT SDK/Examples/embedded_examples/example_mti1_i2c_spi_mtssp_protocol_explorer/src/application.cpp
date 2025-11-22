
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
#include <algorithm>

/*!	\class Application
	The main application class of 'example_mti1_i2c_spi_mtssp_protocol_explorer'
*/


/*!	\brief Constructs an Application
	\param[in] driver The MtsspDriver for communicating with the MTi
*/
Application::Application(HostInterface* hostInterface, MtsspDriver* driver)
	: m_host(hostInterface)
	, m_driver(driver)
{
	m_device = new MtsspInterface(m_driver);
	setGpioInterruptInterface(this);
}


/*!	\brief Defines the main loop of the program which handles user commands
*/
void Application::run()
{
	printHelpText();

	while (true)
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

		if (c == 'i')
		{
			uint8_t version, dataReadyConfig;
			m_device->readProtocolInfo(version, dataReadyConfig);
			m_host->printf("Protocol version: %d\n", version);
			printDataReadyConfig(dataReadyConfig);
			m_host->printf("\n");
		}

		if (c == 'o')
		{
			uint8_t dataReadyConfig;
			bool result = enterDataReadyConfig(dataReadyConfig);
			if (result)
			{
				m_host->printf("You entered:\n");
				printDataReadyConfig(dataReadyConfig);
				m_host->printf("Write this to device? (y/n)\n");
				char c = m_host->getch();
				if (c == 'y')
				{
					m_device->configureProtocol(dataReadyConfig);
				}
			}
		}

		if (c == 'c')
		{
			Xbus_message(m_xbusTxBuffer, 0xFF, XMID_GotoConfig, 0);
			m_device->sendXbusMessage(m_xbusTxBuffer);
		}

		if (c == 'm')
		{
			Xbus_message(m_xbusTxBuffer, 0xFF, XMID_GotoMeasurement, 0);
			m_device->sendXbusMessage(m_xbusTxBuffer);
		}

		if (c == 'd')
		{
			Xbus_message(m_xbusTxBuffer, 0xFF, XMID_ReqDid, 0);
			m_device->sendXbusMessage(m_xbusTxBuffer);
		}

		if (c == 'f')
		{
			Xbus_message(m_xbusTxBuffer, 0xFF, XMID_ReqFirmwareRevision, 0);
			m_device->sendXbusMessage(m_xbusTxBuffer);
		}

		if (c == 's')
		{
			uint16_t notificationMessageSize, measurementMessageSize;
			m_device->readPipeStatus(notificationMessageSize, measurementMessageSize);
			m_host->printf("notificationMessageSize = %d, measurementMessageSize = %d\n", notificationMessageSize, measurementMessageSize);
		}

		if (c == 'r')
		{
			m_host->printf("From which pipe?\n");
			m_host->printf("Press 'n' for notification pipe\n");
			m_host->printf("Press 'm' for measurement pipe\n");
			char c2 = m_host->getch();
			m_host->printf("\n");
			uint8_t pipe = (c2 == 'm') ? XBUS_MEASUREMENT_PIPE : XBUS_NOTIFICATION_PIPE;
			m_host->printf("How many bytes should be read?\n");
			size_t nofBytes = m_host->readInteger();
			nofBytes = std::min(nofBytes, sizeof(m_rxBuffer));
			m_device->readFromPipe(m_rxBuffer, nofBytes, pipe);
			m_host->printf("Data read from %s pipe\n", (pipe == XBUS_MEASUREMENT_PIPE ? "measurement" : "notification"));
			printData(m_rxBuffer, nofBytes);
		}

	}
}


/*!	\brief Prints the help text to the console
*/
void Application::printHelpText()
{
	m_host->printf("\n");
	m_host->printf("(h) help:     Print this help text\n");
	m_host->printf("(R) reset:    Reset the device\n");
	m_host->printf("(i) info:     Request protocol information (Opcode 0x01)\n");
	m_host->printf("(o) options:  Configure protocol options (Opcode 0x02)\n");
	m_host->printf("(c) config:   Goto config mode (Opcode 0x03)\n");
	m_host->printf("(m) measure:  Goto measurement mode (Opcode 0x03)\n");
	m_host->printf("(d) deviceid: Request device id (Opcode 0x03)\n");
	m_host->printf("(f) fwrev:    Request firmware revision (Opcode 0x03)\n");
	m_host->printf("(s) status:   Request pipe status (Opcode 0x04))\n");
	m_host->printf("(r) read:     Read data from notification or measurement pipe (Opcode 0x05/0x06)\n");
	m_host->printf("\n");
}


/*!	\brief Resets the MTi
*/
void Application::resetDevice()
{
	HAL_GPIO_WritePin(RESET_PORT, RESET_PIN, GPIO_PIN_SET);
	wait_us(1000);
	HAL_GPIO_WritePin(RESET_PORT, RESET_PIN, GPIO_PIN_RESET);
}


/*!	\brief Prints binary data as hex bytes to the console
*/
void Application::printData(const uint8_t* data, int dataSize)
{
	for (int n = 0; n < dataSize; n++)
	{
		m_host->printf("%02X ", data[n]);
	}
	m_host->printf("\n");
}


/*!	\brief Prints the flags in the DataReadyConfig byte
*/
void Application::printDataReadyConfig(uint8_t dataReadyConfig)
{
	m_host->printf("DataReady config: %d (0x%02X)\n", dataReadyConfig, dataReadyConfig);
	if (dataReadyConfig & 0xF0)
	{
		m_host->printf("Invalid value\n");
		return;
	}

	if (dataReadyConfig & (1 << DRDY_CONFIG_POL_POS))
		m_host->printf("\tPolarity: Idle high\n");
	else
		m_host->printf("\tPolarity: Idle low\n");

	if (dataReadyConfig & (1 << DRDY_CONFIG_OTYPE_POS))
		m_host->printf("\tOutput type: Open drain\n");
	else
		m_host->printf("\tOutput type: Push-pull\n");

	if (dataReadyConfig & (1 << DRDY_CONFIG_NEVENT_POS))
		m_host->printf("\tDRDY on notification pipe is enabled\n");
	else
		m_host->printf("\tDRDY on notification pipe is disabled\n");

	if (dataReadyConfig & (1 << DRDY_CONFIG_MEVENT_POS))
		m_host->printf("\tDRDY on measurement pipe is enabled\n");
	else
		m_host->printf("\tDRDY on measurement pipe is disabled\n");
}


/*!	\brief Let the user interactively configure a new DataReady configuration
*/
bool Application::enterDataReadyConfig(uint8_t& dataReadyConfig)
{
	dataReadyConfig = 0;

	{
		uint8_t polarity;
		m_host->printf("Enter polarity (0 = idle low, 1 = idle high): ");
		polarity = m_host->readInteger();
		dataReadyConfig |= (polarity << DRDY_CONFIG_POL_POS);
	}

	{
		uint8_t outputType;
		m_host->printf("Enter output type (0 = push-pull, 1 = open drain): ");
		outputType = m_host->readInteger();
		dataReadyConfig |= (outputType << DRDY_CONFIG_OTYPE_POS);
	}

	{
		uint8_t enableNotificationPipeEvent;
		m_host->printf("Enable event on notification pipe (0 = disable, 1 = enable): ");
		enableNotificationPipeEvent = m_host->readInteger();
		dataReadyConfig |= (enableNotificationPipeEvent << DRDY_CONFIG_NEVENT_POS);
	}

	{
		uint8_t enableMeasurementPipeEvent;
		m_host->printf("Enable event on measurement pipe (0 = disable, 1 = enable): ");
		enableMeasurementPipeEvent = m_host->readInteger();
		dataReadyConfig |= (enableMeasurementPipeEvent << DRDY_CONFIG_MEVENT_POS);
	}

	return true;
}


/*!	\brief Handles interrupts on the DataReady line
*/
void Application::handleGpioInterrupt()
{
	if (HAL_GPIO_ReadPin(DATA_READY_PORT, DATA_READY_PIN) == GPIO_PIN_SET)
		m_host->printf("Data ready line became high\n");
	else
		m_host->printf("Data ready line became low\n");
}

