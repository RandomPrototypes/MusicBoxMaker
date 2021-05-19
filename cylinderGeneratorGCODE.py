import musicBoxMaker

prefix = ""
suffix = ""
#load the prefix and suffix gcode (for initialization and finish). 
#Generate one gcode from your favorite software and copy paste the sections before and after the print of the object itself
#Make sure to adjust the parameter start_extrusion_val for the generateGCODE function
with open ("prefix.gcode", "r") as myfile:
    prefix=str(myfile.read())
with open ("suffix.gcode", "r") as myfile:
    suffix=str(myfile.read())

partition = musicBoxMaker.parsePartitionFile("listNotes.txt")#put your partition here

#adjust the parameters to adjust to your music box
gcode = musicBoxMaker.generateGCODE(center=[110.0,110.0], height=20, radius=6.5, layerHeight=0.2, startZ = 1.35, endZ = 17.55, sheet=partition, start_extrusion_val=10.71106, prefix=prefix, suffix=suffix)
#save the gcode
with open("result_cylinder.gcode", "w") as myfile:
    print("saving...")
    myfile.write(gcode)
    print("Done!!!")
