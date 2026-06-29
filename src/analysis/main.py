import os
import sys
from getpass import getpass

from arcgis.gis import GIS
from arcgis.features import FeatureCollection, FeatureLayer, FeatureSet
from arcgis.features.analysis import find_existing_locations


_MIN_PYTHON_VERSION = (3, 11)
_MAX_PYTHON_VERSION = (3, 12)
_API_KEY_TOOLBOX_ERROR = (
    "ArcGIS API keys currently do not expose the analysis toolbox that "
    "`find_existing_locations` depends on. Provide a Publisher/Administrator "
    "user account instead."
)


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
    input_layers = [weather_events_layer, islands_featurset.to_dict()]
    expressions = [{
        "operator": "",
        "layer": 0,
        "selectingLayer": 1,
        "spatialRel": "withinDistance",
        "distance": 1500.0,
        "units": "Kilometers",
    }]
    nearby_weather_events_feature_collection: FeatureCollection = find_existing_locations(input_layers=input_layers, expressions=expressions)
    nearby_weather_events_featureset = nearby_weather_events_feature_collection.query()
    if len(nearby_weather_events_featureset.features) < 1:
        print("No weather events nearby...")
    else:
        for weather_event_feature in nearby_weather_events_featureset.features:
            region_name = weather_event_feature.attributes["NAME"]
            effective_date = weather_event_feature.attributes["EFFECTIVE"]
            expire_date = weather_event_feature.attributes["EXPIRES"]
            certainty = weather_event_feature.attributes["CERTAINTY"]
            headline = weather_event_feature.attributes["HEADLINE"]
            description = weather_event_feature.attributes["DESCRIPTION"]
            instructions = weather_event_feature.attributes["INSTRUCTION"]
            print("...")


def _ensure_supported_python():
    current = sys.version_info
    if current < _MIN_PYTHON_VERSION or current >= _MAX_PYTHON_VERSION:
        raise RuntimeError(
            "The ArcGIS API for Python still depends on `distutils`, which "
            "was removed in Python 3.12. Run this module with Python 3.11.x."
        )


def _run_with_api_key(api_key: str) -> bool:
    portal = GIS(api_key=api_key)
    try:
        print_weather_warnings(portal)
    except AttributeError as exc:
        if "_tbx" in str(exc):
            print(_API_KEY_TOOLBOX_ERROR, file=sys.stderr)
            return False
        raise
    return True


def main():
    _ensure_supported_python()

    api_key = os.environ.get("SPATIAL_ANALYSIS_API_KEY")
    if api_key and _run_with_api_key(api_key):
        return

    user = input("User:")
    secret = getpass("Secret:")
    portal = GIS(username=user, password=secret)
    print_weather_warnings(portal)


if __name__ == "__main__":
    main()
