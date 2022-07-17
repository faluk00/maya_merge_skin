import math
import time
import maya.cmds as cmds

def calculate_distance(
	position1, position2
):
	distanceX = position1[0] - position2[0]
	distanceY = position1[1] - position2[1]
	distanceZ = position1[2] - position2[2]
		
	distance = math.sqrt(
		(distanceX * distanceX)
		+ (distanceY * distanceY)
		+ (distanceZ * distanceZ)
	)
	return distance

def get_object_skin_data(mesh):
	# get vertex count
	vertex_count = cmds.getAttr(mesh+".vtx[*]")
	# get mesh shape
	mesh_shapes = cmds.listRelatives(
		mesh,
		shapes=True
	)
	# get connected skin cluster
	skin_cluster = cmds.listConnections(
		mesh_shapes[0],
		type="skinCluster"
	)
	# if this mesh isn't bind skin yet then return None
	if not skin_cluster:
		return None
	
	mesh_data = {
		"name": mesh,
		"vertex_count": len(vertex_count),
		"skin_cluster": skin_cluster[0],
	}
	
	vertex = []
	
	for i in range(len(vertex_count)):
		# get vertex name
		vtx = "{0}.vtx[{1}]".format(mesh, str(i))
		# get position
		position = cmds.xform(
			vtx,
			q = True,
			ws = True,
			t = True
		)
		# get vertex skin percent
		skin_percent = cmds.skinPercent(
			skin_cluster[0],
			vtx,
			q = True,
			value = True
		)
		# get influence joints
		influence_joints = cmds.skinPercent(
			skin_cluster[0],
			vtx,
			q = True,
			transform = None
		)
		# match skin data
		skin_data = []
		for n in range(len(skin_percent)):
			skin_data.append([influence_joints[n], skin_percent[n]])
		
		vtx_data = {
			"vertex": vtx,
			"position": position,
			"skin_data": skin_data
		}
		vertex.append(vtx_data)
	
	mesh_data["vertex"] = vertex
	
	return mesh_data

def transfer_skin_percent(
		base_data,
		output_data
	):
	
	# get output mesh vertex count
	vertex_count = output_data.get("vertex_count")
	vertex = output_data.get("vertex")
	
	# get base mesh vertex count
	base_vertex_count = base_data.get("vertex_count")
	base_vertex = base_data.get("vertex")
	
	for i in range(vertex_count):
		# get output position
		output_position = vertex[i].get("position")
		
		all_distance = []
		
		for n in range(base_vertex_count):
			# get base position
			base_position = base_vertex[n].get("position")
			result = calculate_distance(
				output_position,
				base_position
			)
			all_distance.append(result)
		
		nearest_pos = min( all_distance )
		nearest_index = all_distance.index( nearest_pos )
		# check distance before add into list
		# if distance is more than 0.001. Maybe this vertex is for another shapes
		if all_distance[nearest_index] < 0.001:
			try:
				cmds.skinPercent(output_data.get("skin_cluster"),
					vertex[i].get("vertex"),
					transformValue = base_vertex[nearest_index].get("skin_data")
				)
			except:
				pass

# ============================================================

def merge_skin_weights(
	base_meshes, output_mesh
	):
	
	# get output mesh data
	output_data = get_object_skin_data(output_mesh)
	
	for i in range(len(base_meshes)):
		base_data = get_object_skin_data(base_meshes[i])
		transfer_skin_percent(
			base_data,
			output_data
		)
	
	print("Done")

# ============================================================

# base_meshes = cmds.ls(sl=True)
# merge_skin_weights(base_meshes=base_meshes,
# 					output_mesh="hair")