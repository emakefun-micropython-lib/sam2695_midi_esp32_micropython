import time
from sam2695_midi_timbre import SAM2695_MIDI_TIMBRE_BANK_0, SAM2695_MIDI_TIMBRE_BANK_127


class Sam2695Midi:

    def __init__(self, stream):
        """
        Initializes the SAM2695 MIDI interface.

        Args:
            stream: MicroPython流对象。
        """

        self._stream = stream

        time.sleep_ms(50)

    def _write(self, command: list[int]) -> None:
        """
        Sends a MIDI command to the device.

        Args:
            command: MIDI command bytes to send.
        """

        self._stream.write(bytearray(command))

    def _send_nrpn_or_rpn_parameter(
        self,
        channel: int,
        most_significant_byte_controller: int,
        most_significant_byte: int,
        least_significant_byte_controller: int,
        least_significant_byte: int,
        value: int,
    ) -> None:
        """
        Send NRPN (unregistered parameter number) or RPN (registered parameter number) parameter values to the specified channel.

        Args:
            channel: Designated channel (0-15).
            most_significant_byte_controller: High byte controller number (0x63/NRPN or 0x65/RPN).
            most_significant_byte: High byte of parameter category.
            least_significant_byte_controller: Low byte controller number (0x62/NRPN or 0x64/RPN).
            least_significant_byte: Low order bytes of specific parameters.
            value: Parameter values to be set (0-127).
        """

        command_most_significant_byte = [
            0xB0 | (channel & 0x0F),
            most_significant_byte_controller,
            most_significant_byte,
        ]
        self._write(command_most_significant_byte)

        command_least_significant_byte = [
            0xB0 | (channel & 0x0F),
            least_significant_byte_controller,
            least_significant_byte,
        ]
        self._write(command_least_significant_byte)

        command_set_value = [0xB0 | (channel & 0x0F), 0x06, value & 0x7F]
        self._write(command_set_value)

    def _null_nrpn_or_rpn(
        self,
        channel: int,
        most_significant_byte_controller: int,
        least_significant_byte_controller: int,
    ) -> None:
        """
        Cancel the currently selected NRPN/RPN parameters (empty parameter selection) to prevent future data input commands from mistakenly modifying the current parameters.

        Args:
            channel:Designated channel (0-15).
            most_significant_byte_controller: High byte controller number (0x63/NRPN or 0x65/RPN).
            least_significant_byte_controller: Low byte controller number (0x62/NRPN or 0x64/RPN).
        """

        command_most_significant_byte = [
            0xB0 | (channel & 0x0F),
            most_significant_byte_controller,
            0x7F,
        ]
        self._write(command_most_significant_byte)

        command_least_significant_byte = [
            0xB0 | (channel & 0x0F),
            least_significant_byte_controller,
            0x7F,
        ]
        self._write(command_least_significant_byte)

    def note_on(self, channel: int, midi_note: int, note_velocity: int) -> None:
        """
        Generate the given MIDI note on the designated channel (0-15).

        Args:
            channel: Designated channel (0-15).
            midi_note: MIDI notes (0-127), please refer to sam2695_midi_note.py for reference; Among them, for the notes of channel 9, please refer to sam2695_midi_percussion_note.py .
            note_velocity: Note velocity (0-127), controls the volume and tone brightness of notes, on a keyboard this corresponds to how hard the key,0: silent (equivalent to noteOff), 1-126: from weak to strong, 127: maximum strength.
        """

        command = [0x90 | (channel & 0x0F), midi_note & 0x7F, note_velocity & 0x7F]
        self._write(command)

    def note_off(self, channel: int, midi_note: int) -> None:
        """
        Close the note in the specified channel, which was previously opened at a given pitch using the noteOn() command.

        Args:
            channel: Designated channel (0-15).
            midi_note: MIDI notes (0-127), please refer to sam2695_midi_note.py for reference; Among them, for the notes of channel 9, please refer to sam2695_midi_percussion_note.py.
        """

        command = [0x80 | (channel & 0x0F), midi_note & 0x7F, 0x00]
        self._write(command)

    def set_channel_timbre(self, channel: int, bank: int, timbre: int) -> None:
        """
        Change the tone of the specified channel. Among them, channel 9 is a dedicated drum channel, and the timbre and notes of channel 9 can be found in reference sam2695_midi_percussion_note.py .

        Args:
            channel: Designated channels (0-15), where channel 9 is a dedicated drum group channel.
            bank: Selection of timbre library, with parameter values of SAM2695_MIDI_TIMBRE_BANK_0 or SAM2695_MIDI_TIMBRE_BANK_127.
            timbre: Timbre number (0-127), please refer to the macro in reference sam2695_midi_timbre.py (e.g. SAM2695_MIDI_TIMBRE_BANK_0_GRAND_PIANO); Among them, for the timbre of channel 9, please refer to sam2695_midi_percussion_note.py .
        """

        if bank != SAM2695_MIDI_TIMBRE_BANK_0 and bank != SAM2695_MIDI_TIMBRE_BANK_127:
            print(
                "Error: bank parameter error, can only be SAM2695_MIDI_TIMBRE_BANK_0 or SAM2695_MIDI_TIMBRE_BANK_127."
            )
            return

        command_bank = [0xB0 | (channel & 0x0F), 0x00, bank]
        self._write(command_bank)

        command_timbre = [0xC0 | (channel & 0x0F), timbre & 0x7F]
        self._write(command_timbre)

    def pitch_bend(self, channel: int, pitch_bend_value: int) -> None:
        """
        Bend the pitch upwards or downwards, with a default swing of+/-1 semitone.

        Args:
            channel: Designated channel (0-15).
            pitch_bend_value: Pitch bend value (0-1023), 0: maximum downward bend, 512: center position (no bend), 1023: maximum upward bend.
        """

        mapped_value = int(min(pitch_bend_value, 1023) * 0x3FFF / 1023)
        command = [0xE0 | (channel & 0x0F), mapped_value & 0x7F, mapped_value >> 7]
        self._write(command)

    def pitch_bend_range(self, channel: int, pitch_bend_range_value: int) -> None:
        """
        Set the pitch bend range (sensitivity).

        Args:
            channel: Designated channel (0-15).
            pitch_bend_range_value: Pitch bend range value (number of semitones, 0-127), typical value: 1-24 (semitones), default value: 2 (± 2 semitones).
        """

        self._send_nrpn_or_rpn_parameter(
            channel, 0x65, 0x00, 0x64, 0x00, pitch_bend_range_value
        )

        self._null_nrpn_or_rpn(channel, 0x65, 0x64)

    def midi_reset(self) -> None:
        """MIDI system reset sends MIDI system reset command (0xFF) to reset all connected MIDI devices to their initial state."""

        self._write([0xFF])

    def channel_all_notes_off(self, channel: int) -> None:
        """
        Send a noteOff() for each note on the specified channel.

        Args:
            channel: Designated channel (0-15).
        """

        command = [0xB0 | (channel & 0x0F), 0x7B, 0x00]
        self._write(command)

    def set_channel_volume(self, channel: int, volume: int) -> None:
        """
        Set specific channel volume.

        Args:
            channel: Designated channel (0-15).
            volume: Volume level (0-127), 0: mute, 127: maximum volume.
        """

        command = [0xB0 | (channel & 0x0F), 0x07, volume & 0x7F]
        self._write(command)

    def set_all_channel_volume(self, volume: int) -> None:
        """
        Set the volume for all channels.

        Args:
            volume: Volume level (0-127), 0: mute, 127: maximum volume.
        """

        command = [0xF0, 0x7F, 0x7F, 0x04, 0x01, 0x00, volume & 0x7F, 0xF7]
        self._write(command)

    def set_reverberation(
        self,
        channel: int,
        reverberation_type: int,
        reverberation_volume: int,
        delay_feedback: int,
    ) -> None:
        """
        Apply reverberation effect to the specified channel.

        Args:
            channel: Designated channel (0-15).
            reverberation_type: Reverberation type, refer to macros in sam2695_midi_chorus_reverberation.py (e.g., SAM2695_MIDI_REVERBERATION_ROOM_1).
            reverberation_volume: Reverberation transmission amount (0-127), 0: no reverberation, 127: maximum reverberation amount.
            delay_feedback: Delayed feedback quantity (0-127), 0: no feedback, 127: maximum feedback.
        """

        command = [0xB0 | (channel & 0x0F), 0x50, reverberation_type & 0x07]
        self._write(command)

        command[1] = 0x5B
        command[2] = reverberation_volume & 0x7F
        self._write(command)

        command_delay = [
            0xF0,
            0x41,
            0x10,
            0x42,
            0x12,
            0x40,
            0x01,
            0x35,
            delay_feedback & 0x7F,
            0x00,
            0xF7,
        ]
        self._write(command_delay)

    def set_chorus(
        self,
        channel: int,
        chorus_effect_type: int,
        chorus_effect_volume: int,
        chorus_effect_feedback: int,
        chorus_delay_time: int,
    ) -> None:
        """
        Apply a chorus effect to a specified channel.

        Args:
            channel: Designated channel (0-15).
            chorus_effect_type: chorus effect type, refer to macros in sam2695_midi_chorus_reverberation.py (e.g., SAM2695_MIDI_CHORUS_1).
            chorus_effect_volume: chorus effect sending volume (0-127), 0: none, 127: maximum sending volume.
            chorus_effect_feedback: Effect feedback amount (0-127, 0 means not set).
            chorus_delay_time: chorus delay time (0-127, 0 indicates not set), unit: ms.
        """

        command = [0xB0 | (channel & 0x0F), 0x51, chorus_effect_type & 0x07]
        self._write(command)

        command[1] = 0x5D
        command[2] = chorus_effect_volume & 0x7F
        self._write(command)

        command_feedback = [
            0xF0,
            0x41,
            0x10,
            0x42,
            0x12,
            0x40,
            0x01,
            0x3B,
            chorus_effect_feedback & 0x7F,
            0x00,
            0xF7,
        ]
        self._write(command_feedback)

        command_chorus_delay = [
            0xF0,
            0x41,
            0x10,
            0x42,
            0x12,
            0x40,
            0x01,
            0x3C,
            chorus_delay_time & 0x7F,
            0x00,
            0xF7,
        ]
        self._write(command_chorus_delay)

    def set_pan_position(self, channel: int, pan_position_value: int) -> None:
        """
        Set the pan position.

        Args:
            channel: Designated channel (0-15).
            pan_position_value: pan position value (0-127), 0: far left (completely left channel), 64: center position (balanced left and right channel),127: far right (completely right channel).
        """

        command = [0xB0 | (channel & 0x0F), 0x0A, pan_position_value & 0x7F]
        self._write(command)

    def set_equalizer(
        self,
        channel: int,
        low_frequency_gain: int,
        medium_low_frequency_gain: int,
        medium_high_frequency_gain: int,
        high_frequency_gain: int,
        low_frequency: int,
        medium_low_frequency: int,
        medium_high_frequency: int,
        high_frequency: int,
    ) -> None:
        """
        Set up a four segment equalizer.

        Args:
            channel: Designated channel (0-15).
            low_frequency_gain: Low frequency gain value (0-127).
            medium_low_frequency_gain: Medium-low frequency gain value (0-127).
            medium_high_frequency_gain: Medium-high frequency gain value (0-127).
            high_frequency_gain: High frequency gain value (0-127).
            low_frequency: Low frequency center value (0-127).
            medium_low_frequency: Medium-low frequency center value (0-127).
            medium_high_frequency: Medium-high frequency center value (0-127).
            high_frequency: High frequency center value (0-127).
        """

        params = [
            (0x00, low_frequency_gain),
            (0x01, medium_low_frequency_gain),
            (0x02, medium_high_frequency_gain),
            (0x03, high_frequency_gain),
            (0x08, low_frequency),
            (0x09, medium_low_frequency),
            (0x0A, medium_high_frequency),
            (0x0B, high_frequency),
        ]

        for param, value in params:
            self._send_nrpn_or_rpn_parameter(channel, 0x63, 0x37, 0x62, param, value)

        self._null_nrpn_or_rpn(channel, 0x63, 0x62)

    def set_tuning(self, channel: int, fine_tuning: int, coarse_tuning: int) -> None:
        """
        Set tone (coarse/fine).

        Args:
            channel: Designated channel (0-15).
            fine_tuning: Fine tuning value (0-127), affecting subtle changes in pitch.
            coarse_tuning: Coarse tuning values (0-127), affect the octave variation of pitch.
        """

        self._send_nrpn_or_rpn_parameter(channel, 0x65, 0x00, 0x64, 0x01, fine_tuning)
        self._send_nrpn_or_rpn_parameter(channel, 0x65, 0x00, 0x64, 0x02, coarse_tuning)

        self._null_nrpn_or_rpn(channel, 0x65, 0x64)

    def set_vibrato(
        self,
        channel: int,
        vibrato_rate: int,
        vibrato_depth: int,
        vibrato_delay_modify: int,
    ) -> None:
        """
        Set vibrato parameters.

        Args:
            channel: Designated channel (0-15).
            vibrato_rate: Vibrato rate (0-127) - controls the speed of vibrato oscillation.
            vibrato_depth: Vibrato depth (0-127) - controls the amplitude of vibrato oscillation.
            vibrato_delay_modify: Vibrato Delay Modification (0-127) - Control the delay time before the start of vibrato.
        """

        self._send_nrpn_or_rpn_parameter(channel, 0x63, 0x01, 0x62, 0x08, vibrato_rate)
        self._send_nrpn_or_rpn_parameter(channel, 0x63, 0x01, 0x62, 0x09, vibrato_depth)
        self._send_nrpn_or_rpn_parameter(
            channel, 0x63, 0x01, 0x62, 0x0A, vibrato_delay_modify
        )

        self._null_nrpn_or_rpn(channel, 0x63, 0x62)

    def set_time_varying_filter(
        self, channel: int, cutoff: int, resonance: int
    ) -> None:
        """
        Set Time Varying Filter (TVF).

        Args:
            channel: Designated channel (0-15).
            cutoff: Cut off frequency value (0-127) - controls the frequency range that the filter passes through.
            resonance: Resonance peak/resonance value (0-127) - Control the gain of the filter near the cutoff frequency.
        """

        self._send_nrpn_or_rpn_parameter(channel, 0x63, 0x01, 0x62, 0x20, cutoff)
        self._send_nrpn_or_rpn_parameter(channel, 0x63, 0x01, 0x62, 0x21, resonance)

        self._null_nrpn_or_rpn(channel, 0x63, 0x62)

    def set_envelope(
        self, channel: int, attack_time: int, attenuation_time: int, release_time: int
    ) -> None:
        """
        Set envelope parameters.

        Args:
            channel: Designated channel (0-15).
            attack_time: Start time (0-127) - controls the time for the sound to reach its maximum amplitude from zero, unit: ms.
            attenuation_time: Attenuation time (0-127) - controls the time for sound to decay from maximum amplitude to maintain a level, unit: ms.
            release_time: Release time (0-127) - controls the time it takes for the volume to decay to zero after the note is released, unit: ms.
        """

        self._send_nrpn_or_rpn_parameter(channel, 0x63, 0x01, 0x62, 0x63, attack_time)
        self._send_nrpn_or_rpn_parameter(
            channel, 0x63, 0x01, 0x62, 0x64, attenuation_time
        )
        self._send_nrpn_or_rpn_parameter(channel, 0x63, 0x01, 0x62, 0x66, release_time)

        self._null_nrpn_or_rpn(channel, 0x63, 0x62)

    def set_scale_tuning(
        self,
        channel: int,
        note_c: int,
        note_c_sharp: int,
        note_d: int,
        note_d_sharp: int,
        note_e: int,
        note_f: int,
        note_f_sharp: int,
        note_g: int,
        note_g_sharp: int,
        note_a: int,
        note_a_sharp: int,
        note_b: int,
    ) -> None:
        """
        Set the 12 scale tuning parameters for the specified MIDI channel (independent pitch offset for each semitone).

        Args:
            channel: Designated channel (0-15).
            scale_tuning_parameter: Set the 12 scale tuning parameters(C, C#, D, D#, E, F, F#, G, G#, A, A#, B) for the specified channel (independent pitch offset for each semitone).
            note_c: C note fine-tuning value (0-127).
            note_c_sharp: C# note fine-tuning value (0-127).
            note_d: D note fine-tuning value (0-127).
            note_d_sharp: D# note fine-tuning value (0-127).
            note_e: E note fine-tuning value (0-127).
            note_f: F note fine-tuning value (0-127).
            note_f_sharp: F# note fine-tuning value (0-127).
            note_g: G note fine-tuning value (0-127).
            note_g_sharp: G# note fine-tuning value (0-127).
            note_a: A note fine-tuning value (0-127).
            note_a_sharp: A# note fine-tuning value (0-127).
            note_b: B note fine-tuning value (0-127).
        """

        command = [
            0xF0,
            0x41,
            0x00,
            0x42,
            0x12,
            0x40,
            0x10 | (channel & 0x0F),
            0x40,
            note_c & 0x7F,
            note_c_sharp & 0x7F,
            note_d & 0x7F,
            note_d_sharp & 0x7F,
            note_e & 0x7F,
            note_f & 0x7F,
            note_f_sharp & 0x7F,
            note_g & 0x7F,
            note_g_sharp & 0x7F,
            note_a & 0x7F,
            note_a_sharp & 0x7F,
            note_b & 0x7F,
            0xF7,
        ]
        self._write(command)

    def set_modulation_wheel(
        self,
        channel: int,
        high_pitch_volume: int,
        time_varying_timbre_cutoff: int,
        amplitude: int,
        low_frequency_oscillator_rate: int,
        pitch_depth: int,
        time_varying_filter_depth: int,
        time_varying_amplifier_depth: int,
    ) -> None:
        """
        Set modulation wheel parameters and configure multiple control effects for modulation wheel sound.

        Args:
            channel: Designated channel (0-15).
            high_pitch_volume: High pitch volume intensity (0-127).
            time_varying_timbre_cutoff: Time-varying timbre cutoff frequency (0-127).
            amplitude: Amplitude modulation depth (0-127).
            low_frequency_oscillator_rate: Low-frequency oscillator rate (0-127).
            pitch_depth: Pitch modulation depth (0-127).
            time_varying_filter_depth: Time-varying filter depth (0-127).
            time_varying_amplifier_depth: Time-varying amplifier depth (0-127).
        """

        command = [
            0xF0,
            0x41,
            0x00,
            0x42,
            0x12,
            0x40,
            0x20 | (channel & 0x0F),
            0x00,
            high_pitch_volume & 0x7F,
            0x00,
            0xF7,
        ]
        self._write(command)

        command[8] = 0x01
        command[9] = time_varying_timbre_cutoff & 0x7F
        self._write(command)

        command[8] = 0x02
        command[9] = amplitude & 0x7F
        self._write(command)

        command[8] = 0x03
        command[9] = low_frequency_oscillator_rate & 0x7F
        self._write(command)

        command[8] = 0x04
        command[9] = pitch_depth & 0x7F
        self._write(command)

        command[8] = 0x05
        command[9] = time_varying_filter_depth & 0x7F
        self._write(command)

        command[8] = 0x06
        command[9] = time_varying_amplifier_depth & 0x7F
        self._write(command)

    def all_drums(self) -> None:
        """Activate all drum channels and set all 16 MIDI channels (0-15) as drum channels."""

        command = [0xF0, 0x41, 0x00, 0x42, 0x12, 0x40, 0x00, 0x15, 0x01, 0x00, 0xF7]

        for i in range(16):
            command[6] = 0x10 | (i & 0x0F)
            self._write(command)
