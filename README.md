# Lights Camera Pants Texture Converter
Python scripts that batch convert the textures from "SpongeBob SquarePants: Lights, Camera, Pants!" (Xbox) into readable pngs. Extract textures from .paks w/ PakTool by seilweiss
### It reads all of the tex, tx1, and tx8 file prefixes as images, no need to convert it all to .dds beforehand!!

# Requirements
Python 3.6 or newer & Pillow (Python Imaging Library)

You can install the required library with pip:
```
pip install Pillow
```

# Tutorial
After extracting all of your .pak assets into a folder, just put in the script location and the folder location like so:

```
python fix_spongebob_tex_png.py mg_0010
```
another example
```
C:\Users\123>C:\Users\123\Downloads\LCP_Export\xbox\fix_spongebob_tex_dds.py C:\Users\123\Downloads\LCP_Export\xbox\mg_0010
```

and it will create a subfolder named "png_converted", filled with a batch conversion of all of your textures as accurate pngs!
