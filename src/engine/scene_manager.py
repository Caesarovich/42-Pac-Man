from typing import TYPE_CHECKING, Literal

from engine import Scene2D

if TYPE_CHECKING:
    from engine.engine import Engine

type SceneManagerPendingOperation = (
    tuple[Literal["push"], Scene2D]
    | tuple[Literal["pop"], None]
    | tuple[Literal["replace"], Scene2D]
)


class SceneManager:
    """
    Manages a stack of scenes, allowing for scene transitions and updates.
    """

    # PROPERTIES
    @property
    def current_scene(self) -> Scene2D | None:
        return self._stack[-1] if self._stack else None

    # PUBLIC METHODS
    def push(self, scene: Scene2D) -> None:
        """
        Push a new scene onto the stack.
        The new scene will become the current scene.
        """
        self._pending.append(("push", scene))

    def pop(self) -> None:
        """
        Pop the current scene from the stack.
        The previous scene will become the current scene.
        """
        self._pending.append(("pop", None))

    def replace(self, scene: Scene2D) -> None:
        """
        Replace the current scene with a new scene.
        The new scene will become the current scene.
        """
        self._pending.append(("replace", scene))

    def clear_immediately(self) -> None:
        """
        Clear all scenes from the stack immediately.
        This is useful when you want to exit the game or reset the scene stack.
        """
        while self._stack:
            old = self._stack.pop()
            old._exit()

    # PRIVATE METHODS
    def __init__(self, engine: Engine) -> None:
        self._stack: list[Scene2D] = []
        self._pending: list[SceneManagerPendingOperation] = []
        self._engine = engine

    def _apply_pending(self) -> None:
        """
        Apply all pending scene operations (push, pop, replace).
        This method should be called at the end of the frame to ensure
        that scene transitions occur after all updates are complete.
        """
        for op, scene in self._pending:
            if op == "push":
                assert scene is not None
                scene.manager = self
                self._stack.append(scene)
                scene._enter()
            elif op == "pop" and self._stack:
                old = self._stack.pop()
                old._exit()
            elif op == "replace":
                if self._stack:
                    old = self._stack.pop()
                    old._exit()
                assert scene is not None
                scene.manager = self
                self._stack.append(scene)
                scene._enter()
        self._pending.clear()

    def _update(self, dt: float) -> None:
        """
        Update the current scene.
        This method is called every frame to update the scene's state.
        """
        if self.current_scene:
            self.current_scene._update(dt)

    def _process_deferred_deletions(self) -> None:
        """
        Process deferred deletions for the current scene.
        This method should be called after the update to ensure that any
        nodes marked for deletion are properly removed from the scene.
        """
        if self.current_scene:
            self.current_scene._process_deferred_deletions()

    def _draw(self) -> None:
        """
        Draw the current scene.
        This method is called every frame to render the scene.
        """
        if self.current_scene:
            self.current_scene._draw()
