import math
import numpy as np
from pydub import AudioSegment
from pydub.playback import play
#import musicalbeeps
from time import sleep
from numpy import fft as fft

#load a partition data from string
def parsePartition(dataStr):
    lines = dataStr.split('\n')
    if len(lines) != 18:
        print("partition should be 18 lines!!!")
        exit()
    resultData = []
    for i in range(len(lines)):
        line = lines[i]
        segments = line.split("|")
        segments.pop(0)
        lineData = []
        for j in range(len(segments)):
            segment = segments[j]
            if j == len(segments)-1 and len(segment) == 0:
                continue
            elif len(segment) != 8:
                print("error line "+str(i)+" segment "+str(j)+" : each segment should be 8 divisions")
                exit()
            for k in range(8):
                if segment[k] == 'X':
                    lineData.append(True)
                elif segment[k] == '-':
                    lineData.append(False)
                else:
                    print("error line "+str(i)+" segment "+str(j)+" : only '-' and 'X' characters are allowed, '"+segment[k]+"' is not'")
        resultData.append(lineData)
    #resultData.reverse()
    return np.array(resultData)

#load the partition data from file
def parsePartitionFile(filename):
    with open(filename, 'r') as file:
        data = file.read()
        return parsePartition(data)

#generate the gcode for the music box cylinder
def generateGCODE(center, sheet, start_extrusion_val, prefix, suffix, height=20,radius=6.5, bump_delta = 0.9, layerHeight=0.2, startZ = 1.35, endZ = 17.55, filament_diameter = 1.75, mainLayerWidth = 0.6, bottomLayerWidth = 0.3, topLayerWidth = 0.6):
    #start of the gcode (after prefix)
    gcode = ";----------------------\n"
    gcode += ";start\n"
    gcode += ";----------------------\n"
    gcode += "G1 F600\n"

    n1 = round(height/layerHeight)#number of layers
    n2 = 192#288
    extrusion_val = start_extrusion_val
    lastZ = [0.0]*n2
    listState = []
    for i in range(n1):#vertical loop
        z0 = layerHeight*i
        #set the layer width
        layerWidth = mainLayerWidth
        if z0 < startZ:#we may want thinner or thicker layer width at the bottom to fit the plastic caps
            layerWidth = bottomLayerWidth + (mainLayerWidth-bottomLayerWidth)*z0/startZ #mainLayerWidth*(0.5 + 0.5*z0/startZ)
        elif z0 > endZ:#we may want thinner or thicker layer width at the top to fit the plastic caps
            layerWidth = mainLayerWidth + (topLayerWidth-mainLayerWidth)*(z0-endZ)/(height-endZ) #mainLayerWidth*(1 - 0.5*(z0-endZ)/(height-endZ))
        r = radius - layerWidth/2
        prev_x = center[0]-r*math.cos(0)
        prev_y = center[1]-r*math.sin(0)
        prev_bump = False
        oldSheetX = -1
        for j in range(n2):#angular loop 
            angle = 2*math.pi*j/n2 #current angle
            r2 = r
            layerWidth2 = layerWidth

            z = z0

            #because we print in spiral, the height of the first and last layer depend on the angle
            if i == 0:
                z = layerHeight * (1 + angle/(2*math.pi)) / 2
            elif i < n1 - 1:
                z += layerHeight*angle/(2*math.pi)
            thickness = z - lastZ[j] #the thickness is equal to distance to the previous layer. Except for the first and last layers, it is equal to layerHeight
            lastZ[j] = z

            #position in the partition
            sheetY = sheet.shape[0]*(z-startZ)/(endZ-startZ)
            sheetX = sheet.shape[1]*angle/(2*math.pi)

            bump = False
            #detect the start of a bump
            if sheetY >= 0 and sheetY < sheet.shape[0] and sheetX >= 0 and sheetX < sheet.shape[1] and sheet[int(sheetY),sheet.shape[1]-int(sheetX)-1] > 0:
                bump = True

            x = center[0]-r2*math.cos(angle)
            y = center[1]-r2*math.sin(angle)
            dx = x-prev_x
            dy = y-prev_y
            length = math.sqrt(dx*dx + dy*dy)

            #apply the bump
            if bump != prev_bump or length >= 1 or j == 0 or j+1 == n2:
                listState.append((x,y,z,layerWidth2,thickness))
                prev_x = x
                prev_y = y
            if bump == True and int(sheetX) != int(oldSheetX):
                alpha = (bump_delta/2) * (1.0 + min(1.0, 2*(sheetY - int(sheetY))))
                r2 += alpha
                x = center[0]-r2*math.cos(angle)
                y = center[1]-r2*math.sin(angle)
                listState.append((x,y,z,layerWidth2,thickness))
            prev_bump = bump
            oldSheetX = sheetX

    prev_x = None
    prev_y = None
    prev_z = None
    #convert the list of states into GCode
    for (x,y,z,width,thickness) in listState:
        if prev_x is None:
            gcode += "G1 X"+str(x)+" Y"+str(y)+" Z"+str(z)+"\n"
        else:
            dx = x-prev_x
            dy = y-prev_y
            dz = z-prev_z
            length = math.sqrt(dx*dx + dy*dy + dz*dz)
            A_layer = thickness*(width-thickness) + math.pi*(thickness**2)/4
            extrusion_length = A_layer*length/(math.pi*(filament_diameter/2)**2)
            extrusion_val += extrusion_length
            gcode += "G1 X"+str(x)+" Y"+str(y)+" Z"+str(z)+" E"+str(extrusion_val)+" ;thick="+str(thickness)+"\n"
        prev_x = x
        prev_y = y
        prev_z = z


    #end of the gcode, before the suffix
    gcode += ";----------------------\n"
    gcode += ";end\n"
    gcode += ";----------------------\n"
    return prefix+'\n'+gcode+suffix+'\n'

