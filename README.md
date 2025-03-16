# Python Ray-Tracer

This is a small ray tracer written in Python.
It was created as a school project.

## Features
- Path tracing
- Smooth Shading
- Material smoothness
- Export meshes from [Blender](https://www.blender.org/) to JSON for rendering in the ray tracer
- Transform meshes (location, rotation and scale)
  - Create Scene by adding multiple objects with color and transformations
- Adjustable camera field of view
- Move the camera through the scene
 

## Installation

### Linux

```sh
git clone https://github.com/leomartinch/python-ray-tracer.git
cd python-ray-tracer/
```

Install `tqdm` using your package manager of choice:

Arch Linux:
```sh
sudo pacman -S python-tqdm
```
Debian/Ubuntu:
```sh
sudo apt-get -y install python3-tqdm
```


### Windows
Download the repository and unzip it.
Install `tqdm` for the progress meter
```
pip install tqdm
```

### Mac (Not Tested!)
Try the same steps as for Windows.



## Usage
Because of the computationally heavy task of ray tracing and the slow nature of python, the image will take a while to render.
I have implemented multiprocessing but it still can take hours on high end hardware.


### Configure Scene
At the bottom of the `ray-tracer.py` script, you can define your scene.
Each object in the scene is defined as a Python object:
```python
example_object = Object(
  "object_name",  # name of the object
  "cube",         # mesh type, can be found in the objects/ folder
  (-4,0,0),       # x,y,z translation
  (0,0,0),        # x,y,z rotation
  2,              # scale factor
  (1,0,0),        # r,g,b color value
  1,              # albedo
  1,              # roughness
  0,              # emission
  False           # smooth shading or not
)
```
Modify these values as desired.

Then, add the object to the scene dictionary.
Make sure to reference the object name and the corresponding variable:
```python
scene = {
    "object_name": example_object,
}
```

### Configure Camera
You can also configure the camera.
Note: Camera rotation has not been implemented yet.



### Render Image
Open your terminal and run the ray tracer with Python:
```sh
python ray-tracer.py
```
If you don't want to use the multiprocessing you can run:
```sh
python ray-tracer-no-multiprocessing.py
```



### Export Mesh from Blender
If you want to render a custom mesh, you first need to export it as a JSON file.
The 3D modeling program I use is [Blender](https://www.blender.org/), which is free and open source.

To export a mesh from Blender:
1. Open Blender and go to the `Scripting` tab.
1. Add the `blender-export-mesh.py` script.
1. Adjust the variables as needed and specify the export directory.
1. Run the script.

> [!IMPORTANT]  
> You must triangulate the mesh before exporting it, as my ray tracer only supports triangles.
To triangulate a mesh, select it and press `Ctr + T`.

After exporting, move the JSON file into the `objects/` folder to use it in the ray tracer.



## Contribute

This project was created because I wanted to learn how ray tracers work.
I've been using Blender for the past 8 years but never fully understood how rendering technology works.

There are several things I'd like to improve (see the Issues tab).
If you would like to contribute, feel free to email me.
More information can be found on my website: [leomartin.ch](https://www.leomartin.ch/).

I’m interested in learning how to optimize the ray tracer to reduce render times, so any suggestions are welcome!



