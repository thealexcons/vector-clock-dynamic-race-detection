from vector_clock import init_vector_clock_state, run_algorithm
from instructions import *

threads = 3
locks = []
atomic_objects = ['f']
shared_locations = ['d1', 'd2']

program = [
  Write(0, 'd1'),
  AtomicStore(0, 'f'),
  Write(1, 'd2'),
  AtomicStore(1, 'f'),
  AtomicLoad(2, 'f'),
  Read(2, 'd1')
]

state = init_vector_clock_state(threads, locks, atomic_objects, shared_locations)
print(state)

final_state, race = run_algorithm(state, program, verbose=True)
