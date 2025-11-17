#!/usr/bin/python3
import time
import rp

# === TOGGLE THESE FLAGS TO SWITCH SETTINGS QUICKLY ===

# 1 = High Voltage acquisition (±20V), 0 = Low Voltage (±1V)
if 1:
    acq_mode = rp.RP_HIGH
else:
    acq_mode = rp.RP_LOW

# 1 = High Impedance (Hi-Z), 0 = 50 Ohm output load
if 1:
    gen_imp_mode = rp.RP_GEN_HI_Z
else:
    gen_imp_mode = rp.RP_GEN_50Ohm

# 1 = 5× Gain, 0 = 1× Gain
if 1:
    gen_gain_mode = rp.RP_GAIN_5X
else:
    gen_gain_mode = rp.RP_GAIN_1X

# === INITIALIZE AND APPLY SETTINGS ===

# Initialize hardware
rp.rp_Init()
channel_1 = rp.RP_CH_1
channel_2 = rp.RP_CH_2

# Reset settings
rp.rp_GenReset()
rp.rp_AcqReset()

# Set acquisition gain (ADC range)
rp.rp_AcqSetGain(channel_1, acq_mode)
rp.rp_AcqSetGain(channel_2, acq_mode)

# Set output load impedance (DAC)
rp.rp_GenSetLoadMode(channel_1, gen_imp_mode)
rp.rp_GenSetLoadMode(channel_2, gen_imp_mode)

# Set output gain (DAC)
rp.rp_GenSetGainOut(channel_1, gen_gain_mode)
rp.rp_GenSetGainOut(channel_2, gen_gain_mode)

# === READ BACK & INTERPRET SETTINGS ===

# ADC gain
adc_gain_ch1 = rp.rp_AcqGetGainV(channel_1)[1]
adc_gain_ch2 = rp.rp_AcqGetGainV(channel_2)[1]
adc_mode_desc = lambda v: "High Voltage Mode (±20V)" if v == 20.0 else "Low Voltage Mode (±1V)"

# DAC load and gain
dac_imp_ch1 = rp.rp_GenGetLoadMode(channel_1)[1]
dac_imp_ch2 = rp.rp_GenGetLoadMode(channel_2)[1]
dac_gain_ch1 = rp.rp_GenGetGainOut(channel_1)[1]
dac_gain_ch2 = rp.rp_GenGetGainOut(channel_2)[1]

imp_desc = lambda v: "High Impedance (Hi-Z)" if v == 0 else "50 Ohm"
gain_desc = lambda v: "5× Gain" if v == 1 else "1× Gain"

# Determine DAC output voltage range
def dac_output_range(gain, impedance):
    if gain == 0 and impedance == 0:
        return "±2 V"
    elif gain == 0 and impedance == 1:
        return "±1 V"
    elif gain == 1 and impedance == 0:
        return "±10 V"
    elif gain == 1 and impedance == 1:
        return "±5 V"
    else:
        return "Unknown"

dac_range_ch1 = dac_output_range(dac_gain_ch1, dac_imp_ch1)
dac_range_ch2 = dac_output_range(dac_gain_ch2, dac_imp_ch2)

# === PRINT CONFIGURATION SUMMARY ===
print("\n=== ADC Configuration ===")
print(f"ADC Channel 1: {adc_mode_desc(adc_gain_ch1)}")
print(f"ADC Channel 2: {adc_mode_desc(adc_gain_ch2)}")

print("\n=== DAC Configuration ===")
print(f"DAC Channel 1: {imp_desc(dac_imp_ch1)}, {gain_desc(dac_gain_ch1)} → Output range: {dac_range_ch1}")
print(f"DAC Channel 2: {imp_desc(dac_imp_ch2)}, {gain_desc(dac_gain_ch2)} → Output range: {dac_range_ch2}")

# Optionally release hardware
# rp.rp_Release()


