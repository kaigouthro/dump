import sqlite3
import uuid
from difflib import SequenceMatcher

import nltk
from fuzzywuzzy import fuzz


def check_duplicate(existing_names, new_name, threshold=0.2):
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
            return True

    return False



class TaskStorage:
    """
    A class to store and manage tasks in an SQLite database.

    This class provides functionalities to create, update, delete, and retrieve tasks. It supports the creation of subtasks,
    marking tasks as completed, and fetching tasks based on various criteria such as parent task ID, completeness, and priority.

    The TaskStorage class uses an SQLite database to efficiently store and retrieve task information. It provides a clean
    and organized way to manage tasks and their relationships, making it easier to track and prioritize tasks in a project.

    Usage:
        - Create an instance of TaskStorage by providing the path to the SQLite database.
        - Use the create_task() method to save a new task with its details such as task name, description, completeness, parent task ID, etc.
        - Use the update_task() method to update the details of an existing task.
        - Use the delete_task() method to delete a task from the storage.
        - Use the get_all_tasks() method to retrieve all tasks from the storage.
        - Use the get_completed_tasks() method to retrieve only completed tasks from the storage.
        - Use the get_incomplete_tasks() method to retrieve only incomplete tasks from the storage.
        - Use the get_tasks_by_parent() method to retrieve tasks with a specific parent task ID.
        - Use the create_subtask() method to create a subtask under an existing parent task.
        - Use the mark_task_completed() method to mark a task as completed.

    Examples:
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

        # Get all tasks
        ALL_TASKS = STORAGE.get_all_tasks()
        for task in ALL_TASKS:
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
        for task in SUBTASKS:
            print(task)

        # Mark Task 2 as completed
        STORAGE.mark_task_completed(task_id=ALL_TASKS[1]["id"])

        # Get incomplete tasks
        INCOMPLETE_TASKS = STORAGE.get_incomplete_tasks()
        for task in INCOMPLETE_TASKS:
            print(task)

        # Update Task 3 description and priority
        STORAGE.update_task(
            task_id=ALL_TASKS[2]["id"],
            description="Updated description for Task 3",
            priority=2,
        )

        # Delete Task 1
        STORAGE.delete_task(task_id=ALL_TASKS[0]["id"])

        # Get all tasks again
        ALL_TASKS = STORAGE.get_all_tasks()
        for task in ALL_TASKS:
            print(task)
    """

    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._create_tables()

    def _create_tables(self):
        """
        Creates basic tables if needed.

        Args:
            self: The parent TaskStorage object.

        Returns:
            None
        """
        with self.conn:
            self.conn.execute(
                """CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                task TEXT NOT NULL,
                description TEXT,
                completed BOOLEAN NOT NULL,
                parent_task_id TEXT,
                dependent_task_ids TEXT,
                expected_result_note TEXT,
                constraints TEXT,
                priority INTEGER,
                FOREIGN KEY(parent_task_id) REFERENCES tasks(id)
            )"""
            )

    @staticmethod
    def _generate_task_id():
        """
        Unique task ID string.

        Returns:
            str: String representation of the generated UUID.
        """
        return str(uuid.uuid4())

    def _check_task_exists(self, task, description):
        """
        Checks if a task with the given task and description exists in the database.
        first get all names and check `check_duplicate` for each.
        any that are close, then check task descriptions for `check_duplicate`, with its threshold.
        if true, return true otherwise, return false.

        Args:
            task (str): The task name.
            description (str): The task description.

        Returns:
            bool: True if the task exists, False otherwise.
        """
        tasks = self.get_all_tasks()
        for t in tasks:
            taskname = t["task"]
            if check_duplicate(task, taskname) and check_duplicate(description, t["description"]):
                return True
        return False

    def create_task(
        self,
        task: str,
        description: str = "",
        completed: bool = False,
        parent_task_id=None,
        dependent_task_ids=None,
        expected_result_note=None,
        constraints=None,
        priority: int = 0,
    ):
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
        if self._check_task_exists(task, description):
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

    def get_all_tasks(self):
        """
        Retrieves all tasks from the storage.

        Returns:
            list: A list of dictionaries representing the tasks.
        """
        with self.conn:
            cursor = self.conn.execute("SELECT * FROM tasks")
            columns = [column[0] for column in cursor.description]
            tasks = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return tasks

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

