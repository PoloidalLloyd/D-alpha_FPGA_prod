#!/usr/bin/env python3

"""
Write calibration factors to FPGA registers in Q16.16 fixed-point format
Supports dual-channel calibration for both ADC channels

Uses memory-mapped system bus register
"""

import struct
import mmap
import sys

# System bus base address for sys[7]
SYS7_BASE_ADDR = 0x40700000
MEMORY_SIZE = 4096

# Register offsets (SWAPPED ADDRESSES!)
ADC_A_OFFSET = 0x04  # ADC channel A calibration gain NOW AT 0x04
ADC_B_OFFSET = 0x00  # ADC channel B calibration gain NOW AT 0x00

def float_to_q16_16(value):
    """Convert float to Q16.16 fixed-point format"""
    # Clamp to reasonable range
    value = max(-32768.0, min(32767.999, value))
    # Multiply by 2^16 and convert to integer
    return int(value * 65536) & 0xFFFFFFFF

def write_calibration(calib_value_a, calib_value_b=None):
    """Write calibration factors to FPGA registers"""

    if calib_value_b is None:
        calib_value_b = calib_value_a  # Default to same value for both channels

    print(f"Writing calibration factors:")
    print(f"  ADC 1 (D-alpha upper): {calib_value_a}")
    print(f"  ADC 2 (D-alpha lower): {calib_value_b}")
    print(f"System bus address: 0x{SYS7_BASE_ADDR:08X}")

    # Convert to Q16.16
    q16_value_a = float_to_q16_16(calib_value_a)
    q16_value_b = float_to_q16_16(calib_value_b)

    try:
        with open('/dev/mem', 'r+b', buffering=0) as f:
            mem = mmap.mmap(
                f.fileno(),
                MEMORY_SIZE,
                mmap.MAP_SHARED,
                mmap.PROT_READ | mmap.PROT_WRITE,
                offset=SYS7_BASE_ADDR
            )

            # Write ADC A calibration to offset 0x04 (SWAPPED!)
            bytes_to_write_a = struct.pack('<I', q16_value_a)
            mem.seek(ADC_A_OFFSET)
            mem.write(bytes_to_write_a)

            # Write ADC B calibration to offset 0x00 (SWAPPED!)
            bytes_to_write_b = struct.pack('<I', q16_value_b)
            mem.seek(ADC_B_OFFSET)
            mem.write(bytes_to_write_b)

            mem.flush()
            mem.close()

        print("Successfully written to FPGA registers!")
        return True
    except PermissionError:
        print("ERROR: Permission denied. Run with sudo!")
        return False
    except Exception as e:
        print(f"ERROR: {e} - ignore [Errno 22], it still works!")
        return False

if __name__ == '__main__':
    def get_float_input(prompt, default=None):
        while True:
            user_input = input(prompt).strip()
            if user_input == "":
                if default is not None:
                    return default
                else:
                    print("  Please enter a value.")
                    continue
            try:
                return float(user_input)
            except ValueError:
                print("  Please enter a valid floating point number.")

    print("Please enter the calibration gain for each ADC channel.\n")

    adc1_default = 1.0
    adc2_default = 1.0  # Will default to ADC1 if not entered

    calib_value_a = get_float_input(
        "Enter calibration gain for ADC 1 (D-alpha upper) [default: 1.0]: ",
        default=adc1_default
    )

    calib_value_b = get_float_input(
        "Enter calibration gain for ADC 2 (D-alpha lower) [default: 1.0]: ",
        default=adc2_default
    )
    print("\n")
    success = write_calibration(calib_value_a, calib_value_b)
    sys.exit(0 if success else 1)

