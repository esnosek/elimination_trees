import time
import mesh_structure.Mesh as Mesh
import numpy as np
import algorithms.DivisionsTree as DivisionsTree
import algorithms.OptimalEliminationTries as OptimalEliminationTries
import tree_view.meshDrawer as md
import argparse
import sys

def create_mesh(fileName):
    mesh_table = load_file(fileName)
    mesh_table = add_points(mesh_table)
    return create_mesh_structure(mesh_table)


def find_all_divisions_tree(mesh):
    dt = DivisionsTree.DivisionsTree(mesh)
    dt.create_all_divisions_tree()
    return dt


def create_optimal_elimination_tries(root_contour_node):
    oet = OptimalEliminationTries.OptimalEliminationTries(root_contour_node)
    oet.create_optimal_elimination_tries()
    return oet.optimal_tree_contour_node


def load_file(path):
    return np.loadtxt(path, dtype='int', skiprows=2)


def add_points(mesh_table):
    mesh_table = np.append(mesh_table, mesh_table[:, [2, 5]], 1)
    mesh_table = np.append(mesh_table, mesh_table[:, [4, 3]], 1)
    return mesh_table[:, np.array([0, 1, 2, 3, 6, 7, 4, 5, 8, 9])]


def create_mesh_structure(mesh_table):
    mesh = Mesh.Mesh()
    for row in mesh_table:
        v1 = mesh.create_vertex(row[2], row[3])
        v2 = mesh.create_vertex(row[4], row[5])
        v3 = mesh.create_vertex(row[6], row[7])
        v4 = mesh.create_vertex(row[8], row[9])
        mesh.create_edge(v1, v2)
        mesh.create_edge(v1, v4)
        mesh.create_edge(v2, v3)
        mesh.create_edge(v4, v3)
    mesh.create_mesh_contour()
    return mesh
    
def app_start():
    
    try:
        file = sys.argv[1]

        start_time = int(round(time.time() * 100000))
        
        mesh = create_mesh(file)
        root_contour_node = find_all_divisions_tree(mesh).root_contour_node
        optimal_tree_contour_node = create_optimal_elimination_tries(root_contour_node)
    except:
        sys.exit('file error')
        
    print("""all contours: %d
unique contours hash keys:%d
all elimination trees:%d
optimal trees:%d""" % 
            (
            mesh.get_all_contour_nodes_count(),
            mesh.get_unique_hash_key_count(),
            root_contour_node.all_divisions_tree_counter,
            optimal_tree_contour_node.optimal_tree_counter
            )
        )

    md.clear_tmp()
    tree_string = md.create_tree_string(mesh, optimal_tree_contour_node)
    tree_string += ';'
    md.draw_tree(tree_string)
    
    end_time = int(round(time.time() * 100000))
    #print('czas: ' + str((end_time - start_time)/100000) + 's')

app_start()

# 'mesh_tests/vertex'

