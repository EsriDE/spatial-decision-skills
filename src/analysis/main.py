from arcgis.gis import GIS
from arcgis.features import FeatureLayer, FeatureSet
from arcgis.features.analysis import find_existing_locations
from getpass import getpass
import os


def get_travel_regions_in_germany(portal: GIS) -> FeatureLayer:
    item_id = "b3ed11cda69349cb8b064025c01d00f1"
    layers_item = portal.content.get(item_id)
    if 1 != len(layers_item.layers):
        raise ValueError("Unexpected layer count for travel regions in Germany!")

    return layers_item.layers[0]

def query_northern_islands(portal: GIS) -> FeatureSet:
    travel_regions_layer = get_travel_regions_in_germany(portal)
    feature_set = travel_regions_layer.query("SN_RG='G01'")
    return feature_set
    
def get_weather_events_in_germany(portal: GIS) -> FeatureLayer:
    item_id = "e7e4164319284754a9f72f0c956efb40"
    layers_item = portal.content.get(item_id)
    if 2 != len(layers_item.layers):
        raise ValueError("Unexpected layer count for weather events in Germany!")
    
    return layers_item.layers[1]

def print_weather_warnings(portal: GIS):
    weather_events_layer = get_weather_events_in_germany(portal)
    #print(weather_events_layer)
    islands_featurset = query_northern_islands(portal)
    #print(islands_featurset)
    input_layers = [weather_events_layer, islands_featurset]
    expressions = [{
        "operator": "",
        "layer": 0,
        "selectingLayer": 1,
        "spatialRel": "withinDistance",
        "distance": 15.0,
        "units": "Kilometers",
    }]
    nearby_weather_events_featureset = find_existing_locations(input_layers=input_layers, expressions=expressions)
    print(nearby_weather_events_featureset)


def main():
    api_key = os.environ.get("SPATIAL_ANALYSIS_API_KEY")
    if not api_key:
        raise ValueError("You must authenticate using an arcgis API key!")

    # API key authentication leads to "AttributeError: 'NoneType' object has no attribute '_tbx'"
    portal = GIS(api_key=api_key)
    """
    # Fallback user auth creates ModuleNotFoundError: No module named 'distutils'
    user = input("User:")
    secret = getpass("Secret:")
    portal = GIS(username=user, password=secret)
    """
    print_weather_warnings(portal)
    


if __name__ == "__main__":
    main()
