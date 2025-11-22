TARGETS=example_mti1_i2c_spi_mtssp_protocol_explorer example_mti1_i2c_spi_receive_measurement_data example_mti1_i2c_spi_firmware_updater

CLEAN_TARGETS=$(patsubst %,%.clean,$(TARGETS))

.PHONY: all $(TARGETS) clean
all: $(TARGETS)

$(TARGETS):
	$(MAKE) -C $@/gcc
	
$(CLEAN_TARGETS):
	$(MAKE) -C $(patsubst %.clean,%,$@)/gcc clean

clean: $(CLEAN_TARGETS)
