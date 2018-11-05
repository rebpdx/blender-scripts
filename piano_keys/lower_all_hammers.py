"""
Move all strike hammers to the down/resting position
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
# Keys, Hammer, and Damper naming is out of order make sure components have been
# renamed first before running this script see rename_components.py

import bpy


def main():
    """
    Drops all striker hammers of piano rig while preserving user state
    """
    # Save user selected state in case they are working on something
    user_active_objects = bpy.context.scene.objects.active
    user_selected_objects = bpy.context.selected_objects

    # Select all the strike hammers
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_pattern(pattern='Hammer_*')
    hammers = bpy.context.selected_editable_objects

    for hammer in hammers:
        # Set a hamemr to be the active object
        bpy.context.scene.objects.active = hammer
        current = bpy.context.object

        # Drop the hammer to the rig's constraint location
        hammer_constraint = current.constraints["Limit Rotation"]
        move_angle = hammer_constraint.min_x
        current.rotation_euler.x = move_angle

    # Return to user selected objects
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = user_active_objects
    for selected_object in user_selected_objects:
        selected_object.select = True


if __name__ == '__main__':
    main()
