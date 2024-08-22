import os
import typing
import jsonpath
import allensdk.core.cell_types_cache
import allensdk.api.queries.cell_types_api
import allensdk.api.queries.glif_api

from ..log.logging import LOGGER


class CTDbCellCacheQuery:
    def __init__(self, **init_params):
        """
        Initialixe Cache Query
        Parameters
        ----------
        download_base : str
           File location to store the manifest and the cells.json files

        """
        self.name = "allensdk.core.cell_types_cache.CellTypesCache"
        self.download_base = init_params["download_base"]

    def run(self, **qry_params):
        """
        Get the cell types information from allensdk.core.cell_types_cache.CellTypesCache

        Parameters
        ----------
        download_base : str
           File location to store the manifest and the cells.json files
        species : list
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
            {**default_args, **qry_params} if qry_params is not None else default_args
        )
        #
        self.manifest_file = os.path.join(self.download_base, rarg["mainfest"])
        self.cells_file = os.path.join(self.download_base, rarg["cells"])
        ctc = allensdk.core.cell_types_cache.CellTypesCache(
            manifest_file=self.manifest_file
        )
        ct_list = ctc.get_cells(file_name=self.cells_file, species=rarg["species"])
        return ct_list


class CTDbCellApiQuery:
    def __init__(self, **init_params):
        self.name = "allensdk.api.queries.cell_types_api.CellTypesApi"

    def run(self, **qry_params):
        """
        Get the cell types information from allensdk.api.queries.cell_types_api.CellTypesApi

        Parameters
        ----------
        species : list
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
        default_args = {
            "species": None,
            "mainfest": "manifest.json",
            "cells": "cells.json",
        }
        rarg = (
            {**default_args, **qry_params} if qry_params is not None else default_args
        )
        ctxa = allensdk.api.queries.cell_types_api.CellTypesApi()
        return ctxa.list_cells_api(species=rarg["species"])


class CTDbGlifApiQuery:
    def __init__(self, **init_params):
        self.name = "allensdk.api.queries.glif_api.GlifApi"
        self.glif_api = allensdk.api.queries.glif_api.GlifApi()
        self.key_fn = lambda x: x

    def run(self, **params):
        """
        Get neuronal models using GlifApi for a given iterator of specimen ids

        Parameters
        ----------
        **params: {
            "input"    : Input Iterator (mandatory)
            "key"   : Access value for specimen ids (default: None),
            "first" : bool (default: False)
        }

        Returns
        -------
        dict : {spec_id : model}
          glif neuronal_models
        """
        default_args = {"first": False, "key": None}
        rarg = {**default_args, **params} if params is not None else default_args
        input_iter = params["input"]
        if rarg["key"]:
            self.key_fn = lambda x: x[rarg["key"]]
        if bool(rarg["first"]) is False:
            return iter(
                {
                    "input": x,
                    "glif": self.glif_api.get_neuronal_models(self.key_fn(x)),
                }
                for x in input_iter
                if x is not None
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
                if x is not None
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

    def map(self, in_iter: typing.Iterable, **map_params):
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
        self.name = "Filter by attribute"
        self.key_fn = lambda x: x

    def filter(self, ct_iter, **params):
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
        filters_itr = params["filters"]
        if params and "key" in params and params["key"]:
            self.key_fn = lambda x: x[params["key"]]
        return iter(
            x
            for x in ct_iter
            if x is not None
            and all(
                getattr(self.key_fn(x)[attr], bin_op)(val)
                for attr, bin_op, val in filters_itr
            )
        )


class CTDbCellAttrJPathFilter:
    def __init__(self, **init_params):
        self.name = "Filter by json path attribute"

    def apply_filter(self, ctx, filter_exp, dest_path):
        fx = jsonpath.findall(filter_exp, ctx)
        try:
            return (
                jsonpath.patch.apply(
                    [{"op": "replace", "path": dest_path, "value": fx}], ctx
                )
                if fx is not None
                else []
            )
        except jsonpath.JSONPatchError as jpex:
            print("JPEX : ", jpex)
            print("FX: ", fx)
            pass

    def filter(self, ct_iter, **filter_params):
        """
        Filter cell type descriptions matching all the values for the
        given attrs using JSONPath expressions.

        Parameters
        ----------
        ct_iter : Iterator
           iterator of cell type descriptions
        filter_params: requires the following keyword parameters
          {
            filter_exp : JSON path filter expression
            dest_path : JSON Path destination
          }

        Returns
        -------
        ct_iter: iterator
           iterator of cell type descriptions
        """
        filter_exp = filter_params["filter_exp"]
        dest_path = filter_params["dest_path"]
        return iter(
            self.apply_filter(x, filter_exp, dest_path)
            for x in ct_iter
            if x is not None
        )


def select_ct_neuronal_models(ct_desc, attribute, value):
    """
    Filter neuronal_models in the give cell type desc. that had the
      value for given attribute

    Parameters
    ----------
    ct_desc : dict
       Cell types description dictionary with neuronal_models entry
    attribute : str
       Attribute of the cell type; key of the cell type descr. dict
    value : str
       Acceptive value in the cell type descr. dict for the attribute


    Returns
    -------
    models_iter: iterator
       iterator of neuronal_models which includes the value for the attribute
    """
    if ct_desc is None or "neuronal_models" not in ct_desc:
        return None
    return (x for x in ct_desc["neuronal_models"] if value in x[attribute])


def filter_ct_neuronal_models(ct_desc, attribute, value):
    fltr_models = select_ct_neuronal_models(ct_desc, attribute, value)
    if fltr_models:
        ct_desc["neuronal_models"] = list(fltr_models)
        return ct_desc
    return ct_desc


def filter_first_glif_models(ct_desc, spid_attr, filter_attr, filter_value):
    spec_id = ct_desc[spid_attr]
    qry_result = CTDbGlifApiQuery().run(iter=iter(spec_id), first=True)
    return filter_ct_neuronal_models(
        (x[spec_id] for x in qry_result), filter_attr, filter_value
    )


ABMCT_QUERY_REGISTER = {
    "CTDbCellCacheQuery": CTDbCellCacheQuery,
    "CTDbCellApiQuery": CTDbCellApiQuery,
    "CTDbGlifApiQuery": CTDbGlifApiQuery,
    __name__ + ".CTDbCellCacheQuery": CTDbCellCacheQuery,
    __name__ + ".CTDbCellApiQuery": CTDbCellApiQuery,
    __name__ + ".CTDbGlifApiQuery": CTDbGlifApiQuery,
}

ABMCT_FILTER_REGISTER = {
    "CTDbCellAttrFilter": CTDbCellAttrFilter,
    __name__ + ".CTDbCellAttrFilter": CTDbCellAttrFilter,
    "CTDbCellAttrJPathFilter": CTDbCellAttrJPathFilter,
    __name__ + ".CTDbCellAttrJPathFilter": CTDbCellAttrJPathFilter,
}

ABMCT_MAPPER_REGISTER = {
    "CTDbCellAttrMapper": CTDbCellAttrMapper,
    __name__ + ".CTDbCellAttrMapper": CTDbCellAttrMapper,
}
