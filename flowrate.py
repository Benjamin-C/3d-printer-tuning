# 3d Printer Flowrate Test Tower Generator by Benjamin Crall
# Liscensed under GNU General Public License v3.0
# See GitHub for more info on the script, the liscense, and usage
# https://github.com/Benjamin-C/3d-printer-tuning

import numpy as np
import inspect # Used to put the shape function in the GCODE

# =======================
# CONFIG
# =======================

# Flow rate values to test in mm3/s. Values should increase
values = [10, 11, 12, 13, 14, 15]
# values = [10, 10, 10, 10, 10, 10]

# Width of extrusion in mm
extrusionWidth = 0.4

# Maximum accelleration in mm/s2
maxAccel = 20000

# Layer thickness in mm
layerHeight = 0.2

# Height of each section
sectionHeight = 10

# Number of loops in the brim. Also used for initial purge
brimLoops = 5

# Fan speed [0,255] for after the first layers
fanSpeed = 255

# The height to turn the fan on in mm
fanOnHeight = 3

# Filament extrusion multiplier, should probably be 1
extrusionMult = 1.0

# Filament diameter in mm
filamentDiam = 1.75

# Max width or height of the shape in mm
size = 100

# Center coordinates of the test [x, y] in mm
center = [60, 60]

# Filename to save GCODE to
filename = "demo.gcode"

# Start GCODE. Include any homing and other startup code here. Copy from slicer. At a minimum set and wait for temperature, and home the machine.
startgcode = '''\
print_start EXTRUDER=215 BED=60
'''

# End GCODE. Copy from slicer
endgcode = '''\
G1 E-2 ; Small retract at the end
print_end    ;end script from macro
'''
# =======================
# ADVANCED CONFIG - probably don't touch
# =======================

# Number of points around shape
numPoints = 128

# The bumpyness of the default shape. Range [0, 1]
bumpyness = 0.2

# Shape of the test piece. Defined as a function in polar coordinates. Will automatically be normalized
# shape = lambda theta: 1 + (bumpyness * np.sin(2 * theta + (np.pi/2)))
shape = lambda theta: np.ones(np.shape(theta)[0])

# Section marker height in mm, subtracted from total section height
sectionMarkerHeight = 2

# Section marker depth in mm
sectionMarkerDepth = 1

# Shape of marker. Takes a value [0,1] for the input height, and returns a change in mm of the size
sectionMarkerShape = lambda h: (np.cos(2 * np.pi * h) / 2) + 0.5

# =======================
# END CONFIG
# =======================

values = np.array(values)

# Prepare the points for a loop. The size is 1, you have to scale to the desired size.
# Multiply X,Y, and E by the (num desired mm max)/2
# Z is calculated from layer height, leave it alone

# Calculate the angles the points go at
theta = np.linspace(0, 2*np.pi, numPoints, endpoint=False)
# Calculate the points in polar coordinates
r = shape(theta)
# Convert the points to xy
shapex = np.cos(theta) * r
shapey = np.sin(theta) * r
# Normalize so the max X or Y is 1 or -1
norm = max(np.max(np.abs(shapex)), np.max(np.abs(shapey)))
# Apply normalization, scale, and offset
shapex = (shapex / norm)
shapey = (shapey / norm)
# Calculate Z for a constant spiral
shapez = np.linspace(0, layerHeight, numPoints)

# Calculate extrusion per linear mm
area = layerHeight * extrusionWidth
filarea = np.pi * ((filamentDiam/2) ** 2)
extr = area / filarea
# Calculate lengths of each segment
dists = np.zeros(np.shape(shapex)[0])
dists[1:] = np.sqrt((np.diff(shapex) ** 2) + (np.diff(shapey) ** 2))
dists[0] = np.sqrt(((shapex[-1]-shapex[0]) ** 2) + ((shapey[-1]-shapey[0]) ** 2))
# Calculate extrusions per segment. Last point connects to first
extrusions = dists * extr * extrusionMult

gcodeNumFmt = ".3f"

