__author__ = 'AmirHS'

from random import randint, choice

# Defiles the Zone where a dragon can distribute it's power without danger
safe_zone_len = 3

class AI():
    def __set_all_need(self): # Added by Geamny
        """Calculate and set `need` attribute of node objects"""
        # Set `need` to `0` for all enemy nodes
        for node in self.world.opponent_nodes:
            node.need = 0
        # Set need for any node with the shortest distance with enemy nodes
        current_nodes = set(self.world.opponent_nodes) # Last nodes that their `need` was set
        next_nodes = set() # Nodes that their `need` is going to be set
        all_nodes = set(self.world.opponent_nodes) # Nodes that their `need` was set
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


    def do_turn(self, world):
        # Set attributes of AI class
        self.world = world

        # Function calls for initializing
        self.__set_all_need()

        ### Decision making
        ## Before the concept of need
        # for source in world.my_nodes:
        #     all_neighbours_are_mine = True
        #     for neighbour in source.neighbours:
        #         if neighbour.owner != world.my_id:
        #             world.move_army(source, neighbour, source.army_count)
        #             all_neighbours_are_mine = False
        #             break
        #     if all_neighbours_are_mine:
        #         world.move_army(source, choice(source.neighbours), source.army_count // len(source.neighbours))
        ## After concept of need
        for my_node in world.my_nodes:
            nodes_with_lowest_need = [my_node] # Actually with highest need
            for neighbour in my_node.neighbours:
                # If `neighbour` have less need than all list, delete all items in list and put
                # that `neighbour` instead. Why comparing just one item in the list? Because all
                # items in the list have the same need.
                if nodes_with_lowest_need[0].need > neighbour.need:
                    nodes_with_lowest_need = [neighbour]
                # If need of `neighbour` is equal to need of items, add `neighbour` to list
                elif nodes_with_lowest_need[0].need == neighbour.need:
                    nodes_with_lowest_need.append(neighbour)

            # Priority of sending power to node: empty, enemy, our
            # Three below list are generated from `nodes_with_lowest_need`
            empty_nodes = [node for node in nodes_with_lowest_need if node.owner == -1]
            enemy_nodes = [node for node in nodes_with_lowest_need if node.owner == int(not self.world.my_id)]
            our_nodes = [node for node in nodes_with_lowest_need if node.owner == self.world.my_id]
            # Define `nodes_to_send_power` with the highest priority nodes if there is any node in that list
            nodes_to_send_power = our_nodes
            if len(empty_nodes):
                nodes_to_send_power = empty_nodes
            elif len(enemy_nodes):
                nodes_to_send_power = enemy_nodes
            # Choose one of neighbours of `my_node` with lowest need and highest priority to send all power
            self.world.move_army(my_node, choice(nodes_to_send_power), my_node.army_count)

    def is_safe(self, node):
        neighbours = node.neighbours
        neighbours_of_neighbours = []
        is_there_enemy = False
        for i in range(safe_zone_len):
            for neighbour in neighbours:
                if neighbour.owner == int(not bool(self.world.my_id)):
                    is_there_enemy = True
                    break
                neighbours_of_neighbours.append(neighbour)
            if is_there_enemy:
                break
            else:
                neighbours = neighbours_of_neighbours
                neighbours_of_neighbours = []
        return False if is_there_enemy else True