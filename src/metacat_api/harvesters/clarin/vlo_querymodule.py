import jq
import requests


def extractFacetValues(collectionDef):
    queries = collectionDef["queries"]
    print(f"Processing query collection definition containing {len(queries)} facets.")

    jqQueryString = collectionDef["interpretation"]["jqQuery"]
    jqQuery = jq.compile(jqQueryString)
    print(f"Collecting values using JQ query: {jqQuery}")

    result = {}
    for facet in queries:
        if facet["catalogue"] == "vlo" and facet["url"]:
            name = facet["facet"]
            url = facet["url"]
            print(f"* Retrieving data for facet '{name}' at <{url}>")

            # Query facet values and counts
            responseJson = requests.get(url).json()
            result[name] = jqQuery.input_value(responseJson).all()
    return result
