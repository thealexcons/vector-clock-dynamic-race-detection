from vector_clock import ReadWriteRace, WriteReadRace, WriteWriteRace, init_vector_clock_state, run_algorithm
from instructions import *

class Program1:
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

  def test(self):
    _, race = run_algorithm(self.state, self.program)
    assert not race

class Program2:
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

  def test(self):
    _, race = run_algorithm(self.state, self.program)
    assert race and isinstance(race, WriteReadRace) and race.x == 'd1'

class Program3:
  threads = 2
  locks = ['m', 'n']
  atomic_objects = []
  shared_locations = ['x', 'y']

  program = [
    Acquire(0, 'm'),
    Read(0, 'x'),
    Write(0, 'y'),
    Release(0, 'm'),
    Acquire(1, 'n'),
    Read(1, 'x'),
    Release(1, 'n'),
    Acquire(0, 'm'),
    Write(0, 'x')
  ]

  state = init_vector_clock_state(threads, locks, atomic_objects, shared_locations)

  def test(self):
    _, race = run_algorithm(self.state, self.program)
    assert race and isinstance(race, ReadWriteRace) and race.x == 'x'


if __name__ == "__main__":
  p1 = Program1()
  p1.test()

  p2 = Program2()
  p2.test()
  
  p3 = Program3()
  p3.test()
  