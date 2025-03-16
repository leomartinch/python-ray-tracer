# Python Ray-Tracer

This is a small ray tracer written in python.
It was created for a school project.

## Features
- Path tracing
- Smooth Shading
- Material smoothnes
- Export meshes from [Blender](https://www.blender.org/) to JSON, for rendering in the ray tracer
- Transform Meshes (Location, Rotation and Scale)
  - Create Scene by adding multiple objects with color and transformations
- Camera field of view
- Move camera through scene
 

## Installation:

### Linux

```sh
git clone https://github.com/leomartinch/python-ray-tracer.git
cd python-ray-tracer/
```

Install `tqdm` in your distribution of choice.

Arch Linux:
```sh
sudo pacman -S python-tqdm
```
Debian:
```sh
sudo apt-get -y install python3-tqdm
```


### Windows
Download the file and unzip it.
Install `tqdm` for the progress meter
```
pip install tqdm
```

### Mac (Not Tested!)
Try same as for Windows.


## Usage
Because of the computationally heavy task of ray tracing and the slow nature of python, the image will take a while to render.
I have implemented multiprocessing but it still can take hours on high end hardware.


### Export Mesh from Blender
If you want to render a custom mesh you firs tneed to export it to json.
The 3D-Modeling programm of my choice is [Blender](https://www.blender.org/) which is free and open source.

Open Blender and go to `Scripting` and add the `blender-export-mesh.py` script.
Change the Variables to your liking and add the directory to which you want to export to.

> [!IMPORTANT]  
> You have to triangulate the mesh before exporting it. 
My ray tracer only renders using triangles.
Select mesh and press `Ctr + T` to triangulate it.

After exporting, move the file into the `objects/` folder to call it in the ray tracer.