def calculateVertex(center, z, angle, radius):
    x = center[0]-radius*math.cos(angle)
    y = center[1]-radius*math.sin(angle)
    return np.array( [x,y,z])

def generateTriangleList(center,sheet, height=20,radius=6.5, layerHeight=0.2, bump_delta = 0.9, startZ = 1.35, endZ = 17.55, mainLayerWidth = 0.6, bottomLayerWidth = 0.3, topLayerWidth = 0.6):
    print("generating triangle list...")
    n1 = round(height/layerHeight)
    n2 = 192#288
    listLayers = []
    listLayerWidth = []
    for i in range(n1):#vertical loop
        z = layerHeight*i

        #set the layer width
        layerWidth = mainLayerWidth
        if z < startZ:#we may want thinner or thicker layer width at the bottom to fit the plastic caps
            layerWidth = bottomLayerWidth + (mainLayerWidth-bottomLayerWidth)*z/startZ
        elif z > endZ:#we may want thinner or thicker layer width at the bottom to fit the plastic caps
            layerWidth = mainLayerWidth + (topLayerWidth-mainLayerWidth)*(z-endZ)/(height-endZ)
        r = radius - layerWidth/2
        oldSheetX = -1
        currentLayer = []
        for j in range(n2):#angular loop
            angle = 2*math.pi*j/n2
            r2 = r

            thickness = layerHeight

            #position in the partition
            sheetY = sheet.shape[0]*(z-startZ)/(endZ-startZ)
            sheetX = sheet.shape[1]*angle/(2*math.pi)

            bump = False
            #detect the start of a bump
            if sheetY >= 0 and sheetY < sheet.shape[0] and sheetX >= 0 and sheetX < sheet.shape[1] and sheet[int(sheetY),sheet.shape[1]-int(sheetX)-1] > 0:
                bump = True
            
            #apply the bump
            if bump == True and int(sheetX) != int(oldSheetX):
                alpha = (bump_delta/2) * (1.0 + min(1.0, 2*(sheetY - int(sheetY))))
                r2 += alpha
            elif bump == True:
                alpha = (bump_delta/2) * (1.0 + min(1.0, 2*(sheetY - int(sheetY)))) * (1 + int(sheetX) - sheetX )
                r2 += alpha
            currentLayer.append(r2)
            oldSheetX = sheetX
        listLayers.append(currentLayer)
        listLayerWidth.append(layerWidth)

    #generates the list of triangles
    listTriangles = []
    for i in range(n1):
        i1 = max(i-1, 0)
        i2 = i
        z1 = i*layerHeight
        z2 = (i+1)*layerHeight
        for j in range(n2):
            angle1 = 2*math.pi*j/n2
            angle2 = 2*math.pi*((j+1)%n2)/n2
            p1 = calculateVertex(center, z1, angle1, listLayers[i1][j] + listLayerWidth[i1]/2)
            p2 = calculateVertex(center, z2, angle1, listLayers[i2][j] + listLayerWidth[i2]/2)
            p3 = calculateVertex(center, z1, angle2, listLayers[i1][(j+1)%n2] + listLayerWidth[i1]/2)
            p4 = calculateVertex(center, z2, angle2, listLayers[i2][(j+1)%n2] + listLayerWidth[i2]/2)

            listTriangles.append(p3)
            listTriangles.append(p2)
            listTriangles.append(p1)

            listTriangles.append(p4)
            listTriangles.append(p2)
            listTriangles.append(p3)


            p5 = calculateVertex(center, z1, angle1, radius - listLayerWidth[i1])# listLayers[i1][j] - listLayerWidth[i1]/2)
            p6 = calculateVertex(center, z2, angle1, radius - listLayerWidth[i2])#listLayers[i2][j] - listLayerWidth[i2]/2)
            p7 = calculateVertex(center, z1, angle2, radius - listLayerWidth[i1])#listLayers[i1][(j+1)%n2] - listLayerWidth[i1]/2)
            p8 = calculateVertex(center, z2, angle2, radius - listLayerWidth[i2])#listLayers[i2][(j+1)%n2] - listLayerWidth[i2]/2)

            listTriangles.append(p5)
            listTriangles.append(p6)
            listTriangles.append(p7)

            listTriangles.append(p7)
            listTriangles.append(p6)
            listTriangles.append(p8)

            if i1 == 0:
                listTriangles.append(p1)
                listTriangles.append(p5)
                listTriangles.append(p7)

                listTriangles.append(p1)
                listTriangles.append(p7)
                listTriangles.append(p3)
            
            if i2 == n1-1:
                listTriangles.append(p8)
                listTriangles.append(p6)
                listTriangles.append(p2)

                listTriangles.append(p4)
                listTriangles.append(p8)
                listTriangles.append(p2)
    print("triangle list generated!!!")
    return listTriangles

#save a list of triangles into STL file
def saveToSTL(filename, listTriangles):
    print("saving to "+filename+" ...")
    with open(filename, "w") as myfile:
        nbTri = len(listTriangles)//3
        myfile.write("solid music_cylinder\n")
        for i in range(nbTri):
            v1 = listTriangles[i*3]
            v2 = listTriangles[i*3+1]
            v3 = listTriangles[i*3+2]
            n = np.cross( v2 - v1  , v3 - v1)
            n /= np.sqrt(n.dot(n))
            myfile.write("facet normal "+str(n[0])+" "+str(n[1])+" "+str(n[2])+"\n")
            myfile.write("outer loop\n")
            myfile.write("vertex "+str(v1[0])+" "+str(v1[1])+" "+str(v1[2])+"\n")
            myfile.write("vertex "+str(v2[0])+" "+str(v2[1])+" "+str(v2[2])+"\n")
            myfile.write("vertex "+str(v3[0])+" "+str(v3[1])+" "+str(v3[2])+"\n")
            myfile.write("endloop\n")
            myfile.write("endfacet\n")
        myfile.write("endsolid music_cylinder\n")
    print("Done!!!")
