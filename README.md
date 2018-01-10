# Star Wars Episode 1: Racer - Tools (swe1r-tools)

This is a collection of small tools to work with files from the 1999 Game "Star Wars Episode 1: Racer".

- out_modelblock.py: Extract out_modelblock.bin to Wavefront OBJ files
- out_splineblock.py: Extract out_splineblock.bin to Wavefront OBJ files
- out_spriteblock.py: Extract out_spriteblock.bin to PNG files
- out_textureblock.py: Extract out_textureblock.bin to PNG files
- scr2wav.py: Converts SCR audio files from the webdemo to WAV files
- extract-racer-tab.py: Extracts strings from swep1rcr.exe which are typcially translated
- parse-racer-tab.py: Validates racer.tab translation files
- decompress.c: Decompress "Comp" modelblock chunks (found in N64 version)

## Installation

You will need a C11 Toolchain and CMake to compile some of these tools.
The Python scripts will require Python version 3.

```
git clone https://github.com/OpenSWE1R/swe1r-tools.git
cd swe1r-tools
mkdir build
cd build
cmake ..
make
```

---

**© 2017 OpenSWE1R Maintainers**

Source code licensed under GPLv2 or any later version.
