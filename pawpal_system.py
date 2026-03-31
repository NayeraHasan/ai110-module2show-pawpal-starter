"""
PawPal+ — core logic layer.

Classes:
    Task      — a single pet care activity
    Pet       — a pet with a list of tasks
    Owner     — manages multiple pets
    Scheduler — retrieves, sorts, filters, and validates tasks
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """Represents a single pet care activity."""

    description: str
    time: str          # "HH:MM" 24-hour format
    frequency: str     # "once" | "daily" | "weekly"
    priority: str = "medium"   # "high" | "medium" | "low"
    completed: bool = False
    due_date: date = field(default_factory=date.today)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """Stores a pet's details and its list of tasks."""

    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's schedule."""
        self.tasks.append(task)

    def task_count(self) -> int:
        """Return the total number of tasks for this pet."""
        return len(self.tasks)


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    """Manages a collection of pets and provides access to their tasks."""

    def __init__(self, name: str) -> None:
        """Initialise with the owner's name and an empty pet list."""
        self.name = name
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's household."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Tuple[str, Task]]:
        """Return all (pet_name, Task) pairs across every pet."""
        result = []
        for pet in self.pets:
            for task in pet.tasks:
                result.append((pet.name, task))
        return result

    def get_pet(self, name: str) -> Optional[Pet]:
        """Return the Pet with the given name, or None if not found."""
        for pet in self.pets:
            if pet.name.lower() == name.lower():
                return pet
        return None


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """
    The 'brain' of PawPal+.

    Retrieves tasks from the owner's pets and provides:
    - Chronological sorting
    - Filtering by completion status or pet name
    - Conflict detection (same pet, same time slot)
    - Automatic recurrence when a daily/weekly task is completed
    """

    def __init__(self, owner: Owner) -> None:
        """Attach the scheduler to an owner."""
        self.owner = owner

    # ------------------------------------------------------------------
    # Retrieval helpers
    # ------------------------------------------------------------------

    def get_all_tasks(self) -> List[Tuple[str, Task]]:
        """Return all (pet_name, Task) pairs from the owner."""
        return self.owner.get_all_tasks()

    # ------------------------------------------------------------------
    # Sorting
    # ------------------------------------------------------------------

    # Priority rank used as a tiebreaker: lower number = higher urgency
    _PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}

    def sort_by_time(self) -> List[Tuple[str, Task]]:
        """Return tasks sorted chronologically; priority breaks ties at the same time."""
        return sorted(
            self.get_all_tasks(),
            key=lambda pair: (
                pair[1].time,
                self._PRIORITY_RANK.get(pair[1].priority, 1),
            ),
        )

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def filter_by_priority(self, priority: str) -> List[Tuple[str, Task]]:
        """Return tasks matching the given priority ('high', 'medium', or 'low')."""
        return [
            (pet_name, task)
            for pet_name, task in self.get_all_tasks()
            if task.priority == priority
        ]

    def filter_by_status(self, completed: bool = False) -> List[Tuple[str, Task]]:
        """Return tasks matching the given completion status."""
        return [
            (pet_name, task)
            for pet_name, task in self.get_all_tasks()
            if task.completed == completed
        ]

    def filter_by_pet(self, pet_name: str) -> List[Tuple[str, Task]]:
        """Return tasks belonging to the named pet (case-insensitive)."""
        return [
            (name, task)
            for name, task in self.get_all_tasks()
            if name.lower() == pet_name.lower()
        ]

    # ------------------------------------------------------------------
    # Conflict detection
    # ------------------------------------------------------------------

    def detect_conflicts(self) -> List[str]:
        """
        Detect scheduling conflicts.

        A conflict occurs when the same pet has two tasks at the exact
        same time.  Returns a list of human-readable warning strings.
        """
        seen: dict = {}          # (pet_name, time) -> description
        warnings: List[str] = []

        for pet_name, task in self.get_all_tasks():
            key = (pet_name.lower(), task.time, task.due_date)
            if key in seen:
                warnings.append(
                    f"⚠️  Conflict for {pet_name} at {task.time}: "
                    f"'{seen[key]}' and '{task.description}'"
                )
            else:
                seen[key] = task.description

        return warnings

    # ------------------------------------------------------------------
    # Task completion + recurrence
    # ------------------------------------------------------------------

    def mark_task_complete(self, pet_name: str, task_description: str) -> bool:
        """
        Mark the first matching incomplete task as done.

        For 'daily' tasks a new instance is scheduled for the next day.
        For 'weekly' tasks a new instance is scheduled seven days out.
        Returns True if the task was found and completed, False otherwise.
        """
        pet = self.owner.get_pet(pet_name)
        if pet is None:
            return False

        for task in pet.tasks:
            if task.description == task_description and not task.completed:
                task.mark_complete()
                self._schedule_next_occurrence(pet, task)
                return True

        return False

    def _schedule_next_occurrence(self, pet: Pet, completed_task: Task) -> None:
        """Create the next Task instance for recurring tasks."""
        if completed_task.frequency == "daily":
            delta = timedelta(days=1)
        elif completed_task.frequency == "weekly":
            delta = timedelta(weeks=1)
        else:
            return  # "once" — no recurrence

        next_task = Task(
            description=completed_task.description,
            time=completed_task.time,
            frequency=completed_task.frequency,
            priority=completed_task.priority,
            due_date=completed_task.due_date + delta,
        )
        pet.add_task(next_task)
