import abc
import typing
import tqdm
import itertools
from .abm_celltypes import CTDbGlifApiQuery, CTDbCellApiQuery, CTDbCellCacheQuery
from .abm_celltypes import CTDbCellAttrMapper, CTDbCellAttrFilter, CTDbCellAttrJPathFilter
from .abm_celltypes import ABMCT_QUERY_REGISTER, ABMCT_FILTER_REGISTER, ABMCT_MAPPER_REGISTER
from ..log.logging import LOGGER


class DbQuery(abc.ABC):
    @abc.abstractmethod
    def run(
        self, **params: typing.Dict[str, typing.Any]
    ) -> typing.Iterable[typing.Dict[str, typing.Any]]:
        return None


class DbRecordMapper(abc.ABC):
    @abc.abstractmethod
    def map(
        self, in_iter: typing.Iterable, **params
    ) -> typing.Iterable:
        return None


class DbRecordFilter(abc.ABC):
    @abc.abstractmethod
    def filter(
        self, in_iter: typing.Iterable, **params
    ) -> typing.Iterable:
        return None


class TQDMWrapper():
    def map(self, in_lst, **params):
        return tqdm.tqdm(in_lst)


class DataSlicer():
    def filter(self, in_iter, **params):
        default_args = {"stop" : 10, "list": True}
        rarg = (
            {**default_args, **params} if params is not None else default_args
        )
        ditr = itertools.islice(in_iter, rarg["stop"])
        return list(ditr) if bool(rarg["list"]) else ditr


# ----- Registring the Sub-classes ------
#
DbRecordMapper.register(TQDMWrapper)
#
DbQuery.register(CTDbCellCacheQuery)
DbQuery.register(CTDbCellApiQuery)
DbQuery.register(CTDbGlifApiQuery)
#
DbRecordMapper.register(CTDbCellAttrMapper)
DbRecordMapper.register(CTDbCellAttrJPathFilter)
#
DbRecordFilter.register(CTDbCellAttrFilter)
DbRecordFilter.register(DataSlicer)

# ----- Mapper, Filter and Query Registers ------
#
BASE_MAPPER_REGISTER = {
    "TQDMWrapper" : TQDMWrapper,
    __name__ + ".TQDMWrapper" : TQDMWrapper,
}
BASE_FILTER_REGISTER = {
    "DataSlicer" : DataSlicer,
    __name__ + ".DataSlicer" : DataSlicer,
}
#
QUERY_REGISTER = ABMCT_QUERY_REGISTER
FILTER_REGISTER = {**BASE_FILTER_REGISTER, **ABMCT_FILTER_REGISTER}
MAPPER_REGISGTER = {**BASE_MAPPER_REGISTER, **ABMCT_MAPPER_REGISTER}


def get_query_object(query_key, **init_params) -> typing.Union[DbQuery, None]:
    if query_key not in QUERY_REGISTER:
        return None
    return QUERY_REGISTER[query_key](**init_params)


def get_mapper_object(mapper_key, **init_params) -> typing.Union[DbRecordMapper, None]:
    if mapper_key not in MAPPER_REGISGTER:
        return None
    return MAPPER_REGISGTER[mapper_key](**init_params)  # type:ignore


def get_filter_object(filter_key, **init_params) -> typing.Union[DbRecordFilter, None]:
    if filter_key not in FILTER_REGISTER:
        return None
    return FILTER_REGISTER[filter_key](**init_params)  # type:ignore


def run_dc_workflow(workflow_steps):
    wf_stream = None
    for stx in workflow_steps:
        sname = stx["name"]
        iparams = stx["init_params"]
        eparams = stx["exec_params"]
        if stx["type"] == "query":
            LOGGER.info("Running Query : " + sname)
            qobj: typing.Union[DbQuery, None] = get_query_object(
                sname, **iparams
            )
            if qobj and wf_stream:
                eparams["input"] = wf_stream
                wf_stream = qobj.run(**eparams)
                LOGGER.info("Completed Query : " + sname)
            elif qobj:
                wf_stream = qobj.run(**eparams)
                LOGGER.info("Completed Query : " + sname)
            else:
                LOGGER.error("Failed to find Query : " + sname)
        elif stx["type"] == "map":
            LOGGER.info("Running Mapper : " + stx["name"])
            mobj: typing.Union[
                DbRecordMapper, None
            ] = get_mapper_object(sname, **iparams)
            if mobj and wf_stream:
                wf_stream = mobj.map(wf_stream, **eparams)
            else:
                LOGGER.error("Failed to find Mapper : " + sname)
        elif stx["type"] == "filter":
            LOGGER.info("Running Filter : " + stx["name"])
            fobj: typing.Union[
                DbRecordFilter, None
            ] = get_filter_object(sname, **iparams)
            if fobj and wf_stream:
                wf_stream = fobj.filter(wf_stream, **eparams)
                LOGGER.info("Completed Filter : " + sname)
            else:
                LOGGER.error("Failed to find Filter : " + sname)
    return wf_stream
