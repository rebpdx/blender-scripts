"""
Renames Keys, Hammers and Mutes to piano key numbering order
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
# Keys, Hammer, and Damper naming is out of order

# General notes:
# Piano Key numbering: https://en.wikipedia.org/wiki/Piano_key_frequencies

import os
import bpy

SCRIPT_PATH = os.path.dirname(bpy.context.space_data.text.filepath)


def main():
    """
    Renames Keys, Hammers and Mutes to piano key numbering order
    """
    # Save user selected state in case they are working on something
    user_active_objects = bpy.context.scene.objects.active
    user_selected_objects = bpy.context.selected_objects

    with open(os.path.join(SCRIPT_PATH, "component_list.txt")) as file:
        for line in file:
            (original_name, new_name) = line.split()
            bpy.context.scene.objects.active = bpy.data.objects[original_name]
            current = bpy.context.object
            current.name = new_name

    # Return to user selected objects
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = user_active_objects
    for selected_object in user_selected_objects:
        selected_object.select = True

if __name__ == '__main__':
    main()
