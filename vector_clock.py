from typing import List, Tuple, Union, Optional
import copy
from instructions import *
from dataclasses import dataclass


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

    joined_vec = list(map(max, zip(self.vector, vector)))
    return VectorClock(len(joined_vec), joined_vec)

  def __le__(self, other):
    return all(map(lambda p: p[0] <= p[1], zip(self.vector, other.vector)))
  
  def __str__(self):
    return str(self.vector)
    
  def __repr__(self):
    return str(self.vector)



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

@dataclass
class WriteReadRace:
  u : int
  t: int
  x: str

  def __str__(self) -> str:
    return f"WriteReadRace({self.u}, {self.t}, {self.x})"

@dataclass
class ReadWriteRace:
  u : int
  t: int
  x: str

  def __str__(self) -> str:
    return f"ReadWriteRace({self.u}, {self.t}, {self.x})"

@dataclass
class WriteWriteRace:
  u : int
  t: int
  x: str

  def __str__(self) -> str:
    return f"WriteWriteRace({self.u}, {self.t}, {self.x})"

Race = Union[ReadWriteRace, WriteWriteRace, WriteReadRace]

def report_race(race, instr):
  print(f"!!! {race} when executing {instr} !!!")


def run_algorithm(state, program, verbose=False) -> Tuple[VectorClockState, Optional[Race]]:
  C = 0
  L = 1
  R = 2
  W = 3

  for instr in program:
    if isinstance(instr, Read):
      t = instr.thread_id
      x = instr.location
      # check write-read race
      if not (state[W][x] <= state[C][t]):
        u = find_racy_thread(state[W][x], state[C][t])
        race = WriteReadRace(u, t, x)
        if verbose:
          report_race(race, instr)
        return state, race
        
      state[R][x][t] = state[C][t][t]

    elif isinstance(instr, Write):
      t = instr.thread_id
      x = instr.location
      # Check write-write and read-write race
      if not (state[W][x] <= state[C][t]):
        u = find_racy_thread(state[W][x], state[C][t])
        race = WriteWriteRace(u, t, x)
        if verbose:
          report_race(race, instr)
        return state, race

      elif not (state[R][x] <= state[C][t]): 
        u = find_racy_thread(state[R][x], state[C][t])
        race = ReadWriteRace(u, t, x)
        if verbose:
          report_race(race, instr)
        return state, race
        
      state[W][x][t] = state[C][t][t]
    
    elif isinstance(instr, Acquire) or isinstance(instr, AtomicLoad):
      t = instr.thread_id
      m = instr.lock if isinstance(instr, Acquire) else instr.atomic_obj
      state[C][t] = state[C][t] + state[L][m]
      
    elif isinstance(instr, Release) or isinstance(instr, AtomicStore):
      t = instr.thread_id
      m = instr.lock if isinstance(instr, Release) else instr.atomic_obj
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

    if verbose:
      print(f"{instr} : {state}")
  
  return state, None
