# Python
from collections import namedtuple
from re import compile

# Source files
from mapViz.Helpers.colors_helpers import colors


default_image_name = 'default_map.pgm'

dimensions = namedtuple('dimensions', 'width height')

# when entry input is false, background changes
error_background = "QLineEdit{background:red;}"
warning_background = "QLineEdit{background:yellow;}"
success_background = "QLineEdit{background:white;}"

# regex for entry user input validation
valid_filename_regex = compile(r'^[^<>:;,?"*|/]+$')
list_sanitizer_regex = compile(r'[0-9., \[\]+-]*$')


# GUI-specific magic numbers
top_menu_button_width, top_menu_button_height = 90, 60
left_menu_width = 222
history_box_total_height = 300
history_box_column_width = 192
history_box_row_height = 40

angle_button_width, angle_button_height = 25, 25
yaml_button_width, yaml_button_height = 25, 25
canvas_minimum_dimensions = dimensions(width=820, height=800)
canvas_height_offset = 50
default_brush_size = 10
color_icon_width = 15 ; color_icon_height = color_icon_width
default_paint_color = colors['Nav2-blue']

top_menu_button_dimensions = dimensions(width=top_menu_button_width, height=top_menu_button_height)
load_button_dimensions = top_menu_button_dimensions
save_button_dimensions = top_menu_button_dimensions
undo_button_dimensions = top_menu_button_dimensions
redo_button_dimensions = top_menu_button_dimensions
help_button_dimensions = top_menu_button_dimensions
about_button_dimensions = top_menu_button_dimensions

angle_button_dimensions = dimensions(width=angle_button_width, height=angle_button_height)
yaml_button_dimensions = dimensions(width=yaml_button_width, height=yaml_button_height)

# Waypoints magic numbers
waypoint_menu_width = 142
waypoint_column_width = waypoint_menu_width - 15
wp_text_size_divider = 4
wp_default_text_size = 4
default_color_text = colors['Nav2-blue']
default_color_shape_outline = colors['Nav2-blue']
default_color_shape_inside = colors['Nav2-blue']

default_max_speed = 7
default_target_speed = 2.03  # 29% because of Nav2-blue
