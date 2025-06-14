from qiskit import transpile
from qiskit_aer import Aer
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.quantum_info import Statevector
# was used for testing in Jupyter
#%matplotlib inline 
from numpy import pi
#from IPython.display import display

#########
### MAIN DRIVER OF ANY ACTION IN THE BATTLE
#########
class QuantumState:

    #initialize with a state |0000> as starting. This state will be modified throughout the whole game
    def __init__(self):
        self.qreg = QuantumRegister(4)
        self.creg = ClassicalRegister(4)
        self.circuit = QuantumCircuit(self.qreg, self.creg)

    def draw_a_circut(self):
        self.circuit.draw(output='mpl')

    #########
    ### NB! gate application to a quantum state evoked as
    ### class_instance.circuit.ry((pi/2), 0), without a need to make a separate function for it (all evoked in game_logic.py)
    #########

    def measurement(self, shots = 1, print_statistics = False):
        self.circuit.measure(self.qreg, self.creg)

        # defining Aer (qasm) as backend
        backend = Aer.get_backend('qasm_simulator')
        
        # providing a circuit to backend
        new_circuit = transpile(self.circuit, backend)
        
        # running circuit
        job = backend.run(new_circuit, shots = shots)
        
        # accessing the results of a job run
        counts = job.result().get_counts(self.circuit)

        if print_statistics == True:
            print(counts)

        result_string = list(counts.keys())[0]
        return result_string

    # any observation in the game is collapsing the state, and any new gate are applied to collapsed state
    def measure_and_collapse(self, shots = 1):
        collapsed_state = self.measurement(shots)

        new_qreg = QuantumRegister(4)
        new_creg = ClassicalRegister(4)
        
        new_circuit = QuantumCircuit(new_qreg, new_creg)

        for i, bit in enumerate(reversed(collapsed_state)):
            if bit == '1':
                new_circuit.x(i)


        #re-assigning state is cruciall to make a collapse, plus be able to use get_statevector() again (as no measurement is done on the new state)
        self.circuit = new_circuit
        self.qreg = new_qreg
        self.creg = new_creg

        #print(collapsed_state)
        return collapsed_state

    def get_statevector(self):
        current_statevector = Statevector.from_instruction(self.circuit) 
        #display(current_statevector.draw(output = 'latex'))
        #print(current_statevector)
        return current_statevector


