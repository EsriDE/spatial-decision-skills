## overview

This package demonstrates how to combine ArcGIS analysis services in a spatial
decision skill. The entry point fetches curated FeatureLayers for German travel
regions and weather events, then reacts to nearby warnings using
`arcgis.features.analysis.find_existing_locations`.

## setup

1. Install [uv](https://github.com/python-poetry/uv) (or reuse the copy in this
   repo) and make sure your environment is running **Python 3.11**. The ArcGIS
   API for Python still imports `distutils`, which was removed in Python 3.12
   and later, so any interpreter outside the `>=3.11,<3.12` range will fail at
   import-time.
2. From `src/analysis`, run `uv sync` to install dependencies, then use
   `uv run main` (or another tooling command) to execute the skill.

## authentication

The skill prefers an API key stored in `SPATIAL_ANALYSIS_API_KEY`. If you do not
provide one it prompts for a user name and password. Because the analysis
toolbox relies on ArcGIS Online geoprocessing services, the public API key path
currently fails inside `find_existing_locations` with
`AttributeError: 'NoneType' object has no attribute '_tbx'`. In practice you must
use a user account (Publisher or Administrator role) so that the analysis tools
can be provisioned. The code raises a clear message when the API key path fails
and falls back to the interactive credential prompt.
