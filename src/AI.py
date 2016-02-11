__author__ = 'AmirHS'

from random import randint, choice

# Defiles the Zone where a dragon can distribute it's power without danger
safe_zone_len = 3

class AI():
    def do_turn(self, world):
        # AI Attributes
        self.world = world
        for source in world.my_nodes:
            all_neighbours_are_mine = True
            for neighbour in source.neighbours:
                if neighbour.owner != world.my_id:
                    world.move_army(source, neighbour, source.army_count)
                    all_neighbours_are_mine = False
                    break
            if all_neighbours_are_mine:
                world.move_army(source, choice(source.neighbours), source.army_count // len(source.neighbours))

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