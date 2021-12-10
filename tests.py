from vector_clock import WriteReadRace, WriteWriteRace, init_vector_clock_state, run_algorithm
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


if __name__ == "__main__":
  p1 = Program1()
  p1.test()

  p2 = Program2()
  p2.test()
  