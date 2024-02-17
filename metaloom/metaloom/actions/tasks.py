
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
        return self.task_storage._check_task_exists(task=self.task, description=self.description)

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
