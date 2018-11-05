"""
Moves the piano keys from a provided midi file.
"""

__author__ = "Robert Brown"
__copyright__ = "Copyright 2018"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Rob Brown"
__email__ = "hi@robbrown.io"
__status__ = "Prototype"

# General notes:
# Piano Key numbering: https://en.wikipedia.org/wiki/Piano_key_frequencies
# Midi Key Numbering: http://newt.phys.unsw.edu.au/jw/notes.html
# Mido library for reading Midi: https://mido.readthedocs.io/en/latest/intro.html

from math import ceil, floor
from mido import MidiFile, tick2second

import bpy

MIDI_FILE = #FULL PATH TO MIDI FILE!!!

MID = MidiFile(MIDI_FILE)

# Midi information
TICKS_PER_BEAT = MID.ticks_per_beat
SONG_LENGTH = MID.length

# Timing information for making key frames
FRAME_RATE = bpy.context.scene.render.fps

MIDI_KEY_OFFSET = 20

# Default key return velocity since midi usualy has zero
KEY_UP_VELOCITY = 90
KEY_DEPTH = 0.5

bpy.context.scene.frame_end = ceil(SONG_LENGTH * FRAME_RATE)
bpy.context.scene.frame_start = 0

class ActuateKeys():
    """
    Class for actuating the piano keys from a midi file
    """

    current_time = 0
    current_key_frame = 0

    msg_tempo = 500000

    @staticmethod
    def select_object(object_name):
        """
        Selects one object and sets it as the active object to be edited
        """
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern=object_name)
        if not bpy.context.selected_editable_objects:
            return -1

        bpy.context.scene.objects.active = bpy.context.selected_editable_objects[0]
        return 0

    def get_velocity_time(self, tick_velocity):
        """
        Convert the velocity to the length of time based on tempo
        """
        # Convert velocity to some number of ticks
        tick_velocity = tick_velocity if tick_velocity < 127 else 127
        tick_velocity = tick_velocity if tick_velocity > 0 else 1
        ticks = 127 - tick_velocity
        return tick2second(ticks, TICKS_PER_BEAT, self.msg_tempo)

    def run(self):
        """
        Run function itterates over the midi file to actuate the piano keys
        """

        for msg in MID:
            if msg.time > 0:
                # Update current keyframe if Midi adds more time
                self.current_time += msg.time
                self.current_key_frame = floor(self.current_time * FRAME_RATE)

            if msg.type == 'set_tempo':
                self.msg_tempo = msg.tempo

            if msg.type == 'note_on' or msg.type == 'note_off':
                # Determine if key is going up or down
                move_distance = - KEY_DEPTH if msg.type == 'note_on' else KEY_DEPTH

                # Determine what key to move
                move_note = msg.note - MIDI_KEY_OFFSET

                # Calculate how many frames until key movement is done
                velocity = msg.velocity if msg.velocity != 0 else KEY_UP_VELOCITY
                velocity_time = self.get_velocity_time(velocity)
                motion_end_frame = ceil((velocity_time + self.current_time)
                                        * FRAME_RATE)

                # Select the key to be moved
                self.select_object('Key ({0:0>2d})'.format(move_note))
                current = bpy.context.object

                # Set piano key locations with blender key frames
                current.keyframe_insert(data_path="location",
                                        frame=self.current_key_frame)
                current.location.z += move_distance
                current.keyframe_insert(data_path="location",
                                        frame=motion_end_frame)

if __name__ == '__main__':
    ActuateKeys().run()
