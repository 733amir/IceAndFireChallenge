__author__ = 'AmirHS'

import time


class Graph:
    def __init__(self, nodes):
        self.nodes = nodes
    def __repr__(self): # Added by Geamny
        return "Graph: " + str(self.nodes)
    def __str__(self): # Added by Geamny
        return self.__repr__()


class Node:
    def __init__(self, index):
        self.index = index
        self.owner = -1
        self.army_count = 0
        self.neighbours = []
        # Actually `need` is the distance to the enemy nodes
        self.need = 0 # Added by Geamny

    def set_neighbours(self, neighbours):
        self.neighbours = neighbours

    def set_owner(self, owner):
        self.owner = owner

    def set_army_count(self, army_count):
        self.army_count = army_count

    def set_index(self, index):
        self.index = index

    def __hash__(self): # Added by Geamny
        return self.index

    def __eq__(self, other): # Added by Geamny
        return self.index == other.index

    def __repr__(self): # Added by Geamny
        return "N[I: {}, O: {}, P: {}, N: {}]".format(self.index, self.owner, self.army_count, self.need)

    def __str__(self): # Added by Geamny
        return self.__repr__()


class World:
    def __init__(self, queue):
        self.total_turns = None
        self.turn_start_time = None
        self.turn_timeout = None
        self.escape = None
        self.node_bonus = None
        self.edge_bonus = None
        self.low_army_bound = None
        self.medium_army_bount = None
        self.medium_casualty_coefficient = None
        self.low_casualty_coefficient = None
        self.queue = queue
        self.turn_number = 0
        self.my_id = 0
        self.map = 0
        self.my_nodes = []
        self.opponent_nodes = []
        self.free_nodes = []
        self.nodes = [[], [], []]

    def handle_init_message(self, msg):
        constants = msg[Constants.KEY_ARGS][0]
        self.total_turns = int(constants['turns'])
        self.turn_timeout = int(constants['turnTimeout'])
        self.escape = int(constants['escape'])
        self.node_bonus = int(constants['nodeBonus'])
        self.edge_bonus = int(constants['edgeBonus'])
        self.low_army_bound = int(constants['firstlvl'])
        self.medium_army_bount = int(constants['secondlvl'])
        self.medium_casualty_coefficient = float(constants['lossRate1'])
        self.low_casualty_coefficient = float(constants['lossRate2'])

        self.my_id = int(msg[Constants.KEY_ARGS][1])

        adj_list_init = msg[Constants.KEY_ARGS][2]
        nodes = []

        for i in range(len(adj_list_init)):
            nodes.append(Node(i))

        for i in range(len(adj_list_init)):
            # neighbours_int = adj_list_init[i]
            neighbours = []
            for j in adj_list_init[i]:
                neighbours.append(nodes[j])
            nodes[i].set_neighbours(neighbours)
        graph_diff = msg[Constants.KEY_ARGS][3]
        for i in range(len(graph_diff)):
            node_diff = graph_diff[i]
            node = int(node_diff[0])
            owner = int(node_diff[1])
            army_count = int(node_diff[2])
            nodes[node].set_owner(owner)
            nodes[node].set_army_count(army_count)
        self.map = Graph(nodes)
        self.update_nodes_list()

    def handle_turn_message(self, msg):
        self.turn_start_time = int(round(time.time() * 1000))
        self.turn_number = int(msg[Constants.KEY_ARGS][0])

        graph_diff = msg[Constants.KEY_ARGS][1]
        for i in range(len(graph_diff)):
            node_diff = graph_diff[i]
            node_index = int(node_diff[0])
            self.map.nodes[node_index].set_owner(int(node_diff[1]))
            self.map.nodes[node_index].set_army_count(int(node_diff[2]))
        self.update_nodes_list()

    def update_nodes_list(self):
        # dummies! :))
        nodes_list = [[], [], []]
        for n in self.map.nodes:
            nodes_list[n.owner + 1].append(n)

            # for i in range(len(self.nodes)):
            #    self.nodes[i] = nodes_list[i]
            #print(nodes_list[i], file=sys.stderr)
        self.my_nodes = nodes_list[self.my_id + 1]
        self.opponent_nodes = nodes_list[2 - self.my_id]
        self.free_nodes = nodes_list[0]

    def get_turn_time_passed(self):
        return int(round(time.time() * 1000)) - self.turn_start_time

    def get_turn_remaining_time(self):
        return self.turn_timeout - self.get_turn_time_passed()

    def move_army(self, src, dst, count):
        if isinstance(src, Node):
            self.queue.put(Event('m', [src.index, dst.index, count]))
        else:
            self.queue.put(Event('m', [src, dst, count]))


class Event:
    EVENT = "event"

    def __init__(self, type, args):
        self.type = type
        self.args = args

    def add_arg(self, arg):
        self.args.append(arg)

        # def to_message(self):
        #    return {
        #        'name': Event.EVENT,
        #        'args': [{'type': self.type, 'args': self.args}]
        #    }


class Constants:
    KEY_ARGS = "args"
    KEY_NAME = "name"

    CONFIG_KEY_IP = "ip"
    CONFIG_KEY_PORT = "port"
    CONFIG_KEY_TOKEN = "token"

    MESSAGE_TYPE_EVENT = "event"
    MESSAGE_TYPE_INIT = "init"
    MESSAGE_TYPE_SHUTDOWN = "shutdown"
    MESSAGE_TYPE_TURN = "turn"
