

# def check_duplicate(existing_names, new_name, threshold=0.3):
#     """
#     Checks if a new task name is similar to existing names using difflib.

#     Args:
#         existing_names: A list of existing task names.
#         new_name: The new task name to check.

#     Returns:
#         True if a duplicate is found, False otherwise.
#     """
#     for name in existing_names:
#         # Create a SequenceMatcher object for comparing names
#         matcher = SequenceMatcher(None, name, new_name)
#         # Calculate the ratio of matched characters
#         ratio = matcher.ratio()
#         # Set a threshold for identifying similar names (adjust as needed)
#         if ratio > threshold:
#             return True
#     return False

import sqlite3
import uuid
from difflib import SequenceMatcher


from difflib import SequenceMatcher
from fuzzywuzzy import fuzz
import nltk

def check_duplicate(existing_names, new_name, threshold=0.5):
  """
  Checks for duplicate task names using combined approach.

  Args:
    existing_names: List of existing task names.
    new_name: The new task name to check.

  Returns:
    True if a duplicate is found, False otherwise.
  """
  # Preprocess text
  processed_names = [nltk.word_tokenize(name.lower()) for name in existing_names]
  processed_new_name = nltk.word_tokenize(new_name.lower())

  # Fuzzy matching
  potential_duplicates = []
  for name in processed_names:
    score = fuzz.ratio(processed_new_name, name)
    if score > threshold * 50:  # Adjust threshold as needed
      potential_duplicates.append(name)

  # Refine with difflib
  for name in potential_duplicates:
    ratio = SequenceMatcher(None, name, processed_new_name).ratio()
    if ratio > threshold:  # Adjust threshold as needed
      return False

  return True

        """
        Saves a new task in the database.

        Args:
            task (str): The task name.
            description (str): The task description. (Default: "")
            completed (bool): The completion status of the task. (Default: False)
            parent_task_id: The task ID of the parent task. (Default: None)
            dependent_task_ids: The task IDs of the dependent tasks. (Default: None)
            expected_result_note: The expected result note of the task. (Default: None)
            constraints: The constraints of the task. (Default: None)
            priority (int): The priority of the task. (Default: 0)

        Returns:
            None
        """
        if self.check_task_exists(task, description):
            return

        task_id = self._generate_task_id()
        with self.conn:
            self.conn.execute(
                "INSERT INTO tasks (id, task, description, completed, parent_task_id, dependent_task_ids, expected_result_note, constraints, priority) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    task_id,
                    task,
                    description,
                    completed,
                    parent_task_id,
                    dependent_task_ids,
                    expected_result_note,
                    constraints,
                    priority,
            ),)

    def update_task(
        self,
        task_id: str,
        task=None,
        description=None,
        completed=None,
        parent_task_id=None,
        dependent_task_ids=None,
        expected_result_note=None,
        constraints=None,
        priority=None,
    ):
        """
        Updates an existing task in the database.

        Args:
            task_id (str): The ID of the task to update.
            task (str): The task name.
            description (str): The task description. (Default: "")
            completed (bool): The completion status of the task. (Default: False)
            parent_task_id: The task ID of the parent task. (Default: None)
            dependent_task_ids: The task IDs of the dependent tasks. (Default: None)
            expected_result_note: The expected result note of the task. (Default: None)
            constraints: The constraints of the task. (Default: None)
            priority (int): The priority of the task. (Default: 0)

        Returns:
            None
        """
        update_fields = []
        params = []

        if task is not None:
            update_fields.append("task = ?")
            params.append(task)

        if description is not None:
            update_fields.append("description = ?")
            params.append(description)

        if completed is not None:
            update_fields.append("completed = ?")
            params.append(completed)

        if parent_task_id is not None:
            update_fields.append("parent_task_id = ?")
            params.append(parent_task_id)

        if dependent_task_ids is not None:
            update_fields.append("dependent_task_ids = ?")
            params.append(dependent_task_ids)

        if expected_result_note is not None:
            update_fields.append("expected_result_note = ?")
            params.append(expected_result_note)

        if constraints is not None:
            update_fields.append("constraints = ?")
            params.append(constraints)

        if priority is not None:
            update_fields.append("priority = ?")
            params.append(priority)

        if update_fields:
            with self.conn:
                self.conn.execute(
                    f'UPDATE tasks SET {", ".join(update_fields)} WHERE id = ?',
                    params + [task_id],
                )

    def delete_task(self, task_id: str):
        """
        Deletes a task from the database.

        Args:
            task_id (str): The ID of the task to delete.

        Returns:
            None
        """
        with self.conn:
            self.conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    def get_completed_tasks(self):
        """
        Retrieves a list of completed tasks from the database.

        Returns:
            list: A list of dictionaries representing the completed tasks. Each dictionary contains the task's ID, task name, description, completion status, parent task ID, dependent task IDs, expected result note, constraints, and priority.
        """
        return self._read_tasks(
            "SELECT id, task, description, completed, parent_task_id, dependent_task_ids, expected_result_note, constraints, priority "
            "FROM tasks WHERE completed = TRUE"
        )

    def get_incomplete_tasks(self):
        """
        Retrieves a list of incomplete tasks from the database.

        Returns:
            list: A list of dictionaries representing the incomplete tasks. Each dictionary contains the task's ID, task name, description, completion status, parent task ID, dependent task IDs, expected result note, constraints, and priority.
        """
        return self._read_tasks(
            "SELECT id, task, description, completed, parent_task_id, dependent_task_ids, expected_result_note, constraints, priority "
            "FROM tasks WHERE completed = FALSE"
        )
    def get_task_names(self):
        """
        Retrieves a list of task names from the database.

        Returns:
            list: A list of task names.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT task FROM tasks")
        return [row[0] for row in cursor.fetchall()]

    def _read_tasks(self, arg0):
        cursor = self.conn.cursor()
        cursor.execute(arg0)
        return [{
            "id": row[0],
            "task": row[1],
            "description": row[2],
            "completed": row[3],
            "parent_task_id": row[4],
            "dependent_task_ids": row[5],
            "expected_result_note": row[6],
            "constraints": row[7],
            "priority": row[8],
            }
            for row in cursor.fetchall()
        ]

    def get_tasks_by_parent(self, parent_task_id: str):
        """
        Retrieves a list of tasks with a specific parent task ID from the database.

        Args:
            parent_task_id (str): The ID of the parent task.

        Returns:
            list: A list of dictionaries representing the tasks. Each dictionary contains the task's ID, task name, description, completion status, parent task ID, dependent task IDs, expected result note, constraints, and priority.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, task, description, completed, parent_task_id, dependent_task_ids, expected_result_note, constraints, priority "
            "FROM tasks WHERE parent_task_id = ?",
            (parent_task_id,),
        )
        return [{
            "id": row[0],
            "task": row[1],
            "description": row[2],
            "completed": row[3],
            "parent_task_id": row[4],
            "dependent_task_ids": row[5],
            "expected_result_note": row[6],
            "constraints": row[7],
            "priority": row[8],
            }
            for row in cursor.fetchall()
        ]

    def create_subtask(
        self,
        parent_task_id: str,
        task: str,
        description: str = "",
        completed: bool = False,
        dependent_task_ids=None,
        expected_result_note=None,
        constraints=None,
        priority: int = 0,
    ):
        """
        Creates a subtask for a parent task with the specified parameters.

        Args:
            parent_task_id (str): The ID of the parent task.
            task (str): The name of the subtask.
            description (str, optional): The description of the subtask. Defaults to an empty string.
            completed (bool, optional): The completion status of the subtask. Defaults to False.
            dependent_task_ids ([type], optional): The IDs of dependent tasks. Defaults to None.
            expected_result_note ([type], optional): The expected result note of the subtask. Defaults to None.
            constraints ([type], optional): The constraints of the subtask. Defaults to None.
            priority (int, optional): The priority of the subtask. Defaults to 0.

        Returns:
            None
        """
        self.create_task(
            task,
            description,
            completed,
            parent_task_id,
            dependent_task_ids,
            expected_result_note,
            constraints,
            priority,
        )

    def mark_task_completed(self, task_id: str):
        """
        Marks a task as completed in the database.

        Args:
            task_id (str): The ID of the task to mark as completed.

        Returns:
            None
        """
        self.update_task(task_id, completed=True)

    def __del__(self):
        """
        Closes the database connection when the object is destroyed.

        Returns:
            None
        """
        self.conn.close()

