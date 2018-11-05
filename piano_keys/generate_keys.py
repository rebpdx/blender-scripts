"""
This script generates an object of basic keys for testing with so that
a full piano does not need to be rendered when testing actuating the keyboard
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

from math import floor
import bpy

PADDING = 0.05
NUMBER_OF_OCTIVES = 8
STARTING_KEY = 4
NUMBER_OF_WKEYS = NUMBER_OF_OCTIVES * 7
NUMBER_OF_BKEYS = NUMBER_OF_OCTIVES * 5
TOTAL_KEYS = NUMBER_OF_OCTIVES * 12


class GenerateKeys():
    """
    Class for Generating White and Black Piano Keys as Rectangles
    """

    @staticmethod
    def white_key_number(range_number):
        """
        Returns white key numbering from a value counting in base 10 to ensure
        that a black key number is not returned.
        """
        # http://mathforum.org/kb/message.jspa?messageID=7365626
        return floor((12 * range_number + 5) / 7)

    @staticmethod
    def black_key_skip(range_number):
        """
        Returns 0 if a black key exists and 1 if a skip should occur
        """
        if (range_number % 5 == 0) or ((range_number + 2) % 5 == 0):
            return 1

        return 0

    @staticmethod
    def name_key_and_mesh(blender_object, key_number):
        """
        Names the object and mesh based on the given object and key number so
        that all keys follow the same format
        """
        blender_object.name = 'Key ({0:0>2d})'.format(key_number)
        blender_object.data.name = 'Mesh ({0:0>2d})'.format(key_number)

    def run(self):
        """
        Main function call to generate keys
        """
        # Stretch existing cube to a rectangle
        bpy.ops.transform.resize(value=(2, 0.5, 0.5))
        bpy.ops.transform.translate(value=(0, -(NUMBER_OF_WKEYS)/2, 0.5))

        # Generate a list of white key numbers
        wkey_list = list(map(lambda x: self.white_key_number(x) + STARTING_KEY,
                             range(0, NUMBER_OF_WKEYS)))

        # Duplicate and name each white key
        for key_num in wkey_list:
            current = bpy.context.object
            self.name_key_and_mesh(current, key_num)

            bpy.ops.object.duplicate_move(TRANSFORM_OT_translate=({"value": (0, 1 + PADDING, 0)}))

        # Manipulate the last extra key into a black key
        bpy.ops.transform.resize(value=(0.6, 0.75, 1))
        bpy.ops.transform.translate(value=(-0.8, -(1.5 + PADDING), 0.5))

        # Generate list of black key numbers
        all_keys_list = range(STARTING_KEY, TOTAL_KEYS + STARTING_KEY)
        bkey_list = list(set(all_keys_list) - set(wkey_list))
        bkey_list.sort(reverse=True)

        skip_list = list(map(self.black_key_skip,
                             range(1, len(bkey_list) + 1)))

        # Duplicate and name each black key
        for bkey_num, skip in zip(bkey_list[:-1], skip_list[:-1]):
            # Name the key based on it's note number
            current = bpy.context.object
            self.name_key_and_mesh(current, bkey_num)

            bpy.ops.object.duplicate_move(TRANSFORM_OT_translate=(
                {"value": (0, -((1 + PADDING) * (1 + skip)), 0)}))

        # Name the last key
        current = bpy.context.object
        self.name_key_and_mesh(current, bkey_list[-1])

if __name__ == '__main__':
    GenerateKeys().run()
