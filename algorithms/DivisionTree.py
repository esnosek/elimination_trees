# -*- coding: utf-8 -*-
import algorithms.CuttingUtils as cu
import numpy as np
from test import create_mesh
import bintrees as bt
import unittest
import tree_view.meshDrawer as md

all_countours = bt.FastRBTree()
optimal_tree_nodes = bt.FastRBTree()
counter = 0
all_contour_counter = 1
ilosc_rozwiazan = 1
root = None
root_contour_node = None
global_mesh = None
node_id = 0
division_counter = 0
optimal_tree_counter = 1


def start(mesh):
    global all_countours
    global root
    global root_contour_node
    global global_mesh
    global_mesh = mesh
    root_contour_node = ContourNode(mesh.contour, None)
    all_countours[root_contour_node.contour.hash_key] = np.array([root_contour_node])
    root_contour_node.generate_all_children_division_nodes()
    root_contour_node.set_lowest_cost()
    root = create_optimal_tree(root_contour_node)
    print("wszystkie podziały ", division_counter)
    print("optymalne drzewa ", optimal_tree_counter)
    #md.draw_leaf(mesh, root.children[0].child2.children[0], 'h')
    
#    i = 1
#        file_name = "podzial" + str(i)
#        i += 1
#        md.draw_contour_with_interior_and_slice_from_division_node(mesh, d, file_name)

def create_optimal_tree(contour_node):
    global optimal_tree_counter
    if contour_node.is_atomic_square(contour_node.contour):
        return TreeLeaf(contour_node.contour, contour_node.lowest_cost)
    lowest_cost_divisions = contour_node.get_divisions_with_lowest_cost()
    tree_node = TreeNode(contour_node.lowest_cost)
    optimal_tree_counter = optimal_tree_counter + len(lowest_cost_divisions)-1
    for division in lowest_cost_divisions:
        child_1 = create_optimal_tree(division.contour_node_1)
        child_2 = create_optimal_tree(division.contour_node_2)
        tree_node.add_child(child_1, child_2, contour_node.contour, division.path)
    return tree_node

def create_tree(parent_contour_node, parent_division_node):
    global all_countours
    global all_contour_counter
    
    if is_in_all_contours(parent_contour_node):
        existing_contour_node = get_from_all_contours(parent_contour_node)
        existing_contour_node.add_parent_division(parent_division_node)
        return existing_contour_node.lowest_cost
    else:
        all_contour_counter += 1
        perent_hash = parent_contour_node.contour.hash_key
        if perent_hash in all_countours:
            all_countours[perent_hash] = np.append(all_countours[perent_hash], parent_contour_node)
        else:
            all_countours[perent_hash] = np.array([parent_contour_node])
        return parent_contour_node.generate_all_children_division_nodes()

def is_in_optimal_tree_nodes(contour_node):
    contour_hash_key = contour_node.contour.hash_key
    if contour_hash_key in optimal_tree_nodes:
        for tree_node in optimal_tree_nodes[contour_hash_key]:
            if tree_node.contour == contour_node.contour:
                return True
    return False
    
def get_from_optimal_tree_nodes(contour_node):
    contour_hash_key = contour_node.contour.hash_key
    if contour_hash_key in optimal_tree_nodes:
        for tree_node in optimal_tree_nodes[contour_hash_key]:
            if tree_node.contour == contour_node.contour:
                return tree_node
    return False
         
def is_in_all_contours(contour_node):
    contour_hash_key = contour_node.contour.hash_key
    if contour_hash_key in all_countours:
        for c in all_countours[contour_hash_key]:
            if c == contour_node:
                return True
    return False
    
def get_from_all_contours(contour_node):
    contour_hash_key = contour_node.contour.hash_key
    if contour_hash_key in all_countours:
        for c in all_countours[contour_hash_key]:
            if c == contour_node:
                return c
    return False
    
def create_tree_string(mesh, node):
    global node_id

    if type(node) is TreeNode:
        node_id += 1
        my_id = node_id
        md.draw_contour_with_interior_and_slice(mesh, node.children[0], 'tmp/%s.png' % node_id, node.cost)
        c1_str = create_tree_string(mesh, node.children[0].child1)
        c2_str = create_tree_string(mesh, node.children[0].child2)
        return '(' + c1_str + ',' + c2_str + ')' + str(my_id)
    else:
        node_id += 1
        md.draw_leaf(mesh, node, 'tmp/%s.png' % node_id, node.cost)
        return str(node_id)

def clear_tmp():
    import os
    folder = 'tmp'
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except e:
            print(e)

class TreeNode:
    
    def __init__(self, cost):
        self.children = []
        self.cost = cost
        
    def add_child(self, child1, child2, contour, path):
        self.children.append(TreeNodeChild(child1, child2, contour, path))

