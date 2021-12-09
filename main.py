
from typing import List, Tuple
from dataclasses import dataclass
import copy

class VectorClock:
  def __init__(self, num_threads: int, values: List[int] = []):
    self.num_threads = num_threads
    if values == []:
      self.vector = [0 for _ in range(num_threads)]
    else:
      assert num_threads == len(values)
      self.vector = values

  def increment(self, i):
    self.vector[i] += 1
    return self

  def __getitem__(self, item):
    return self.vector[item]

  def __setitem__(self, key, value):
    self.vector[key] = value
  
  def __add__(self, other):
    vector = None
    if isinstance(other, VectorClock):
      vector = other.vector
    elif isinstance(other, list):
      vector = other
    else:
      raise ValueError("Invalid types for joining two VectorClocks")

    joined_vec = list(map(max, zip(self.vector, other.vector)))
    return VectorClock(len(joined_vec), joined_vec)

  def __str__(self):
    return str(self.vector)
    
  def __repr__(self):
    return str(self.vector)

@dataclass
class Read:
  thread_id : int
  location: str

@dataclass
class Write:
  thread_id : int
  location: str

@dataclass
class Acquire:
  thread_id : int
  lock: str

@dataclass
class Release:
  thread_id : int
  lock: str

@dataclass
class AtomicLoad:
  thread_id : int
  atomic_obj: str

@dataclass
class AtomicStore:
  thread_id : int
  atomic_obj: str

@dataclass
class AtomicRMW:
  thread_id : int
  atomic_obj: str


def init_vector_clock_state(num_threads: int, locks: List, atomic_objects:List, shared_locations: List) -> Tuple[List, dict, dict, dict]:
  C = [VectorClock(num_threads) for _ in range(num_threads)]
  for i, vec in enumerate(C):
    vec.increment(i)

  L = dict((l, VectorClock(num_threads)) for l in locks + atomic_objects)
  R = dict((loc, VectorClock(num_threads)) for loc in shared_locations)
  W = dict((loc, VectorClock(num_threads)) for loc in shared_locations)

  return C, L, R, W


def run_algorithm(state, program):
  for instr in program:
    if isinstance(instr, Read):
      t = instr.thread_id
      x = instr.location
      # todo check read-write race
      # if not (state[3][x] <= state[0][t]): report_read_write_race(state)
      state[2][x][t] = state[0][t][t]

    elif isinstance(instr, Write):
      t = instr.thread_id
      x = instr.location
      # todo check write-write and write-read race
      state[3][x][t] = state[0][t][t]
    
    elif isinstance(instr, Acquire) or isinstance(instr, AtomicLoad):
      t = instr.thread_id
      m = instr.lock if isinstance(instr, Acquire) else instr.atomic_obj
      state[0][t] = state[0][t] + state[1][m]
      
    elif isinstance(instr, Release) or isinstance(instr, AtomicStore):
      t = instr.thread_id
      m = instr.lock if isinstance(instr, Acquire) else instr.atomic_obj
      state[1][m] = copy.deepcopy(state[0][t])
      state[0][t].increment(t)
    
    elif isinstance(instr, AtomicRMW):
      t = instr.thread_id
      o = instr.atomic_obj
      D = state[0][t] + state[1][o]
      state[1][o] = D
      state[0][t] = copy.deepcopy(D).increment(t)
      
    else:
      raise ValueError("Unknown instruction")

    print(f"{instr} : {state}")


# Algorithm config
threads = 2
locks = []
atomic_objects = ['bit']
shared_locations = ['x']

program = [
  AtomicRMW(0, 'bit'),
  AtomicRMW(1, 'bit'),
  AtomicRMW(1, 'bit'),
  Read(0, 'x'),
  Write(0, 'x'),
  AtomicRMW(1, 'bit'),
  AtomicStore(0, 'bit'),
  AtomicRMW(1, 'bit'),
  Read(1, 'x'),
  Write(1, 'x'),
  AtomicStore(1, 'bit')
]

state = init_vector_clock_state(threads, locks, atomic_objects, shared_locations)
print(state)

run_algorithm(state, program)

