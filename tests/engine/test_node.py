import pytest

from engine.node import Node, RootNode


class TraceNode(Node):
    def __init__(self, name: str, events: list[str]) -> None:
        super().__init__(name=name)
        self._events = events

    def _on_enter_tree(self) -> None:
        self._events.append(f"enter:{self.name}")

    def _on_exit_tree(self) -> None:
        self._events.append(f"exit:{self.name}")

    def _on_ready(self) -> None:
        self._events.append(f"ready:{self.name}")


def test_add_child_sets_parent_and_children_list() -> None:
    parent = Node(name="parent")
    child = Node(name="child")

    parent.add_child(child)

    assert child.parent is parent
    assert parent.children == [child]


def test_children_property_returns_copy() -> None:
    parent = Node(name="parent")
    child = Node(name="child")
    parent.add_child(child)

    children_copy = parent.children
    children_copy.clear()

    assert parent.children == [child]


def test_groups_property_returns_copy_and_group_management() -> None:
    node = Node(name="n")
    node.add_to_group("ghosts")

    groups_copy = node.groups
    groups_copy.clear()

    assert "ghosts" in node.groups

    node.remove_from_group("ghosts")
    assert "ghosts" not in node.groups


def test_add_to_group_rejects_empty_name() -> None:
    node = Node(name="n")

    with pytest.raises(AssertionError, match="Group name cannot be empty"):
        node.add_to_group("")


def test_remove_from_group_rejects_empty_name() -> None:
    node = Node(name="n")

    with pytest.raises(AssertionError, match="Group name cannot be empty"):
        node.remove_from_group("")


def test_path_uses_unnamed_for_missing_names() -> None:
    root = Node(name=None)
    child = Node(name="child")
    grandchild = Node(name=None)

    root.add_child(child)
    child.add_child(grandchild)

    assert grandchild.path == "<unnamed>/child/<unnamed>"


def test_is_ancestor_of() -> None:
    a = Node(name="a")
    b = Node(name="b")
    c = Node(name="c")

    a.add_child(b)
    b.add_child(c)

    assert a.is_ancestor_of(c)
    assert b.is_ancestor_of(c)
    assert not c.is_ancestor_of(a)


def test_find_child_direct_and_recursive() -> None:
    root = Node(name="root")
    branch = Node(name="branch")
    leaf = Node(name="leaf")

    root.add_child(branch)
    branch.add_child(leaf)

    assert root.find_child("branch") is branch
    assert root.find_child("leaf") is None
    assert root.find_child("leaf", recursive=True) is leaf


def test_add_child_rejects_self() -> None:
    node = Node(name="self")

    with pytest.raises(AssertionError, match="cannot be a child of itself"):
        node.add_child(node)


def test_add_child_rejects_child_with_existing_parent() -> None:
    p1 = Node(name="p1")
    p2 = Node(name="p2")
    child = Node(name="child")
    p1.add_child(child)

    with pytest.raises(AssertionError, match="already has a parent"):
        p2.add_child(child)


def test_add_child_rejects_cycle() -> None:
    root = Node(name="root")
    child = Node(name="child")

    root.add_child(child)

    with pytest.raises(AssertionError, match="ancestor of the current node"):
        child.add_child(root)


def test_reparent_moves_node_between_parents() -> None:
    p1 = Node(name="p1")
    p2 = Node(name="p2")
    child = Node(name="child")
    p1.add_child(child)

    child.reparent(p2)

    assert child.parent is p2
    assert child not in p1.children
    assert child in p2.children


def test_reparent_rejects_self_and_cycle() -> None:
    a = Node(name="a")
    b = Node(name="b")
    a.add_child(b)

    with pytest.raises(AssertionError, match="cannot be a parent of itself"):
        a.reparent(a)

    with pytest.raises(AssertionError, match="ancestor of the current node"):
        a.reparent(b)


def test_remove_child_disconnects_and_calls_exit_when_active() -> None:
    events: list[str] = []
    root = RootNode()
    parent = TraceNode("parent", events)
    child = TraceNode("child", events)

    root.add_child(parent)
    parent.add_child(child)
    events.clear()

    parent.remove_child(child)

    assert child.parent is None
    assert child not in parent.children
    assert events == ["exit:child"]


def test_remove_child_rejects_non_child() -> None:
    parent = Node(name="parent")
    child = Node(name="child")

    with pytest.raises(AssertionError, match="not a child"):
        parent.remove_child(child)


def test_queue_for_deletion_sets_flag() -> None:
    node = Node(name="n")

    assert not node.is_queued_for_deletion
    node.queue_for_deletion()
    assert node.is_queued_for_deletion


def test_adding_to_root_calls_enter_then_ready_in_order() -> None:
    events: list[str] = []
    root = RootNode()
    parent = TraceNode("parent", events)
    child = TraceNode("child", events)

    parent.add_child(child)
    root.add_child(parent)

    assert events == [
        "enter:parent",
        "enter:child",
        "ready:child",
        "ready:parent",
    ]


def test_reparent_between_active_parents_exits_and_reenters() -> None:
    events: list[str] = []
    root = RootNode()
    node = TraceNode("node", events)

    root.add_child(node)

    # Reparent through another active parent to verify the full lifecycle.
    middle = TraceNode("middle", events)
    root.add_child(middle)
    node.reparent(middle)

    assert events == [
        "enter:node",
        "ready:node",
        "enter:middle",
        "ready:middle",
        "exit:node",
        "enter:node",
    ]


def test_reparent_from_inactive_to_active_tree_enters_and_readies() -> None:
    events: list[str] = []
    root = RootNode()
    inactive_parent = Node(name="inactive")
    node = TraceNode("node", events)

    inactive_parent.add_child(node)

    assert not node.is_in_active_tree

    node.reparent(root)

    assert node.parent is root
    assert node.is_in_active_tree
    assert events == ["enter:node", "ready:node"]


def test_reparent_from_active_to_inactive_tree_exits_only() -> None:
    events: list[str] = []
    root = RootNode()
    active_parent = TraceNode("active-parent", events)
    inactive_parent = Node(name="inactive")
    node = TraceNode("node", events)

    root.add_child(active_parent)
    active_parent.add_child(node)
    events.clear()

    node.reparent(inactive_parent)

    assert node.parent is inactive_parent
    assert not node.is_in_active_tree
    assert events == ["exit:node"]
