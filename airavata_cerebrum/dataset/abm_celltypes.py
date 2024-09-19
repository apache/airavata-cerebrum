import os
import typing
import logging
import allensdk.core.cell_types_cache
import allensdk.api.queries.cell_types_api
import allensdk.api.queries.glif_api
import traitlets

from .. import base


def _log():
    return logging.getLogger(__name__)


class CTDbCellCacheQuery(base.DbQuery):
    class QryTraits(traitlets.HasTraits):
        download_base = traitlets.Unicode()
        species = traitlets.Unicode()
        manifest = traitlets.Unicode()
        cells = traitlets.Unicode()

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

    def run(
        self,
        in_iter: typing.Iterable | None,
        **params: typing.Dict[str, typing.Any],
    ) -> typing.Iterable | None:
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
            {**default_args, **params} if params is not None else default_args
        )
        #
        _log().debug("CTDbCellCacheQuery Args : %s", rarg)
        self.manifest_file = os.path.join(self.download_base, rarg["mainfest"])
        self.cells_file = os.path.join(self.download_base, rarg["cells"])
        ctc = allensdk.core.cell_types_cache.CellTypesCache(
            manifest_file=self.manifest_file
        )
        ct_list = ctc.get_cells(file_name=self.cells_file, species=rarg["species"])
        _log().debug("CTDbCellCacheQuery CT List : %d", len(ct_list))
        return ct_list

    @classmethod
    def trait_type(cls) -> type[traitlets.HasTraits]:
        return cls.QryTraits


class CTDbCellApiQuery(base.DbQuery):
    class QryTraits(traitlets.HasTraits):
        species = traitlets.Unicode()

    def __init__(self, **params):
        self.name = "allensdk.api.queries.cell_types_api.CellTypesApi"

    def run(
        self,
        in_iter: typing.Iterable | None,
        **run_params
    ) -> typing.Iterable:
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
        _log().debug("CTDbCellApiQuery Args : %s", rarg)
        ctxa = allensdk.api.queries.cell_types_api.CellTypesApi()
        ct_list = ctxa.list_cells_api(species=sp_arg)
        _log().debug("CTDbCellApiQuery CT List : %d", len(ct_list))
        return ct_list

    @classmethod
    def trait_type(cls) -> type[traitlets.HasTraits]:
        return cls.QryTraits


class CTDbGlifApiQuery(base.DbQuery):
    class QryTraits(traitlets.HasTraits):
        key = traitlets.Unicode()
        first = traitlets.Bool()

    def __init__(self, **params):
        self.name = "allensdk.api.queries.glif_api.GlifApi"
        self.glif_api = allensdk.api.queries.glif_api.GlifApi()
        self.key_fn = lambda x: x

    def run(
        self,
        in_iter: typing.Iterable | None,
        **params
    ) -> typing.Iterable | None:

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
        if not in_iter:
            return None
        default_args = {"first": False, "key": None}
        rarg = {**default_args, **params} if params else default_args
        _log().debug("CTDbGlifApiQuery Args : %s", rarg)
        if rarg["key"]:
            self.key_fn = lambda x: x[rarg["key"]]
        if bool(rarg["first"]) is False:
            return iter(
                {
                    "input": x,
                    "glif": self.glif_api.get_neuronal_models(self.key_fn(x)),
                }
                for x in in_iter
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
                for x in in_iter
                if x
            )

    @classmethod
    def trait_type(cls) -> type[traitlets.HasTraits]:
        return cls.QryTraits


#
# ------- Query and Xform Registers -----
#
def query_register() -> typing.List[type[base.DbQuery]]:
    return [
        CTDbCellCacheQuery,
        CTDbCellApiQuery,
        CTDbGlifApiQuery,
    ]


def xform_register() -> typing.List[type[base.OpXFormer]]:
    return []
