"""
PawPal+ — Streamlit UI
Run with: streamlit run app.py
"""

import streamlit as st
from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")
st.title("🐾 PawPal+")
st.caption("Smart pet care management — keep your furry friends happy and healthy.")

# ── Session state bootstrap ───────────────────────────────────────────────────
# st.session_state acts as persistent in-memory storage across reruns.
# We initialise the Owner once; subsequent reruns reuse the same object.

if "owner" not in st.session_state:
    st.session_state.owner = Owner("My Household")

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

# ── Sidebar — Add a pet ───────────────────────────────────────────────────────

st.sidebar.header("Add a New Pet")
with st.sidebar.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name")
    species   = st.selectbox("Species", ["Dog", "Cat", "Rabbit", "Bird", "Other"])
    submitted = st.form_submit_button("Add Pet")
    if submitted:
        if not pet_name.strip():
            st.sidebar.error("Please enter a pet name.")
        elif owner.get_pet(pet_name.strip()) is not None:
            st.sidebar.warning(f"'{pet_name}' already exists.")
        else:
            owner.add_pet(Pet(pet_name.strip(), species))
            st.sidebar.success(f"Added {pet_name} ({species})!")

# ── Sidebar — Schedule a task ─────────────────────────────────────────────────

st.sidebar.header("Schedule a Task")
pet_names = [p.name for p in owner.pets]
if pet_names:
    with st.sidebar.form("add_task_form", clear_on_submit=True):
        target_pet  = st.selectbox("For pet", pet_names)
        description = st.text_input("Task description")
        task_time   = st.time_input("Time")
        frequency   = st.selectbox("Frequency", ["once", "daily", "weekly"])
        due_date    = st.date_input("Due date", value=date.today())
        task_submit = st.form_submit_button("Add Task")

        if task_submit:
            if not description.strip():
                st.sidebar.error("Please enter a task description.")
            else:
                pet = owner.get_pet(target_pet)
                if pet:
                    time_str = task_time.strftime("%H:%M")
                    pet.add_task(Task(description.strip(), time_str, frequency, due_date=due_date))
                    st.sidebar.success(f"Scheduled '{description}' for {target_pet}.")
else:
    st.sidebar.info("Add a pet first to schedule tasks.")

# ── Main area ─────────────────────────────────────────────────────────────────

if not owner.pets:
    st.info("No pets yet. Use the sidebar to add your first pet!")
    st.stop()

# ── Conflict warnings ─────────────────────────────────────────────────────────

conflicts = scheduler.detect_conflicts()
if conflicts:
    st.subheader("⚠️ Scheduling Conflicts")
    for warning in conflicts:
        st.warning(warning)

# ── Tabs ──────────────────────────────────────────────────────────────────────

tab_today, tab_pets, tab_complete = st.tabs(
    ["📅 Today's Schedule", "🐶 My Pets", "✅ Mark Complete"]
)

# ── Tab 1: Today's Schedule ───────────────────────────────────────────────────

with tab_today:
    st.subheader("Today's Schedule (sorted by time)")

    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        filter_pet = st.selectbox(
            "Filter by pet", ["All"] + pet_names, key="filter_pet"
        )
    with col_filter2:
        filter_status = st.selectbox(
            "Filter by status", ["Pending", "Completed", "All"], key="filter_status"
        )

    # Build the display list
    if filter_pet == "All":
        tasks = scheduler.sort_by_time()
    else:
        tasks = sorted(
            scheduler.filter_by_pet(filter_pet),
            key=lambda pair: pair[1].time
        )

    if filter_status == "Pending":
        tasks = [(n, t) for n, t in tasks if not t.completed]
    elif filter_status == "Completed":
        tasks = [(n, t) for n, t in tasks if t.completed]

    if not tasks:
        st.info("No tasks match the current filters.")
    else:
        rows = []
        for pet_name, task in tasks:
            rows.append({
                "Status":      "✓ Done" if task.completed else "○ Pending",
                "Time":        task.time,
                "Pet":         pet_name,
                "Task":        task.description,
                "Frequency":   task.frequency,
                "Due":         str(task.due_date),
            })
        st.table(rows)

# ── Tab 2: My Pets ────────────────────────────────────────────────────────────

with tab_pets:
    st.subheader("Your Pets")
    for pet in owner.pets:
        with st.expander(f"{pet.name}  ({pet.species})  —  {pet.task_count()} task(s)"):
            if not pet.tasks:
                st.write("No tasks scheduled yet.")
            else:
                for task in pet.tasks:
                    status = "✓" if task.completed else "○"
                    st.write(
                        f"**[{status}]** `{task.time}`  {task.description}  "
                        f"_{task.frequency}_  due {task.due_date}"
                    )

# ── Tab 3: Mark Complete ──────────────────────────────────────────────────────

with tab_complete:
    st.subheader("Mark a Task Complete")

    pending = scheduler.filter_by_status(completed=False)
    if not pending:
        st.success("All tasks are completed!")
    else:
        options = {
            f"{pet_name} — {task.description} ({task.time})": (pet_name, task.description)
            for pet_name, task in pending
        }
        choice = st.selectbox("Select task to complete", list(options.keys()))
        if st.button("Mark as Complete ✓"):
            pet_name, task_desc = options[choice]
            result = scheduler.mark_task_complete(pet_name, task_desc)
            if result:
                st.success(f"'{task_desc}' marked complete for {pet_name}!")
                # Check if a recurrence was created
                pet = owner.get_pet(pet_name)
                if pet:
                    for t in reversed(pet.tasks):
                        if t.description == task_desc and not t.completed:
                            st.info(
                                f"Next occurrence scheduled for {t.due_date} at {t.time}."
                            )
                            break
                st.rerun()
            else:
                st.error("Could not complete the task.")

# ── Footer ────────────────────────────────────────────────────────────────────

st.divider()
st.caption("PawPal+ — built with Python OOP + Streamlit")
