from metacat_api.harvesters.ariadne import AriadneHarvester
from metacat_api.harvesters.clarin import ClarinHarvester
from metacat_api.harvesters.gotriple import GotripleHarvester
from metacat_api.harvesters.harvester import Harvester
from metacat_api.harvesters.sshomp import SshompHarvester

HARVESTERS: list[Harvester] = [
    GotripleHarvester(),
    AriadneHarvester(),
    SshompHarvester(),
    ClarinHarvester(),
]
