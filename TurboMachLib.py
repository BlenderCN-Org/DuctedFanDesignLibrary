
#///////////////////////////////////////////////
# 	
#    Turbomachinery Design Library (Python/Blender)
#    Copyright (C) 2014  Circuit Grove
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    To contribute to the Circuit Grove distribution, contact contrib@circuitgrove.com 
#
#//////////////////////////////////////////////
# 	
#   
#
#	
#
#///////////////////////////////////////////////

import bpy
import math
import DLUtils
import mathutils

def NACA4Profile(camber=10,thickness=10,camberPos=30,chord=50,npts=50):

    #//////////////////////
    #   This function creates the vertices in 2D of a NACA4 airfoil profile.
    #   This function can be used as the basis for creating turbomachinery blades.
    #   The governing equations for the NACA 4-digit series airfoils can be obtained 
    #   From: http://en.wikipedia.org/wiki/NACA_airfoil
    #
	#   Inputs:
	#       camber: As %chord (0.0 = 0%, 100.0 = 100%)
	#       thickness: max thickness of airfoil as %chord (0.0 = 0%, 100.0 = 100%)
	#       chord: chord length of foil (mm)
	#       npts: number of pts used to discretise both the upper and lower airfoil profile surface.
 
    x=[]
    yt=[]
    yc=[]
    xu=[]
    xl=[]
    yu=[]
    yl=[]
    verts = []
    
    if(camber < 0.0 or camber > 100.0):
        #error handling
        print("Warning in TurboMachLib.NACA4Profile(): Camber must be between 0 and 100 and represents a percentage.")
        camber = 0.0 #choosing a default
    if(thickness < 0.0 or thickness > 100.0):
        #error handling
        print("Warning in TurboMachLib.NACA4Profile(): thickness must be between 0 and 100 and represents a percentage.")
        thickness = 10 #choosing a default
        
    m=camber/100
    t=thickness/100
    p=camberPos/100  #camber position

        
    #Generate vertex coordinates for unmodified airfoil shape
    for i in range(0,npts+1):
        x.append(1-math.cos(i*(math.pi/2)/npts))
        yt.append(t*5*(0.2969*math.pow(x[i],0.5)-0.126*x[i]-0.3516*math.pow(x[i],2)+0.2843*math.pow(x[i],3) - 0.1015*math.pow(x[i],4)))
        if(x[i]<p):
            yc.append(m*x[i]/pow(p,2)*(2*p - x[i]))
            dycdx = 2*m/pow(p,2)*(p-x[i])
        else: 
            yc.append(m*(1-x[i])/pow(1-p,2)*(1 - 2*p + x[i]))
            dycdx = 2*m/pow(1-p,2)*(p-x[i])
			
        theta = math.atan(dycdx)	
        xu.append(x[i] - yt[i]*(math.sin(theta)))
        xl.append(x[i] + yt[i]*(math.sin(theta)))
        yu.append(-yc[i] + yt[i]*(math.cos(theta)))
        yl.append(-yc[i] - yt[i]*(math.cos(theta)))
        
       

    #Create a contiguous array of vertices for output and scale the chord.   
    for i in range(0,npts):
        verts.append([xu[i]*chord,yu[i]*chord,0.0])
    for i in range(0,npts-1):
        verts.append([xl[i+1]*chord,yl[i+1]*chord,0.0])
    	
    return verts
    
    
