from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.scene2d import Scene2D


class Node:
    """
    Represents the basic building block of the scene graph.
    This class is responsible for managing the hierarchical
    structure of the scene,
    allowing for parent-child relationships between nodes.
    """

    # HOOKS
    def _on_enter_tree(self) -> None:
        """
        Hook: Called when the node is added to the active scene tree.

        This method can be overridden by subclasses to perform initialization
        that depends on the node being part of the scene graph, such as
        accessing parent nodes or setting up connections.

        This hook is called top-down, meaning that parent nodes will
        have their _on_enter_tree method called before their children.
        """

    def _on_exit_tree(self) -> None:
        """
        Hook: Called when the node is removed from the active scene tree.

        This method can be overridden by subclasses to perform cleanup
        that depends on the node being part of the scene graph, such as
        disconnecting signals or stopping animations.

        This hook is called top-down,
        meaning that parent nodes will have their _on_exit_tree
        method called before their children.
        """

    def _on_ready(self) -> None:
        """
        Hook: Called when the node and all its children have entered the tree.

        This method can be overridden by subclasses to perform initialization
        that requires all child nodes to be ready, such as accessing child
        nodes or starting animations.

        This hook is called depth-first,
        meaning that child nodes will have their _on_ready
        method called before their parent nodes.
        """

    def _on_update(self, dt: float) -> None:
        """
        Hook: Called every frame to update the node.

        This method can be overridden by subclasses to implement per-frame
        logic, such as moving the node, checking for collisions, or
        updating animations.

        The dt (delta time) parameter represents the time elapsed since the
        last update call, allowing for frame-rate independent updates.
        """

    def _on_draw(self) -> None:
        """
        Hook: Called every frame to render the node.

        This method can be overridden by subclasses to implement custom
        rendering logic, such as drawing sprites, shapes, or text.

        The rendering order is determined by the scene graph hierarchy,
        with parent nodes being drawn before their children.
        """

    # PROPERTIES
    @property
    def name(self) -> str | None:
        """
        Human readable identifier for the node,
        useful for debugging and scene management.
        """
        return self._name

    @property
    def parent(self) -> Node | None:
        """
        Reference to the parent node in the scene graph.
        """
        return self._parent

    @property
    def children(self) -> list[Node]:
        """
        List of child nodes in the scene graph.
        """
        return self._children.copy()

    @property
    def enabled(self) -> bool:
        """
        Indicates whether the node is active and should be updated.

        Marking a node as disabled will prevent it and its children
        from being updated by the engine.
        """
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value

    @property
    def visible(self) -> bool:
        """
        Indicates whether the node should be rendered.

        Marking a node as invisible will prevent it and its children
        from being rendered by the engine.
        """
        return self._visible

    @visible.setter
    def visible(self, value: bool) -> None:
        self._visible = value

    @property
    def is_queued_for_deletion(self) -> bool:
        """
        Indicates whether the node is marked for deletion.

        Nodes that are queued for deletion will be removed from the scene
        graph at the end of the current update cycle.
        This allows for safe removal of nodes without disrupting ongoing
        updates or rendering.
        """
        return self._queued_for_deletion

    @property
    def is_in_active_tree(self) -> bool:
        """
        Indicates whether the node is currently part of the active scene tree.

        A node is considered to be in the active tree if it has been added
        to the scene graph and has not been marked for deletion.
        This property can be used to check if a node is currently active
        in the scene.
        """
        return self._is_in_active_tree

    @property
    def groups(self) -> set[str]:
        """
        Set of group names that this node belongs to.

        Groups are a way to categorize nodes for efficient querying
        and management. A node can belong to multiple groups.
        """
        return self._groups.copy()

    @property
    def path(self) -> str:
        """
        Returns the full path of the node in the scene graph.

        The path is constructed by concatenating the names of the node
        and its ancestors, separated by slashes.
        If a node does not have a name, it is represented as "<unnamed>".
        """
        parts = []
        current: Node | None = self
        while current is not None:
            parts.append(current._name if current._name is not None else "<unnamed>")
            current = current._parent
        return "/".join(reversed(parts))

    # PUBLIC METHODS
    def queue_for_deletion(self) -> None:
        """
        Marks the node for deletion.

        This method sets a flag indicating that the node should be removed
        from the scene graph at the end of the current update cycle.
        This allows for safe removal of nodes without disrupting ongoing
        updates or rendering.

        All the node's children will also be removed when the node is deleted,
        so there is no need to explicitly queue them for deletion.
        """
        self._queued_for_deletion = True

    def get_root(self) -> RootNode:
        """
        Returns the root node of the scene graph.

        This method traverses up the parent chain to find the top-most
        ancestor, which is considered the root of the scene graph.
        """
        current: Node = self
        while current._parent is not None:
            current = current._parent
        assert isinstance(current, RootNode), "Root node is not a RootNode instance."
        return current

    def get_scene(self) -> Scene2D | None:
        """
        Returns the scene that this node belongs to.

        This method traverses up the parent chain to find the root node,
        which holds a reference to the scene. If the node is not part of
        a scene, this method returns None.
        """
        root = self.get_root()
        if isinstance(root, RootNode):
            return root.scene
        return None

    def add_to_group(self, group_name: str) -> None:
        """
        Adds the node to a group.

        This method allows you to categorize nodes into groups for
        efficient querying and management.
        A node can belong to multiple groups.
        """
        assert len(group_name) > 0, "Group name cannot be empty."
        self._groups.add(group_name)

    def remove_from_group(self, group_name: str) -> None:
        """
        Removes the node from a group.

        This method removes the node from the specified group.
        If the node is not part of the group, this method does nothing.
        """
        assert len(group_name) > 0, "Group name cannot be empty."
        self._groups.discard(group_name)

    def is_ancestor_of(self, node: Node) -> bool:
        """
        Checks if the current node is an ancestor of the given node.

        This method traverses up the parent chain of the provided node
        to determine if the current node is one of its ancestors.
        """
        current = node._parent
        while current is not None:
            if current is self:
                return True
            current = current._parent
        return False

    def add_child(self, child: Node) -> None:
        """
        Adds a child node to this node.

        This method establishes a parent-child relationship between
        the current node and the provided child node.

        The child cannot be the node itself
        or any of its ancestors to prevent circular references.

        The child should not already have a parent,
        as a node can only have one parent in the scene graph.
        """
        assert child is not self, "A node cannot be a child of itself."
        assert child._parent is None, "The child node already has a parent."
        assert not child.is_ancestor_of(self), (
            "The child node is an ancestor of the current node."
        )
        child._parent = self
        self._children.append(child)
        if self._is_in_active_tree:
            child._enter_tree()
        if self._is_ready:
            child._ready()

    def remove_child(self, child: Node) -> None:
        """
        Removes a child node from this node.

        This method breaks the parent-child relationship between
        the current node and the provided child node.

        The child must be a direct child of the current node.
        """
        assert child in self._children, "The specified node is not a child."
        self._children.remove(child)
        child._exit_tree()
        child._parent = None

    def reparent(self, new_parent: Node) -> None:
        """
        Changes the parent of this node to a new parent.

        This method updates the parent-child relationships accordingly,
        ensuring that the node is removed from its current parent (if any)
        and added to the new parent.

        The new parent cannot be the node itself
        or any of its ancestors to prevent circular references.
        """
        assert new_parent is not self, "A node cannot be a parent of itself."
        assert not self.is_ancestor_of(new_parent), (
            "The new parent node is an ancestor of the current node."
        )
        if self._parent is not None:
            self._parent.remove_child(self)
        new_parent.add_child(self)

    def find_child(self, name: str, recursive: bool = False) -> Node | None:
        """
        Finds a child node by name.

        This method searches for a child node with the specified name.
        If recursive is False, only direct children are searched.
        If recursive is True, the search includes all descendants.
        Returns the first matching node found, or None if no match is found.
        """
        for child in self._children:
            if child._name == name:
                return child
            if recursive:
                found = child.find_child(name, recursive=True)
                if found is not None:
                    return found
        return None

    # PRIVATE METHODS
    def __init__(
        self,
        name: str | None = None,
        parent: Node | None = None,
        children: list[Node] | None = None,
        enabled: bool = True,
        visible: bool = True,
    ) -> None:
        self._name = name
        self._parent = parent
        self._children = children if children is not None else []
        self._enabled = enabled
        self._visible = visible
        self._groups: set[str] = set()
        self._queued_for_deletion = False
        self._is_in_active_tree = False
        self._is_ready = False

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"<{class_name} name={self._name} path={self.path}>"

    def _enter_tree(self) -> None:
        """
        Internal method to handle entering the tree.

        This method is called when the node is added to the scene graph
        and is responsible for setting the __is_in_active_tree flag and
        calling the _enter_tree hook recursively on the node and its children.

        This is called top-down, meaning that parent nodes will have their
        _enter_tree method called before their children.
        """
        if self._is_in_active_tree:
            return
        self._is_in_active_tree = True
        self._on_enter_tree()
        for child in self._children:
            child._enter_tree()

    def _exit_tree(self) -> None:
        """
        Internal method to handle exiting the tree.

        This method is called when the node is removed from the scene graph
        and is responsible for clearing the _is_in_active_tree flag and
        calling the _on_exit_tree hook recursively
        on the node and its children.

        This is called top-down, meaning that parent nodes will have their
        _on_exit_tree method called before their children.
        """
        if not self._is_in_active_tree:
            return
        self._on_exit_tree()
        self._is_in_active_tree = False
        for child in self._children:
            child._exit_tree()

    def _ready(self) -> None:
        """
        Internal method to handle the ready state.

        This method is called after a node and all its children have entered
        the tree, and is responsible for setting the _is_ready flag and
        calling the _on_ready hook recursively on the node and its children.

        This is called depth-first, meaning that child nodes will
        have their _on_ready method called before their parent nodes.
        """
        for child in self._children:
            child._ready()
        if self._is_ready:
            return
        self._on_ready()
        self._is_ready = True

    def _update(self, dt: float) -> None:
        """
        Updates the node and its children.

        This method is called every frame by the engine to update the node's
        state. It first calls the _on_update hook for the current node,
        and then recursively updates all child nodes.

        The dt (delta time) parameter represents the time elapsed since the
        last update call, allowing for frame-rate independent updates.
        """
        if not self._enabled:
            return
        self._on_update(dt)
        for child in self._children:
            child._update(dt)

    def _draw(self) -> None:
        """
        Draws the node and its children.

        This method is called every frame by the engine to render the node.
        It first calls the _draw hook for the current node, and then
        recursively draws all child nodes.

        The rendering order is determined by the scene graph hierarchy,
        with parent nodes being drawn before their children.
        """
        if not self._visible:
            return
        self._on_draw()
        for child in self._children:
            child._draw()

    def _process_deferred_deletions(self) -> None:
        """
        Processes deferred deletions for the node and its children.

        This method is called at the end of the update cycle to remove any
        nodes that have been marked for deletion. It first processes
        deferred deletions for all child nodes, and then checks if the
        current node is queued for deletion. If it is, the node is removed
        from its parent and cleaned up.

        This ensures that nodes are safely removed from the scene graph
        without disrupting ongoing updates or rendering.
        """
        for child in self._children[:]:
            child._process_deferred_deletions()
            if child._queued_for_deletion:
                self.remove_child(child)


class RootNode(Node):
    """
    A special node that serves as the root of the scene graph.
    This node is always present and cannot be removed from the scene.

    It is responsible for managing the overall structure of the scene graph
    and serves as the parent for all other nodes in the scene.
    """

    def __init__(self, scene: Scene2D | None = None, name: str = "Root") -> None:
        super().__init__(name=name)
        self._is_in_active_tree = True
        self._is_ready = True
        self._scene = scene

    @property
    def scene(self) -> Scene2D | None:
        """
        The scene that this root node belongs to.
        This property provides access to the scene that this root node
        belongs to, allowing for interaction with the scene's properties
        and methods.
        """
        return self._scene
