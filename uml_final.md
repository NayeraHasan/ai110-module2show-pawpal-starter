# PawPal+ — Final UML Class Diagram

```mermaid
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
        +task_count() int
    }

    class Owner {
        +str name
        +List~Pet~ pets
        +add_pet(pet)
        +get_all_tasks() List
        +get_pet(name) Pet
    }

    class Scheduler {
        +Owner owner
        +get_all_tasks() List
        +sort_by_time() List
        +filter_by_status(completed) List
        +filter_by_pet(pet_name) List
        +detect_conflicts() List
        +mark_task_complete(pet_name, description) bool
        -_schedule_next_occurrence(pet, task)
    }

    Owner "1" --> "*" Pet : owns
    Pet "1" --> "*" Task : schedules
    Scheduler --> Owner : reads from
```

## Relationships

- **Owner → Pet** (composition): An Owner manages one or more Pets. Pets don't exist independently of an Owner in this system.
- **Pet → Task** (composition): A Pet owns a list of Tasks. Tasks belong to the Pet they were added to.
- **Scheduler → Owner** (association): The Scheduler holds a reference to the Owner and queries it for pet/task data at runtime. This keeps the algorithmic layer separate from the data layer.
