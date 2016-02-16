__author__ = 'KheiliBaShakhsiati*3'

# List of works we should do in code
# TODO How to and When should we attack? In straight line or all together (categorize all nodes in inner category)?
# TODO Define a way to transfer power of one edge node to another edge node
# TODO Improve set need function, find parameters and constants
# TODO Discover node with more adjacent safe nodes first

from random import randint, choice
from queue import Queue

class AI:
    def __init__(self):
        # Constants
        self.__ATTACKER_NODE_CHOOSE_TURN = 0
        # One attacker to distract enemy, One attacker to kill enemy in the beginning, One attacker to make spread faster
        self.__attacker_node = None



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
            nodes_with_lowest_need = [node] # Actually with highest need for power
            for neighbour in node.neighbours:
                # If `neighbour` have less need than all list, delete all items in list and put
                # that `neighbour` instead. Why comparing just one item in the list? Because all
                # items in the list have the same need.
                if nodes_with_lowest_need[0].need > neighbour.need:
                    nodes_with_lowest_need = [neighbour]
                # If need of `neighbour` is equal to need of items, add `neighbour` to list
                elif nodes_with_lowest_need[0].need == neighbour.need:
                    nodes_with_lowest_need.append(neighbour)
            # Choose one of neighbours of `my_node` with lowest need and send all power to that node
            # TODO Choose which one, don't use random
            # going_to_be_discovered = choice(nodes_with_lowest_need)
            going_to_be_discovered = nodes_with_lowest_need[0]
            for i in nodes_with_lowest_need[1:]:
                if i.army_count < going_to_be_discovered.army_count:
                    going_to_be_discovered = i

            if self.__world.turn_number > self.__world.total_turns // 4:
                self.__world.move_army(node, going_to_be_discovered, node.army_count * 3 // 4)
            else:
                self.__world.move_army(node, going_to_be_discovered, node.army_count)
            # TODO Check indices instead of obejcts (maybe)
            if self.__attacker_node is node:
                self.__attacker_node = going_to_be_discovered


    def __decision_for_edge_nodes(self, edge_nodes=None): # Added by Geamny
        """If the node is safe (no enemy around it) send all power to empty neighbour node with highest need.
If the node is not safe send all power to the enemy that the node can kill."""
        # If no argument for `edge_nodes` not passed, set it to `self.__edge_nodes`
        if edge_nodes is None:
            edge_nodes = self.__edge_nodes
        for node in edge_nodes:
            empty_neighbours = []
            enemy_neighbours = []
            # Check all neighbours and find all empty and enemy nodes
            for neighbour in node.neighbours:
                if neighbour.owner == int(not node.owner):
                    enemy_neighbours.append(neighbour)
                elif neighbour.owner == -1:
                    empty_neighbours.append(neighbour)
            # If there is no enemy around go to an empty node with highest need
            if len(enemy_neighbours) == 0:
                nodes_with_highest_need = []
                for empty_neighbour in empty_neighbours:
                    if len(nodes_with_highest_need) == 0:
                        nodes_with_highest_need = [empty_neighbour]
                    elif nodes_with_highest_need[0].need < empty_neighbour.need:
                        nodes_with_highest_need = [empty_neighbour]
                    elif nodes_with_highest_need[0].need == empty_neighbour.need:
                        nodes_with_highest_need.append(empty_neighbour)
                # Prevent two edge nodes sending their power to one place
                unique_node = [i for i in nodes_with_highest_need if i not in self.__under_discover_nodes]
                # If all edges with highest need are under discover,
                # we select randomly from all empty edges around
                if len(unique_node) == 0:
                    unique_node = [i for i in empty_neighbours if i not in self.__under_discover_nodes and i not in nodes_with_highest_need]
                if len(unique_node) == 0:
                    unique_node = [i for i in empty_neighbours if i not in self.__under_discover_nodes]
                if len(unique_node) == 0:
                    unique_node = nodes_with_highest_need
                # TODO Choose which one, don't use random
                going_to_be_discovered = choice(unique_node)
                self.__under_discover_nodes.append(going_to_be_discovered)

                # BFS to find enemies
                q = Queue()
                q.put(going_to_be_discovered)
                visited = {node}
                found_enemy = False
                while not q.empty():
                    current_node = q.get()
                    if current_node.owner == int(not self.__world.my_id):
                        found_enemy = True
                        break
                    for neighbour in current_node.neighbours:
                        if neighbour not in visited:
                            visited.add(neighbour)
                            q.put(neighbour)

                if not found_enemy: # No enemy found
                    # send 1 power just to occupy nodes
                    self.__world.move_army(node, going_to_be_discovered, 1)
                else:
                    # if going_to_be_discovered.need >= node.need:
                    #     self.__world.move_army(node, going_to_be_discovered, 1)
                    # elif going_to_be_discovered.need < 2:
                    #     self.__world.move_army(node, going_to_be_discovered, node.army_count)
                    # else:
                    #     self.__world.move_army(node, going_to_be_discovered, node.army_count // 2 + 1)
                    self.__world.move_army(node, going_to_be_discovered, node.army_count)

            # Otherwise find most powerful enemy that we can attack and kill (lowest difference power)
            else:
                # TODO Build a list of adjacent enemies and calculate the minimum power needed to win the fight
                # TODO Find most powerful enemy that we can attack and kill (lowest difference power)
                # TODO To attack send 1 + power of enemy node + (all power of enemy adjacent to that enemy node) / 2
                # TODO Choose which one, don't use random
                power_difference_with_enemy_neighbours = [self.__power_difference(node, i) for i in enemy_neighbours]
                max_difference = max(power_difference_with_enemy_neighbours)
                to_attack = enemy_neighbours[power_difference_with_enemy_neighbours.index(max_difference)]
                if max_difference > 0:
                    power = min(node.army_count, int(self.__attacking_power(to_attack)))
                    # print(self.__world.turn_number, node, to_attack, max_difference, power)
                    self.__world.move_army(node, to_attack, power)
                else:
                    node.need -= 1 # stay and wait for backup


    def __choose_attacker(self): # Added by Geamny
        least_need_nodes = []
        for edge_node in self.__edge_nodes:
            if len(least_need_nodes) == 0 or least_need_nodes[0].need == edge_node.need:
                least_need_nodes.append(edge_node)
            elif least_need_nodes[0].need > edge_node.need:
                least_need_nodes = [edge_node]
        return choice(least_need_nodes)


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

        ### # Attacker strategy
        if self.__world.turn_number == self.__ATTACKER_NODE_CHOOSE_TURN:
            self.__attacker_node = self.__choose_attacker()
        elif not self.__attacker_node is None and self.__attacker_node.owner != self.__world.my_id:
            self.__attacker_node = None
        if not self.__attacker_node is None:
            self.__decision_for_inner_nodes([self.__attacker_node])