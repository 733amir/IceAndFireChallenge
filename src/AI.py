__author__ = 'AmirHS'

from random import randint


class AI():
    def do_turn(self, world):
        # fill this method, we've presented a stupid AI for example!
        my_nodes = world.my_nodes
        for source in my_nodes:
            # get neighbours
            neighbours = source.neighbours
            if len(neighbours) > 0:
                # select a random neighbour
                destination = neighbours[randint(0, len(neighbours) - 1)]
                # move half of the source's army to the neighbour node
                world.move_army(source, destination, int(source.army_count/2))
