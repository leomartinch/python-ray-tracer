import bpy
import json

"""EXPORT MESH TO JSON"""
"""Leo Martin (2025)"""


### FUNCTION ###
def get_triangles_and_vertices(mesh_name):
    obj = bpy.data.objects.get(mesh_name) # get the blender object

    if obj is None:
        print("Error: Object does not Exist")
        return

    mesh = obj.data
    triangles = []
    vertices = []

    for vertice in mesh.vertices:
        vertices.append((vertice.co.x, vertice.co.y, vertice.co.z))

    for face in mesh.polygons:
        face_indices = face.vertices[:]
        triangles.append(face_indices)

    data["mesh"] = triangles
    data["vertices"] = vertices


### VARIABLES ###
blender_mesh_name = "Sphere" # name of the mesh you want to export
file_location = "C:/Users/randy/Downloads" # location where you want to export the file
export_file_name = "sphere" # name of the exported file

"""IMPORTANT: Traingulate the mesh before exporting"""


### SCRIPT ###
data = {}
get_triangles_and_vertices(blender_mesh_name)

export_file = f"{file_location}/{export_file_name}.json"

with open(export_file, "w") as file: # convert tuples to lists and save as JSON
    json.dump(data, file, indent=0)

print(f"Sucessfully exported mesh: {blender_mesh_name}")
