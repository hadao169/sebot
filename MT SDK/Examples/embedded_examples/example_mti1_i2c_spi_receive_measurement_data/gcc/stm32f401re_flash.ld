
OUTPUT_FORMAT("elf32-littlearm", "elf32-bigarm", "elf32-littlearm")
OUTPUT_ARCH(arm)
ENTRY(Reset_Handler)

C_HEAP_SIZE	= 0x1000;
C_STACK_SIZE 	= 0x0B00;

MEMORY
{
	ROM (rx) : ORIGIN = 0x08000000, LENGTH = 512K
	RAM (xrw) : ORIGIN = 0x20000000, LENGTH = 96K
}

SECTIONS
{
	.reset :
	{
		. = ALIGN(4);
		KEEP (*(.isr_vector))
		. = ALIGN(4);
	} > ROM

	.text :
	{
		*(.text .text.* .gnu.linkonce.t.*)
		*(.filterfuser.* .filtercoremath.*)
		KEEP (*(.init))
		KEEP (*(.fini))
		
		. = ALIGN(4);
		*(.rodata, .rodata.*, .gnu.linkonce.r.*)

		KEEP(*(.eh_frame))
	} > ROM

	.ARM.exidx :
	{
		__exidx_start = .;
		*(.ARM.exidx* .gnu.linkonce.armexidx.*)
		__exidx_end = .;
	} > ROM

	.preinit_array     :
	{
		PROVIDE_HIDDEN (__preinit_array_start = .);
		KEEP (*(.preinit_array*))
		PROVIDE_HIDDEN (__preinit_array_end = .);
	} > ROM

	.init_array :
	{
		PROVIDE_HIDDEN (__init_array_start = .);
		KEEP (*(SORT(.init_array.*)))
		KEEP (*(.init_array*))
		PROVIDE_HIDDEN (__init_array_end = .);
	} > ROM

	.fini_array :
	{
		PROVIDE_HIDDEN (__fini_array_start = .);
		KEEP (*(SORT(.fini_array.*)))
		KEEP (*(.fini_array*))
		PROVIDE_HIDDEN (__fini_array_end = .);
	} > ROM

	.data :
	{
		_sidata = LOADADDR (.data);
		_sdata = .;
		KEEP (*(.jcr))
		*(.got.plt) *(.got)
		*(.data .data.* .gnu.linkonce.d.*)
		. = ALIGN (4);
		_edata = .;
	} > RAM AT>ROM

	. = ALIGN (4);

	.bss :
	{
		_sbss = .;
		__bss_start__ = .;
		*(.bss .bss.* .gnu.linkonce.b.*)
		*(COMMON)
		_ebss = .;
		__bss_end__ = .;
	} > RAM

	. = ALIGN (8);

	.heap :
	{
		PROVIDE(end = .);
		PROVIDE(_end = .);
		. += C_HEAP_SIZE;
	} > RAM

	. = ALIGN (8);

	.stack :
	{
		. += C_STACK_SIZE;
		. = ALIGN(8);
		PROVIDE(_estack = .);
	} > RAM
}
