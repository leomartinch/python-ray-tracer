import math
import random
import json
import multiprocessing
from tqdm import tqdm

"""RAY TRACER"""
"""Leo Martin (2025)"""


### VECTOR-FUNCTIONS ###

def add(v1, v2):
    return (v1[0] + v2[0],
            v1[1] + v2[1],
            v1[2] + v2[2])

def subtract(v1, v2):
    return (v1[0] - v2[0],
            v1[1] - v2[1],
            v1[2] - v2[2])

def invert(vector):
    return (-vector[0], 
            -vector[1], 
            -vector[2])

def multiply(v1, v2):
    return (v1[0] * v2[0],
            v1[1] * v2[1],
            v1[2] * v2[2])

def divide(v1, v2):
    return (v1[0] / v2[0],
            v1[1] / v2[1],
            v1[2] / v2[2])


def multiply_scalar(vector, t):
    return (vector[0] * t, 
            vector[1] * t, 
            vector[2] * t)

def divide_scalar(vector, t):
    return (vector[0] / t, 
            vector[1] / t, 
            vector[2] / t)

def length(vector):
    return (vector[0]**2 + vector[1]**2 + vector[2]**2) ** 0.5

def length_squared(vector):
    return vector[0]**2 + vector[1]**2 + vector[2]**2

def dot_product(v1, v2): # skalarprodukt
    return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]

def cross(v1, v2): # vektorprodukt
    return (
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    )

def normalize(vector): # einheitsvektor
    return divide_scalar(vector, length(vector))

def lerp(v1, v2, factor): # blend between two vectors
    return (
        v1[0] * (1-factor) + v2[0] * factor,
        v1[1] * (1-factor) + v2[1] * factor,
        v1[2] * (1-factor) + v2[2] * factor,
    )



### IMAGE RENDERING FUNCTIONS ###

def render_chunk(start_row, end_row, width, height, pixel_size, start_x, start_y, scene, pbar, camera_data):
    rows = []
    center_pixel = pixel_size / 2
    
    image_start = camera_data["image_start"]
    column_vector = camera_data["column_vector"]
    row_vector = camera_data["row_vector"]
    ray_origin = camera_data["camera_ray_origin"]
    samples = camera_data["samples"]
    max_bounces = camera_data["max_bounces"]

    for h in range(start_row, end_row):  # row loop
        y_pos = multiply_scalar(row_vector, ((pixel_size * h) + center_pixel))
        row = []

        for w in range(width):  # column loop
            x_pos = multiply_scalar(column_vector, ((pixel_size * w) + center_pixel))
            x_pos = add(image_start, x_pos)

            column_progress = add(x_pos, y_pos)
            ray_direction = normalize(subtract(column_progress, ray_origin))

            color = trace_path(ray_origin, ray_direction, scene, samples, max_bounces)

            red = int(255 * min(color[0], 1))
            green = int(255 * min(color[1], 1))
            blue = int(255 * min(color[2], 1))

            row.append(f"{red} {green} {blue}")
        
        rows.append(row)
        pbar.update(1)  # update progress for each completed row
    return rows


def render_image(image_width, image_height, image_resolution, samples, max_bounces, yaw, pitch, camera_location, field_of_view, filename, scene):
    filename += ".ppm"

    start_x = -(image_width / 2)
    start_y = image_height
    pixel_size = image_width / image_resolution
    height = int(image_height / pixel_size)
    width = int(image_width / pixel_size)

    camera_data = get_camera_data(image_width, image_height, yaw, pitch,camera_location, field_of_view, samples, max_bounces)

    # instead of dividing into chunks for multiprocessing, we process all rows in sequence
    rows = []
    with tqdm(total=height, desc="Rendering Progress", unit="rows") as pbar:
        rows.extend(render_chunk(0, height, width, height, pixel_size, start_x, start_y, scene, pbar, camera_data))

    # combine results and write the final image to file (PPM format)
    with open(filename, 'w') as f:
        f.write(f"P3\n{width} {height}\n255\n")  # PPM header
        for row in rows:
            f.write(' '.join(row) + '\n')

    print(f"Image rendered: {filename}")


def progress_monitor(queue, total):
        with tqdm(total=total, desc="Rendering Progress", unit="rows") as pbar:
            completed = 0
            while completed < total:
                completed += queue.get()
                pbar.update(1)



### RAY FUNCTIONS ###

