"""
Moves the piano components from a provided midi file.
"""

__author__ = "Robert Brown"
__copyright__ = "Copyright 2018"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Rob Brown"
__email__ = "hi@robbrown.io"
__status__ = "Prototype"

# This script was built for the asset by pixelpoems.de from blender market
# https://blendermarket.com/products/grand-piano-full-rigged-full-interior-detailed
# Asset does requrie some work prior to using this scripts
# Keys, Hammer, and Damper naming is out of order, see rename_components.py
# Hammers are up by default see lower_all_hammers.py to drop them first

# General notes:
# Piano Key numbering: https://en.wikipedia.org/wiki/Piano_key_frequencies
# Midi Key Numbering: http://newt.phys.unsw.edu.au/jw/notes.html
# Mido library for reading Midi: https://mido.readthedocs.io/en/latest/intro.html
# Timing of key, hammer, and mute hammer https://youtu.be/vFXBIFyG4tU?t=207

from math import ceil, floor
from mido import MidiFile, tick2second

import os
import bpy

SCRIPT_PATH = os.path.dirname(bpy.context.space_data.text.filepath)
MIDI_FILE = 'Gymnopedie1.mid'

MID = MidiFile(os.path.join(SCRIPT_PATH, MIDI_FILE))

# Midi information
TICKS_PER_BEAT = MID.ticks_per_beat
SONG_LENGTH = MID.length

# Timing information for making key frames
FRAME_RATE = bpy.context.scene.render.fps

MIDI_KEY_OFFSET = 20

# Default key return velocity since midi usualy has zero
KEY_UP_VELOCITY = 90

# Set frame_start & frame_end to song length
bpy.context.scene.frame_end = ceil(SONG_LENGTH * FRAME_RATE)
bpy.context.scene.frame_start = 0

class ActuatePiano():
    """
    Class for actuating the piano from a midi file
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

    def get_key_action_time(self, tick_velocity):
        """
        Convert the velocity to the length of time based on tempo
        """
        # Convert velocity to some number of ticks
        tick_velocity = tick_velocity if tick_velocity < 127 else 127
        tick_velocity = tick_velocity if tick_velocity > 0 else 1
        ticks = 127 - tick_velocity

        # Return some number of seconds
        return tick2second(ticks, TICKS_PER_BEAT, self.msg_tempo)

    def move_key(self, note, note_on, end_frame):
        """
        Move the specified key at specified start and end frames
        """
        if self.select_object('Key_{0:0>2d}'.format(note)) != 0:
            return

        current = bpy.context.object

        # Delay the keyframe one so that the hammer has time to strike the
        current.keyframe_insert(data_path="rotation_euler",
                                frame=self.current_key_frame - 1)

        key_limit = current.constraints["Limit Rotation"]
        move_rotation = key_limit.max_x if note_on else key_limit.min_x
        current.rotation_euler = move_rotation, 0, 0
        current.keyframe_insert(data_path="rotation_euler",
                                frame=end_frame)

    def move_hammer(self, note, note_on, strike_frame, end_frame):
        """
        Move the specified hammer at specified start, strike, and drop frames
        """
        # No need to continue if it's a note off
        if not note_on:
            return

        if self.select_object('Hammer_{0:0>2d}'.format(note)) != 0:
            return

        current = bpy.context.object

        current.keyframe_insert(data_path="rotation_euler",
                                frame=self.current_key_frame)

        hammer_constraint = current.constraints["Limit Rotation"]

        current.rotation_euler = hammer_constraint.max_x, 0, 0
        current.keyframe_insert(data_path="rotation_euler", frame=strike_frame)

        current.rotation_euler = hammer_constraint.min_x, 0, 0
        current.keyframe_insert(data_path="rotation_euler", frame=end_frame)

    def move_mute_hammer(self, note, note_on, mid_frame, finish_frame):
        """
        Move the specified mute hammer at the given start, and end frame
        """
        if self.select_object('Mute_{0:0>2d}'.format(note)) != 0:
            return

        current = bpy.context.object

        current.keyframe_insert(data_path="location",
                                frame=self.current_key_frame)

        mute_constraint = current.constraints["Limit Location"]
        move_distance = mute_constraint.max_z if note_on else mute_constraint.min_z
        end_frame = finish_frame if note_on else mid_frame

        current.location = mute_constraint.min_x, mute_constraint.min_y, move_distance
        current.keyframe_insert(data_path="location", frame=end_frame)

    def run(self):
        """
        Run fuction itterates over the midi file to actuate the piano
        """
        for msg in MID:
            if msg.time > 0:
                self.current_time += msg.time
                self.current_key_frame = floor(self.current_time * FRAME_RATE) + 1

            if msg.type == 'set_tempo':
                self.msg_tempo = msg.tempo

            if msg.type == 'note_on' or msg.type == 'note_off':
                move_note = msg.note - MIDI_KEY_OFFSET

                # Calculate how many frames until key movement is done
                midi_velocity = msg.velocity if msg.velocity != 0 else KEY_UP_VELOCITY
                key_action_time = self.get_key_action_time(midi_velocity)
                motion_end_frame = ceil((key_action_time + self.current_time) * FRAME_RATE)

                # Calculate a frame between start and end for hammers
                motion_half_frame = ceil(
                    (motion_end_frame - self.current_key_frame) / 2) + self.current_key_frame

                # Make sure key frames do not overlap
                if motion_half_frame == motion_end_frame:
                    print("Warning: Extending key frames midi song may be too fast\
                     for {} fps".format(FRAME_RATE))
                    motion_end_frame += 1

                # Setup keyframes for actuation of piano components
                self.move_key(move_note, (msg.type == 'note_on'),
                              motion_end_frame)

                self.move_hammer(move_note, (msg.type == 'note_on'),
                                 motion_half_frame, motion_end_frame)

                self.move_mute_hammer(move_note, (msg.type == 'note_on'),
                                      motion_half_frame, motion_end_frame)

if __name__ == '__main__':
    ActuatePiano().run()
