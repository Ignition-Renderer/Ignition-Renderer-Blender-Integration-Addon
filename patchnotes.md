# 9/11/21 3:50pm PST
- Mostly Finished Material Exporting
- Image Finding does not work. If any materials have an image texture plugged into a texture input, the export will not work.
# 9/8/21 9:52pm PST
- Continued Work on scene exporter
- Got basic material output working (non-color values should work if not 0)
- Updated file writing algorithm
- Removed useless debug
# 7/30/21 12:53pm PST
- Started Fixing Quad Lights being incorrectly loaded in (incomplete fix)
- Added two new nodes; `LavaFrameLightNodeSphere` and `LavaFrameLightNodeQuad`
- Advanced work on exporter (meshes, lights, and materials are still not exported and is subject to crashing)
- Renamed most buttons from Ignition to LavaFrame