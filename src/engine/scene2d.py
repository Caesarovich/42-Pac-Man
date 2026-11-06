from typing import TYPE_CHECKING

from engine import RootNode2D

if TYPE_CHECKING:
    from engine import SceneManager


class Scene2D:
    # HOOKS
    def _on_enter(self) -> None:
        """
        Hook method called when the scene is entered.
        Override this method to perform setup tasks.
        """

    def _on_exit(self) -> None:
        """
        Hook method called when the scene is exited.
        Override this method to perform cleanup tasks.
        """

    def _on_update(self, dt: float) -> None:
        """
        Hook method called every frame to update the scene.
        Override this method to implement custom update logic.
        """

    def _on_draw(self) -> None:
        """
        Hook method called every frame to draw the scene.
        Override this method to implement custom drawing logic.
        """

    # PRIVATE METHODS
    def _update(self, dt: float) -> None:
        """
        Updates the scene.
        This method is called every frame to update the scene's state.
        """
        self._on_update(dt)
        self.root._update(dt)

    def _draw(self) -> None:
        """
        Draws the scene.
        This method is called every frame to render the scene.
        """
        self._on_draw()
        self.root._draw()

    def _process_deferred_deletions(self) -> None:
        """
        Processes deferred deletions for the scene.
        This method should be called after the update to ensure that any
        nodes marked for deletion are properly removed from the scene.
        """
        self.root._process_deferred_deletions()

    def _enter(self) -> None:
        """
        Called when the scene is entered.
        """
        self._on_enter()

    def _exit(self) -> None:
        """
        Called when the scene is exited.
        """
        self._on_exit()

    def __init__(self, name: str) -> None:
        self.manager: SceneManager | None = None
        self.root = RootNode2D(scene=self, name=name)
