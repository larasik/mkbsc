import networkx as nx
from networkx.drawing.nx_pydot          import to_pydot
from subprocess import call

class State:
    """Represents a game state, with separate knowledge for each player

    The knowledge is stored as a tuple, and can be accessed by State().knowledges[playerindex]
    or simply State()[playerindex]. The players are zero-indexed. In the base game, the states'
    knowledge should be an integer or short string, the same for all players. This case is
    treated separately and the tuple State().knowledges is a singleton. When applying the KBSC, the new
    states' knowledge are sets of states from the previous iteration. For example, after two
    iterations the states' knowledge are sets of states, whose knowledge are sets of states,
    whose knowledge could be integers."""
    
    def __init__(self, *knowledges):
        """Create a new state

        ex. s = State(1)"""
        
        self.knowledges = tuple(knowledges)
        
    def __getitem__(self, index):
        """Get the knowledge of the specified player

        Will work as expected even if knowledges is a singleton"""
        
        if len(self.knowledges) == 1:
            return self.knowledges[0]
        else:
            return self.knowledges[index]
            
    def __str__(self):
        return repr(self)
        
    compact_representation = False
    def __repr__(self):
        """Return a compact string representation of the knowledge"""

        #if we are writing to a dot file we only need a unique string, not the full representation
        if State.compact_representation:
            return str(id(self))
        
#        return "s" + str(self.knowledges)
        if len(self.knowledges) == 1:
            if type(self.knowledges[0]) is frozenset:
                return str(set(self.knowledges[0]))
            else:
                return str(self.knowledges[0])
        else:
            return str(tuple(set(self.knowledges[i]) for i in range(len(self.knowledges))))
    
    __indent = "\t"
    def epistemic_verbose(self, level=0):
        """Return a verbose representation of the knowledge. Not recommended for overly iterated games."""
        if len(self.knowledges) == 1:
            return State.__indent * level + "We are in " + str(self.knowledges[0]) + "\n"
        
        s = ""
        for player, knowledge in enumerate(self.knowledges):
            s += State.__indent * level + "Player " + str(player) + " knows:\n"
            s += (State.__indent * (level + 1) + "or\n").join([state.epistemic(level + 1) for state in knowledge])
            
        return s
    
    def epistemic_tree(self, level=0, numPlayers=2, player=):
        """This function makes a tree"""

        # TODO if we do this function recursively we will have to make a separate mfunction where we create the graph
        G = nx.Graph()
        self.parse_knowledge(level, numPlayers, player, G)

    def parse_knowledge(self, level, numplayers, player, G):
        indexedKnowledges = tuple(self.knowledges[player])
        if len(indexedKnowledges[0].knowledges) == 1:
            tree_node = "{" + ", ".join([str(state.knowledges[0]) for state in indexedKnowledges]) + "}"
            print(tree_node)
            G.add_node(str(id(self)), label=tree_node)
            # TODO we might need to return the node here so we can connect an edge to it

        '''
        for firstState in self.knowledges[0]:
            #print(firstState)
            
            initial_state = None

            # TODO: Make less bad
            for secondState in firstState:
                initial_state = "{" + ", ".join([str(state.knowledges[0]) for state in secondState]) + "}"
                G.add_node(initial_state, label=initial_state)
                break

            playerCounter = 0

            for secondState in firstState:
                if not playerCounter % numPlayers == 0:
                    knowledge = "{" + ", ".join([str(state.knowledges[0]) for state in secondState]) + "}"
                    G.add_node(knowledge, label=knowledge)
                    G.add_edge(initial_state, knowledge)
                    G[initial_state][knowledge]["label"] = 1
                    
                playerCounter += 1
        #print(G.nodes())
        #print(G.edges())

        arr = to_pydot(G).to_string()

        with open("pictures/hack.dot", "w") as dotfile:
            dotfile.write(arr)

        call(["dot", "-Tpng", "pictures/hack.dot", "-o", "pictures/hack.png"])
        '''


    def epistemic_nice(self, level=0):
        """Return a compact but still quite readable representation of the knowledge"""
        def __wrap(state, l):
            if len(state.knowledges) > 1:
                print("Wrap")
                return "(" + state.epistemic_nice(l + 1) + ")"
            else:
                print("Wrap : " + str(state.knowledges[0]))
                return str(state.knowledges[0])
        # Outer level of player knowledge
        if level == 0:
            if len(self.knowledges) > 1:
                # More than one epistemic level
                print("Level = 0 : len > 1")
                return "\n".join(["{" + ", ".join([state.epistemic_nice(level + 1) for state in knowledge]) + "}" for knowledge in self.knowledges])
            else:
                # One epistemic level
                if type(self.knowledges[0]) is frozenset:
                    # ??
                    print("Level = 0 : len <= 1 : is frozenset")
                    return "{" + ", ".join([state.epistemic_nice(level + 1) for state in self.knowledges[0]]) + "}"
                else:
                    # Only used when one epistemic level
                    print("Level = 0 : len <= 1 : not frozenset")
                    print("Level = 0 : " + str(self.knowledges[0]))
                    return str(self.knowledges[0])
        # Inner level
        else:
            if len(self.knowledges) > 1:
                # Used when more than two epistemic levels in total
                print("Level > 0  : len > 1")
                return "-".join(["".join([__wrap(state, level) for state in knowledge]) for knowledge in self.knowledges])
            else:
                if type(self.knowledges[0]) is frozenset:
                    # ??
                    print("Level > 0 : len <= 1 : is frozenset")
                    return "{" + ", ".join([state.epistemic_nice(level + 1) for state in self.knowledges[0]]) + "}"
                else:
                    # Only used when two epistemic levels
                    print("Level > 0 : len <= 1 : not frozenset")
                    print("Level > 0 : " + str(self.knowledges[0]))
                    return str(self.knowledges[0])
                
    def epistemic_isocheck(self):
        """Return the most compact representation, only containing which states in the base game are possible in this state"""
        return ", ".join([str(state.knowledges[0]) for state in self.consistent_base()])

    def consistent_base(self):
        """Return the states in the base game that are possible in this state

        This assumes that the knowledges in the base game are singletons"""
        def _pick(_set):
            for x in _set:
                return x
            raise None
        
        states = [self]
        if len(self.knowledges) == 1 and type(self.knowledges[0]) is frozenset:
            states = {self.knowledges[0]}
        
        while len(_pick(states).knowledges) > 1:
            states = set.intersection(*[set.intersection(*[set(state[player]) for player in range(len(self.knowledges))]) for state in states])
        
        return states
    
    #workaround to make sure the networkx isomorphism check works
    orderable = False
    def __gt__(self, other):
        assert State.orderable
        return id(self) > id(other)
    def __lt__(self, other):
        assert State.orderable
        return id(self) < id(other)
