from dataclasses import dataclass

@dataclass
class Read:
  thread_id : int
  location: str

  def __str__(self) -> str:
    return f"rd({self.thread_id}, {self.location})"

@dataclass
class Write:
  thread_id : int
  location: str

  def __str__(self) -> str:
    return f"wr({self.thread_id}, {self.location})"

@dataclass
class Acquire:
  thread_id : int
  lock: str

  def __str__(self) -> str:
    return f"acq({self.thread_id}, {self.lock})"

@dataclass
class Release:
  thread_id : int
  lock: str

  def __str__(self) -> str:
    return f"rel({self.thread_id}, {self.lock})"

@dataclass
class AtomicLoad:
  thread_id : int
  atomic_obj: str

  def __str__(self) -> str:
    return f"a-acq({self.thread_id}, {self.atomic_obj})"


@dataclass
class AtomicStore:
  thread_id : int
  atomic_obj: str

  def __str__(self) -> str:
    return f"a-rel({self.thread_id}, {self.atomic_obj})"

@dataclass
class AtomicRMW:
  thread_id : int
  atomic_obj: str

  def __str__(self) -> str:
      return f"a-RMW({self.thread_id}, {self.atomic_obj})"