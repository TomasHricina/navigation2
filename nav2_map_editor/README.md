# Nav2-map_editor  
![](https://github.com/TomasHricina/navigation2/blob/main/nav2_map_editor/preview_1_0_6.gif)  
Nav2-map_editor is convenience tool, that is useful for:  
- viewing and editing maps and YAML files 
- adding speed restricted areas and keepout zones  
- placing waypoints for navigation  
  
More about Keepout zones:
https://navigation.ros.org/tutorials/docs/navigation2_with_keepout_filter.html
  
### Download source code:  
https://downgit.github.io/#/home?url=https://github.com/TomasHricina/navigation2/tree/main/nav2_map_editor  
  
### Unzip archive:  
cd ~/Downloads/  
unzip nav2_map_editor.zip  
  
  
### Install dependencies:  
sudo apt-get install python3-pyqt5   
pip3 install opencv-python-headless  
pip3 install numpy  
pip3 install qimage2ndarray  
pip3 install pyaml  
  
**Alternatively:**  
sudo apt-get install python3-pyqt5  
cd ~/Downloads/nav2_map_editor/map_editor  
pip3 install -r requirements.txt  
  
### Install map_editor package:  
cd ~/Downloads/nav2_map_editor/map_editor  
pip3 install .  
  
### Usage (In command line):  
map_editor  
  
**Alternatively:**  
if "map_editor" command does not work:  
cd ~/Downloads/nav2_map_editor/map_editor  
python3 main.py 
    
    
  
**Uninstall:**  
pip3 uninstall nav2-map_editor
