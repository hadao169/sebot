
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

#include "system_clock_config.h"
#include "init_gpio.h"
#include "init_uart.h"
#include "init_spi.h"
#include "init_i2c.h"
#include "mtssp_driver_i2c.h"
#include "mtssp_driver_spi.h"
#include "application.h"


#define BUS_MODE BUS_Spi
//#define BUS_MODE BUS_I2c

#define MTI_I2C_DEVICE_ADDRESS 0x6B


/*!	\brief	Main entry point of example_basic_mtssp
	Initializes the board and device drivers and starts the application
*/
int main()
{
	HAL_Init();
	SystemClock_Config();

	initUart(921600);
	HostInterface* host = new HostInterface();

	const BusType busType = BUS_MODE;
	host->printf("\n----------------------------------------------------------------\n");
	host->printf("Example MTi I2C/SPI: Protocol Explorer\n");
	if (busType == BUS_Spi)
		host->printf("Bus mode: SPI\n");
	else
		host->printf("Bus mode: I2C\n");

	initGpio(busType);

	MtsspDriver* driver;
	if (busType == BUS_Spi)
	{
		initSpi();
		driver = new MtsspDriverSpi();
	}
	else if (busType == BUS_I2c)
	{
		initI2c();
		driver = new MtsspDriverI2c(MTI_I2C_DEVICE_ADDRESS);
	}

	Application app(host, driver);
	app.run();
}
