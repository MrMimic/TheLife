import os
from os.path import join
from types import SimpleNamespace
from typing import Any

import imageio
from matplotlib import pyplot as plt


class Drawer:
    def __init__(self, draw_folder: str, configuration: SimpleNamespace) -> None:
        self.draw_folder = draw_folder
        self.configuration = configuration

    def draw_world(self, day: int, world: Any) -> None:
        """
        Draw the world as a PNG image.

        Args:
            day (int): the day number.
            world (Any): the world to draw.
        """
        # Draw the base figure with the configuration
        plt.figure(figsize=(self.configuration.program.drawings.height, self.configuration.program.drawings.width))

        # Get the plot limits from the configuration
        plt.xlim(self.configuration.world.size)
        plt.ylim(self.configuration.world.size)

        # Draw the start of all cells
        plt.plot(0, 0, alpha=0.5, marker="o", color="black", markersize=5)

        # Now, all cells with their positions
        for individual in world.population:
            alpha = 0.1
            alpha_step = 0.9 / len(individual.positions)
            last_position = (0, 0)
            for position in individual.positions:
                x_values = [last_position[0], position[0]]
                y_values = [last_position[1], position[1]]
                plt.plot(x_values, y_values, color="red", alpha=alpha, linewidth=0.5, linestyle="-")
                if position != (0, 0):
                    # The alpha of the point must increase as the cell moves are looped from the first
                    plt.plot(position[0], position[1], alpha=alpha, marker="o", color="red", markersize=5)
                    alpha += alpha_step
                    last_position = position

        # Fix the middle of the plot
        ax = plt.gca()
        for spine in ["top", "bottom", "left", "right"]:
            ax.spines[spine].set_visible(False)
            ax.spines[spine].set_position("center")

        # Save this day as an image
        plt.savefig(fname=join(self.draw_folder, f"day_{day}.png"), dpi=self.configuration.program.drawings.dpi)

    def create_world_gif(self) -> None:
        """
        Create a gif from the images in the draw folder.
        """
        gif_path = join(self.draw_folder, f"{self.__class__.__name__}.gif")
        imageio.mimsave(
            gif_path, [imageio.imread(join(self.draw_folder, file_name)) for file_name in os.listdir(self.draw_folder)],
            format="GIF",
            duration=0.5)
