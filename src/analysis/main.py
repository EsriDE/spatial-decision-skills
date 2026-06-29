import os
import sys
import textwrap
from datetime import datetime
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
        "distance": 50.0,
        "units": "Kilometers",
    }]
    nearby_weather_events_feature_collection: FeatureCollection = find_existing_locations(input_layers=input_layers, expressions=expressions)
    nearby_weather_events_featureset = nearby_weather_events_feature_collection.query()
    if len(nearby_weather_events_featureset.features) < 1:
        print("No weather events nearby...")
    else:
        rows = []
        details = []
        for weather_event_feature in nearby_weather_events_featureset.features:
            attributes = weather_event_feature.attributes
            region_name = attributes.get("NAME")
            effective_date = attributes.get("EFFECTIVE")
            expire_date = attributes.get("EXPIRES")
            certainty = attributes.get("CERTAINTY")
            headline = attributes.get("HEADLINE")
            description = attributes.get("DESCRIPTION")
            instructions = attributes.get("INSTRUCTION")

            rows.append(
                [
                    _shorten(region_name, 32),
                    _shorten(headline, 48),
                    _format_datetime(effective_date),
                    _format_datetime(expire_date),
                    _format_value(certainty),
                ]
            )
            details.append((region_name, description, instructions))

        headers = ["Region", "Headline", "Effective", "Expires", "Certainty"]
        print("\nNearby weather events")
        print(_build_table(headers, rows))

        for index, (region_name, description, instructions) in enumerate(details, start=1):
            region_label = _format_value(region_name)
            print(f"\nEvent {index}: {region_label}")
            if description:
                print(f"  Description : {description}")
            if instructions:
                print(f"  Instructions: {instructions}")


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


def _format_value(value: object) -> str:
    if value is None:
        return "—"
    text = str(value).strip()
    return text if text else "—"


def _format_datetime(value: object) -> str:
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    return _format_value(value)


def _shorten(value: object, width: int) -> str:
    text = _format_value(value)
    return textwrap.shorten(text, width=width, placeholder="…")


def _build_table(headers: list[str], rows: list[list[str]]) -> str:
    column_widths = []
    for index, header in enumerate(headers):
        column_widths.append(
            max(
                len(header),
                max((len(row[index]) for row in rows), default=len(header)),
            )
        )

    separator = "+" + "+".join("-" * (width + 2) for width in column_widths) + "+"
    row_template = "| " + " | ".join(f"{{:{width}}}" for width in column_widths) + " |"

    lines = [separator, row_template.format(*headers), separator]
    for row in rows:
        lines.append(row_template.format(*row))
    lines.append(separator)
    return "\n".join(lines)


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
