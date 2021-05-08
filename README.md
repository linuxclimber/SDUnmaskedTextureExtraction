# SDUnmaskedTextureExtraction
Scripts for extracting textures from the TEXDIC.htd files in Scooby Doo Unmasked for the Gamecube- may also work with other games that use this file format such as Scaler.  Currently only handles CMPR found in the TEXDIC file but going to work on figuring out the other embedded images next.

Running the code:
Once you've pulled down the repository, copy a TEXTDIC.htd file into the same folder as the scripts and then run 'python3 textureFinder.py' to attempt to find and extract all CMPR textures in the file.  Once all the files are extracted to the "textures" sub-folder (you may need to create this before running the script the first time), you will be asked for a new name for the folder and the folder will be renamed to that and a new textures folder will be created.

If you know the filename of the specific texture you want to extract from the TEXDIC file, you can run "python3 textureExtractor.py" and type in that file name when prompted.  If it is successfully found, the texture will be extracted to the "textures" subfolder