from langchain_core.runnables import Runnable


class CreateTaskRunnable(Runnable):
    def __init__(
        self,
        task_storage,
        task,
        description="",
        completed=False,
        parent_task_id=None,
        dependent_task_ids=None,
        expected_result_note=None,
        constraints=None,
        priority=0,
    ):
        super().__init__()
        self.task_storage = task_storage
        self.task = task
        self.description = description
        self.completed = completed
        self.parent_task_id = parent_task_id
        self.dependent_task_ids = dependent_task_ids
        self.expected_result_note = expected_result_note
        self.constraints = constraints
        self.priority = priority

    def invoke(self, input_data):
        self.task_storage.create_task(
            task=self.task,
            description=self.description,
            completed=self.completed,
            parent_task_id=self.parent_task_id,
            dependent_task_ids=self.dependent_task_ids,
            expected_result_note=self.expected_result_note,
            constraints=self.constraints,
            priority=self.priority,
        )
        return None

class CheckTaskExistsRunnable(Runnable):
    def __init__(self, task_storage, task, description):
        super().__init__()
        self.task_storage = task_storage
        self.task = task
        self.description = description

    def invoke(self, input_data):
        return self.task_storage.check_task_exists(task=self.task, description=self.description)


class UpdateTaskRunnable(Runnable):
    def __init__(
        self,
        task_storage,
        task_id,
        task=None,
        description=None,
        completed=None,
        parent_task_id=None,
        dependent_task_ids=None,
        expected_result_note=None,
        constraints=None,
        priority=None,
    ):
        super().__init__()
        self.task_storage = task_storage
        self.task_id = task_id
        self.task = task
        self.description = description
        self.completed = completed
        self.parent_task_id = parent_task_id
        self.dependent_task_ids = dependent_task_ids
        self.expected_result_note = expected_result_note
        self.constraints = constraints
        self.priority = priority

    def invoke(self, input_data):
        self.task_storage.update_task(
            task_id=self.task_id,
            task=self.task,
            description=self.description,
            completed=self.completed,
            parent_task_id=self.parent_task_id,
            dependent_task_ids=self.dependent_task_ids,
            expected_result_note=self.expected_result_note,
            constraints=self.constraints,
            priority=self.priority,
        )
        return None

