__author__ = 'AmirHS'

# List of works we should do in code
# TODO Just attack if the map is small (categorize all nodes in inner category)
# TODO How to and When should we attack? In straight line or all together (categorize all nodes in inner category)?
# TODO Define a way to transfer power of one edge node to another edge node
# TODO If at the of path that we are going to discover, is no enemy, don't send all power, just send 1 power.
# TODO Build a list of adjacent enemies and calculate the minimum power needed to win the fight

from random import randint, choice

class AI():
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

    def __decision_for_inner_nodes(self, inner_nodes): # Added by Geamny
        """Sending all the power of a node to its most desperate neighbour."""
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
            self.__world.move_army(node, choice(nodes_with_lowest_need), node.army_count)

    def __decision_for_edge_nodes(self, edge_nodes): # Added by Geamny
        """If the node is safe (no enemy around it) send all power to empty neighbour node with highest need.
If the node is not safe send all power to the enemy that the node can kill."""
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
                unique_node = [i for i in nodes_with_highest_need if i not in self.__under_dicover_nodes]
                # If all edges with highest need are under discover,
                # we select randomly from all empty edges around
                if len(unique_node) == 0:
                    unique_node = [i for i in empty_neighbours if i not in self.__under_dicover_nodes and i not in nodes_with_highest_need]
                if len(unique_node) == 0:
                    unique_node = [i for i in empty_neighbours if i not in self.__under_dicover_nodes]
                if len(unique_node) == 0:
                    unique_node = nodes_with_highest_need
                # TODO Choose which one, don't use random
                going_to_be_discovered = choice(unique_node)
                self.__under_dicover_nodes.append(going_to_be_discovered)
                self.__world.move_army(node, going_to_be_discovered, node.army_count)
            # Otherwise find most powerful enemy that we can attack and kill (lowest difference power)
            else:
                # TODO Find most powerful enemy that we can attack and kill (lowest difference power)
                # TODO To attack send 1 + power of enemy node + (all power of enemy adjacent to that enemy node) / 2
                # TODO Choose which one, don't use random
                self.__world.move_army(node, choice(enemy_neighbours), node.army_count)

    def do_turn(self, world):
        # Set attributes of AI class
        self.__world = world
        self.__inner_nodes = []
        self.__edge_nodes = []
        self.__under_dicover_nodes = [] # To prevent edge nodes sending powers to 1 place.

        ## Function calls for initializing
        self.__set_all_need()
        self.__inner_nodes, self.__edge_nodes = self.__group_nodes()

        ### Decision making
        self.__decision_for_inner_nodes(self.__inner_nodes)
        self.__decision_for_edge_nodes(self.__edge_nodes)
