from lxml import etree
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, XSD

def convert_citygml_to_rdf(citygml_data):
    namespaces = {
        'gml': 'http://www.opengis.net/gml',
        'city': 'http://www.opengis.net/citygml/2.0',
        'bldg': 'http://www.opengis.net/citygml/building/2.0',
    }

    root = etree.fromstring(citygml_data)
    building_elements = root.findall(".//bldg:Building", namespaces)

    CITY = Namespace("http://www.opengis.net/citygml/2.0/")
    BLDG = Namespace("http://www.opengis.net/citygml/building/2.0/")
    GML = Namespace("http://www.opengis.net/gml/")
    EX = Namespace("http://example.com/buildings/")

    graph = Graph()

    for building_element in building_elements:
        building_id = building_element.attrib[f"{{{namespaces['gml']}}}id"]
        creation_date = building_element.find("city:creationDate", namespaces).text

        envelope_element = building_element.find(".//gml:Envelope", namespaces)
        lower_corner = envelope_element.find("gml:lowerCorner", namespaces).text
        upper_corner = envelope_element.find("gml:upperCorner", namespaces).text

        building_uri = URIRef(EX + building_id)
        graph.add((building_uri, RDF.type, BLDG.Building))
        graph.add((building_uri, CITY.creationDate, Literal(creation_date, datatype=XSD.date)))

        envelope = URIRef(EX + building_id + "/envelope")
        graph.add((building_uri, BLDG.boundedBy, envelope))
        graph.add((envelope, RDF.type, GML.Envelope))
        graph.add((envelope, GML.lowerCorner, Literal(lower_corner)))
        graph.add((envelope, GML.upperCorner, Literal(upper_corner)))

        solid = URIRef(EX + building_id + "/solid")
        graph.add((building_uri, BLDG.lod1Solid, solid))
        graph.add((solid, RDF.type, GML.Solid))

    return graph.serialize(format='xml')

with open("a.gml", "rb") as file:
    citygml_data = file.read()
rdf_output = convert_citygml_to_rdf(citygml_data)
with open("out.xml", "w") as file:
    file.write(rdf_output)