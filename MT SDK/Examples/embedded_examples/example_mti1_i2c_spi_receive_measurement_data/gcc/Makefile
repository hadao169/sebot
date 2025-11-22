MODULE_NAME	:= example_mti1_i2c_spi_receive_measurement_data

EXAMPLE_ROOT	:= ../..
EXAMPLE_SRC	:= $(EXAMPLE_ROOT)/$(MODULE_NAME)/src

MODULE_CPPSRC	:= \
	$(EXAMPLE_SRC)/main.cpp \
	$(EXAMPLE_SRC)/application.cpp \
	$(EXAMPLE_SRC)/xbustostring.cpp	\
	$(EXAMPLE_ROOT)/lib/mtinterface/mtssp_driver_i2c.cpp \
	$(EXAMPLE_ROOT)/lib/mtinterface/mtssp_driver_spi.cpp \
	$(EXAMPLE_ROOT)/lib/mtinterface/mtssp_interface.cpp \
	$(EXAMPLE_ROOT)/lib/fifobuffer.cpp \
	$(EXAMPLE_ROOT)/lib/hostinterface.cpp \
	$(EXAMPLE_ROOT)/lib/init_gpio.cpp \
	$(EXAMPLE_ROOT)/lib/init_spi.cpp \
	$(EXAMPLE_ROOT)/lib/init_i2c.cpp \
	$(EXAMPLE_ROOT)/lib/init_uart.cpp \
	$(EXAMPLE_ROOT)/lib/runtimeerror.cpp \
	$(EXAMPLE_ROOT)/lib/systick.cpp \
	$(EXAMPLE_ROOT)/lib/wait.cpp \
	$(EXAMPLE_ROOT)/lib/system_clock_config.cpp \
	
	
	
	
	
MODULE_CSRC	:= \
	$(EXAMPLE_ROOT)/lib/xbus/xbus.c \
	$(EXAMPLE_ROOT)/lib/drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal.c \
	$(EXAMPLE_ROOT)/lib/drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_cortex.c \
	$(EXAMPLE_ROOT)/lib/drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_dma.c \
	$(EXAMPLE_ROOT)/lib/drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_dma_ex.c \
	$(EXAMPLE_ROOT)/lib/drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_gpio.c \
	$(EXAMPLE_ROOT)/lib/drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_i2c.c \
	$(EXAMPLE_ROOT)/lib/drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_rcc.c \
	$(EXAMPLE_ROOT)/lib/drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_rcc_ex.c \
	$(EXAMPLE_ROOT)/lib/drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_spi.c \
	$(EXAMPLE_ROOT)/lib/drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_uart.c \
	$(EXAMPLE_ROOT)/lib/drivers/CMSIS/Device/ST/STM32F4xx/Source/Templates/system_stm32f4xx.c

	
MODULE_ASRC += \
	$(EXAMPLE_ROOT)/lib/drivers/CMSIS/Device/ST/STM32F4xx/Source/Templates/gcc/startup_stm32f401xe.s
	

VPATH := $(EXAMPLE_SRC)
VPATH += $(EXAMPLE_ROOT)/lib
VPATH += $(EXAMPLE_ROOT)/lib/mtinterface
VPATH += $(EXAMPLE_ROOT)/lib/xbus
VPATH += $(EXAMPLE_ROOT)/lib/drivers/STM32F4xx_HAL_Driver/Src
VPATH += $(EXAMPLE_ROOT)/lib/drivers/CMSIS/Device/ST/STM32F4xx/Source/Templates
VPATH += $(EXAMPLE_ROOT)/lib/drivers/CMSIS/Device/ST/STM32F4xx/Source/Templates/gcc


TOOLCHAIN_DEFINES		:= -DUSE_HAL_DRIVER -DSTM32F401xE

TOOLCHAIN_ARCHOPTS		:= -mcpu=cortex-m0 -mthumb
TOOLCHAIN_COMMONOPTS    	:= $(TOOLCHAIN_ARCHOPTS) $(TOOLCHAIN_DEFINES) -ffunction-sections -fdata-sections -fmessage-length=0 -Os 
TOOLCHAIN_CCOPTS		:= -std=c99 -include preinclude.h
TOOLCHAIN_CXXOPTS		:= -fno-rtti -fno-exceptions -include preinclude.h
LINKER_SCRIPT			:= stm32f401re_flash.ld
TOOLCHAIN_LDOPTS		:= $(TOOLCHAIN_ARCHOPTS) -fno-rtti -fno-exceptions -T $(LINKER_SCRIPT)