class TreeNodeChild:
    def __init__(self, child1, child2, contour, path):
        self.contour = contour
        self.child1 = child1
        self.child2 = child2
        self.path = path
        
class TreeLeaf:

    def __init__(self, contour, cost):
        self.contour = contour
        self.cost = cost
    
class ContourNode:

    def __init__(self, contour, parent_division_node):
        self.contour = contour
        self.children_division_nodes = np.empty(dtype=object, shape=0)
        self.parent_division_nodes = np.empty(dtype=object, shape=0)
        self.add_parent_division(parent_division_node)
        self.lowest_cost = None

    def __eq__(self, other):
        return self.contour == other.contour

    def add_parent_division(self, parent_division_node):
        self.parent_division_nodes = np.append(self.parent_division_nodes, parent_division_node)

    def add_children_division(self, children_division_node):
        self.children_division_nodes = np.append(self.children_division_nodes, children_division_node)

    def get_divisions_with_lowest_cost(self):
        lowest_divisions = np.empty(dtype=object, shape=0)
        for division in self.children_division_nodes:
            if self.lowest_cost == division.cost:
                lowest_divisions = np.append(lowest_divisions, division)
        return lowest_divisions
        
    def set_lowest_cost(self):
        costs = []
        for division in self.children_division_nodes:
            costs.append(division.cost)
        self.lowest_cost = min(costs)
        
    def get_cost(self):
        a = 1
        b = 9
        return self.cost(a, b)

    def generate_all_children_division_nodes(self):
        global division_counter
        lowest_cost = 9999999
        
        if not self.is_atomic_square(self.contour):
            possible_cuts = cu.get_possible_cuts(self.contour)
            for path in possible_cuts:
                division_counter += 1
                new_division_node = DivisionNode(path, self)
                self.add_children_division(new_division_node)
                cost_of_child_1 = create_tree(new_division_node.contour_node_1, new_division_node)
                cost_of_child_2 = create_tree(new_division_node.contour_node_2, new_division_node)
                new_division_node.contour_node_1.lowest_cost = cost_of_child_1
                new_division_node.contour_node_2.lowest_cost = cost_of_child_2
                zlaczenia_koszt = self.__dej_mi_zlaczenia_koszt(new_division_node)
                total_cost = cost_of_child_1 + cost_of_child_2 + zlaczenia_koszt
                new_division_node.cost = total_cost
                if total_cost < lowest_cost:
                    lowest_cost = total_cost
                
            return lowest_cost
        else:
            return self.get_cost()

    def __dej_mi_zlaczenia_koszt(self, division_node):
        a = 2*len(division_node.path) - 3
        b = 2 * len(division_node.parent_contour_node.contour) + a
        cost = self.cost(a, b)
        return cost
        
    def cost(self, a, b):
        return a * (6*b**2 - 6*a*b + 6*b + 2*a**2 - 3*a + 1) / 6

    def is_atomic_square(self, parent_contour):
        if len(parent_contour) == 4:
            return True
        else:
            return False
        for v in parent_contour.contour:
            index_curr_v = np.where(parent_contour.contour == v)[0][0]
            prev_v = parent_contour[index_curr_v - 1]
            next_v = parent_contour[index_curr_v + 1]
            inside_directions = parent_contour.get_inside_directions(prev_v, v, next_v)
            existing_directions = v.get_existing_edge_directions()
            possible_directions = list(set(inside_directions).intersection(existing_directions))
            if len(possible_directions) > 0:
                return False
        return True


class DivisionNode:

    def __init__(self, path, parent_contour_node):
        self.path = path
        self.parent_contour_node = parent_contour_node
        new_contour1, new_contour2 = parent_contour_node.contour.slice_contour(path)
        
        self.contour_node_1 = ContourNode(new_contour1, self)
        if is_in_all_contours(self.contour_node_1):
            existing_contour_node = get_from_all_contours(self.contour_node_1)
            self.contour_node_1 = existing_contour_node
                
        self.contour_node_2 = ContourNode(new_contour2, self)
        if is_in_all_contours(self.contour_node_2):
            existing_contour_node = get_from_all_contours(self.contour_node_2)
            self.contour_node_2 = existing_contour_node
        
        self.cost = None

class DivisionTreeTests(unittest.TestCase):

    def test_cut(self):
        global all_countours
        global counter
        mesh = create_mesh()
        start(mesh)
        print("ilość unikalnych hashcodów: ", len(all_countours))
        print("ilosc wszystkich kontorów: ", all_contour_counter)
        print(ilosc_rozwiazan)
        
        clear_tmp()        
        tree_string = create_tree_string(mesh, root)
        tree_string += ';'
        md.draw_tree(tree_string)

if __name__ == '__main__':
    unittest.main()
