from metaloom.task_store.task_db import TaskStorage

# Create an instance of TaskStorage
STORAGE = TaskStorage("tasks.db")


# Save tasks
STORAGE.create_task(
    "Task 1",
    description="Description for Task 1",
    completed=True,
    parent_task_id=None,
    dependent_task_ids="2,3",
    expected_result_note="Expected result for Task 1",
    constraints="Constraints for Task 1",
    priority=1,
)

STORAGE.create_task(
    "Task 2",
    description="Description for Task 2",
    completed=False,
    parent_task_id=None,
    dependent_task_ids="",
    expected_result_note="Expected result for Task 2",
    constraints="Constraints for Task 2",
)

STORAGE.create_task(
    "Task 3",
    description="Description for Task 3",
    completed=True,
    parent_task_id=None,
    dependent_task_ids="",
    expected_result_note="Expected result for Task 3",
    constraints="Constraints for Task 3",
)

# Get all tasks
ALL_TASKS = STORAGE.get_all_tasks()
print("\nAll Tasks:")
for task in ALL_TASKS:
    print(task)

# Get completed tasks
COMPLETED_TASKS = STORAGE.get_completed_tasks()
print("\nCompleted Tasks:")
for task in COMPLETED_TASKS:
    print(task)

# Create a subtask for Task 1
STORAGE.create_subtask(
    parent_task_id=ALL_TASKS[0]["id"],
    task="Subtask 1",
    description="Description for Subtask 1",
    dependent_task_ids="",
    expected_result_note="Expected result for Subtask 1",
    constraints="Constraints for Subtask 1",
)

# Get tasks with parent task ID '1'
SUBTASKS = STORAGE.get_tasks_by_parent(parent_task_id=ALL_TASKS[0]["id"])
print("\nSubtasks for Task 1:")
for task in SUBTASKS:
    print(task)

# Mark Task 2 as completed
STORAGE.mark_task_completed(task_id=ALL_TASKS[1]["id"])

# Get incomplete tasks
INCOMPLETE_TASKS = STORAGE.get_incomplete_tasks()
print("\nIncomplete Tasks:")
for task in INCOMPLETE_TASKS:
    print(task)

# Update Task 3 description and priority
STORAGE.update_task(
    task_id=ALL_TASKS[1]["id"],
    description="Updated description for Task 3",
    priority=2,
)

# Delete Task 1
STORAGE.delete_task(task_id=ALL_TASKS[0]["id"])

# Get all tasks again
ALL_TASKS = STORAGE.get_all_tasks()
print("\nAll Tasks (after updates and deletion):")
for task in ALL_TASKS:
    print(task)
