# 3d-printer-tuning
Collection of Script(s) to generate GCODE files to tune 3d printers

DISCLAIMER: These tests may or may not be accurate. I've done my best to ensure they are, but I may have missed something. If I did, please let me know! Also, these do not have most of the protections that most slicers do, so it is up to you to make sure that the GCODE files won't hurt your printer (or you). It is probably a good idea to use a GCODE viewer to verify the files before printing.

NOTE: Most printers have internal software limitations on things such as speed and acceleration that will slow down the print if it is too fast. These scripts DO NOT take those into account, so they might mean that the actual things you're testing may be lower than desired. Some printer interfaces will give you real-time statistics, so you should use those to ensure you're actually testing what you think you are.

# Flowrate
This script generates towers to test flowrates. Each tower is one continuous spiral with sections of different flow rates with markers between. Run a tower starting with rates you know work, then go to rates you're unsure of. You'll then have to look at the prints and see what you think about each rate. Each parameter is documented in the code, as well as in more detail below.

Settings:
| Name   | Use
|--------|------
| values | List of flow rate values to test in mm3/s. Values should increase so that higher rates don't disturb lower ones. The first value is used for the brim, so make sure it actually works.
| extrusionWidth | The expected extrusion width. This is normally your nozzle diameter if you've tuned your extrusion just right. This is used for calculating flow rates and brim width
| layerHeight | The desired layer thickness in mm
| sectionHeight | The height of each flowrate section. This includes the markers, which are 2mm tall by default.
| brimLoops | The number of loops on the brim. This is both for purging at the beginning, as well as bed adhesion. If you are testing a bedslinger, you might want to increase this.
| extrusionMult | The extrusion multiplier. Generally this should be 1, but if you've tuned something else in, put that here.
| filamentDiam | The diameter of the filament you're using in mm. This should probably be 1.75 unless you know it should be different.
| size | The size of the test piece in mm. The test piece will be scaled to fit in a size x size square
| center | The center of the test piece, this should generally be the center of your bed
| filename | The filename to save the GCODE file to. It will be saved in the same folder as the `.py` file unless you specify otherwise. Include the `.gcode` extension, or specify your own.
| startgcode | The start GCODE for the printer. This MUST at a minimum (1) Set and wait for hotend temperature (2) Turn on the heatbed here if you use it (3) Home the printer. Probably just copy this from your slicer, and replace any variables. My default is provided as an example, but you may need to modify it.
| endgcode | The end GCODE for the printer. You might not need anything here, although a small retraction can help keep the printer clean.