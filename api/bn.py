class Error(Exception):
    """Classe base para exceções neste módulo"""
    pass


class NodeInvalidStateError(Error):
    """
    Exceção para nodes com estados incompatíveis

    expression -- onde o erro ocorreu (o nó)
    message -- explicação do erro
    """
    def __init__(self, expression, message):
        self.expression = expression

        
class WSA:
    def __init__(self):
        pass

    @staticmethod
    def apply(node):
        """
        Gera o restante da tabela a partir das combinações de pais compatíveis.

        node - nó em que será aplicado o WSA
        """

        # tabela que vamos alterar
        npt = node.npt  
        
        # why .99999999...? 
        # .3+.6+.1 == .9999999999999999 not 1
        if sum(npt.child.parents_weight) < .99:
            raise NodeInvalidStateError("At: Applying WSA", "The sum of weights should be 1")

        # Gera a distribuição para cada combinação de pais usando uma soma ponderada
        # entry = distribuição probabilística de uma certa combinação de pais
        # A NPT é composta por n objetos do tipo Entry
        for entry in npt.distributions:
            #  Se a entrada for de uma combinação de pais compatíveis, ignora.
            if not entry.is_compatible: 
                # Dado um nó-filho A e os nós-pais B e C
                # Obtemos a probabilidade para cada estado de A
                # state_of_interest vai ser L, M e finalmente H (caso tenha 3 estados)  
                for state_of_interest in range (0, len(npt.child.state_values)):
                    res = 0  # Vai guardar a probabilidade resultante
                    for current_parent in range (0, len(npt.child.parents)):
                        # Realiza a soma ponderada
                        # 
                        # peso_b = 0.4
                        # peso_c = 0.6
                        #
                        # p(A = l | B = l, C = h) 
                        # = 
                        # peso_b * p(A = l | {Comp(B = l)}) + peso_c * p(A = l | {Comp(C = h)})
                        #
                        # {Comp(B = l)} = [l = 0.7, m = 0.3, h = 0]
                        # {Comp(C = h)} = [l = 0.2, m = 0.4, h = 0.4]
                        #   
                        # Neste caso, o estado l do nó-filho A é igual a soma ponderada da probabilidade que está no estado l nos pais compatíveis com B = l e C = h.
                        # Ou seja, para saber o valor de l para o nó-filho o seguinte cálculo deve ser realizado: .4 * .7 + .6 * .2  
                        res += npt.child.parents_weight[current_parent] * npt.compatible_parents[current_parent][entry.evidences_as_int[current_parent]][state_of_interest]                            
                    entry.state_values[state_of_interest] = res  # Guarda o resultado da soma ponderada


class NPTEntry:
    def __init__(self, evidences, evidences_as_int, state_values, is_compatible = False):
        self.evidences = evidences
        self.evidences_as_int = evidences_as_int
        self.state_values = state_values
        self.is_compatible = is_compatible


class NPT:
    def __init__(self, child):
        self.child = child
        self.compatible_parents = [] 
        self.distributions = []
    
    def to_list(self):
        result = []
        for d in self.distributions:
            result += d.state_values
        return result

    def apply_wsa(self):
        # why .99999999...? 
        # .3+.6+.1 == .9999999999999999 not 1
        if sum(self.child.parents_weight) < .98:
            raise NodeInvalidStateError("At: Applying WSA", "The sum of weights should be 1")

        for entry in self.distributions:
            if not entry.is_compatible:
                for state_of_interest in range (0, len(self.child.state_values)):
                    res = 0
                    for current_parent in range (0, len(self.child.parents)):
                        res += self.child.parents_weight[current_parent] * self.compatible_parents[current_parent][entry.evidences_as_int[current_parent]][state_of_interest]                            
                    entry.state_values[state_of_interest] = res

    def generate_empty_dist(self, evidences, evidences_as_int, empty_dist, parent_index):
        for state in self.child.parents[parent_index].state_names:
            evidences[parent_index] = state
            evidences_as_int[parent_index] = self.child.parents[parent_index].state_names.index(state)
            if parent_index + 1 == len(self.child.parents):
                c_evidences = evidences.copy()
                c_evidences_as_int = evidences_as_int.copy()
                c_empty_dist = empty_dist.copy()
                entry = NPTEntry(c_evidences, c_evidences_as_int, c_empty_dist)
                self.distributions.append(entry)
                if state == self.child.parents[parent_index].state_names[-1]:
                    return 0
            else:
                self.generate_empty_dist(evidences, evidences_as_int, empty_dist, parent_index + 1)

    def init_compatible_parents(self):
        self.compatible_parents = []
        for p in self.child.parents:
            x = []
            for v in p.state_values:
                x.append([])    
            self.compatible_parents.append(x)

    def init_distributions(self):
        self.distributions = []
        n_states = len(self.child.state_values)
        empty_dist = []
        for i in range(0, n_states):
            empty_dist.append(0)
        evidences = []
        evidences_as_int = []
        for i in range(0, len(self.child.parents)):
            evidences.append("")
            evidences_as_int.append(0)
        self.generate_empty_dist(evidences, evidences_as_int, empty_dist, 0)
    
    def init(self):
        self.init_compatible_parents()
        self.init_distributions()

    def get_npt_entry(self, evidences_as_int):
        for entry in self.distributions:
            if entry.evidences_as_int == evidences_as_int:
                return entry

    def add_compatible(self, evidence_as_int, state_values, parent_index):
        entry = self.get_npt_entry(evidence_as_int)
        entry.state_values = state_values
        entry.is_compatible = True
        self.compatible_parents[parent_index][evidence_as_int[parent_index]] = state_values

    def print(self):
        print ("{", end=" ")
        for entry in self.distributions:
            for v in entry.state_values:
                print (v, end=",")
        print("}")


class Node:
    def __init__(self, title, state_names):
        self.title = title
        self.state_names = state_names
        self.state_values = []
        self.parents = []
        self.parents_weight = []
        self.children = []
        self.npt = NPT(self)
        self.evidence = ""
        self.evidence_as_int = -1

        number_of_states = len(self.state_names)
        for state in self.state_names:
            self.state_values.append(1/number_of_states)

        if len(self.parents) != len(self.parents_weight):
            raise NodeInvalidStateError("At: " + self.title + " creation", "Number of parents and number of parent's weight should be equal")
        if len(self.state_names) != len(self.state_values):
            raise NodeInvalidStateError("At: " + self.title + " creation", "State names and state values should have the same length")

    def add_parent(self, parent_node, weight):
        self.parents.append(parent_node)
        self.parents_weight.append(weight)
        parent_node.__add_child(self)
        self.has_changed()

    def __add_child(self, child_node):
        self.children.append(child_node)    

    def print_parents(self):
        print("Parents of {}: ".format(self.title))
        for p in self.parents:
            print(p.title)

    def has_changed(self):
        self.npt.init()

    def __repr__(self):
        return self.title