import pydantic
import typing


class Neuron(pydantic.BaseModel):
    ei: typing.Literal["e", "i"]  # Either e or i
    fraction: float
    ncells: int = 0
    dims: typing.Dict[str, typing.Any] = {}


class Region(pydantic.BaseModel):
    name: str
    inh_fraction: float = 0.0
    region_fraction: float = 0.0
    neurons: typing.Dict[str, Neuron] = {}
    ncells: int = 0
    inh_ncells: int = 0
    exc_ncells: int = 0
    dims: typing.Dict[str, typing.Any] = {}


class Network(pydantic.BaseModel):
    name: str
    locations: typing.Dict[str, Region] = {}
    ncells: int = 0
    dims: typing.Dict[str, typing.Any] = {}


NETWORK_STATS_EXAMPLE = Network(
    name="v1",
    locations={
        "VISp1": Region(
            name="VISp1",
            inh_fraction=0.4051546391752577,
            region_fraction=0.0696625945317044,
            neurons={
                "Sst": Neuron(ei="i", fraction=0.0356234096692111),
                "Lamp5": Neuron(ei="i", fraction=0.7201017811704835),
                "Sst-Chodl": Neuron(ei="i", fraction=0.0076335877862595),
                "Pvalb": Neuron(ei="i", fraction=0.0381679389312977),
                "Vip": Neuron(ei="i", fraction=0.1475826972010178),
                "GABA-Other": Neuron(ei="i", fraction=0.0508905852417302),
                "IT": Neuron(ei="e", fraction=0.9896013864818024),
                "ET": Neuron(ei="e", fraction=0.0),
                "CT": Neuron(ei="e", fraction=0.0),
                "NP": Neuron(ei="e", fraction=0.0),
                "Glut-Other": Neuron(ei="e", fraction=0.0103986135181975),
            },
        ),
        "VISp2/3": Region(
            name="VISp2/3",
            inh_fraction=0.0787551960453881,
            region_fraction=0.3486199987072587,
            neurons={
                "Sst": Neuron(ei="i", fraction=0.1619115549215406),
                "Lamp5": Neuron(ei="i", fraction=0.1583452211126961),
                "Sst-Chodl": Neuron(ei="i", fraction=0.0021398002853067),
                "Pvalb": Neuron(ei="i", fraction=0.3323823109843081),
                "Vip": Neuron(ei="i", fraction=0.3166904422253923),
                "GABA-Other": Neuron(ei="i", fraction=0.028530670470756),
                "IT": Neuron(ei="e", fraction=1.0),
                "ET": Neuron(ei="e", fraction=0.0),
                "CT": Neuron(ei="e", fraction=0.0),
                "NP": Neuron(ei="e", fraction=0.0),
                "Glut-Other": Neuron(ei="e", fraction=0.0),
            },
        ),
        "VISp4": Region(
            name="VISp4",
            inh_fraction=0.1119157340355497,
            region_fraction=0.2096987912869239,
            neurons={
                "Sst": Neuron(ei="i", fraction=0.315126050420168),
                "Lamp5": Neuron(ei="i", fraction=0.0184873949579831),
                "Sst-Chodl": Neuron(ei="i", fraction=0.0),
                "Pvalb": Neuron(ei="i", fraction=0.5327731092436975),
                "Vip": Neuron(ei="i", fraction=0.1319327731092437),
                "GABA-Other": Neuron(ei="i", fraction=0.0016806722689075),
                "IT": Neuron(ei="e", fraction=0.9626178121359736),
                "ET": Neuron(ei="e", fraction=0.0293338981255956),
                "CT": Neuron(ei="e", fraction=0.0002117970983797),
                "NP": Neuron(ei="e", fraction=0.0074128984432913),
                "Glut-Other": Neuron(ei="e", fraction=0.0004235941967595),
            },
        ),
        "VISp5": Region(
            name="VISp5",
            inh_fraction=0.165427954926876,
            region_fraction=0.1776064895611143,
            neurons={
                "Sst": Neuron(ei="i", fraction=0.4557971014492754),
                "Lamp5": Neuron(ei="i", fraction=0.022463768115942),
                "Sst-Chodl": Neuron(ei="i", fraction=0.0065217391304347),
                "Pvalb": Neuron(ei="i", fraction=0.4876811594202898),
                "Vip": Neuron(ei="i", fraction=0.0217391304347826),
                "GABA-Other": Neuron(ei="i", fraction=0.0057971014492753),
                "IT": Neuron(ei="e", fraction=0.5212582591209423),
                "ET": Neuron(ei="e", fraction=0.3230393565067509),
                "CT": Neuron(ei="e", fraction=0.0439528871014076),
                "NP": Neuron(ei="e", fraction=0.1041367423154266),
                "Glut-Other": Neuron(ei="e", fraction=0.0076127549554725),
            },
        ),
        "VISp6a": Region(
            name="VISp6a",
            inh_fraction=0.0627792416084316,
            region_fraction=0.163661043242195,
            neurons={
                "Sst": Neuron(ei="i", fraction=0.3485401459854014),
                "Lamp5": Neuron(ei="i", fraction=0.0255474452554744),
                "Sst-Chodl": Neuron(ei="i", fraction=0.010948905109489),
                "Pvalb": Neuron(ei="i", fraction=0.5620437956204379),
                "Vip": Neuron(ei="i", fraction=0.0383211678832116),
                "GABA-Other": Neuron(ei="i", fraction=0.0145985401459854),
                "IT": Neuron(ei="e", fraction=0.2159882654932159),
                "ET": Neuron(ei="e", fraction=0.0006111722283339),
                "CT": Neuron(ei="e", fraction=0.7593203764820926),
                "NP": Neuron(ei="e", fraction=0.0053783156093387),
                "Glut-Other": Neuron(ei="e", fraction=0.0187018701870187),
            },
        ),
        "VISp6b": Region(
            name="VISp6b",
            inh_fraction=0.0529100529100529,
            region_fraction=0.0307510826708034,
            neurons={
                "Sst": Neuron(ei="i", fraction=0.275),
                "Lamp5": Neuron(ei="i", fraction=0.0875),
                "Sst-Chodl": Neuron(ei="i", fraction=0.075),
                "Pvalb": Neuron(ei="i", fraction=0.475),
                "Vip": Neuron(ei="i", fraction=0.0375),
                "GABA-Other": Neuron(ei="i", fraction=0.05),
                "IT": Neuron(ei="e", fraction=0.0467877094972067),
                "ET": Neuron(ei="e", fraction=0.0),
                "CT": Neuron(ei="e", fraction=0.7255586592178771),
                "NP": Neuron(ei="e", fraction=0.0),
                "Glut-Other": Neuron(ei="e", fraction=0.2276536312849162),
            },
        ),
    },
)
