# PawPal+ — Reflection

---

## System Design

### Core actions a user should be able to perform

1. **Add a pet** — register a pet (name + species) under their household.
2. **Schedule a task** — attach a care activity (walk, feeding, medication, vet visit) with a time, frequency, and due date to a specific pet.
3. **See today's tasks** — view a sorted, filterable list of all upcoming activities across every pet.

---

### 1a. Initial design

Four classes were chosen:

| Class | Responsibility |
|---|---|
| `Task` | Represents a single care activity. Holds description, time (HH:MM), frequency, completion status, and due date. Implemented as a Python dataclass for clean, minimal boilerplate. |
| `Pet` | Stores a pet's identity and owns a list of Tasks. Provides `add_task()` and `task_count()`. Also a dataclass. |
| `Owner` | Acts as the top-level container. Holds a list of Pets and provides `get_all_tasks()` and `get_pet()` as convenience methods. A regular class because it has meaningful initialisation logic. |
| `Scheduler` | The algorithmic "brain." Accepts an Owner and provides sorting, filtering, conflict detection, and task completion with automatic recurrence. Separated from Owner so the algorithmic layer remains independently testable. |

The key design decision was to give `Scheduler` a reference to `Owner` rather than to a flat list of tasks. This mirrors real-world delegation: the scheduler asks the owner for its pets and their tasks at query time, so the data is always up-to-date.

---

### 1b. Design changes

- **Conflict detection key** — initially keyed on `(pet_name, time)` only, which caused false positives when a completed daily task generated a new recurrence at the same time on a different day. Updated the key to `(pet_name, time, due_date)` to scope conflicts to the same calendar day.
- **`get_pet()` on Owner** — added after recognising that `Scheduler.mark_task_complete()` needed a reliable way to locate a pet without iterating manually every call. Centralising the lookup in `Owner` also makes the UI code cleaner.

---

## Algorithmic Layer

### 2a. Algorithms implemented

| Algorithm | Approach |
|---|---|
| Sorting | `sorted()` with a lambda key on `task.time` (lexicographic order works correctly for `"HH:MM"` strings). O(n log n). |
| Filtering by status | List comprehension comparing `task.completed`. O(n). |
| Filtering by pet | List comprehension with case-insensitive name match. O(n). |
| Conflict detection | Single-pass dictionary scan keyed on `(pet, time, date)`. O(n). |
| Daily recurrence | On `mark_task_complete`, if frequency is `"daily"`, a new `Task` is appended with `due_date + timedelta(days=1)`. |
| Weekly recurrence | Same as daily but with `timedelta(weeks=1)`. |

### 2b. Tradeoffs

**Conflict detection** only flags exact time matches (e.g., two tasks both at `"08:00"`). It does not detect overlapping durations (e.g., a 30-minute walk at `"07:45"` overlapping with a task at `"08:00"`). This was a deliberate simplification: tasks in this system don't carry a duration attribute, so overlap detection would require adding that field and a more expensive pairwise comparison. Exact-match detection is O(n) and covers the most common user error (accidentally scheduling two things at the same slot).

---

## AI Strategy

### Copilot features most effective for this build

- **Agent Mode** was the most powerful tool for the initial scaffold. Prompting it with the UML design and asking for full class implementations with docstrings saved significant boilerplate time.
- **Inline Chat** was ideal for targeted refinements — e.g., asking "how do I use `timedelta` for daily recurrence" or "suggest a cleaner way to write this list comprehension."
- **Separate chat sessions per phase** kept context clean. The testing session didn't inherit half-finished implementation discussions, which meant suggestions were more focused and relevant.

### One AI suggestion rejected

When asked to generate the conflict detection logic, the AI initially proposed a nested `O(n²)` loop comparing every pair of tasks. While correct, this was unnecessarily complex for the scale of a household pet app. The single-pass dictionary approach was substituted instead — more readable, more efficient, and easier to unit-test.

### Role as lead architect

Using AI as a collaborator rather than an author meant every design decision passed through a human judgement filter. The AI accelerated the typing and surfaced options, but choices like the `Scheduler`/`Owner` separation, the conflict-key fix, and the O(n) detection strategy were made by evaluating tradeoffs — not by accepting the first suggestion. The most important skill practised here was knowing *when* to accept AI output and *when* to push back with a better requirement.