def trace_path(start_ray_origin, start_ray_direction, scene, samples, max_bounces):
    final_color = (0.0, 0.0, 0.0)

    for _ in range(samples):
        ray_origin = start_ray_origin
        ray_direction = start_ray_direction

        # holds the accumulated color
        throughput = (1.0, 1.0, 1.0)

        for _ in range(max_bounces):
            intersection_point, normal, object_id = get_object_hit(ray_origin, ray_direction, scene)
            
            if intersection_point:
                object = scene[object_id]

                emitted_light = multiply_scalar(object.color, object.emission_strength)
                final_color = add(final_color, multiply(throughput, emitted_light))

                throughput = multiply(throughput, object.color)
                throughput = multiply_scalar(throughput, object.albedo)

                ray_origin = intersection_point

                diffuse_direction = get_diffuse_direction(normal)
                specular_direction = get_specular_direction(ray_direction, normal)
                ray_direction = lerp(specular_direction, diffuse_direction, object.roughness)
            else:
                break

    return divide_scalar(final_color, samples) # average the final color


def get_object_hit(ray_origin, ray_direction, scene):   
    global_closest_distance = float('inf')
    closest_intersection = None
    closest_normal = None
    closest_object = None

    for object_id in scene:
        object = scene[object_id]

        if not ray_intersects_bounding_box(ray_origin, ray_direction, object.bounding_box):
            continue

        for triangle in object.mesh:
            local_vertices = (
                object.vertices[triangle[0]], 
                object.vertices[triangle[1]], 
                object.vertices[triangle[2]]
            )
            local_vertex_normals = (
                object.vertex_normals[triangle[0]], 
                object.vertex_normals[triangle[1]], 
                object.vertex_normals[triangle[2]]
            )
            normal_vector, intersection_point = get_normal_vector(
                    ray_origin, ray_direction, local_vertices, local_vertex_normals, object.is_smooth
            )
            if normal_vector and not is_backfacing(ray_direction, normal_vector):
                distance = length(subtract(intersection_point, ray_origin))
                if distance < global_closest_distance:
                    global_closest_distance = distance
                    closest_object = object_id
                    closest_intersection = intersection_point
                    closest_normal = normal_vector

    if closest_normal:
        return closest_intersection, closest_normal, closest_object
    else:
        return None, None, None


def is_backfacing(ray_direction, triangle_normal):
    return dot_product(ray_direction, triangle_normal) > 0


def get_ray_triangle_intersection(ray_origin, ray_direction, vertices):
    edge_1 = subtract(vertices[1], vertices[0])
    edge_2 = subtract(vertices[2], vertices[0])

    p_vector = cross(ray_direction, edge_2)
    determinant = dot_product(edge_1, p_vector)

    if abs(determinant) < 1e-8:
        return None # ray is parallel or invalid

    inverse_determinant = 1 / determinant
    ray_to_vertice_0 = subtract(ray_origin, vertices[0])

    u = dot_product(ray_to_vertice_0, p_vector) * inverse_determinant
    if u < 0 or u > 1:
        return None

    q = cross(ray_to_vertice_0, edge_1)
    v = dot_product(ray_direction, q) * inverse_determinant
    if v < 0 or u + v > 1:
        return None

    t = dot_product(edge_2, q) * inverse_determinant
    if t > 0:
        intersection_point = add(ray_origin, multiply_scalar(ray_direction, t))
        return intersection_point

    return None # ray intersects triangle behind camera


def get_normal_vector(ray_origin, ray_direction, vertices, vertex_normals, is_smooth):
    v0, v1, v2 = vertices
    normal_0, normal_1, normal_2 = vertex_normals    

    edge_1 = subtract(v1, v0)
    edge_2 = subtract(v2, v0)

    h = cross(ray_direction, edge_2)
    a = dot_product(edge_1, h)

    if abs(a) < 1e-8:  # parallel ray check
        return None, None

    f = 1.0 / a
    s = subtract(ray_origin, v0)
    u = f * dot_product(s, h)

    if u < 0.0 or u > 1.0: # outside triangle
        return None, None

    q = cross(s, edge_1)
    v = f * dot_product(ray_direction, q)

    if v < 0.0 or u + v > 1.0: # outside triangle
        return None, None

    t = f * dot_product(edge_2, q)

    if t > 1e-8: # intersection exists in future
        w = 1.0 - u - v
        intersection_point = add(ray_origin, multiply_scalar(ray_direction, t))

        if not is_smooth: # no smooth shading
            return cross(edge_1, edge_2), intersection_point

        # interpolate normal using barycentric coordinates for smooth shading
        interpolated_normal = add(
                multiply_scalar(normal_0, w),
                add(multiply_scalar(normal_1, u), multiply_scalar(normal_2, v))
        )
        
        return normalize(interpolated_normal), intersection_point

    return None, None


