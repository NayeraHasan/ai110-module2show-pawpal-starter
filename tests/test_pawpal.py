"""
Automated tests for PawPal+ — pawpal_system.py
Run with: python -m pytest
"""

from datetime import date, timedelta
import pytest
from pawpal_system import Owner, Pet, Task, Scheduler


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_owner():
    owner = Owner("Jordan")
    dog = Pet("Rex", "Dog")
    dog.add_task(Task("Walk",     "07:00", "daily"))
    dog.add_task(Task("Feeding",  "18:00", "daily"))
    dog.add_task(Task("Vet",      "10:00", "once"))
    cat = Pet("Luna", "Cat")
    cat.add_task(Task("Feeding",  "08:00", "daily"))
    cat.add_task(Task("Pill",     "08:00", "daily"))   # intentional conflict
    owner.add_pet(dog)
    owner.add_pet(cat)
    return owner


@pytest.fixture
def scheduler(sample_owner):
    return Scheduler(sample_owner)


# ── Task tests ────────────────────────────────────────────────────────────────

def test_task_mark_complete():
    """mark_complete() should set completed to True."""
    task = Task("Morning walk", "07:00", "daily")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_task_default_due_date():
    """A Task created without a due_date should default to today."""
    task = Task("Walk", "07:00", "once")
    assert task.due_date == date.today()


# ── Pet tests ─────────────────────────────────────────────────────────────────

def test_pet_add_task_increases_count():
    """Adding a task to a Pet should increase task_count by 1."""
    pet = Pet("Buddy", "Dog")
    initial = pet.task_count()
    pet.add_task(Task("Walk", "07:00", "daily"))
    assert pet.task_count() == initial + 1


def test_pet_with_no_tasks():
    """A newly created Pet should have zero tasks."""
    pet = Pet("Max", "Dog")
    assert pet.task_count() == 0


# ── Owner tests ───────────────────────────────────────────────────────────────

def test_owner_get_pet_found(sample_owner):
    """get_pet should return the correct Pet object."""
    pet = sample_owner.get_pet("Rex")
    assert pet is not None
    assert pet.name == "Rex"


def test_owner_get_pet_not_found(sample_owner):
    """get_pet should return None for unknown names."""
    assert sample_owner.get_pet("Ghost") is None


def test_owner_get_pet_case_insensitive(sample_owner):
    """get_pet should be case-insensitive."""
    assert sample_owner.get_pet("rex") is not None


# ── Scheduler — sorting ───────────────────────────────────────────────────────

def test_sort_by_time_returns_chronological_order(scheduler):
    """sort_by_time() must return tasks in ascending HH:MM order."""
    sorted_tasks = scheduler.sort_by_time()
    times = [task.time for _, task in sorted_tasks]
    assert times == sorted(times)


def test_sort_by_time_correct_first(scheduler):
    """The earliest task in the fixture should be Rex's walk at 07:00."""
    sorted_tasks = scheduler.sort_by_time()
    first_pet, first_task = sorted_tasks[0]
    assert first_task.time == "07:00"


# ── Scheduler — filtering ─────────────────────────────────────────────────────

def test_filter_by_status_returns_pending_only(scheduler):
    """filter_by_status(completed=False) should return only incomplete tasks."""
    pending = scheduler.filter_by_status(completed=False)
    assert all(not task.completed for _, task in pending)


def test_filter_by_pet_returns_correct_pet(scheduler):
    """filter_by_pet('Rex') should return only Rex's tasks."""
    rex_tasks = scheduler.filter_by_pet("Rex")
    assert len(rex_tasks) > 0
    assert all(name == "Rex" for name, _ in rex_tasks)


def test_filter_by_pet_no_cross_contamination(scheduler):
    """filter_by_pet('Rex') should never include Luna's tasks."""
    rex_tasks = scheduler.filter_by_pet("Rex")
    assert all(name != "Luna" for name, _ in rex_tasks)


# ── Scheduler — conflict detection ───────────────────────────────────────────

