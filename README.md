# MusicBoxMaker

This code allows to generate the GCODE for custom music box cylinder.  
Please check the video first :  
[![IMAGE ALT TEXT](http://img.youtube.com/vi/Hx4FuogXTyk/0.jpg)](http://www.youtube.com/watch?v=Hx4FuogXTyk "Custom music box with 3D printed cylinder")

The main part of the code is in the file musicBoxMaker.py which contains the cylinder generation and partition/music score loading.
To generate a STL or GCODE, you should adapt and execute cylinderGeneratorSTL.py or cylinderGeneratorGCODE.py
It's recommended to use the GCODE generation instead of the STL, but the STL may be usable if your printer is well calibrated.

Sorry, due to a translation error, I used the term "partition" instead of "music score", I'll update the source code in a future commit.

# Run the scripts

To run the scripts, you need to install python with the modules numpy, pydub, and simpleaudio.
On windows, you may need to install visualc++ build tools to solve some errors.

There are 3 scripts that you can modify and use : 
* play_partition.py, to play a partition/music score file using your recorded notes
* cylinderGeneratorSTL.py, to generate a STL file corresponding to the cylinder of your partition/music score
* cylinderGeneratorGCODE.py, to generate a GCODE file corresponding to the cylinder of your partition/music score

# Parameter list

Both the STL and GCODE generating scripts have a list of parameters to tune for your music box.
The default parameters should be close, but you may have to adjust slightly.

Parameter | Description
----------|------------
center | center coordinate of your 3D model (use the center coordinate of your 3D printer if you generate GCODE)
sheet  | the partition/music score
height | height of the cylinder
radius | outer radius of the cylinder (not including the pins)
startZ | start position (in Z) of your partition/music score on the cylinder. Adjust this parameter to align the pins to the comb.
endZ   | end position (in Z) of your partition/music score on the cylinder. Adjust this parameter to align the pins to the comb.
bump_delta | Increase or decrease it to adjust the size of the pins
layerHeight | layer height/thickness
filament_diameter | Diameter of your filament (GCODE only)
start_extrusion_val | starting value for extruding the plastic in the GCODE. Should be adapted based on the prefix GCODE you use. (GCODE only)
prefix | GCODE that will be executed before the printing of the cylinder. You must adapt it based on your printer. (GCODE only)
suffix | GCODE that will be executed after the printing of the cylinder. You must adapt it based on your printer. (GCODE only)
mainLayerWidth | layer width for the main part of your cylinder
bottomLayerWidth | layer width for the bottom of your cylinder (gradient until 0 to startZ). Adjust it to fit the plastic bottom plastic cap.
topLayerWidth | layer width for the top of your cylinder (gradient from endZ to height). Adjust it to fit the plastic top plastic cap.

# Partition/music score file

a partition/music score file is a txt file with 18 lines (for 18 tones).
Each line is composed of multiple segments of 8 notes separated by a vertical bar |--------|--------|--------|  
A hyphen - is used when the note is not played, and a X is used when the note is played.  
Before the first vertical bar |, you can add text such as the name of the corresponding tone (ex: B5#|----X---|).  
 
# STL generation script
In cylinderGeneratorSTL.py, you can generate a STL file for your partition/music score :
First, you need to load your partition/music score file :
``` python
partition = musicBoxMaker.parsePartitionFile("yourPartition.txt")
``` 
Then, you generate the list of triangles using the function musicBoxMaker.generateTriangleList. See the parameters description in the section "Parameter list".  
Finally, you can generate the STL file using :  
``` python
musicBoxMaker.saveToSTL("yourFile.stl", listTri)
``` 

For better control of the print, it is recommended to generate the GCODE instead.

# Generate your prefix and suffix gcode

To generate the GCODE of your cylinder, you will need to provide a prefix and suffix GCODE (code executed before and after the print of the cylinder), and the start extrusion value (the extrusion value just after the prefix).  
To obtain these, I recommend you to generate a STL and slice it with your favorite slicer configured for your 3D printer (in my case, I used CURA).  
Then, you open the generated GCODE with a text editor and you search for the beginning of the print.
If you use CURA, you should search for comments such as `;MESH:yourFile.stl`, followed by a few G0 commands, followed by `;TYPE:WALL-OUTER` followed by a G1 command similar to `G1 F2700 E10.71106`. If you find it, copy that into a prefix.gcode file. The 'E' value (in this example, 10.71106) is the value you should specify for the parameter `start_extrusion_val`.  
For the suffix, search for the commend `;TIME_ELAPSED:` and copy from the G0 command just before (example: `G0 F12000 X109.984 Y116.489`) until the end of the file.
You can find example of prefix and suffix GCODE in this project files, but DO NOT USE THEM if you have a different printer than an ender 5 or if you print with different filament than PLA. You should generate your own one adapted for your printer, and watch carefully for the first use.

# GCODE generation script

In the cylinderGeneratorGCODE.py script, you can generate the GCODE by modifying these lines :

You should set your own prefix and suffix gcode in these lines :
```python
with open ("prefix.gcode", "r") as myfile:
    prefix=str(myfile.read())
with open ("suffix.gcode", "r") as myfile:
    suffix=str(myfile.read())
```
Check the previous section for explanation. USE ONLY a prefix and suffix adapted to your printer.
 
Then, you can load the partition/music score by modifying this line :  
``` python
partition = musicBoxMaker.parsePartitionFile("yourPartition.txt")
``` 

Adjust the generation parameters on the function musicBoxMaker.generateGCODE

And save the result :
``` python
with open("result_cylinder.gcode", "w") as myfile:
    print("saving...")
    myfile.write(gcode)
    print("Done!!!")
``` 

# Disclaimer
Be careful when using the GCODE for the first time, please watch it to be sure that everything works properly.  
Before the first run, you can visualize your GCODE with a viewer such as https://gcode.ws/  
Make sure you set properly the prefix, suffix, start_extrusion_val, center, and all the other parameters to values that are compatible to your printer.
