# MusicBoxMaker

This code allows to generate the GCODE for custom music box cylinder.
Please check the video first : (soon)

Most of the code is in the musicBoxMaker.py file, but you don't need to modify it to generate your music box cylinder.
It's possible to generate STL file or GCODE directly. STL may be usable if your printer is well calibrated, but generating the GCODE is recommended.

# Run the scripts

You need to install python with the modules numpy, pydub, simpleaudio.
On windows, you may need visualc++ build tools.

There are 3 scripts that you can modify and use : 
* play_partition.py, to play a partition file using your recorded notes
* cylinderGeneratorSTL.py, to generate a STL file corresponding to the cylinder of your partition
* cylinderGeneratorGCODE.py, to generate a GCODE file corresponding to the cylinder of your partition

# Parameter list

Both the STL and GCODE generating scripts have a list of parameters to tune for your music box.
The default parameters should be close, but you may have to adjust slightly.

Parameter | Description
----------|------------
center | center coordinate of your 3D model (use the center coordinate of your 3D printer if you generate GCODE)
sheet  | the partition
height | height of the cylinder
radius | outer radius of the cylinder (not including the pins)
startZ | start position (in Z) of your partition on the cylinder. Adjust this parameter to align the pins to the comb.
endZ   | end position (in Z) of your partition on the cylinder. Adjust this parameter to align the pins to the comb.
bump_delta | Increase or decrease it to adjust the size of the pins
layerHeight | layer height/thickness
filament_diameter | Diameter of your filament (GCODE only)
start_extrusion_val | starting value for extruding the plastic in the GCODE. Should be adapted based on the prefix GCODE you use. (GCODE only)
prefix | GCODE that will be executed before the printing of the cylinder. You must adapt it based on your printer. (GCODE only)
suffix | GCODE that will be executed after the printing of the cylinder. You must adapt it based on your printer. (GCODE only)
mainLayerWidth | layer width for the main part of your cylinder
bottomLayerWidth | layer width for the bottom of your cylinder (gradient until 0 to startZ). Adjust it to fit the plastic bottom plastic cap.
topLayerWidth | layer width for the top of your cylinder (gradient from endZ to height). Adjust it to fit the plastic top plastic cap.


# Generate your prefix and suffix gcode

You should first use your favorite slicing software to generate the gcode corresponding to any object.
