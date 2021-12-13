import os
from random import choice, random
from types import SimpleNamespace
from typing import Dict, List, Optional
from uuid import uuid4

from planet.living_things.dna.genes import Gene
from utils.logger import get_logger


class Cell(object):
    def __init__(self, run_path: str, configuration: SimpleNamespace) -> None:
        """
        Args:
            run_path (str): path to the actual run to store stuff.
        """
        self.configuration = configuration
        """ Run configuration """

        self.cell_name = f"{self.__class__.__name__}_{uuid4()}"

        self.logger = get_logger(log_folder=os.path.join(run_path, "logs"), log_name=self.cell_name)
        self.logger.info(f"Cell creation: {self.__class__.__name__} ({self.cell_name})")
        """ Cell logger """

        self.energy: int = 0
        """ The ennergy is the base fuel of the cell. """

        self.nucleotids = ["A", "T", "C", "G"]
        """ List of possible nucleotids """

        self.gene_list: List[Gene] = []
        """ Genes allow cells to have a variety of traits. """

        self._generate_dna()
        self._get_aquiered_genes()
        """ DNA is the genetic code of the cell. Generates it and get first genes. """

    def _generate_dna(self) -> None:
        # DNA size is provided in Mbp, so x 1000000
        self.dna = "".join([choice(self.nucleotids) for _ in range(int(self.configuration.cells.dna_size * 1_000_000))])

    def _get_aquiered_genes(self) -> None:
        old_gene_list = self.gene_list
        for gene in self.gene_pool:
            if gene.sequence in self.dna and not gene.acquired:
                self.logger.info(f"Acquisition of gene {gene.name} to process {gene.process_component}")
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
        Mutate the cell.
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
        """ Check if the cell can process the element """
        processing_facilities = [key for key in dir(self) if "processing" in key]
        for facility in processing_facilities:
            for key in self.__getattribute__(facility):
                if key == element:
                    return self.__getattribute__(facility)[key]

    def _find_breathable_gas(self, air_composition: Dict[str, float]) -> Optional[Dict[str, str]]:
        """
        Find breathable gas
        """
        breathable_gas = {
            gas: compo
            for gas, compo in air_composition.items()
            if gas in [gene.process_component for gene in self.gene_list if gene.acquired]
        }
        if len(breathable_gas.keys()) == 0:
            return None
        else:
            return breathable_gas

    def breathe(self, air_composition: Dict[str, float]) -> None:
        """
        Breathe in air
        """
        possible_breathing = self._find_breathable_gas(air_composition)
        if possible_breathing is not None:
            # Up ennergy with the one that have been found
            for gas, proportion in possible_breathing.items():
                # Increase ennergy regarding the proportion of the gas
                self.logger.debug(f"Breathing {gas}: {proportion}%, {proportion} energy points restaured")
                # Here, the energy restaured should correspond to the actual energy of the element
                if self.energy + proportion < self.configuration.cells.energy.maximum:
                    self.energy += proportion
                else:
                    self.logger.info(f"Cell energy is filled up, by breathing {gas}")
                    self.energy = self.max_energy

    def reproduce(self) -> None:
        """
        Reproduce the cell
        """
        # Reproduction uses energy no matter the success
        self.energy -= self.configuration.cells.reproduction.energy_cost
        # Chance to reproduce

    def eat(self, food_composition: Dict[str, float]) -> None:
        """
        Eat food
        """
        food = "stuff"
        energy = 42
        self.logger.debug(f"TODO: Eating {food}: {energy} energy points restaured")

    def sleep(self) -> None:
        """
        Sleep
        """
        self.logger.debug("TODO: Sleeping")
