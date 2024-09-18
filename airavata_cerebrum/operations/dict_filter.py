import typing
import traitlets
#
from ..util.log.logging import LOGGER
from .. import base


class IterAttrMapper(base.OpXFormer):
    class MapperTraits(traitlets.HasTraits):
        attribute = traitlets.Unicode()

    def __init__(self, **init_params):
        """
        Attribute value mapper

        Parameters
        ----------
        attribute : str
           Attribute of the cell type; key of the cell type descr. dict
        """
        self.name = __name__ + ".IterAttrMapper"
        self.attr = init_params["attribute"]

    def xform(
        self,
        in_iter: typing.Iterable | None,
        **params
    ) -> typing.Iterable | None:
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
        if not in_iter:
            return None
        return iter(x[self.attr] for x in in_iter)

    @classmethod
    def trait_type(cls):
        return cls.MapperTraits


class IterAttrFilter:
    class FilterTraits(traitlets.HasTraits):
        key = traitlets.Unicode()
        filters = traitlets.List()

    def __init__(self, **init_params):
        self.name = __name__ + ".IterAttrFilter"
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
        LOGGER.info("CTDbCellAttrFilter Args : %s", params)
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

    @classmethod
    def trait_type(cls):
        return cls.FilterTraits


#
#
base.OpXFormer.register(IterAttrFilter)
base.OpXFormer.register(IterAttrMapper)


def query_register():
    return []


def xform_register():
    return [
        IterAttrMapper,
        IterAttrFilter,
    ]
