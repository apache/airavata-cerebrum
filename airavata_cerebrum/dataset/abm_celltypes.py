import os
import typing
import allensdk.core.cell_types_cache
import allensdk.api.queries.cell_types_api
import allensdk.api.queries.glif_api

from .. import base
from ..util.log.logging import LOGGER


class CTDbCellCacheQuery:
    def __init__(self, **params):
        """
        Initialixe Cache Query
        Parameters
        ----------
        download_base : str
           File location to store the manifest and the cells.json files

        """
        self.name = "allensdk.core.cell_types_cache.CellTypesCache"
        self.download_base = params["download_base"]

    def run(self, in_stream: typing.Iterable, **run_params) -> typing.Iterable:
        """
        Get the cell types information from allensdk.core.cell_types_cache.CellTypesCache

        Parameters
        ----------
        run_params: dict with the following keys:
            species : list [default: None]
               Should contain one of CellTypesApi.MOUSE or CellTypesApi.HUMAN
            manifest : str [default: manifest.json]
               Name of the manifest json file
            cells : str [default: cells.json]
               Name of the manifest json file

        Returns
        -------
        dict of three elements:
        {
            manifest : manifest file location,
            cells : cells json file location,
            result : list of cell type descriptions; each of which is a dict
        }
        """
        #
        default_args = {
            "species": None,
            "mainfest": "manifest.json",
            "cells": "cells.json",
        }
        rarg = (
            {**default_args, **run_params} if run_params is not None else default_args
        )
        #
        LOGGER.debug("CTDbCellCacheQuery Args : %s", rarg)
        self.manifest_file = os.path.join(self.download_base, rarg["mainfest"])
        self.cells_file = os.path.join(self.download_base, rarg["cells"])
        ctc = allensdk.core.cell_types_cache.CellTypesCache(
            manifest_file=self.manifest_file
        )
        ct_list = ctc.get_cells(file_name=self.cells_file, species=rarg["species"])
        LOGGER.debug("CTDbCellCacheQuery CT List : %d", len(ct_list))
        return ct_list


class CTDbCellApiQuery:
    def __init__(self, **params):
        self.name = "allensdk.api.queries.cell_types_api.CellTypesApi"

    def run(self, in_stream: typing.Iterable, **run_params) -> typing.Iterable:
        """
        Get the cell types information from allensdk.api.queries.cell_types_api.CellTypesApi

        Parameters
        ----------
        run_params: dict with the following keys:
          species : list [default: None]
             Should contain one of CellTypesApi.MOUSE or CellTypesApi.HUMAN

        Returns
        -------
        dict of on elements:
        {
           result : list
           A list of descriptions of cell types; each description is a dict
        }
        """
        #
        default_args = {"species": None}
        rarg = (
            {**default_args, **run_params} if run_params else default_args
        )
        sp_arg = [rarg["species"]] if rarg["species"] else None
        #
        LOGGER.debug("CTDbCellApiQuery Args : %s", rarg)
        ctxa = allensdk.api.queries.cell_types_api.CellTypesApi()
        ct_list = ctxa.list_cells_api(species=sp_arg)
        LOGGER.debug("CTDbCellApiQuery CT List : %d", len(ct_list))
        return ct_list


class CTDbGlifApiQuery:
    def __init__(self, **init_params):
        self.name = "allensdk.api.queries.glif_api.GlifApi"
        self.glif_api = allensdk.api.queries.glif_api.GlifApi()
        self.key_fn = lambda x: x

    def run(self, input_iter, **params):
        """
        Get neuronal models using GlifApi for a given iterator of specimen ids

        Parameters
        ----------
        input_iter : Input Iterator of objects with specimen ids (mandatory)
        params: dict ofthe following keys
        {
            "key"   : Access key to obtain specimen ids (default: None),
            "first" : bool (default: False)
        }

        Returns
        -------
        dict : {spec_id : model}
          glif neuronal_models
        """
        default_args = {"first": False, "key": None}
        rarg = {**default_args, **params} if params else default_args
        LOGGER.debug("CTDbGlifApiQuery Args : %s", rarg)
        if rarg["key"]:
            self.key_fn = lambda x: x[rarg["key"]]
        if bool(rarg["first"]) is False:
            return iter(
                {
                    "input": x,
                    "glif": self.glif_api.get_neuronal_models(self.key_fn(x)),
                }
                for x in input_iter
                if x
            )
        else:
            return iter(
                {
                    "ct": x,
                    "glif": next(
                        iter(self.glif_api.get_neuronal_models(self.key_fn(x))), None
                    ),
                }
                for x in input_iter
                if x
            )


#
# Query and Xform Registers
#
base.DbQuery.register(CTDbCellCacheQuery)
base.DbQuery.register(CTDbGlifApiQuery)
base.DbQuery.register(CTDbCellApiQuery)
#


def query_register():
    return [
        CTDbCellCacheQuery,
        CTDbCellApiQuery,
        CTDbGlifApiQuery,
    ]


def xform_register():
    return []
