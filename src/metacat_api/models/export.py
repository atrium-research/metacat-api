from rdflib.namespace import DC, DCTERMS, FOAF, RDFS, SKOS, XSD, Namespace
from rdflib.plugins.serializers.turtle import TurtleSerializer


class CustomTurtleSerializer(TurtleSerializer):
    indentString = "  "
    _spacious = False


ATRIUM = Namespace("https://atrium-research.eu/")

ATRIUM_CATALOGUE = Namespace("https://atrium-research.eu/Catalogue/")
ATRIUM_CATALOGUE_VERSION = Namespace("https://atrium-research.eu/CatalogueVersion/")
ATRIUM_VOCABULARY = Namespace("https://atrium-research.eu/Vocabulary/")
ATRIUM_FACET = Namespace("https://atrium-research.eu/Facet/")
ATRIUM_FACET_EXPOSURE = Namespace("https://atrium-research.eu/FacetExposure/")
ATRIUM_FACET_VALUE = Namespace("https://atrium-research.eu/FacetValue/")

AO_CAT = Namespace("https://ariadne-infrastructure.eu/aocat/")
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
CRMPE = Namespace("http://parthenos.d4science.org/CRMext/CRMpe/")

NAMESPACES = {
    "dc": DC,
    "dct": DCTERMS,
    "foaf": FOAF,
    "rdfs": RDFS,
    "skos": SKOS,
    "xsd": XSD,
    "crm": CRM,
    "crmpe": CRMPE,
    "aocat": AO_CAT,
    "atrium": ATRIUM,
    "cat": ATRIUM_CATALOGUE,
    "catver": ATRIUM_CATALOGUE_VERSION,
    "voc": ATRIUM_VOCABULARY,
    "facet": ATRIUM_FACET,
    "fe": ATRIUM_FACET_EXPOSURE,
    "fv": ATRIUM_FACET_VALUE,
}
