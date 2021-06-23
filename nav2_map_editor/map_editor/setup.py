from setuptools import setup

setup(
    name='nav2-map_editor',
    version='0.1',
    license='BSD',
    author='Tomas Hricina',
    author_email='t.hri@seznam.cz',
    url='https://navigation.ros.org/',
    long_description="README.txt",
    packages=['map_editor',
     'map_editor.Canvas',
     'map_editor.Helpers',
     'map_editor.Images',
     'map_editor.Left_Menu',
     'map_editor.Paint_Menu',
     'map_editor.Waypoint_Menu'],
    include_package_data=True,
    package_data={'map_editor.Images' : ['default_button.png', 'default_map.pgm', 'default_map.yaml', 'map_editor_logo.png', 'waypoint_logo.png']},
    description="Tool for editing maps, adding speed restrictions and waypoints",
)
