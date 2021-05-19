import musicBoxMaker

partition = musicBoxMaker.parsePartitionFile("listNotes.txt")#put your partition here

#adjust the parameters to adjust to your music box
listTri = musicBoxMaker.generateTriangleList(center=[110.0,110.0], height=20, radius=6.5, layerHeight=0.2, startZ = 1.35, endZ = 17.55, sheet=partition)
musicBoxMaker.saveToSTL("result_cylinder.stl", listTri)#save to STL
