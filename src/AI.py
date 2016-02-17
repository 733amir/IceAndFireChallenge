__author__ = 'KheiliBaShakhsiati*3'

# List of works we should do in code
# TODO How to and When should we attack? In straight line or all together (categorize all nodes in inner category)?
# TODO Define a way to transfer power of one edge node to another edge node
# TODO Improve set need function, find parameters and constants
# TODO Discover node with more adjacent safe nodes first

from random import choice
from queue import Queue

class AI:

    def __init__(self):
        # Constants
        # Global variables
        self.__first_attack = False

    def __attacking_power(self, dest):
        DEST_SUPPORT = 0.125
        average_power = [9, 25, 50]
        return average_power[dest.army_count] + DEST_SUPPORT * sum([average_power[i.army_count] for i in dest.neighbours if i.owner == dest.owner])

    def __power_difference(self, src, dest):
        """
        Calculates power of source node and destination node and returns the difference
        :param src: Our node
        :param dest: Enemy node
        :return: Source power - Destination power
        """
        # Constants
        SRC_SUPPORT = 0.05
        DEST_SUPPORT = 0.125
        average_power = [5, 20, 45]
        # Calculate powers of both sides
        source_power = src.army_count + SRC_SUPPORT * sum([i.army_count for i in src.neighbours if i.owner == self.__world.my_id])
        dest_power = average_power[dest.army_count] + DEST_SUPPORT * sum([average_power[i.army_count] for i in dest.neighbours if i.owner == 1 - self.__world.my_id])
        # Return
        return source_power - dest_power

    def __set_all_need(self): # Added by Geamny
        """Calculate and set `need` attribute of node objects."""
        # Set `need` to `0` for all enemy nodes
        for node in self.__world.opponent_nodes:
            node.need = 0
        # Set need for any node with the shortest distance with enemy nodes
        current_nodes = set(self.__world.opponent_nodes) # Last nodes that their `need` was set
        next_nodes = set() # Nodes that their `need` is going to be set
        all_nodes = set(self.__world.opponent_nodes) # Nodes that their `need` was set
        # Going throw all nodes until there is no node in `current_nodes`
        while len(current_nodes):
            # Finding all adjacent nodes to `current_nodes` that their `need` have not been set
            for node in current_nodes:
                for neighbour in node.neighbours:
                    if neighbour not in all_nodes:
                        next_nodes.add(neighbour)
                        all_nodes.add(neighbour)
            # Finding `need` of `current_nodes` and set it to `next_nodes`
            next_need = current_nodes.pop().need + 1
            for next_node in next_nodes:
                next_node.need = next_need
            # `next_nodes` become `current_nodes`
            current_nodes = next_nodes
            next_nodes = set()

    def __group_nodes(self): # Added by Geamny
        """Group nodes into inner nodes that all of their neighbours are safe and edge nodes that their neighbours
are not all safe."""
        inner, edge = [], []
        for node in self.__world.my_nodes:
            all_neighbours_are_safe = True
            for neighbour in node.neighbours:
                if neighbour.owner != self.__world.my_id:
                    all_neighbours_are_safe = False
                    break
            if all_neighbours_are_safe:
                inner.append(node)
            else:
                edge.append(node)
        return (inner, edge)

    def __decision_for_inner_nodes(self, inner_nodes=None): # Added by Geamny
        """Sending all the power of a node to its most desperate neighbour."""
        if inner_nodes is None:
            inner_nodes = self.__inner_nodes
        for node in inner_nodes:
            _ = sorted(node.neighbours, key=lambda i: i.need)
            __ = sorted([i for i in _ if i.need == _[0].need], key=lambda i: i.army_count)
            nodes_with_lowest_need_and_power = [i for i in __ if i.army_count == __[0].army_count]
            going_to_be_discovered = choice(nodes_with_lowest_need_and_power)

            if self.__first_attack:
                self.__world.move_army(node, going_to_be_discovered, node.army_count * 9 // 10)
            else:
                self.__world.move_army(node, going_to_be_discovered, node.army_count)

    def __decision_for_edge_nodes(self, edge_nodes=None):

        # Default value of `edge_nodes` is `self.__edge_nodes`
        if edge_nodes is None:
            edge_nodes = self.__edge_nodes

        # Sort edge nodes with count of empty or enemy neighbours
        edge_nodes.sort(key=lambda i: len([j for j in i.neighbours if j.owner != self.__world.my_id]))

        # Decision for each edge node
        for edge_node in edge_nodes:

            # Finding empty or enemy neighbours of `edge_node`
            empty_neighbours = [i for i in edge_node.neighbours if i.owner == -1]
            enemy_neighbours = [i for i in edge_node.neighbours if i.owner == 1 - self.__world.my_id]

            if len(enemy_neighbours): # There is enemy, Attack
                self.__first_attack = True

                self.__world.move_army(edge_node, choice(enemy_neighbours), edge_node.army_count)

            else: # No enemy, Discover
                # TODO Don't send all power for discovery
                # TODO Don't send all power to worthless node (node with no enemy at the end of it's path)
                # Delete under discover nodes from empty neighbours list
                empty_neighbours_not_under_discover = [i for i in empty_neighbours if i not in self.__under_discover_nodes]

                # Sort empty neighbours by count of safe neighbours around it
                more_neighbours = sorted(empty_neighbours_not_under_discover, key=lambda i: len([j for j in i.neighbours if j.owner == self.__world.my_id or j in self.__under_discover_nodes]), reverse=True)

                if not more_neighbours: # All neighbours under discover
                    empty_neighbours_sorted_by_need = sorted(empty_neighbours, key=lambda i: i.need)
                    self.__under_discover_nodes.append(empty_neighbours_sorted_by_need[0])
                    self.__world.move_army(edge_node, empty_neighbours_sorted_by_need[0], edge_node.army_count)

                else: # Not all neighbours under discover
                    self.__under_discover_nodes.append(more_neighbours[0])
                    self.__world.move_army(edge_node, more_neighbours[0], edge_node.army_count)

    def __enemy_is_there(self, node):
        visited = {node}
        q = Queue()
        q.put(node)
        found_enemy = False
        while not q.empty():
            cur_node = q.get()
            if cur_node.owner == 1 - self.__world.my_id: # enemy found
                found_enemy = True
                break
            for next_node in cur_node.neighbours:
                if next_node not in visited:
                    q.put(next_node)
                    visited.add(next_node)
        return found_enemy

    def do_turn(self, world):
        # Set attributes of AI class
        self.__world = world
        self.__inner_nodes = []
        self.__edge_nodes = []
        self.__under_discover_nodes = [] # To prevent edge nodes sending powers to 1 place.
        self.__under_attack_nodes = [] # To decide for best attack

        ## Function calls for initializing
        self.__set_all_need()
        self.__inner_nodes, self.__edge_nodes = self.__group_nodes()

        ### Decision making
        self.__decision_for_edge_nodes()
        self.__decision_for_inner_nodes()