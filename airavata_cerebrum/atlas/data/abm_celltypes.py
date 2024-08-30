import os
import typing
import allensdk.core.cell_types_cache
import allensdk.api.queries.cell_types_api
import allensdk.api.queries.glif_api

from ..log.logging import LOGGER


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

    def run(self, in_stream, **run_params):
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

    def run(self, in_stream, **run_params):
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
        #
        LOGGER.debug("CTDbCellApiQuery Args : %s", rarg)
        ctxa = allensdk.api.queries.cell_types_api.CellTypesApi()
        ct_list = ctxa.list_cells_api(species=rarg["species"])
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


class CTDbCellAttrMapper:
    def __init__(self, **init_params):
        """
        Attribute value mapper

        Parameters
        ----------
        attribute : str
           Attribute of the cell type; key of the cell type descr. dict
        """
        self.attr = init_params["attribute"]

    def xform(self, in_iter: typing.Iterable, **params):
        """
        Get values from cell type descriptions

        Parameters
        ----------
        in_iter : Iterator
           iterator of cell type descriptions
        attribute : str
           Attribute of the cell type; key of the cell type descr. dict

        Returns
        -------
        value_iter: iterator
           iterator of values from cell type descriptions for given attribute
        """
        return iter(x[self.attr] for x in in_iter)


class CTDbCellAttrFilter:
    def __init__(self, **init_params):
        self.name = __name__ + ".CTDbCellAttrFilter"
        self.key_fn = lambda x: x

    def xform(self, ct_iter, **params):
        """
        Filter cell type descriptions matching all the values for the given attrs.

        Parameters
        ----------
        ct_iter : Iterator
           iterator of cell type descriptions
        filter_params: requires the following keyword parameters
        {
            filters (mandatory): Iterater of triples [attribute, bin_op, value]
                attribute : attribute of the cell type;
                  key of the cell type descr. dict
                bin_op    : binary operation special function (mandatory)
                value     : attributes acceptable value (mandatory)
                  value in the cell type descr. dict
        }

        Returns
        -------
        ct_iter: iterator
           iterator of cell type descriptions
        """
        LOGGER.debug("CTDbCellAttrFilter Args : %s", params)
        filters_itr = params["filters"]
        if params and "key" in params and params["key"]:
            self.key_fn = lambda x: x[params["key"]]
        return iter(
            x
            for x in ct_iter
            if x and all(
                getattr(self.key_fn(x)[attr], bin_op)(val)
                for attr, bin_op, val in filters_itr
            )
        )


#
# Query and Xform Registers
#
ABMCT_QUERY_REGISTER = {
    "CTDbCellCacheQuery": CTDbCellCacheQuery,
    "CTDbCellApiQuery": CTDbCellApiQuery,
    "CTDbGlifApiQuery": CTDbGlifApiQuery,
    __name__ + ".CTDbCellCacheQuery": CTDbCellCacheQuery,
    __name__ + ".CTDbCellApiQuery": CTDbCellApiQuery,
    __name__ + ".CTDbGlifApiQuery": CTDbGlifApiQuery,
}

ABMCT_XFORM_REGISTER = {
    "CTDbCellAttrFilter": CTDbCellAttrFilter,
    __name__ + ".CTDbCellAttrFilter": CTDbCellAttrFilter,
    "CTDbCellAttrMapper": CTDbCellAttrMapper,
    __name__ + ".CTDbCellAttrMapper": CTDbCellAttrMapper,
}
