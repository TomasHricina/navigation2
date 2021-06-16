from setuptools import setup

setup(
    name='nav2-mapviz',
    version='0.1',
    license='BSD',
    author='Tomas Hricina',
    author_email='t.hri@seznam.cz',
    url='https://navigation.ros.org/',
    long_description="README.txt",
    packages=['mapviz',
     'mapviz.Canvas',
     'mapviz.Helpers',
     'mapviz.Images',
     'mapviz.Left_Menu',
     'mapviz.Paint_Menu',
     'mapviz.Waypoint_Menu'],
    include_package_data=True,
    package_data={'mapviz.Images' : ['default_button.png', 'default_map.pgm', 'default_yaml.yaml', 'mapviz_logo.png', 'waypoint_logo.png']},
    description="Tool for editing maps, adding speed restrictions and waypoints",
)
