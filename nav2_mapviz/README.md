# Nav2-MapViz  
  
## Download source code:  
https://downgit.github.io/#/home?url=https://github.com/TomasHricina/navigation2/tree/main/nav2_mapviz  
  
**Unzip archive:**  
cd ~/Downloads/  
unzip nav2_mapviz.zip  
  
  
**Install dependencies:**  
sudo apt-get install python3-pyqt5   
pip3 install opencv-python-headless  
pip3 install numpy  
pip3 install qimage2ndarray  
pip3 install pyaml  
  
**Alternatively:**  
sudo apt-get install python3-pyqt5  
cd ~/Downloads/nav2_mapviz/mapviz  
pip3 install -r requirements.txt  
  
**Install MapViz package:**  
cd ~/Downloads/nav2_mapviz/mapviz  
pip3 install .  
  
**Usage (In command line):**  
mapviz  
  
**Alternatively:**  
if "mapviz" command does not work:  
cd ~/Downloads/nav2_mapviz/mapviz  
python3 main.py 
    
    
  
**Uninstall:**  
pip3 uninstall nav2-mapviz
