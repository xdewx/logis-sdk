import pytest
from networkx import NetworkXError

from logis.task.model import Task, TaskGraph


def test_task_graph():
    graph = TaskGraph()
    task1 = Task(id="task1")
    task2 = Task(id="task2")
    graph.add_task(task1)
    graph.add_task_if_absent(task1.model_copy(update=dict(name="task1 copy")))
    assert graph.get_task(task1.id).name is None

    # 测试父子关系
    graph.add_task(task2, parent=task1)
    assert graph.get_parent_id(task2.id) == task1.id
    assert list(graph.get_children_id(task1.id)) == [task2.id]

    # 测试删除
    with pytest.raises(NetworkXError):
        graph.remove_task("not exist")
    graph.remove_task_if_present(task2)
    assert task2 not in graph

    assert list(graph.get_children_id(task1)) == []
    assert task1.get_task_id() in graph
