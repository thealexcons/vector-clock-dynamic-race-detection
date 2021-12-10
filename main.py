
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

  def __le__(self, other):
    return all(map(lambda p: p[0] <= p[1], zip(self.vector, other.vector)))
  
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


class VectorClockState:
  def __init__(self, C, L, R, W):
    self.state = (C, L, R, W)
  
  def __getitem__(self, item):
    return self.state[item]

  def __setitem__(self, key, value):
    self.state[key] = value

  def __str__(self):
    return str(self.state)
  

def init_vector_clock_state(num_threads: int, locks: List, atomic_objects:List, shared_locations: List) -> VectorClockState:
  C = [VectorClock(num_threads) for _ in range(num_threads)]
  for i, vec in enumerate(C):
    vec.increment(i)

  L = dict((l, VectorClock(num_threads)) for l in locks + atomic_objects)
  R = dict((loc, VectorClock(num_threads)) for loc in shared_locations)
  W = dict((loc, VectorClock(num_threads)) for loc in shared_locations)

  return VectorClockState(C, L, R, W)

def find_racy_thread(location_vec, clock_vec) -> int:
  for i in range(len(location_vec.vector)):
    if location_vec.vector[i] > clock_vec.vector[i]:
      return i

  assert "Could not find racy thread u"

def report_write_read_race(u, t, x):
  print(f"WriteReadRace({u}, {t}, {x})")

def report_write_write_race(u, t, x):
  print(f"WriteWriteRace({u}, {t}, {x})")

def report_read_write_race(u, t, x):
  print(f"ReadWriteRace({u}, {t}, {x})")

def run_algorithm(state, program):
  C = 0
  L = 1
  R = 2
  W = 3
  for instr in program:
    if isinstance(instr, Read):
      t = instr.thread_id
      x = instr.location
      # todo check write-read race
      if not (state[W][x] <= state[C][t]):
        u = find_racy_thread(state[W][x], state[C][t])
        report_write_read_race(u, t, x)
        break
        
      state[R][x][t] = state[C][t][t]

    elif isinstance(instr, Write):
      t = instr.thread_id
      x = instr.location
      # Check write-write and write-read race
      if not (state[W][x] <= state[C][t]):
        u = find_racy_thread(state[W][x], state[C][t])
        report_write_write_race(u, t, x)
        break
      elif not (state[R][x] <= state[C][t]): 
        u = find_racy_thread(state[R][x], state[C][t])
        report_read_write_race(u, t, x)
        break
        
      state[W][x][t] = state[C][t][t]
    
    elif isinstance(instr, Acquire) or isinstance(instr, AtomicLoad):
      t = instr.thread_id
      m = instr.lock if isinstance(instr, Acquire) else instr.atomic_obj
      state[C][t] = state[C][t] + state[L][m]
      
    elif isinstance(instr, Release) or isinstance(instr, AtomicStore):
      t = instr.thread_id
      m = instr.lock if isinstance(instr, Acquire) else instr.atomic_obj
      state[L][m] = copy.deepcopy(state[C][t])
      state[C][t].increment(t)
    
    elif isinstance(instr, AtomicRMW):
      t = instr.thread_id
      o = instr.atomic_obj
      D = state[C][t] + state[L][o]
      state[L][o] = D
      state[C][t] = copy.deepcopy(D).increment(t)
      
    else:
      raise ValueError("Unknown instruction")

    print(f"{instr} : {state}")


# Algorithm config
# threads = 2
# locks = []
# atomic_objects = ['bit']
# shared_locations = ['x']

# program = [
#   AtomicRMW(0, 'bit'),
#   AtomicRMW(1, 'bit'),
#   AtomicRMW(1, 'bit'),
#   Read(0, 'x'),
#   Write(0, 'x'),
#   AtomicRMW(1, 'bit'),
#   AtomicStore(0, 'bit'),
#   AtomicRMW(1, 'bit'),
#   Read(1, 'x'),
#   Write(1, 'x'),
#   AtomicStore(1, 'bit')
# ]

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

run_algorithm(state, program)

