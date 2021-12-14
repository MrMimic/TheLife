import os
from math import hypot
from random import choice, random
from types import SimpleNamespace
from typing import List, Optional, Tuple, Union
from uuid import uuid4

from planet.inanimated_elements.air_composition import Element
from planet.inanimated_elements.biomass_composition import Nutrient
from planet.living_things.dna.genes import Gene
from utils.data import directions
from utils.logger import get_logger


class Cell(object):
    def __init__(self, run_path: str, configuration: SimpleNamespace) -> None:
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

        self.logger = get_logger(log_folder=os.path.join(run_path, "logs"), log_name=self.cell_name)
        self.logger.info(f"Cell creation: {self.__class__.__name__} ({self.cell_name})")
        """ Cell logger """

        self.energy: int = 10
        """ The ennergy is the base fuel of the cell. """

        self.nucleotids = ["A", "T", "C", "G"]
        """ List of possible nucleotids """

        self.gene_list: List[Gene] = []
        """ Genes allow cells to have a variety of traits. """

        self._generate_dna()
        self._get_aquiered_genes()
        """ DNA is the genetic code of the cell. Generates it and get first genes. """

        self.position: Tuple[int, int] = (0, 0)
        """ Cell position on the planet. """

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
        for gene in self.gene_pool:
            if gene.sequence in self.dna and not gene.acquired:
                self.logger.info(
                    f"Acquisition of gene {gene.name} to process {gene.process_component} from {gene.compopent_from}")
                gene.acquired = True
            # The mutation lost the gene
            elif gene.sequence not in self.dna and gene.acquired:
                gene.acquired = False
        # Store acquired genes
        self.gene_list = [gene for gene in self.gene_pool if gene.acquired]
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
        self.logger.info(f"Cell energy: {self.energy}, cell genes: {cell_genes}")

        # Mutate all nucleotides
        for nucleotid_index in range(len(self.dna)):
            # Generate a random number between 0 and 1 and mutate if needed
            if random() <= self.configuration.cells.evolution.mutation_rate:
                # Simply pick a new nucleotid randomly from now
                old_nucleotid = self.dna[nucleotid_index]
                possible_nucleotids = [nucleotid for nucleotid in self.nucleotids if nucleotid != old_nucleotid]
                new_nucleotid = choice(possible_nucleotids)
                new_dna = list(self.dna)
                new_dna[nucleotid_index] = new_nucleotid
                self.dna = "".join(new_dna)
                self.logger.debug(f"Mutation of {old_nucleotid} to {new_nucleotid} in position {nucleotid_index}")
        # Once all mutations are done, check if new genes have been acquired
        self._get_aquiered_genes()

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

    def _find_usable_resource(
            self, medium_composition: List[Union[Element, Nutrient]]) -> Optional[List[Union[Element, Nutrient]]]:
        """
        Find a usable resource in the medium composition.

        Args:
            medium_composition (List[Union[Element, Nutrient]]): The list of resources found in the medium.

        Returns:
            Optional[List[Union[Element, Nutrient]]]: None if nothing cxan be process, list otherwise.
        """
        acquired_element_process = [gene.process_component for gene in self.gene_list if gene.acquired]
        usable_resource = [
            element for element in medium_composition if element.name.lower() in acquired_element_process
        ]
        if len(usable_resource) == 0:
            return None
        else:
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
            self.logger.debug(
                f"Cell {mode} {resource.name}: {resource.percentage}%, {resource.energy} energy points restaured")
            # Here, the energy restaured should correspond to the actual energy of the element
            if self.energy < self.configuration.cells.energy.maximum:
                if self.energy + resource.energy < self.configuration.cells.energy.maximum:
                    self.energy += resource.energy
                else:
                    self.logger.info(f"Cell energy is filled up, by {mode} {resource.name}")
                    self.energy = self.configuration.cells.energy.maximum

    def breathe(self, air_composition: List[Element]) -> None:
        """
        Breathe the air of the planet to get energy from gas.

        Args:
            air_composition List[Element]: The list of resources found in the air.
        """
        possible_breathing = self._find_usable_resource(medium_composition=air_composition)
        if possible_breathing is not None:
            self._restaure(resources=possible_breathing, mode="breathing")

    def eat(self, biomass_composition: List[Nutrient]) -> None:
        """
        Eat the biomass of the planet to get energy from food.

        Args:
            biomass_composition (List[Nutrient]): The list of resources found in the biomass.
        """
        possible_nutrients = self._find_usable_resource(medium_composition=biomass_composition)
        if possible_nutrients is not None:
            self._restaure(resources=possible_nutrients, mode="eating")

    def move(self) -> None:
        """
        Move the cell to a new position.
        """
        # Check if the cell can move
        if self.energy > 0:
            # Maximum radius is computed from the energy of the cell (one energy unit = one distance unit)
            max_steps = self.energy / 2
            original_position = self.position
            steps = 0
            while steps < max_steps:
                direction = choice(list(directions.keys()))
                # Compute the new position
                new_position = (self.position[0] + directions[direction][0],
                                self.position[1] + directions[direction][1])
                self.logger.debug(f"Cell moved from {self.position} to {new_position} (direction: {direction})")
                self.position = new_position
                steps += 1
                # Moving forward cost energy
                self.energy -= 1
            # If the cell has not moved, it is not able to move anymore
            distance = round(hypot(original_position[0] - self.position[0], original_position[1] - self.position[1]), 3)
            self.logger.info(
                f"Cell moved {distance} distance units (from {original_position} to {self.position}) in {steps} steps")

    def reproduce(self) -> None:
        """
        Reproduce the cell.
        """
        # Reproduction uses energy no matter the success
        self.energy -= self.configuration.cells.reproduction.energy_cost
        # Chance to reproduce

    def sleep(self) -> None:
        """
        Sleep.
        """
        self.logger.debug("TODO: Sleeping")
