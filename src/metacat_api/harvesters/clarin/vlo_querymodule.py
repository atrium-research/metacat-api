import jq
import requests


def extract_facet_values(collection_def):
    queries = collection_def["queries"]
    print(f"Processing query collection definition containing {len(queries)} facets.")

    jq_query_string = collection_def["interpretation"]["jqQuery"]
    jq_query = jq.compile(jq_query_string)
    print(f"Collecting values using JQ query: {jq_query}")

    result = {}
    for facet in queries:
        if facet["catalogue"] == "vlo" and facet["url"]:
            name = facet["facet"]
            url = facet["url"]
            print(f"* Retrieving data for facet '{name}' at <{url}>")

            # Query facet values and counts
            response_json = requests.get(url).json()
            result[name] = jq_query.input_value(response_json).all()
    return result
