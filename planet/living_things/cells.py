import os
from random import choice, random
from types import SimpleNamespace
from typing import List, Optional, Tuple, Union
from uuid import uuid4

import numpy as np
from planet.earth import Biome
from planet.inanimated_elements.air_composition import Element
from planet.inanimated_elements.biomass_composition import Nutrient
from planet.living_things.dna.genes import Gene
from utils.data import directions
from utils.logger import get_logger
from utils.maths import compute_distance, point_is_in_map


class Cell(object):

    def __init__(self, run_path: str, configuration: SimpleNamespace, gene_pool: List[Gene]) -> None:
        """
        A cell is the basic unit of life on the planet.

        Args:
            run_path (str): path to the actual run to store stuff.
            configuration (SimpleNamespace): configuration of the run.
        """
        self.configuration = configuration
        """ Run configuration """

        self.cell_name = f"{self.__class__.__name__}_{uuid4()}"
        """ Cell name with an uniq UUID """

        self.logger = get_logger(log_folder=os.path.join(run_path, "logs"),
                                 log_name=self.cell_name,
                                 log_level=self.configuration.program.logs.level.upper())
        self.logger.info(f"Cell creation: {self.__class__.__name__} ({self.cell_name})")
        """ Cell logger """

        self.energy: int = 10
        """ The ennergy is the base fuel of the cell. """

        self.nucleotids = ["A", "T", "C", "G"]
        """ List of possible nucleotids """

        self.gene_list: List[Gene] = []
        """ Genes allow cells to have a variety of traits. """

        self.protected_codons: List[List[int]] = []
        """ Genes that are beneficial are protected from mutation. Here are their indexes."""

        self.gene_pool: List[Gene] = gene_pool
        """ Genetic attributes of specific cells."""

        self._generate_dna()
        self._get_aquiered_genes()
        """ DNA is the genetic code of the cell. Generates it and get first genes. """

        self.position: Tuple[int, int] = (0.5, 0.5)
        self.biome = None
        self.last_position: Tuple[int, int] = self.position
        self.positions: List[Tuple[int, int]] = [self.position]
        self.visited_biomes: List[Biome] = []
        """ Cell position on the planet. Initiated at 0.5 to stay in the middle of the biomes. """

        self.is_alive: bool = True
        """ Cell is alive or not. """

        self.color = np.random.rand(3, )
        """ Cell color, for plotting. """

    def _generate_dna(self) -> None:
        """
        The DNA is composed of 4 nucleotids.
        Its size is proivided as Mbp in the conf, then x1_000_000
        """
        self.dna = "".join([choice(self.nucleotids) for _ in range(int(self.configuration.cells.dna_size * 1_000_000))])

    def _get_aquiered_genes(self) -> None:
        """
        Stores a list of acquired genes as attributes.
        """
        old_gene_list = self.gene_list
        protected_codons = []
        for gene in self.gene_pool:
            if gene.sequence in self.dna and not gene.acquired:
                # Store their indexes if the gene is beneficial
                if gene.beneficial:
                    gene_start = self.dna.find(gene.sequence)
                    gene_stop = gene_start + len(gene.sequence)
                    protected_codons.append([gene_start, gene_stop])
                self.logger.info(
                    f"Acquisition of gene {gene.name} to process {gene.process_component} from {gene.compopent_from}")
                gene.acquired = True
            # The mutation lost the gene
            elif gene.sequence not in self.dna and gene.acquired:
                gene.acquired = False
        # Store acquired genes
        self.gene_list = [gene for gene in self.gene_pool if gene.acquired]
        # Store their indexes
        self.protected_codons = protected_codons

        if len(self.gene_list) > len(old_gene_list):
            self.logger.info(
                f"New gene acquired: {', '.join([gene.name for gene in [g for g in self.gene_list if g not in old_gene_list]])}"
            )
        elif len(self.gene_list) < len(old_gene_list):
            self.logger.info(
                f"Old gene lost: {', '.join([gene.name for gene in [g for g in old_gene_list if g not in self.gene_list]])}"
            )

    def mutate(self) -> None:
        """
        Mutate the cell DNA to get of loose genes.
        """
        # Short recap of the cell
        cell_genes = ', '.join([gene.name for gene in self.gene_list]) if len(self.gene_list) > 0 else None
        self.logger.info(f"Cell energy: {self.energy}, cell genes: {cell_genes} ({self.protected_codons})")

        # Mutate all nucleotides
        for nucleotid_index in range(len(self.dna)):
            # Generate a random number between 0 and 1 and mutate if needed
            if random() <= self.configuration.cells.evolution.mutation_rate_general:
                # If the nucleotid is inside a gene
                if any([nucleotid_index in list(range(pc[0], pc[1])) for pc in self.protected_codons]):
                    if random() <= self.configuration.cells.evolution.mutation_rate_in_genes:
                        self.logger.alert("Mutation in DNA in a gene.")
                        self._mutate_nucleotid(nucleotid_index)
                # Else, outside a gene, it already won the chance to mutate
                else:
                    self._mutate_nucleotid(nucleotid_index)

        # Once all mutations are done, check if new genes have been acquired
        self._get_aquiered_genes()

    def _mutate_nucleotid(self, nucleotid_index: int) -> None:
        """
        Change a nucleotid into another one in the DNA.

        Args:
            nucleotid_index (int): index of the nucleotid to mutate.
        """
        old_nucleotid = self.dna[nucleotid_index]
        possible_nucleotids = [nucleotid for nucleotid in self.nucleotids if nucleotid != old_nucleotid]
        new_nucleotid = choice(possible_nucleotids)
        new_dna = list(self.dna)
        new_dna[nucleotid_index] = new_nucleotid
        self.dna = "".join(new_dna)
        self.logger.debug(f"Mutation of {old_nucleotid} to {new_nucleotid} in position {nucleotid_index}")

    def can_process(self, element: str) -> bool:
        """
        Check if the cell can process the element.

        Args:
            element (str): element to process.

        Returns:
            bool: True if the cell can process the element.
        """
        processing_facilities = [key for key in dir(self) if "processing" in key]
        for facility in processing_facilities:
            for key in self.__getattribute__(facility):
                if key == element:
                    return self.__getattribute__(facility)[key]

    def _find_usable_resource(self, medium_composition: List[Union[Element, Nutrient]],
                              from_medium: str) -> Optional[List[Union[Element, Nutrient]]]:
        """
        Find a usable resource in the medium composition.

        Args:
            medium_composition (List[Union[Element, Nutrient]]): The list of resources found in the medium.

        Returns:
            Optional[List[Union[Element, Nutrient]]]: None if nothing cxan be process, list otherwise.
        """
        acquired_element_process = [gene.process_component for gene in self.gene_list if gene.acquired]
        try:
            usable_resource = [
                element for element in medium_composition.contains if element.name.lower() in acquired_element_process
            ]
        except AttributeError:  # The first biome contains nothing
            return None
        if len(usable_resource) == 0:
            return None
        else:
            self.logger.info(
                f"Found resources in biome ({from_medium}): {', '.join([element.name for element in usable_resource])}")
            return usable_resource

    def _restaure(self, resources: List[Union[Element, Nutrient]], mode: str) -> None:
        """
        Restaure the cell energy by using a medium and its genes.

        Args:
            resources (List[Union[Element, Nutrient]]): The list of resources found in the medium.
            mode (str): The mode of the restaurement (eating, breathing).
        """
        # Up ennergy with the one that have been found
        for resource in resources:
            # Increase ennergy regarding the proportion of the gas
            self.logger.info(f"Cell {mode} {resource.name}: {resource.percentage}%, {resource.energy} EU restaured")
            # Here, the energy restaured should correspond to the actual energy of the element
            if self.energy < self.configuration.cells.energy.maximum:
                if self.energy + resource.energy < self.configuration.cells.energy.maximum:
                    self.energy += resource.energy
                else:
                    self.logger.info(f"Cell EU is filled up, by {mode} {resource.name}")
                    self.energy = self.configuration.cells.energy.maximum

    def breathe(self) -> None:
        """
        Breathe the air of the planet to get energy from gas.

        Args:
            air_composition List[Element]: The list of resources found in the air.
        """
        mode = "breathing"
        possible_breathing = self._find_usable_resource(medium_composition=self.biome, from_medium=mode)
        if possible_breathing is not None:
            self._restaure(resources=possible_breathing, mode=mode)

    def eat(self) -> None:
        """
        Eat the biomass of the planet to get energy from food.

        Args:
            biomass_composition (List[Nutrient]): The list of resources found in the biomass.
        """
        mode = "eating"
        possible_nutrients = self._find_usable_resource(medium_composition=self.biome, from_medium=mode)
        if possible_nutrients is not None:
            self._restaure(resources=possible_nutrients, mode=mode)

    def _find_actual_biome(self, biomes: List[Biome], position: List[int]) -> Biome:
        """
        Find the actual biome of the cell.

        Args:
            biomes (List[Biome]): The list of biomes.
            position (List[int]): The position of the cell.

        Returns:
            Biome: The actual biome of the cell.
        """
        for biome in biomes:
            if point_is_in_map(map_coords=[biome.coord_1, biome.coord_2], point_coordinates=position):
                return biome

    def move(self, biomes: List[Biome]) -> None:
        """
        Move the cell to a new position.
        """
        # Use this method to check is the first biome has been inserted
        if self.visited_biomes == []:
            self.visited_biomes.append(self._find_actual_biome(biomes=biomes, position=self.position))

        # Check if the cell can move
        if self.energy > 0:

            # Maximum radius is computed from the energy of the cell (one EU = one DU)
            max_steps = self.energy / 2
            self.last_position = self.position
            steps = 0
            while steps < max_steps:
                direction = choice(list(directions.keys()))
                # Compute the new position
                new_position = (self.position[0] + directions[direction][0],
                                self.position[1] + directions[direction][1])

                # Check if the new position is not out of the map
                map_size = self.configuration.world.size
                map_coords = [[-map_size, -map_size], [map_size, map_size]]
                if point_is_in_map(map_coords=map_coords, point_coordinates=new_position):
                    self.logger.debug(f"Cell moved from {self.position} to {new_position} (direction: {direction})")
                    self.position = new_position
                    steps += 1
                    self.energy -= 1  # Moving forward cost energy

                    # Check if the new position is in a new biome
                    self.biome = self._find_actual_biome(biomes=biomes, position=self.position)

            # Keep a track of all positions of the cell for drawing
            self.positions.append(self.position)
            self.visited_biomes.append(self.biome)

            # Check the distance that the cell moved
            distance = compute_distance(self.last_position, self.position)
            self.logger.info(
                f"Cell moved {distance} distance units (from {self.last_position} to {self.position}) in {steps} steps")

    def reproduce(self) -> None:
        """
        Reproduce the cell.
        """
        # Reproduction uses energy no matter the success
        self.energy -= self.configuration.cells.reproduction.energy_cost
        # Chance to reproduce

    def sleep(self, day: int) -> None:
        """
        The end of the day. An amount of energy is filled up during the night, or the cell ends its life.

        Args:
            day (int): The day of the simulation.
        """
        # The cell dies of exhaustion
        if self.energy <= 0:
            distance = compute_distance((0, 0), self.position)
            self.logger.info(f"No more energy on day {day}. Cell reached {self.position} after {distance}DU")
            self.is_alive = False