def NACA4Blade(name,camber_root,camber_tip,camber_position,\
        thickness,bladeHeight,twistAngle,rootChord,tipChord,\
        centerOfTwist,nspan,npts):

    #//////////////////////
	#//Inputs:
	#//	camber_max: %chord
	#//	camber_position: location of max camber %chord
	#//	thickness: max thickness of airfoil as %chord
	#//	bladeHeight: height of blade
	#//	twist: degrees/unit height
	#// centerOfTwist: %chord
	#//	nspan: number of span wise subdivisions
	#//	npts: number of pts used to discretise both the upper and lower airfoil profile surface.

    #Twist per unit length
    twist=math.radians(twistAngle)/bladeHeight

    
    mr=camber_root/100
    mt=camber_tip/100
    p=camber_position/100
    t=thickness/100
    centerOfTwist[0]= centerOfTwist[0]/100
    centerOfTwist[1]/=100
    
    x=[]
    yt=[]
    yc=[]
    xu=[]
    yu=[]
    xl=[]
    yl=[]
    xuTwist=[0]*npts
    yuTwist=[0]*npts
    xlTwist=[0]*npts
    ylTwist=[0]*npts
    verts=[]
    faces=[]
    origin=(0,0,0)

    

    
    #Generate vertex coordinates with twist and scale along the span        
    dspan = bladeHeight/nspan
    for j in range(0,nspan+1): 
        
        ### bad use of memory, Fix it.  Does this matter in Python?
        x=[]
        yt=[]
        yc=[]
        xu=[]
        xl=[]
        yu=[]
        yl=[]
        
        m=(1-j/(nspan))*mr + j/nspan*mt
        
        #Generate vertex coordinates for unmodified airfoil shape
        for i in range(0,npts+1):
        
            x.append(1-math.cos(i*(math.pi/2)/npts))
            yt.append(t/0.2*(0.2969*math.pow(x[i],0.5)-0.126*x[i]-0.3516*math.pow(x[i],2)+0.2843*math.pow(x[i],3) - 0.1015*math.pow(x[i],4)))
            if(x[i]<p):
                yc.append(m/pow(p,2)*(2*p*x[i] - pow(x[i],2)))
                dycdx = 2*m/pow(p,2)*(p-x[i])
            else:
                yc.append(m/pow(1-p,2)*(1 - 2*p + 2*p*x[i] - pow(x[i],2)))
                dycdx = 2*m/pow(1-p,2)*(p-x[i])
                
            #Shift foil to center of twist
            x[i] -= centerOfTwist[0]
            yc[i] -= centerOfTwist[1]
                
            xu.append(x[i] - yt[i]*(math.sin(math.atan(dycdx))))
            yu.append(yc[i] + yt[i]*(math.cos(math.atan(dycdx))))
            xl.append(x[i] + yt[i]*(math.sin(math.atan(dycdx))))
            yl.append(yc[i] - yt[i]*(math.cos(math.atan(dycdx))))
            
            
        
        #####
           
        angle = twist*j*dspan
        chord = rootChord - j*dspan*(rootChord-tipChord)/bladeHeight	
        for i in range(0,npts):
            xuTwist[i] = xu[i]*math.cos(angle) -yu[i]*math.sin(angle)
            yuTwist[i] = xu[i]*math.sin(angle) +yu[i]*math.cos(angle)
            
            xuTwist[i] *= chord
            yuTwist[i] *= chord
            
            verts.append((xuTwist[i],yuTwist[i],j*dspan))
        for i in range(0,npts):
            xlTwist[i] = xl[i]*math.cos(angle) -yl[i]*math.sin(angle)
            ylTwist[i] = xl[i]*math.sin(angle) +yl[i]*math.cos(angle)
            
            xlTwist[i] *= chord
            ylTwist[i] *= chord
            
            verts.append((xlTwist[i],ylTwist[i],j*dspan))
    
    
    #Generate Polies from vertex IDs
    #Bottom Cap
    faces.append((0,1,npts+1))
    for i in range(0,npts-1):
        faces.append((i,i+1,npts+i+1))    
        faces.append((i,npts+i+1,npts+i))    

    #Middle
    nPerStage = npts*2
    for j in range(0,nspan):
        for i in range(0,npts-1):
            faces.append((nPerStage*j+i,nPerStage*(j+1)+i,nPerStage*(j+1)+i+1))
            faces.append((nPerStage*j+i,nPerStage*(j+1)+i+1,nPerStage*j+i+1))
        for i in range(0,npts-1):
            faces.append((nPerStage*j+i+npts,nPerStage*(j+1)+i+1+npts,nPerStage*(j+1)+i+npts))
            faces.append((nPerStage*j+i+npts,nPerStage*j+i+1+npts,nPerStage*(j+1)+i+1+npts))
        faces.append((nPerStage*j+npts-1,nPerStage*(j+1)+npts-1,nPerStage*(j+1)+npts*2-1))
        faces.append((nPerStage*j+npts-1,nPerStage*(j+1)+npts*2-1,nPerStage*(j)+npts*2-1))
    #Top Cap
    faces.append((nPerStage*(nspan),nPerStage*(nspan)+1,nPerStage*(nspan)+npts+1))
    for i in range(0,npts-1):
        faces.append((nPerStage*(nspan)+i,nPerStage*(nspan)+npts+i+1,nPerStage*(nspan)+i+1))    
        faces.append((nPerStage*(nspan)+i,nPerStage*(nspan)+npts+i,nPerStage*(nspan)+npts+i+1))    
    
    #Create Object    
    ob1 = DLUtils.createMesh(name, origin, verts, [], faces)
    
    #reset Vars
    centerOfTwist[0]*=100
    centerOfTwist[1]*=100

