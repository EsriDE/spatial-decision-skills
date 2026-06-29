from arcgis.gis import GIS
import os


def query_travel_regions(portal: GIS):
    item_id = "b3ed11cda69349cb8b064025c01d00f1"
    layers_item = portal.content.get(item_id)
    travel_regions_layer = layers_item.layers[0]
    feature_set = travel_regions_layer.query("SN_RG='G01'")
    print(feature_set)


def main():
    api_key = os.environ.get("SPATIAL_ANALYSIS_API_KEY")
    if not api_key:
        raise ValueError("You must authenticate using an arcgis API key!")

    portal = GIS(api_key=api_key)
    query_travel_regions(portal)


if __name__ == "__main__":
    main()