print("Writeing GCODE file ...", end='')
with open(filename, "w") as gcf:
    # Save the config values to the GCODE so you can see later what you did
    gcf.write(f";Speed test tower generated by Ben's script\n")
    gcf.write(f";Test Parameters:\n")
    gcf.write(f";Testing values {', '.join([f'{s:.2f}' for s in values])} mm3/s\n")
    gcf.write(f";Layer height: {layerHeight:.2f}mm\n")
    gcf.write(f";Filament diameter: {filamentDiam:.2f}mm\n")
    gcf.write(f";Extrusion multiplier: {extrusionMult:.2f}\n")
    gcf.write(f";Extrusion width (given): {extrusionWidth:.2f}mm\n")
    funcString = str(inspect.getsourcelines(shape)[0])
    funcString = funcString.strip("['\\n']").split(" = ")[1].split(":")[1].strip()
    gcf.write(f";Shape: {funcString}\n")
    gcf.write(f";Bumpyness: {bumpyness}\n")
    gcf.write(f";Shape size: {size:.2f}mm\n")
    gcf.write(f";Sectoin height: {sectionHeight:.2f}mm\n")
    gcf.write(f";Center point: {center[0]:.2f}, {center[1]:.2f} mm\n")
    gcf.write(f";Num points: {numPoints:.0f}mm\n")
    gcf.write("\n")

    # Start GCODE
    gcf.write(startgcode)
    gcf.write("G21 ; set units to millimeters\n")
    gcf.write("G90 ; use absolute coordinates\n")
    gcf.write("M83 ; Extruder relative mode\n")
    gcf.write("107 ; Turn fans off\n")
    gcf.write(f"M204 S{maxAccel}")

    gcf.write("\n")

    # Main GCODE
    lz = layerHeight

    # Make brim
    brimTheta = np.tile(theta, brimLoops)
    brimr = np.tile(r, brimLoops) / norm
    brimr *= size / 2
    brimdr = np.linspace(brimLoops * extrusionWidth, 0, brimLoops * numPoints)
    brimr += brimdr
    brimx = (np.cos(brimTheta) * brimr) + center[0]
    brimy = (np.sin(brimTheta) * brimr) + center[1]
    brimd = np.zeros(np.shape(brimx)[0])
    brimd[1:] = np.sqrt((np.diff(brimx) ** 2) + (np.diff(brimy) ** 2))
    brimd[0] = 0 # Don't extrude to the first point
    # Calculate extrusions per segment
    brime = brimd * extr * extrusionMult


    # Calculate travel feedrates in mm/min
    travel = (values[0] / area) * 60

    # Write the brim
    gcf.write(f";Brim speed: {values[0]:.2f} mm3\n")
    gcf.write(f"G1 F{travel:.2f}\n")
    gcf.write(f"G1 X{brimx[0]:{gcodeNumFmt}} Y{brimy[0]:{gcodeNumFmt}} Z{layerHeight:{gcodeNumFmt}} E{brime[0]:{gcodeNumFmt}}\n")
    for i in range(1, len(brimx)):
        gcf.write(f"G1 X{brimx[i]:{gcodeNumFmt}} Y{brimy[i]:{gcodeNumFmt}} E{brime[i]:{gcodeNumFmt}}\n")
    gcf.write("\n")

    fan = False

    # Calculate and write the tower
    for val in values:
        gcf.write(f";Speed: {val:{gcodeNumFmt}} mm3\n")

        # Calculate travel feedrates in mm/min
        travel = (val / area) * 60
        gcf.write(f"G1 F{travel:{gcodeNumFmt}}\n")

        # Calculate the z position of the next section marker
        markStart = lz + (sectionHeight - sectionMarkerHeight)

        # Generate the section
        for l in range(int(sectionHeight // layerHeight)):
            gcf.write(f";Speed {val:{gcodeNumFmt}} Layer {l}\n")

            # Turn on fan if needed
            if lz > fanOnHeight and not fan:
                gcf.write(f"M106 S{fanSpeed:.0f}")
                fan = True

            # Do a loop
            for i in range(len(shapex)):
                # Get the spiral Z coordinates
                z = shapez[i] + lz

                # Scale factor to apply to the normalized shape. Normally is just size/2, but shrinks a bit to make the layer markers
                factor = (size / 2) - ((sectionMarkerDepth * (1-sectionMarkerShape((z - markStart) / sectionMarkerHeight))) if (z - markStart) > 0 else 0)

                # Calculate all the coordinates
                x = (shapex[i] * factor) + center[0]
                y = (shapey[i] * factor) + center[1]
                e = extrusions[i] * factor

                # Write the next point
                gcf.write(f"G1 X{x:{gcodeNumFmt}} Y{y:{gcodeNumFmt}} Z{z:{gcodeNumFmt}} E{e:.4f}\n")

            # Go to the next layer
            lz += layerHeight

    # End GCODE
    gcf.write("\n")
    gcf.write("M107; Fan off")
    gcf.write(endgcode)

# All done
print(" Done")
