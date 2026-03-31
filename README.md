# 🐾 PawPal+

A smart pet care management system that helps owners keep their pets happy and healthy by tracking daily routines — feedings, walks, medications, and appointments.

---

## 🚀 Setup

```bash
pip install -r requirements.txt
```

Run the Streamlit UI:

```bash
streamlit run app.py
```

Run the CLI demo:

```bash
python main.py
```

---

## 🏗️ Architecture

PawPal+ uses a four-class OOP design defined in `pawpal_system.py`:

```
classDiagram
    class Task {
        +str description
        +str time
        +str frequency
        +bool completed
        +date due_date
        +mark_complete()
    }
    class Pet {
        +str name
        +str species
        +List~Task~ tasks
        +add_task(task)
        +task_count()
    }
    class Owner {
        +str name
        +List~Pet~ pets
        +add_pet(pet)
        +get_all_tasks()
        +get_pet(name)
    }
    class Scheduler {
        +Owner owner
        +get_all_tasks()
        +sort_by_time()
        +filter_by_status(completed)
        +filter_by_pet(pet_name)
        +detect_conflicts()
        +mark_task_complete(pet_name, description)
    }
    Owner "1" --> "*" Pet
    Pet "1" --> "*" Task
    Scheduler --> Owner
```

---

## ✨ Features

### Smarter Scheduling

| Feature | Description |
|---|---|
| **Sorting by time** | `Scheduler.sort_by_time()` returns all tasks in chronological HH:MM order using Python's `sorted()` with a lambda key. |
| **Filtering** | Filter tasks by completion status (`filter_by_status`) or by individual pet (`filter_by_pet`). |
| **Conflict detection** | `detect_conflicts()` scans for two tasks belonging to the same pet at the same time on the same day and returns human-readable warnings. |
| **Daily recurrence** | Completing a `daily` task automatically schedules the next occurrence for tomorrow using `timedelta(days=1)`. |
| **Weekly recurrence** | Completing a `weekly` task schedules the next occurrence 7 days out using `timedelta(weeks=1)`. |

---

## 🧪 Testing PawPal+

```bash
python -m pytest
```

The test suite in `tests/test_pawpal.py` covers:

- **Task completion** — `mark_complete()` correctly flips the `completed` flag.
- **Task addition** — adding a task increases a pet's `task_count`.
- **Sorting correctness** — tasks are returned in strict chronological order.
- **Conflict detection** — duplicate time slots for the same pet are flagged; different pets at the same time are not.
- **Recurrence logic** — completing a daily/weekly task creates a new task with the correct future `due_date`; `once` tasks do not recur.
- **Edge cases** — empty schedules, unknown pets, case-insensitive pet lookup.

**Confidence level: ⭐⭐⭐⭐⭐** — 23 tests, all passing.

---

## 📸 Demo

*(Add a screenshot of the running Streamlit app here.)*

---

## 🗂️ File Structure

```
project2/
├── pawpal_system.py   # Core logic: Task, Pet, Owner, Scheduler
├── app.py             # Streamlit UI
├── main.py            # CLI demo / manual verification
├── requirements.txt
├── reflection.md
└── tests/
    └── test_pawpal.py
```