def test_detect_conflicts_finds_duplicate_time(scheduler):
    """Luna has two tasks at 08:00 on the same day — must be flagged."""
    warnings = scheduler.detect_conflicts()
    assert len(warnings) >= 1
    assert any("Luna" in w and "08:00" in w for w in warnings)


def test_detect_conflicts_no_false_positives():
    """An owner whose pets have no overlapping times should get zero warnings."""
    owner = Owner("Sam")
    dog = Pet("Pip", "Dog")
    dog.add_task(Task("Walk",    "07:00", "daily"))
    dog.add_task(Task("Feeding", "18:00", "daily"))
    owner.add_pet(dog)
    scheduler = Scheduler(owner)
    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_cross_pet_no_warning():
    """Two different pets at the same time should NOT trigger a conflict."""
    owner = Owner("Sam")
    dog = Pet("Pip", "Dog")
    dog.add_task(Task("Walk",    "08:00", "daily"))
    cat = Pet("Mia", "Cat")
    cat.add_task(Task("Feeding", "08:00", "daily"))
    owner.add_pet(dog)
    owner.add_pet(cat)
    scheduler = Scheduler(owner)
    assert scheduler.detect_conflicts() == []


# ── Scheduler — recurrence ────────────────────────────────────────────────────

def test_recurrence_daily_adds_new_task():
    """Completing a daily task should add a new task for the next day."""
    owner = Owner("Alex")
    pet = Pet("Buddy", "Dog")
    today = date.today()
    pet.add_task(Task("Walk", "07:00", "daily", due_date=today))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    before = pet.task_count()
    scheduler.mark_task_complete("Buddy", "Walk")
    assert pet.task_count() == before + 1


def test_recurrence_daily_correct_due_date():
    """The new daily task should be due tomorrow."""
    owner = Owner("Alex")
    pet = Pet("Buddy", "Dog")
    today = date.today()
    pet.add_task(Task("Walk", "07:00", "daily", due_date=today))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    scheduler.mark_task_complete("Buddy", "Walk")
    new_task = pet.tasks[-1]
    assert new_task.due_date == today + timedelta(days=1)
    assert new_task.completed is False


def test_recurrence_weekly_correct_due_date():
    """The new weekly task should be due 7 days from now."""
    owner = Owner("Alex")
    pet = Pet("Buddy", "Dog")
    today = date.today()
    pet.add_task(Task("Flea treatment", "09:00", "weekly", due_date=today))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    scheduler.mark_task_complete("Buddy", "Flea treatment")
    new_task = pet.tasks[-1]
    assert new_task.due_date == today + timedelta(weeks=1)


def test_recurrence_once_no_new_task():
    """Completing a 'once' task should NOT add a new task."""
    owner = Owner("Alex")
    pet = Pet("Buddy", "Dog")
    today = date.today()
    pet.add_task(Task("Vet", "10:00", "once", due_date=today))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    before = pet.task_count()
    scheduler.mark_task_complete("Buddy", "Vet")
    assert pet.task_count() == before   # no new task


def test_mark_task_complete_returns_false_for_unknown_pet(scheduler):
    """mark_task_complete should return False when the pet doesn't exist."""
    result = scheduler.mark_task_complete("Ghost", "Walk")
    assert result is False


def test_mark_task_complete_returns_true_on_success(scheduler):
    """mark_task_complete should return True when the task is found and done."""
    result = scheduler.mark_task_complete("Rex", "Walk")
    assert result is True


# ── Edge cases ────────────────────────────────────────────────────────────────

def test_owner_with_no_pets_returns_empty_tasks():
    """An owner with no pets should have no tasks."""
    owner = Owner("Nobody")
    scheduler = Scheduler(owner)
    assert scheduler.get_all_tasks() == []


def test_sort_empty_task_list():
    """sort_by_time() on an empty schedule should return an empty list."""
    owner = Owner("Empty")
    scheduler = Scheduler(owner)
    assert scheduler.sort_by_time() == []
