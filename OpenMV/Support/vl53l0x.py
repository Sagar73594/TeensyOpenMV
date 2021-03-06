class vl53l0x():

        ADDRESS_DEFAULT                             = 0x29
        SYSRANGE_START                              = 0x00

        SYSTEM_THRESH_HIGH                          = 0x0C
        SYSTEM_THRESH_LOW                           = 0x0E

        SYSTEM_SEQUENCE_CONFIG                      = 0x01
        SYSTEM_RANGE_CONFIG                         = 0x09
        SYSTEM_INTERMEASUREMENT_PERIOD              = 0x04

        SYSTEM_INTERRUPT_CONFIG_GPIO                = 0x0A

        GPIO_HV_MUX_ACTIVE_HIGH                     = 0x84

        SYSTEM_INTERRUPT_CLEAR                      = 0x0B

        RESULT_INTERRUPT_STATUS                     = 0x13
        RESULT_RANGE_STATUS                         = 0x14

        RESULT_CORE_AMBIENT_WINDOW_EVENTS_RTN       = 0xBC
        RESULT_CORE_RANGING_TOTAL_EVENTS_RTN        = 0xC0
        RESULT_CORE_AMBIENT_WINDOW_EVENTS_REF       = 0xD0
        RESULT_CORE_RANGING_TOTAL_EVENTS_REF        = 0xD4
        RESULT_PEAK_SIGNAL_RATE_REF                 = 0xB6

        ALGO_PART_TO_PART_RANGE_OFFSET_MM           = 0x28

        I2C_SLAVE_DEVICE_ADDRESS                    = 0x8A

        MSRC_CONFIG_CONTROL                         = 0x60

        PRE_RANGE_CONFIG_MIN_SNR                    = 0x27
        PRE_RANGE_CONFIG_VALID_PHASE_LOW            = 0x56
        PRE_RANGE_CONFIG_VALID_PHASE_HIGH           = 0x57
        PRE_RANGE_MIN_COUNT_RATE_RTN_LIMIT          = 0x64

        FINAL_RANGE_CONFIG_MIN_SNR                  = 0x67
        FINAL_RANGE_CONFIG_VALID_PHASE_LOW          = 0x47
        FINAL_RANGE_CONFIG_VALID_PHASE_HIGH         = 0x48
        FINAL_RANGE_CONFIG_MIN_COUNT_RATE_RTN_LIMIT = 0x44
        
        PRE_RANGE_CONFIG_SIGMA_THRESH_HI            = 0x61
        PRE_RANGE_CONFIG_SIGMA_THRESH_LO            = 0x62

        PRE_RANGE_CONFIG_VCSEL_PERIOD               = 0x50
        PRE_RANGE_CONFIG_TIMEOUT_MACROP_HI          = 0x51
        PRE_RANGE_CONFIG_TIMEOUT_MACROP_LO          = 0x52

        SYSTEM_HISTOGRAM_BIN                        = 0x81
        HISTOGRAM_CONFIG_INITIAL_PHASE_SELECT       = 0x33
        HISTOGRAM_CONFIG_READOUT_CTRL               = 0x55

        FINAL_RANGE_CONFIG_VCSEL_PERIOD             = 0x70
        FINAL_RANGE_CONFIG_TIMEOUT_MACROP_HI        = 0x71
        FINAL_RANGE_CONFIG_TIMEOUT_MACROP_LO        = 0x72
        CROSSTALK_COMPENSATION_PEAK_RATE_MCPS       = 0x20

        MSRC_CONFIG_TIMEOUT_MACROP                  = 0x46

        SOFT_RESET_GO2_SOFT_RESET_N                 = 0xBF
        IDENTIFICATION_MODEL_ID                     = 0xC0
        IDENTIFICATION_REVISION_ID                  = 0xC2

        OSC_CALIBRATE_VAL                           = 0xF8

        GLOBAL_CONFIG_VCSEL_WIDTH                   = 0x32
        GLOBAL_CONFIG_SPAD_ENABLES_REF_0            = 0xB0
        GLOBAL_CONFIG_SPAD_ENABLES_REF_1            = 0xB1
        GLOBAL_CONFIG_SPAD_ENABLES_REF_2            = 0xB2
        GLOBAL_CONFIG_SPAD_ENABLES_REF_3            = 0xB3
        GLOBAL_CONFIG_SPAD_ENABLES_REF_4            = 0xB4
        GLOBAL_CONFIG_SPAD_ENABLES_REF_5            = 0xB5

        GLOBAL_CONFIG_REF_EN_START_SELECT           = 0xB6
        DYNAMIC_SPAD_NUM_REQUESTED_REF_SPAD         = 0x4E
        DYNAMIC_SPAD_REF_EN_START_OFFSET            = 0x4F
        POWER_MANAGEMENT_GO1_POWER_FORCE            = 0x80

        VHV_CONFIG_PAD_SCL_SDA__EXTSUP_HV           = 0x89

        ALGO_PHASECAL_LIM                           = 0x30
        ALGO_PHASECAL_CONFIG_TIMEOUT                = 0x30
        
        # TCC: Target CentreCheck
        # MSRC: Minimum Signal Rate Check
        # DSS: Dynamic Spad Selection
        #struct SequenceStepEnables
        #{
        #  boolean tcc, msrc, dss, pre_range, final_range
        #}

        #struct SequenceStepTimeouts
        #{
        #  uint16_t pre_range_vcsel_period_pclks, final_range_vcsel_period_pclks

        #  uint16_t msrc_dss_tcc_mclks, pre_range_mclks, final_range_mclks
        #  uint32_t msrc_dss_tcc_us,    pre_range_us,    final_range_us
        #}
        enables = namedtuple('enables', 'tcc msrc dss pre_range final_range')
        timeouts = namedtuple('timeouts', 'pre_range_vcsel_period_pclks final_range_vcsel_period_pclks \
                                msrc_dss_tcc_mclks pre_range_mclks final_range_mclks \
                                msrc_dss_tcc_us pre_range_usfinal_range_us')
        
        #enum vcselPeriodType { VcselPeriodPreRange, VcselPeriodFinalRange };
        vcselPeriodType = ['VcselPeriodPreRange', 'VcselPeriodFinalRange']

        # Record the current time to check an upcoming timeout against
        def startTimeout(self, timeout_start_ms):
                timeout_start_ms = int(round(time.time() * 1000))
                
        # Check if timeout is enabled (set to nonzero value) and has expired    
        def checkTimeoutExpired(self, io_timeout, timeout_start_ms):
                if(io_timeout > 0 and (int(round(time.time() * 1000)) - timeout_start_ms) > io_timeout):
                        return True
                else:
                        return False
        # Decode VCSEL (vertical cavity surface emitting laser) pulse period in PCLKs
        # from register value
        # based on VL53L0X_decode_vcsel_period()                
        def decodeVcselPeriod(self, reg_val):
                return (((reg_val) + 1) << 1)

        # Encode VCSEL pulse period register value from period in PCLKs
        # based on VL53L0X_encode_vcsel_period()
        def encodeVcselPeriod(self, period_pclks):
                return (((period_pclks) >> 1) - 1)
                
        # Calculate macro period in *nanoseconds* from VCSEL period in PCLKs
        # based on VL53L0X_calc_macro_period_ps()
        # PLL_period_ps = 1655 macro_period_vclks = 2304
        def calcMacroPeriod(self, vcsel_period_pclks):
                return (((2304 * (vcsel_period_pclks) * 1655) + 500) / 1000)

        # Constructors ################################

        def __init__(self, i2c, address):
                self.i2c = i2c
                if address == NULL:
                        self._address = ADDRESS_DEFAULT
                else:
                        self._address = address
				print(self._address)
                self.init(True)

                
        # Initialize sensor using sequence based on VL53L0X_DataInit(),
        # VL53L0X_StaticInit(), and VL53L0X_PerformRefCalibration().
        # This function does not perform reference SPAD calibration
        # (VL53L0X_PerformRefSpadManagement()), since the API user manual says that it
        # is performed by ST on the bare modules it seems like that should work well
        # enough unless a cover glass is added.
        # If io_2v8 (optional) is True or not given, the sensor is configured for 2V8
        # mode.
        def init(io_2v8):
                # VL53L0X_DataInit() begin

                # sensor uses 1V8 mode for I/O by default switch to 2V8 mode if necessary
                #self._set_reg8(VHV_CONFIG_PAD_SCL_SDA__EXTSUP_HV,
                #        self._get_reg8(VHV_CONFIG_PAD_SCL_SDA__EXTSUP_HV) | 0x01) # set bit 0
                        
                # "Set I2C standard mode"
                self._set_reg8(0x88, 0x00)

                self._set_reg8(0x80, 0x01)
                self._set_reg8(0xFF, 0x01)
                self._set_reg8(0x00, 0x00)
                stop_variable = self._get_reg8(0x91)
                self._set_reg8(0x00, 0x01)
                self._set_reg8(0xFF, 0x00)
                self._set_reg8(0x80, 0x00)

                # disable SIGNAL_RATE_MSRC (bit 1) and SIGNAL_RATE_PRE_RANGE (bit 4) limit checks
                self._set_reg8(MSRC_CONFIG_CONTROL, self._get_reg8(MSRC_CONFIG_CONTROL) | 0x12)

                # set final range signal rate limit to 0.25 MCPS (million counts per second)
                setSignalRateLimit(0.25)

                self._set_reg8(SYSTEM_SEQUENCE_CONFIG, 0xFF)

                # VL53L0X_DataInit() end

                # VL53L0X_StaticInit() begin

                #uint8_t spad_count
                #bool spad_type_is_aperture
                if (!getSpadInfo(spad_count, spad_type_is_aperture)):
                        return False

                # The SPAD map (RefGoodSpadMap) is read by VL53L0X_get_info_from_device() in
                # the API, but the same data seems to be more easily readable from
                # GLOBAL_CONFIG_SPAD_ENABLES_REF_0 through _6, so read it from there
                # ref_spad_map[6]
                reg_spad_map_0 = bytearray(6)
                ref_spad_map_0 = self._readMulti(GLOBAL_CONFIG_SPAD_ENABLES_REF_0, 6)

                # -- VL53L0X_set_reference_spads() begin (assume NVM values are valid)

                self._set_reg8(0xFF, 0x01)
                self._set_reg8(DYNAMIC_SPAD_REF_EN_START_OFFSET, 0x00)
                self._set_reg8(DYNAMIC_SPAD_NUM_REQUESTED_REF_SPAD, 0x2C)
                self._set_reg8(0xFF, 0x00)
                self._set_reg8(GLOBAL_CONFIG_REF_EN_START_SELECT, 0xB4)

                #first_spad_to_enable = spad_type_is_aperture ? 12 : 0 # 12 is the first aperture spad
                if spad_type_is_aperture:
                        first_spad_to_enable = 12
                else:
                        first_spad_to_enable = 0
                spads_enabled = 0

                while i < 48:
                        if (i < first_spad_to_enable) or (spads_enabled == spad_count):
                                # This bit is lower than the first one that should be enabled, or
                                # (reference_spad_count) bits have already been enabled, so zero this bit
                                ref_spad_map[i / 8] = from_bytes_big(ref_spad_map_0[i / 8]) ~(1 << (i % 8))
                        elif ((from_bytes_big(ref_spad_map_0[i / 8]) >> (i % 8)) & 0x1):
                                spads_enabled = spads_enabled + 1

                self._writeMulti(GLOBAL_CONFIG_SPAD_ENABLES_REF_0, ref_spad_map, 6)

                # -- VL53L0X_set_reference_spads() end

                # -- VL53L0X_load_tuning_settings() begin
                # DefaultTuningSettings from vl53l0x_tuning.h

                self._set_reg8(0xFF, 0x01)
                self._set_reg8(0x00, 0x00)

                self._set_reg8(0xFF, 0x00)
                self._set_reg8(0x09, 0x00)
                self._set_reg8(0x10, 0x00)
                self._set_reg8(0x11, 0x00)

                self._set_reg8(0x24, 0x01)
                self._set_reg8(0x25, 0xFF)
                self._set_reg8(0x75, 0x00)

                self._set_reg8(0xFF, 0x01)
                self._set_reg8(0x4E, 0x2C)
                self._set_reg8(0x48, 0x00)
                self._set_reg8(0x30, 0x20)

                self._set_reg8(0xFF, 0x00)
                self._set_reg8(0x30, 0x09)
                self._set_reg8(0x54, 0x00)
                self._set_reg8(0x31, 0x04)
                self._set_reg8(0x32, 0x03)
                self._set_reg8(0x40, 0x83)
                self._set_reg8(0x46, 0x25)
                self._set_reg8(0x60, 0x00)
                self._set_reg8(0x27, 0x00)
                self._set_reg8(0x50, 0x06)
                self._set_reg8(0x51, 0x00)
                self._set_reg8(0x52, 0x96)
                self._set_reg8(0x56, 0x08)
                self._set_reg8(0x57, 0x30)
                self._set_reg8(0x61, 0x00)
                self._set_reg8(0x62, 0x00)
                self._set_reg8(0x64, 0x00)
                self._set_reg8(0x65, 0x00)
                self._set_reg8(0x66, 0xA0)

                self._set_reg8(0xFF, 0x01)
                self._set_reg8(0x22, 0x32)
                self._set_reg8(0x47, 0x14)
                self._set_reg8(0x49, 0xFF)
                self._set_reg8(0x4A, 0x00)

                self._set_reg8(0xFF, 0x00)
                self._set_reg8(0x7A, 0x0A)
                self._set_reg8(0x7B, 0x00)
                self._set_reg8(0x78, 0x21)

                self._set_reg8(0xFF, 0x01)
                self._set_reg8(0x23, 0x34)
                self._set_reg8(0x42, 0x00)
                self._set_reg8(0x44, 0xFF)
                self._set_reg8(0x45, 0x26)
                self._set_reg8(0x46, 0x05)
                self._set_reg8(0x40, 0x40)
                self._set_reg8(0x0E, 0x06)
                self._set_reg8(0x20, 0x1A)
                self._set_reg8(0x43, 0x40)

                self._set_reg8(0xFF, 0x00)
                self._set_reg8(0x34, 0x03)
                self._set_reg8(0x35, 0x44)

                self._set_reg8(0xFF, 0x01)
                self._set_reg8(0x31, 0x04)
                self._set_reg8(0x4B, 0x09)
                self._set_reg8(0x4C, 0x05)
                self._set_reg8(0x4D, 0x04)

                self._set_reg8(0xFF, 0x00)
                self._set_reg8(0x44, 0x00)
                self._set_reg8(0x45, 0x20)
                self._set_reg8(0x47, 0x08)
                self._set_reg8(0x48, 0x28)
                self._set_reg8(0x67, 0x00)
                self._set_reg8(0x70, 0x04)
                self._set_reg8(0x71, 0x01)
                self._set_reg8(0x72, 0xFE)
                self._set_reg8(0x76, 0x00)
                self._set_reg8(0x77, 0x00)

                self._set_reg8(0xFF, 0x01)
                self._set_reg8(0x0D, 0x01)

                self._set_reg8(0xFF, 0x00)
                self._set_reg8(0x80, 0x01)
                self._set_reg8(0x01, 0xF8)

                self._set_reg8(0xFF, 0x01)
                self._set_reg8(0x8E, 0x01)
                self._set_reg8(0x00, 0x01)
                self._set_reg8(0xFF, 0x00)
                self._set_reg8(0x80, 0x00)

                # -- VL53L0X_load_tuning_settings() end

                # "Set interrupt config to new sample ready"
                # -- VL53L0X_SetGpioConfig() begin

                self._set_reg8(SYSTEM_INTERRUPT_CONFIG_GPIO, 0x04)
                self._set_reg8(GPIO_HV_MUX_ACTIVE_HIGH, readReg(GPIO_HV_MUX_ACTIVE_HIGH) & ~0x10) # active low
                self._set_reg8(SYSTEM_INTERRUPT_CLEAR, 0x01)

                # -- VL53L0X_SetGpioConfig() end

                measurement_timing_budget_us = getMeasurementTimingBudget()

                # "Disable MSRC and TCC by default"
                # MSRC = Minimum Signal Rate Check
                # TCC = Target CentreCheck
                # -- VL53L0X_SetSequenceStepEnable() begin

                self._set_reg8(SYSTEM_SEQUENCE_CONFIG, 0xE8)

                # -- VL53L0X_SetSequenceStepEnable() end

                # "Recalculate timing budget"
                setMeasurementTimingBudget(measurement_timing_budget_us)

                # VL53L0X_StaticInit() end

                # VL53L0X_PerformRefCalibration() begin (VL53L0X_perform_ref_calibration())

                # -- VL53L0X_perform_vhv_calibration() begin

                self._set_reg8(SYSTEM_SEQUENCE_CONFIG, 0x01)
                if (performSingleRefCalibration(0x40)): 
                        return False

                # -- VL53L0X_perform_vhv_calibration() end

                # -- VL53L0X_perform_phase_calibration() begin

                self._set_reg8(SYSTEM_SEQUENCE_CONFIG, 0x02)
                if (performSingleRefCalibration(0x00)):
                        return False

                # -- VL53L0X_perform_phase_calibration() end

                # "restore the previous Sequence Config"
                self._set_reg8(SYSTEM_SEQUENCE_CONFIG, 0xE8)

                # VL53L0X_PerformRefCalibration() end

                return True
          

        # Set the return signal rate limit check value in units of MCPS (mega counts
        # per second). "This represents the amplitude of the signal reflected from the
        # target and detected by the device" setting this limit presumably determines
        # the minimum measurement necessary for the sensor to report a valid reading.
        # Setting a lower limit increases the potential range of the sensor but also
        # seems to increase the likelihood of getting an inaccurate reading because of
        # unwanted reflections from objects other than the intended target.
        # Defaults to 0.25 MCPS as initialized by the ST API and this library.
        def setSignalRateLimit(limit_Mcps):
                if (limit_Mcps < 0) or (limit_Mcps > 511.99):
                        return False

                # Q9.7 fixed point format (9 integer bits, 7 fractional bits)
                self._set_reg16(FINAL_RANGE_CONFIG_MIN_COUNT_RATE_RTN_LIMIT, limit_Mcps * (1 << 7)) # ??????????
                return True

        # Get the return signal rate limit check value in MCPS
        def getSignalRateLimit():
                return self._get_reg16(FINAL_RANGE_CONFIG_MIN_COUNT_RATE_RTN_LIMIT) / (1 << 7) # ??????????

        # Set the measurement timing budget in microseconds, which is the time allowed
        # for one measurement the ST API and this library take care of splitting the
        # timing budget among the sub-steps in the ranging sequence. A longer timing
        # budget allows for more accurate measurements. Increasing the budget by a
        # factor of N decreases the range measurement standard deviation by a factor of
        # sqrt(N). Defaults to about 33 milliseconds the minimum is 20 ms.
        # based on VL53L0X_set_measurement_timing_budget_micro_seconds()
        def setMeasurementTimingBudget(budget_us):
                #SequenceStepEnables enables    # ??????????
                #SequenceStepTimeouts timeouts  # ??????????

                StartOverhead      = 1320 # note that this is different than the value in get_
                EndOverhead        = 960
                MsrcOverhead       = 660
                TccOverhead        = 590
                DssOverhead        = 690
                PreRangeOverhead   = 660
                FinalRangeOverhead = 550

                MinTimingBudget = 20000

                if (budget_us < MinTimingBudget):
                        return False

                used_budget_us = StartOverhead + EndOverhead

                getSequenceStepEnables(enables)   # ??????????
                getSequenceStepTimeouts(enables, timeouts)      # ??????????

                if (enables.tcc):
                        used_budget_us += (timeouts.msrc_dss_tcc_us + TccOverhead)

                if (enables.dss):
                        used_budget_us += 2 * (timeouts.msrc_dss_tcc_us + DssOverhead)
                elif (enables.msrc):
                        used_budget_us += (timeouts.msrc_dss_tcc_us + MsrcOverhead)

                if (enables.pre_range):
                        used_budget_us += (timeouts.pre_range_us + PreRangeOverhead)

                if (enables.final_range):
                        used_budget_us += FinalRangeOverhead

                # "Note that the final range timeout is determined by the timing
                # budget and the sum of all other timeouts within the sequence.
                # If there is no room for the final range timeout, then an error
                # will be set. Otherwise the remaining time will be applied to
                # the final range."

                if (used_budget_us > budget_us):
                        # "Requested timeout too big."
                        return False

                final_range_timeout_us = budget_us - used_budget_us

                # set_sequence_step_timeout() begin
                # (SequenceStepId == VL53L0X_SEQUENCESTEP_FINAL_RANGE)

                # "For the final range timeout, the pre-range timeout
                #  must be added. To do this both final and pre-range
                #  timeouts must be expressed in macro periods MClks
                #  because they have different vcsel periods."

                final_range_timeout_mclks = \
                  timeoutMicrosecondsToMclks(final_range_timeout_us, \
                  timeouts.final_range_vcsel_period_pclks)

                if (enables.pre_range):
                        final_range_timeout_mclks += timeouts.pre_range_mclks

                self._set_reg16(FINAL_RANGE_CONFIG_TIMEOUT_MACROP_HI,
                  encodeTimeout(final_range_timeout_mclks)) # ??????????

                # set_sequence_step_timeout() end

                measurement_timing_budget_us = budget_us # store for internal reuse
          
                return True


        # Get the measurement timing budget in microseconds
        # based on VL53L0X_get_measurement_timing_budget_micro_seconds()
        # in us
        def getMeasurementTimingBudget():

                #SequenceStepEnables enables
                #SequenceStepTimeouts timeouts

                StartOverhead     = 1910 # note that this is different than the value in set_
                EndOverhead        = 960
                MsrcOverhead       = 660
                TccOverhead        = 590
                DssOverhead        = 690
                PreRangeOverhead   = 660
                FinalRangeOverhead = 550

                # "Start and end overhead times always present"
                budget_us = StartOverhead + EndOverhead

                getSequenceStepEnables(enables)
                getSequenceStepTimeouts(enables, timeouts)
				

                if (enables.tcc):
                        budget_us = budget_us + (timeouts.msrc_dss_tcc_us + TccOverhead)

                if (enables.dss):
                        budget_us = budget_us + 2 * (timeouts.msrc_dss_tcc_us + DssOverhead)
                elif (enables.msrc):
                        budget_us = budget_us + (timeouts.msrc_dss_tcc_us + MsrcOverhead)

                if (enables.pre_range):
                        budget_us = budget_us + (timeouts.pre_range_us + PreRangeOverhead)

                if (enables.final_range):
                        budget_us = budget_us + (timeouts.final_range_us + FinalRangeOverhead)

                measurement_timing_budget_us = budget_us # store for internal reuse
                return budget_us


        # Set the VCSEL (vertical cavity surface emitting laser) pulse period for the
        # given period type (pre-range or final range) to the given value in PCLKs.
        # Longer periods seem to increase the potential range of the sensor.
        # Valid values are (even numbers only):
        #  pre:  12 to 18 (initialized default: 14)
        #  final: 8 to 14 (initialized default: 10)
        # based on VL53L0X_set_vcsel_pulse_period()
        def setVcselPulsePeriod(type, period_pclks):

                vcsel_period_reg = encodeVcselPeriod(period_pclks)

                #SequenceStepEnables enables
                #SequenceStepTimeouts timeouts

                getSequenceStepEnables(enables)
                getSequenceStepTimeouts(enables, timeouts)

                # "Apply specific settings for the requested clock period"
                # "Re-calculate and apply timeouts, in macro periods"

                # "When the VCSEL period for the pre or final range is changed,
                # the corresponding timeout must be read from the device using
                # the current VCSEL period, then the new VCSEL period can be
                # applied. The timeout then must be written back to the device
                # using the new VCSEL period.
                #
                # For the MSRC timeout, the same applies - this timeout being
                # dependant on the pre-range vcsel period."


                if (type == VcselPeriodPreRange):
                        # "Set phase check limits"
                        if (period_pclks == 12):
                                writeReg(PRE_RANGE_CONFIG_VALID_PHASE_HIGH, 0x18)
                        elif (period_pclks == 14):
                                writeReg(PRE_RANGE_CONFIG_VALID_PHASE_HIGH, 0x30)
                        elif (period_pclks == 16):
                                writeReg(PRE_RANGE_CONFIG_VALID_PHASE_HIGH, 0x40)
                        elif (period_pclks == 18):
                                writeReg(PRE_RANGE_CONFIG_VALID_PHASE_HIGH, 0x50)
                        else:
                                # invalid period
                                return False
                
                        writeReg(PRE_RANGE_CONFIG_VALID_PHASE_LOW, 0x08)

                        # apply new VCSEL period
                        writeReg(PRE_RANGE_CONFIG_VCSEL_PERIOD, vcsel_period_reg)

                        # update timeouts

                        # set_sequence_step_timeout() begin
                        # (SequenceStepId == VL53L0X_SEQUENCESTEP_PRE_RANGE)

                        new_pre_range_timeout_mclks = \
                                timeoutMicrosecondsToMclks(timeouts.pre_range_us, period_pclks)

                        self._set_reg16(PRE_RANGE_CONFIG_TIMEOUT_MACROP_HI,
                                encodeTimeout(new_pre_range_timeout_mclks))

                        # set_sequence_step_timeout() end

                        # set_sequence_step_timeout() begin
                        # (SequenceStepId == VL53L0X_SEQUENCESTEP_MSRC)

                        new_msrc_timeout_mclks = \
                                timeoutMicrosecondsToMclks(timeouts.msrc_dss_tcc_us, period_pclks)

                        #self._get_Reg8(MSRC_CONFIG_TIMEOUT_MACROP, \
                        #       (new_msrc_timeout_mclks > 256) ? 255 : (new_msrc_timeout_mclks - 1))
                        self._get_Reg8(MSRC_CONFIG_TIMEOUT_MACROP, reg_value)
                        if(reg_value > 256):
                                new_msrc_timeout_mclks =255
                        else:
                                new_msrc_timeout_mclks = new_msrc_timeout_mclks - 1

                        # set_sequence_step_timeout() end

                elif (type == VcselPeriodFinalRange):
                        if (period_pclks == 8):
                                self._get_Reg8(FINAL_RANGE_CONFIG_VALID_PHASE_HIGH, 0x10)
                                self._get_Reg8(FINAL_RANGE_CONFIG_VALID_PHASE_LOW,  0x08)
                                self._get_Reg8(GLOBAL_CONFIG_VCSEL_WIDTH, 0x02)
                                self._get_Reg8(ALGO_PHASECAL_CONFIG_TIMEOUT, 0x0C)
                                self._get_Reg8(0xFF, 0x01)
                                self._get_Reg8(ALGO_PHASECAL_LIM, 0x30)
                                self._get_Reg8(0xFF, 0x00)
                        elif (period_pclks == 10):
                                self._get_Reg8(FINAL_RANGE_CONFIG_VALID_PHASE_HIGH, 0x28)
                                self._get_Reg8(FINAL_RANGE_CONFIG_VALID_PHASE_LOW,  0x08)
                                self._get_Reg8(GLOBAL_CONFIG_VCSEL_WIDTH, 0x03)
                                self._get_Reg8(ALGO_PHASECAL_CONFIG_TIMEOUT, 0x09)
                                self._get_Reg8(0xFF, 0x01)
                                self._get_Reg8(ALGO_PHASECAL_LIM, 0x20)
                                self._get_Reg8(0xFF, 0x00)
                        elif (period_pclks == 12):
                                self._get_Reg8(FINAL_RANGE_CONFIG_VALID_PHASE_HIGH, 0x38)
                                self._get_Reg8(FINAL_RANGE_CONFIG_VALID_PHASE_LOW,  0x08)
                                self._get_Reg8(GLOBAL_CONFIG_VCSEL_WIDTH, 0x03)
                                self._get_Reg8(ALGO_PHASECAL_CONFIG_TIMEOUT, 0x08)
                                self._get_Reg8(0xFF, 0x01)
                                self._get_Reg8(ALGO_PHASECAL_LIM, 0x20)
                                self._get_Reg8(0xFF, 0x00)
                        elif (period_pclks == 14):
                                self._get_Reg8(FINAL_RANGE_CONFIG_VALID_PHASE_HIGH, 0x48)
                                self._get_Reg8(FINAL_RANGE_CONFIG_VALID_PHASE_LOW,  0x08)
                                self._get_Reg8(GLOBAL_CONFIG_VCSEL_WIDTH, 0x03)
                                self._get_Reg8(ALGO_PHASECAL_CONFIG_TIMEOUT, 0x07)
                                self._get_Reg8(0xFF, 0x01)
                                self._get_Reg8(ALGO_PHASECAL_LIM, 0x20)
                                self._get_Reg8(0xFF, 0x00)
                        else:
                                # invalid period
                                return False

                        # apply new VCSEL period
                        self._set_reg8(FINAL_RANGE_CONFIG_VCSEL_PERIOD, vcsel_period_reg)

                        # update timeouts

                        # set_sequence_step_timeout() begin
                        # (SequenceStepId == VL53L0X_SEQUENCESTEP_FINAL_RANGE)

                        # "For the final range timeout, the pre-range timeout
                        #  must be added. To do this both final and pre-range
                        #  timeouts must be expressed in macro periods MClks
                        #  because they have different vcsel periods."

                        new_final_range_timeout_mclks = \
                                timeoutMicrosecondsToMclks(timeouts.final_range_us, period_pclks)

                        if (enables.pre_range):
                                new_final_range_timeout_mclks = new_final_range_timeout_mclks + timeouts.pre_range_mclks

                        self._set_reg16(FINAL_RANGE_CONFIG_TIMEOUT_MACROP_HI,
                                encodeTimeout(new_final_range_timeout_mclks))

                        # set_sequence_step_timeout end
                else:
                        # invalid type
                        return False


                # "Finally, the timing budget must be re-applied"

                setMeasurementTimingBudget(measurement_timing_budget_us)

                # "Perform the phase calibration. This is needed after changing on vcsel period."
                # VL53L0X_perform_phase_calibration() begin

                sequence_config = readReg(SYSTEM_SEQUENCE_CONFIG)
                self._set_reg8(SYSTEM_SEQUENCE_CONFIG, 0x02)
                performSingleRefCalibration(0x0)
                self._set_reg8(SYSTEM_SEQUENCE_CONFIG, sequence_config)

                # VL53L0X_perform_phase_calibration() end

                return True


        # Get the VCSEL pulse period in PCLKs for the given period type.
        # based on VL53L0X_get_vcsel_pulse_period()
        def getVcselPulsePeriod(type):

                if (type == VcselPeriodPreRange):
                        return decodeVcselPeriod(readReg(PRE_RANGE_CONFIG_VCSEL_PERIOD))
                elif (type == VcselPeriodFinalRange):
                        return decodeVcselPeriod(readReg(FINAL_RANGE_CONFIG_VCSEL_PERIOD))
                else:
                        return 255


        # Start continuous ranging measurements. If period_ms (optional) is 0 or not
        # given, continuous back-to-back mode is used (the sensor takes measurements as
        # often as possible) otherwise, continuous timed mode is used, with the given
        # inter-measurement period in milliseconds determining how often the sensor
        # takes a measurement.
        # based on VL53L0X_StartMeasurement()
        def startContinuous(period_ms):
                self._set_reg8(0x80, 0x01)
                self._set_reg8(0xFF, 0x01)
                self._set_reg8(0x00, 0x00)
                self._set_reg8(0x91, stop_variable)
                self._set_reg8(0x00, 0x01)
                self._set_reg8(0xFF, 0x00)
                self._set_reg8(0x80, 0x00)

                if (period_ms != 0):
                        # continuous timed mode

                        # VL53L0X_SetInterMeasurementPeriodMilliSeconds() begin

                        osc_calibrate_val = readReg16Bit(OSC_CALIBRATE_VAL)

                        if (osc_calibrate_val != 0):
                                period_ms = period_ms * osc_calibrate_val

                        self._set_reg32(SYSTEM_INTERMEASUREMENT_PERIOD, period_ms)

                        # VL53L0X_SetInterMeasurementPeriodMilliSeconds() end

                        self._set_reg8(SYSRANGE_START, 0x04) # VL53L0X_REG_SYSRANGE_MODE_TIMED
                else:
                        # continuous back-to-back mode
                        self._set_reg8(SYSRANGE_START, 0x02) # VL53L0X_REG_SYSRANGE_MODE_BACKTOBACK


        # Stop continuous measurements
        # based on VL53L0X_StopMeasurement()
        def stopContinuous():
                self._set_reg8(SYSRANGE_START, 0x01) # VL53L0X_REG_SYSRANGE_MODE_SINGLESHOT

                self._set_reg8(0xFF, 0x01)
                self._set_reg8(0x00, 0x00)
                self._set_reg8(0x91, 0x00)
                self._set_reg8(0x00, 0x01)
                self._set_reg8(0xFF, 0x00)

        # Returns a range reading in millimeters when continuous mode is active
        # (readRangeSingleMillimeters() also calls this function after starting a
        # single-shot range measurement)
        def readRangeContinuousMillimeters():

                startTimeout()
                while ((readReg(RESULT_INTERRUPT_STATUS) & 0x07) == 0):
                        if (checkTimeoutExpired()):
                                did_timeout = True
                        return 65535

                # assumptions: Linearity Corrective Gain is 1000 (default)
                # fractional ranging is not enabled
                range = readReg16Bit(RESULT_RANGE_STATUS + 10)

                self._set_reg8(SYSTEM_INTERRUPT_CLEAR, 0x01)

                return range


        # Performs a single-shot range measurement and returns the reading in
        # millimeters
        # based on VL53L0X_PerformSingleRangingMeasurement()
        def VreadRangeSingleMillimeters():

                self._set_reg8(0x80, 0x01)
                self._set_reg8(0xFF, 0x01)
                self._set_reg8(0x00, 0x00)
                self._set_reg8(0x91, stop_variable)
                self._set_reg8(0x00, 0x01)
                self._set_reg8(0xFF, 0x00)
                self._set_reg8(0x80, 0x00)

                self._set_reg8(SYSRANGE_START, 0x01)

                # "Wait until start bit has been cleared"
                startTimeout()
                while (readReg(SYSRANGE_START) & 0x01):
                        if (checkTimeoutExpired()):
                                did_timeout = True
                                return 65535

                return readRangeContinuousMillimeters()


        # Did a timeout occur in one of the read functions since the last call to
        # timeoutOccurred()?
        def timeoutOccurred():
                tmp = did_timeout
                did_timeout = False
                return tmp


        # Private Methods ,,,,,,,,,,,,,,,,,,,,,,

        # Get reference SPAD (single photon avalanche diode) count and type
        # based on VL53L0X_get_info_from_device(),
        # but only gets reference SPAD count and type
        def getSpadInfo(count, type_is_aperture):

                self._set_reg8(0x80, 0x01)
                self._set_reg8(0xFF, 0x01)
                self._set_reg8(0x00, 0x00)

                self._set_reg8(0xFF, 0x06)
                self._set_reg8(0x83, from_bytes_big(self._get_Reg8(0x83)) | 0x04)
                self._set_reg8(0xFF, 0x07)
                self._set_reg8(0x81, 0x01)

                self._set_reg8(0x80, 0x01)

                self._set_reg8(0x94, 0x6b)
                self._set_reg8(0x83, 0x00)
                startTimeout()
                while (from_bytes_big(self.get_reg8(0x83)) == 0x00):
                        if (checkTimeoutExpired()):
                                return False

                self._set_reg8(0x83, 0x01)
                tmp = self._get_reg8(0x92)

                count = from_bytes_big(tmp) & 0x7f
                type_is_aperture = (tmp >> 7) & 0x01

                self._set_reg8(0x81, 0x00)
                self._set_reg8(0xFF, 0x06)
                self._set_reg8(0x83, from_bytes_big(self.get_reg8( 0x83  & ~0x04)))
                self._set_reg8(0xFF, 0x01)
                self._set_reg8(0x00, 0x01)

                self._set_reg8(0xFF, 0x00)
                self._set_reg8(0x80, 0x00)

                return True

        # Get sequence step enables
        # based on VL53L0X_GetSequenceStepEnables()
        def getSequenceStepEnables(enables):

                sequence_config = self._get_reg8(SYSTEM_SEQUENCE_CONFIG)

                enables.tcc          = (sequence_config >> 4) & 0x1
                enables.dss          = (sequence_config >> 3) & 0x1
                enables.msrc         = (sequence_config >> 2) & 0x1
                enables.pre_range    = (sequence_config >> 6) & 0x1
                enables.final_range  = (sequence_config >> 7) & 0x1

        # Get sequence step timeouts
        # based on get_sequence_step_timeout(),
        # but gets all timeouts instead of just the requested one, and also stores
        # intermediate values
        def getSequenceStepTimeouts(enables, timeouts):
                timeouts.pre_range_vcsel_period_pclks = getVcselPulsePeriod(VcselPeriodPreRange)

                timeouts.msrc_dss_tcc_mclks = self._get_reg8(MSRC_CONFIG_TIMEOUT_MACROP) + 1
                timeouts.msrc_dss_tcc_us = \
                        timeoutMclksToMicroseconds(timeouts.msrc_dss_tcc_mclks,
                                       timeouts.pre_range_vcsel_period_pclks)

                timeouts.pre_range_mclks = \
                        decodeTimeout(self._get_reg16(PRE_RANGE_CONFIG_TIMEOUT_MACROP_HI))
                timeouts.pre_range_us = \
                        timeoutMclksToMicroseconds(timeouts.pre_range_mclks,
                                       timeouts.pre_range_vcsel_period_pclks)

                timeouts.final_range_vcsel_period_pclks = getVcselPulsePeriod(VcselPeriodFinalRange)

                timeouts.final_range_mclks = \
                        decodeTimeout(self._get_reg16(FINAL_RANGE_CONFIG_TIMEOUT_MACROP_HI))

                if (enables.pre_range):
                        timeouts.final_range_mclks = timeouts.final_range_mclks - timeouts.pre_range_mclks

                timeouts.final_range_us = \
                        timeoutMclksToMicroseconds(timeouts.final_range_mclks,
                                       timeouts.final_range_vcsel_period_pclks)


        # Decode sequence step timeout in MCLKs from register value
        # based on VL53L0X_decode_timeout()
        # Note: the original function returned a uint32_t, but the return value is
        # always stored in a uint16_t.
        def decodeTimeout(reg_val):
                # format: "(LSByte * 2^MSByte) + 1"
                return ((reg_val & 0x00FF) <<
                        ((reg_val & 0xFF00) >> 8)) + 1


        # Encode sequence step timeout register value from timeout in MCLKs
        # based on VL53L0X_encode_timeout()
        # Note: the original function took a uint16_t, but the argument passed to it
        # is always a uint16_t.
        def encodeTimeout(timeout_mclks):
                # format: "(LSByte * 2^MSByte) + 1"

                ls_byte = 0
                ms_byte = 0

                if (timeout_mclks > 0):
                        ls_byte = timeout_mclks - 1

                        while ((ls_byte & 0xFFFFFF00) > 0):
                                ls_byte >>= 1

                        return (ms_byte << 8) | (ls_byte & 0xFF)

                else:
                        return 0


        # Convert sequence step timeout from MCLKs to microseconds with given VCSEL period in PCLKs
        # based on VL53L0X_calc_timeout_us()
        def timeoutMclksToMicroseconds(timeout_period_mclks, vcsel_period_pclks):
                macro_period_ns = calcMacroPeriod(vcsel_period_pclks)

                return ((timeout_period_mclks * macro_period_ns) + (macro_period_ns / 2)) / 1000

        # Convert sequence step timeout from microseconds to MCLKs with given VCSEL period in PCLKs
        # based on VL53L0X_calc_timeout_mclks()
        def timeoutMicrosecondsToMclks(timeout_period_us, vcsel_period_pclks):
                macro_period_ns = calcMacroPeriod(vcsel_period_pclks)

                return (((timeout_period_us * 1000) + (macro_period_ns / 2)) / macro_period_ns)


        # based on VL53L0X_perform_single_ref_calibration()
        def performSingleRefCalibration(vhv_init_byte):

                self._get_reg8(SYSRANGE_START, 0x01 | vhv_init_byte) # VL53L0X_REG_SYSRANGE_MODE_START_STOP

                startTimeout()
                while ((self._get_reg8(RESULT_INTERRUPT_STATUS) & 0x07) == 0):
                        if (checkTimeoutExpired()):
                                return False

                self._set_reg8(SYSTEM_INTERRUPT_CLEAR, 0x01)

                self._set_reg8(SYSRANGE_START, 0x00)

                return True

        #
        # I2C Calls
        #
				
        def from_bytes_big(b):
                n = 0
                for x in b:
                n <<= 8
                n |= x
                return n
				
        def _set_reg8(self, reg_address, value):
                #data = ustruct.pack('>HB', address, value)
                self.i2c.writeto_mem(self._address, reg_address, value)

        def _get_reg8(self, address, reg_address):
                data = self.i2c.readfrom_mem(self._address, reg_address, 1)
                return from_bytes_big(data)
                                
        def _set_reg16(self, reg_address, value):
                dst[0] = (value >> 8) & 0xFF     ## value high byte
                dst[1] = ( value      & 0xFF)    ## value low byte
                #self.i2c.writeto_mem(self._address, reg_address, value, *, addrsize = 16 )
                test = 1
                
        def _get_reg16(self, reg_address):
                data = bytearray[2]
                self.i2c.readfrom_into(self._address, reg_address, data)
                value  = from_bytes_big(data[1]) << 8         ## value high byte
                value  = value | from_bytes_big(data[0])      ## value low byte
                return value
                                
        def _set_reg32(self, reg_address, value):
                data[3]  = (value >> 24) & 0xFF       ## value highest byte
                data[2]  = (value >> 16) & 0xFF
                data[1]  = (value >>  8) & 0xFF
                data[0]  = (value >>  8) & 0xFF       ## value lowest byte
                self.i2c.writeto_mem(self._address, reg_address, data)
                return

                
        def _get_reg32(self, reg_address):
                data = bytearrar(4)
                self.i2c.readfrom_into(self._address, reg_address, data)
                value  = data[3] << 24          ## value highest byte
                value  = value | data[2] << 16
                value  = value | data[1] <<  8
                value  = value | data[0]        ## value lowest byte
                return value
                
        # Read an arbitrary number of bytes from the sensor, starting at the given
        # register, into the given array
        def _readMulti(reg_address, count):
                dst = bytearray(count)
                self.i2c.readfrom_mem_into(self._address, reg_address, dst, count)
                return dst
                
        # Write an arbitrary number of bytes from the given array to the sensor,
        # starting at the given register
        def _writeMulti(reg_address, dst, count):
                self.i2c.writeto_mem(self._address, reg_address, dst)