class DeleteTaskRunnable(Runnable):
    def __init__(self, task_storage, task_id):
        super().__init__()
        self.task_storage = task_storage
        self.task_id = task_id

    def invoke(self, input_data):
        self.task_storage.delete_task(task_id=self.task_id)
        return None

class GetAllTasksRunnable(Runnable):
    def __init__(self, task_storage):
        super().__init__()
        self.task_storage = task_storage

    def invoke(self, input_data):
        return self.task_storage.get_all_tasks()

class GetCompletedTasksRunnable(Runnable):
    def __init__(self, task_storage):
        super().__init__()
        self.task_storage = task_storage

    def invoke(self, input_data):
        return self.task_storage.get_completed_tasks()

class GetTaskRunnable(Runnable):
    def __init__(self, task_storage, task_id):
        super().__init__()
        self.task_storage = task_storage
        self.task_id = task_id

    def invoke(self, input_data):
        return self.task_storage.get_task(task_id=self.task_id)

class GetIncompleteTasksRunnable(Runnable):
    def __init__(self, task_storage):
        super().__init__()
        self.task_storage = task_storage

    def invoke(self, input_data):
        return self.task_storage.get_incomplete_tasks()

class GetTasksByParentRunnable(Runnable):
    def __init__(self, task_storage, parent_task_id):
        super().__init__()
        self.task_storage = task_storage
        self.parent_task_id = parent_task_id

    def invoke(self, input_data):
        return self.task_storage.get_tasks_by_parent(parent_task_id=self.parent_task_id)

class CreateSubtaskRunnable(Runnable):
    def __init__(
        self,
        task_storage,
        parent_task_id,
        task,
        description="",
        completed=False,
        dependent_task_ids=None,
        expected_result_note=None,
        constraints=None,
        priority=0,
    ):
        super().__init__()
        self.task_storage = task_storage
        self.parent_task_id = parent_task_id
        self.task = task
        self.description = description
        self.completed = completed
        self.dependent_task_ids = dependent_task_ids
        self.expected_result_note = expected_result_note
        self.constraints = constraints
        self.priority = priority

    def invoke(self, input_data):
        self.task_storage.create_subtask(
            parent_task_id=self.parent_task_id,
            task=self.task,
            description=self.description,
            completed=self.completed,
            dependent_task_ids=self.dependent_task_ids,
            expected_result_note=self.expected_result_note,
            constraints=self.constraints,
            priority=self.priority,
        )
        return None

class MarkTaskCompletedRunnable(Runnable):
    def __init__(self, task_storage, task_id):
        super().__init__()
        self.task_storage = task_storage
        self.task_id = task_id

    def invoke(self, input_data):
        self.task_storage.mark_task_completed(task_id=self.task_id)
        return None
