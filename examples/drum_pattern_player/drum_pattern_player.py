import time
import urandom
from micropython import const
from sam2695_midi import Sam2695Midi
from sam2695_midi_timbre import SAM2695_MIDI_TIMBRE_BANK_0
from sam2695_midi_chorus_reverberation import SAM2695_MIDI_REVERBERATION_PLATE
from sam2695_midi_percussion_note import (
    SAM2695_MIDI_PERCUSSION_TIMBRE_1,
    SAM2695_MIDI_PERCUSSION_TIMBRE_1_NOTE_C_2_KICK_DRUM_1,
    SAM2695_MIDI_PERCUSSION_TIMBRE_1_NOTE_D_2_SNARE_DRUM_1,
    SAM2695_MIDI_PERCUSSION_TIMBRE_1_NOTE_F_SHARP_2_CLOSED_HI_HAT,
    SAM2695_MIDI_PERCUSSION_TIMBRE_1_NOTE_A_SHARP_2_OPEN_HI_HAT,
    SAM2695_MIDI_PERCUSSION_TIMBRE_1_NOTE_G_SHARP_2_PEDAL_HI_HAT,
)

SAM2695_MIDI_PIN: int = const(17)

CHANNEL: int = const(9)
CHANNEL_VOLUME: int = const(100)

REVERBERATION_VOLUME: int = const(127)
REVERBERATION_DELAY_FEEDBACK: int = const(100)

TEMPO_RANDOM_RANGE: int = const(5)
TEMPO_RANDOM_OFFSET: int = const(2)

MIN_TEMPO: int = const(40)
MAX_TEMPO: int = const(250)

TICK_SIZE: int = const(15)

BASS_DRUM_TICK = [127, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 90, 0]
SNARE_DRUM_TICK = [0, 0, 0, 0, 127, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
HI_HAT_OPEN_TICK = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 127, 0]
HI_HAT_CLOSE_TICK = [127, 40, 80, 40, 127, 40, 80, 40, 127, 40, 80, 40, 127, 0, 0]
HI_HAT_PEDAL_TICK = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 127]

assert len(BASS_DRUM_TICK) == TICK_SIZE, "BASS_DRUM_TICK size must be 15"
assert len(SNARE_DRUM_TICK) == TICK_SIZE, "SNARE_DRUM_TICK size must be 15"
assert len(HI_HAT_OPEN_TICK) == TICK_SIZE, "HI_HAT_OPEN_TICK size must be 15"
assert len(HI_HAT_CLOSE_TICK) == TICK_SIZE, "HI_HAT_CLOSE_TICK size must be 15"
assert len(HI_HAT_PEDAL_TICK) == TICK_SIZE, "HI_HAT_PEDAL_TICK size must be 15"

tempo: int = 120
sam2695_midi = Sam2695Midi(tx_pin=SAM2695_MIDI_PIN)


def play_drum_note(midi_note: int, note_velocity: int):
    if note_velocity > 0:
        sam2695_midi.note_on(CHANNEL, midi_note, note_velocity)
        sam2695_midi.note_off(CHANNEL, midi_note)


sam2695_midi.midi_reset()
sam2695_midi.set_channel_timbre(
    CHANNEL, SAM2695_MIDI_TIMBRE_BANK_0, SAM2695_MIDI_PERCUSSION_TIMBRE_1
)
sam2695_midi.set_reverberation(
    CHANNEL,
    SAM2695_MIDI_REVERBERATION_PLATE,
    REVERBERATION_VOLUME,
    REVERBERATION_DELAY_FEEDBACK,
)
sam2695_midi.set_channel_volume(CHANNEL, CHANNEL_VOLUME)

while True:
    for tick_no in range(TICK_SIZE):
        tempo += urandom.getrandbits(3) % TEMPO_RANDOM_RANGE - TEMPO_RANDOM_OFFSET
        tempo = max(MIN_TEMPO, min(tempo, MAX_TEMPO))

        play_drum_note(
            SAM2695_MIDI_PERCUSSION_TIMBRE_1_NOTE_C_2_KICK_DRUM_1,
            BASS_DRUM_TICK[tick_no],
        )
        play_drum_note(
            SAM2695_MIDI_PERCUSSION_TIMBRE_1_NOTE_D_2_SNARE_DRUM_1,
            SNARE_DRUM_TICK[tick_no],
        )
        play_drum_note(
            SAM2695_MIDI_PERCUSSION_TIMBRE_1_NOTE_F_SHARP_2_CLOSED_HI_HAT,
            HI_HAT_CLOSE_TICK[tick_no],
        )
        play_drum_note(
            SAM2695_MIDI_PERCUSSION_TIMBRE_1_NOTE_A_SHARP_2_OPEN_HI_HAT,
            HI_HAT_OPEN_TICK[tick_no],
        )
        play_drum_note(
            SAM2695_MIDI_PERCUSSION_TIMBRE_1_NOTE_G_SHARP_2_PEDAL_HI_HAT,
            HI_HAT_PEDAL_TICK[tick_no],
        )

        time.sleep_ms(tempo)
