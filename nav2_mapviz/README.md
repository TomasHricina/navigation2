# Nav2-MapViz  
![](https://github.com/TomasHricina/navigation2/blob/main/nav2_mapviz/preview_1_0_6.gif)  
Nav2-MapViz is convenience tool, that is useful for:  
- viewing and editing maps and YAML files 
- adding speed restricted areas and keepout zones  
- placing waypoints for navigation  
  
More about Keepout zones:
https://navigation.ros.org/tutorials/docs/navigation2_with_keepout_filter.html
  
### Download source code:  
https://downgit.github.io/#/home?url=https://github.com/TomasHricina/navigation2/tree/main/nav2_mapviz  
  
### Unzip archive:  
cd ~/Downloads/  
unzip nav2_mapviz.zip  
  
  
### Install dependencies:  
sudo apt-get install python3-pyqt5   
pip3 install opencv-python-headless  
pip3 install numpy  
pip3 install qimage2ndarray  
pip3 install pyaml  
  
**Alternatively:**  
sudo apt-get install python3-pyqt5  
cd ~/Downloads/nav2_mapviz/mapviz  
pip3 install -r requirements.txt  
  
### Install MapViz package:  
cd ~/Downloads/nav2_mapviz/mapviz  
pip3 install .  
  
### Usage (In command line):  
mapviz  
  
**Alternatively:**  
if "mapviz" command does not work:  
cd ~/Downloads/nav2_mapviz/mapviz  
python3 main.py 
    
    
  
**Uninstall:**  
pip3 uninstall nav2-mapviz