ARCH_POSTFIX			:= CM0
BOARD_SETUP_PATH		:= ../../board/$(BOARD)/setup
BOARD_DRIVERS_PATH		:= ../../board/$(BOARD)/drivers
BOARD_HAL			:= $(BOARD_DRIVERS_PATH)/STM32F0xx_HAL_Driver
BOARD_CMSIS			:= $(BOARD_DRIVERS_PATH)/CMSIS
BOARD_CMSIS_DEVICE		:= $(BOARD_CMSIS)/Device/ST/STM32F0xx


INCLUDE_PATH += \
	-I$(EXAMPLE_SRC) \
	-I$(EXAMPLE_ROOT)/lib \
	-I$(EXAMPLE_ROOT)/lib/mtinterface \
	-I$(EXAMPLE_ROOT)/lib/xbus \
	-I$(EXAMPLE_ROOT)/lib/setup \
	-I$(EXAMPLE_ROOT)/lib/drivers/CMSIS/Include \
	-I$(EXAMPLE_ROOT)/lib/drivers/CMSIS/Device/ST/STM32F4xx/Include \
	-I$(EXAMPLE_ROOT)/lib/drivers/STM32F4xx_HAL_Driver/Inc


.PHONY: all clean

BUILDPATH	:= build

TARGET		:= $(BUILDPATH)/$(MODULE_NAME).elf

all:		$(TARGET)

TOOLCHAIN	:= arm-none-eabi-

CC		:= $(TOOLCHAIN)gcc
CXX		:= $(TOOLCHAIN)g++
AS		:= $(TOOLCHAIN)gcc
OBJCOPY		:= $(TOOLCHAIN)objcopy

COMMONOPTS	:= $(TOOLCHAIN_COMMONOPTS)
COMMONOPTS	+= $(INCLUDE_PATH)

CXXOPTS		:= $(COMMONOPTS) $(TOOLCHAIN_CXXOPTS)
CCOPTS		:= $(COMMONOPTS) $(TOOLCHAIN_CCOPTS)
ASOPTS		:= -x assembler-with-cpp $(COMMONOPTS)

LD		:= $(TOOLCHAIN)g++
LDOPTS		:= $(TOOLCHAIN_LDOPTS) -Wl,--gc-sections,-Map=$(BUILDPATH)/$(MODULE_NAME).map,--cref -specs=nano.specs -specs=nosys.specs -u _printf_float

compile_c	= echo Compiling C: $1 \
		&& $(CC) $(CCOPTS) -c $1 -o $2

compile_cpp	= echo Compiling C++: $1 \
		&& $(CXX) $(CXXOPTS) -c $1 -o $2

compile_asm 	= echo Assembling: $1 \
		&& $(AS) $(ASOPTS) -c $1 -o $2

build_exe	= echo Creating executable: $1 \
		&& $(LD) -o $1 $2 $3 $(LDOPTS) $(LIBS) \
		&& $(OBJCOPY) -O binary $1 $(basename $1).bin \
		&& $(OBJCOPY) -O ihex $1 $(basename $1).hex

BUILDPATH_FILE	:= $(BUILDPATH)/.empty

$(BUILDPATH_FILE):
	@echo Creating build directory: $(BUILDPATH)
	@mkdir -p $(BUILDPATH)
	@touch $(BUILDPATH_FILE)

$(BUILDPATH)/%.o: %.c $(BUILDPATH_FILE) Makefile
	@$(call compile_c,$<,$@)

$(BUILDPATH)/%.o: %.cpp $(BUILDPATH_FILE) Makefile
	@$(call compile_cpp,$<,$@)

$(BUILDPATH)/%.o: %.s $(BUILDPATH_FILE) Makefile
	@$(call compile_asm,$<,$@)

MODULE_COBJS	:= $(patsubst %.c, $(BUILDPATH)/%.o, $(notdir $(MODULE_CSRC)))
MODULE_CPPOBJS	:= $(patsubst %.cpp, $(BUILDPATH)/%.o, $(notdir $(MODULE_CPPSRC)))
MODULE_AOBJS	:= $(patsubst %.s, $(BUILDPATH)/%.o, $(notdir $(MODULE_ASRC)))

OBJ_FILES 	:= $(MODULE_COBJS) $(MODULE_CPPOBJS) $(MODULE_AOBJS)

$(TARGET): $(OBJ_FILES) $(LINKER_SCRIPT)
	@$(call build_exe,$@,$(OBJ_FILES))

clean:
	@rm -rf $(BUILDPATH)