def get_vertex_normals(vertices, mesh): # get the normals for the vertex points (combination of vertex normal of the three surounding faces)
    vertex_normals = [(0, 0, 0)] * len(vertices)
    for triangle in mesh:
        edge_1 = subtract(vertices[triangle[1]], vertices[triangle[0]])
        edge_2 = subtract(vertices[triangle[2]], vertices[triangle[0]])
        face_normal = normalize(cross(edge_1, edge_2))
        
        for vertex in triangle:
            vertex_normals[vertex] = add(vertex_normals[vertex], face_normal)

    for i in range(len(vertex_normals)):
        vertex_normals[i] = normalize(vertex_normals[i])

    return vertex_normals


### SHADERS ###

def get_specular_direction(hit_direction, normal):
    dot = dot_product(hit_direction, normal)
    reflection = subtract(hit_direction, multiply_scalar(normal, 2 * dot))
    return reflection


def get_diffuse_direction(normal):
    r1 = random.random()
    r2 = random.random()

    phi = 2 * math.pi * r2
    
    x = math.cos(phi) * math.sqrt(1 - r1)
    y = math.sin(phi) * math.sqrt(1 - r1)
    z = math.sqrt(r1)

    if abs(normal[0]) > 0.99:
        tangent = (0, 1, 0)
    else:
        tangent = normalize(cross(normal, (1, 0, 0)))
    
    bitangent = cross(normal, tangent)

    world_dir = add(
        add(multiply_scalar(tangent, x), multiply_scalar(bitangent, y)),
        multiply_scalar(normal, z)
    )
    
    return normalize(world_dir)



### BOUNDING BOX ###

def get_bounding_box(vertices):
    max_x = 0
    min_x = 0

    max_y = 0
    min_y = 0

    max_z = 0
    min_z = 0

    for vertice in vertices:
        if vertice[0] > max_x:
            max_x = vertice[0]
        if vertice[0] < min_x:
            min_x = vertice[0]

        if vertice[1] > max_y:
            max_y = vertice[1]
        if vertice[1] < min_y:
            min_y = vertice[1]

        if vertice[2] > max_z:
            max_z = vertice[2]
        if vertice[2] < min_z:
            min_z = vertice[2]

    bounding_box_max = (max_x, max_y, max_z)
    bounding_box_min = (min_x, min_y, min_z)

    return bounding_box_min, bounding_box_max


def ray_intersects_bounding_box(ray_origin, ray_direction, bounding_box): 
    cube_min = bounding_box[0]
    cube_max = bounding_box[1]
    t_min = float('-inf')
    t_max = float('inf')

    for i in range(3): # loop through x, y, z axes
        if abs(ray_direction[i]) < 1e-9:  # ray is parallel to this axis
            if ray_origin[i] < cube_min[i] or ray_origin[i] > cube_max[i]:
                return False  # ray is outside the slab
        else:
            t1 = (cube_min[i] - ray_origin[i]) / ray_direction[i]
            t2 = (cube_max[i] - ray_origin[i]) / ray_direction[i]
            t1, t2 = min(t1, t2), max(t1, t2) # ensure t1 is the entry point, t2 is the exit
            t_min = max(t_min, t1)
            t_max = min(t_max, t2)
            if t_min > t_max:
                return False  # no intersection

    return t_max >= max(0, t_min) # true if intersection exists



### MESH IMPORT AND TRANSFORM ###

def import_mesh(mesh_filename):
    mesh_folder = "objects"
    filepath = f"{mesh_folder}/{mesh_filename}.json"
    with open(filepath, 'r') as file:
        data = json.load(file)

    vertices = data['vertices']
    mesh = data['mesh']
    
    return vertices, mesh


