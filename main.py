"""
PawPal+ CLI demo script.

Run with:  python main.py
Verifies the core logic in pawpal_system.py before the Streamlit UI is used.
"""

from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler


def section(title: str) -> None:
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print('=' * 50)


def print_schedule(label: str, pairs) -> None:
    print(f"\n--- {label} ---")
    if not pairs:
        print("  (none)")
        return
    for pet_name, task in pairs:
        status = "✓" if task.completed else "○"
        print(
            f"  [{status}] {task.time}  {pet_name}: {task.description}"
            f"  [{task.frequency}]  due {task.due_date}"
        )


# ── Build demo data ───────────────────────────────────────────────────────────

owner = Owner("Alex")

buddy = Pet("Buddy", "Dog")
buddy.add_task(Task("Morning walk",    "07:30", "daily"))
buddy.add_task(Task("Dinner feeding",  "18:00", "daily"))
buddy.add_task(Task("Flea treatment",  "09:00", "weekly"))
buddy.add_task(Task("Vet appointment", "14:00", "once"))

whiskers = Pet("Whiskers", "Cat")
whiskers.add_task(Task("Morning feeding", "08:00", "daily"))
whiskers.add_task(Task("Evening feeding", "18:00", "daily"))
# Intentional conflict — Whiskers has two tasks at 08:00
whiskers.add_task(Task("Medication",     "08:00", "daily"))

owner.add_pet(buddy)
owner.add_pet(whiskers)

scheduler = Scheduler(owner)

# ── Today's sorted schedule ───────────────────────────────────────────────────

section("TODAY'S SCHEDULE (sorted by time)")
print_schedule("All tasks", scheduler.sort_by_time())

# ── Pending tasks only ────────────────────────────────────────────────────────

section("PENDING TASKS")
print_schedule("Incomplete", scheduler.filter_by_status(completed=False))

# ── Filter by pet ─────────────────────────────────────────────────────────────

section("BUDDY'S TASKS")
print_schedule("Buddy", scheduler.filter_by_pet("Buddy"))

# ── Mark a task complete and verify recurrence ────────────────────────────────

section("RECURRENCE DEMO — complete 'Morning walk' for Buddy")
print(f"\n  Buddy's task count before: {buddy.task_count()}")
scheduler.mark_task_complete("Buddy", "Morning walk")
print(f"  Buddy's task count after:  {buddy.task_count()}")
print("\n  Buddy's updated tasks:")
for pet_name, task in scheduler.filter_by_pet("Buddy"):
    status = "✓" if task.completed else "○"
    print(f"    [{status}] {task.time}  {task.description}  due {task.due_date}")

# ── Completed tasks ───────────────────────────────────────────────────────────

section("COMPLETED TASKS")
print_schedule("Done", scheduler.filter_by_status(completed=True))

# ── Conflict detection ────────────────────────────────────────────────────────

section("CONFLICT DETECTION")
warnings = scheduler.detect_conflicts()
if warnings:
    for w in warnings:
        print(f"  {w}")
else:
    print("  No conflicts detected.")

print("\nDemo complete.\n")