def transform_mesh(vertices, translation, rotation, scale):
    new_vertices = []
    if rotation:
        x_axis = (1,0,0)
        y_axis = (0,1,0)
        z_axis = (0,0,1)

        for vertex in vertices:
            scaled_vertex = multiply_scalar(subtract(vertex, (0,0,0)), scale)
            # no scale for individual axes
            rotated_vertex = rotate_point_around_axis(scaled_vertex, x_axis, math.radians(rotation[0]))
            rotated_vertex = rotate_point_around_axis(rotated_vertex, y_axis, math.radians(rotation[1]))
            rotated_vertex = rotate_point_around_axis(rotated_vertex, z_axis, math.radians(rotation[2]))
            translated_vertex = add(rotated_vertex, translation)
            
            new_vertices.append(translated_vertex)
    else:
        return vertices

    return new_vertices


def rotate_point_around_axis(point, axis, angle):
    axis = normalize(axis)

    parallel_component = multiply_scalar(axis, dot_product(axis, point))
    perpendicular_component = subtract(point, parallel_component)
    cross_product_component = cross(axis, point)

    rotated_point = add(
        add(
            multiply_scalar(perpendicular_component, math.cos(angle)),
            multiply_scalar(cross_product_component, math.sin(angle))
        ),
        parallel_component
    )

    return rotated_point



### CAMERA ###

def get_camera_data(image_width, image_height, yaw, pitch, camera_location, field_of_view, samples, max_bounces):
    camera_data = {}
    # yaw und pitch not implemented yet

    fov_radians = math.radians(field_of_view)
    screen_distance = (image_height / 2) / math.tan(fov_radians / 2)

    screen_center = (
        camera_location[0], 
        camera_location[1] + screen_distance, 
        camera_location[2]
    )

    column_vector = (1, 0, 0)
    row_vector = (0, 0, -1)

    image_start = (
        screen_center[0] - (column_vector[0] * image_width / 2),
        screen_center[1],
        screen_center[2] - (row_vector[2] * image_height / 2)
    )

    camera_data["image_start"] = image_start
    camera_data["column_vector"] = column_vector
    camera_data["row_vector"] = row_vector
    camera_data["camera_ray_origin"] = camera_location
    camera_data["samples"] = samples
    camera_data["max_bounces"] = max_bounces

    return camera_data



### MESH OBJECT CLASS ###

class Object:
    def __init__(self, name, mesh_type, translation, rotation, scale, color, albedo, roughness, emission_strength, is_smooth):
        self.name = name
        self.color = color
        self.emission_color = color
        self.albedo = albedo
        self.roughness = roughness
        self.emission_strength = emission_strength
        self.is_smooth = is_smooth

        vertices, mesh = import_mesh(mesh_type)
        self.vertices = transform_mesh(vertices, translation, rotation, scale)
        self.mesh = mesh
        self.bounding_box = get_bounding_box(self.vertices)
        self.vertex_normals = get_vertex_normals(vertices, mesh)




### VARIABLES ###

image_filename = "render-1" # filename of the rendered image

camera_yaw = 0 # not implemented yet
camera_pitch = 0 # not implemented yet
camera_location = (0,-3,0)
field_of_view = 70

image_width = 4
image_height = 3
image_resolution = 100 # width in pixels
samples = 10
max_bounces = 3

# define objects and scene
# "name, mesh-type, translation, rotation, scale, color, albedo, roughness, emission, smooth-shading"
left_wall = Object("left_wall", "cube", (-4,0,0), (0,0,0), 2, (1,0,0), 1, 1, 0, False)
right_wall = Object("right_wall", "cube", (4,0,0), (0,0,0), 2, (0,0,1), 1, 1, 0, False)
bottom_wall = Object("bottom_wall", "cube", (0,0,-4), (0,0,0), 2, (0,1,0), 1, 1, 0, False)
top_wall = Object("top_wall", "cube", (0,0,4), (0,0,0), 2, (1,1,1), 1, 1, 1, False)
back_wall = Object("back_wall", "cube", (0,4,0), (0,0,0), 2, (1,1,1), 1, 1, 0, False)
monke = Object("monke", "monke", (0,0,0), (0,0,0), 0.75, (1,1,1), 1, 1, 0, True)

scene = {
    "left_wall": left_wall,
    "right_wall": right_wall,
    "bottom_wall": bottom_wall,
    "top_wall": top_wall,
    "back_wall": back_wall,
    "monke": monke
}



### RENDER SCRIPT ###

render_image(image_width, image_height, image_resolution, samples, max_bounces, camera_yaw, camera_pitch, camera_location, field_of_view, image_filename, scene)






