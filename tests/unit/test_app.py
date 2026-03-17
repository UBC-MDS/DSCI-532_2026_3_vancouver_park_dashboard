import importlib.util
import os
from pathlib import Path
from unittest import mock

import pandas as pd
import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
APP_PATH = REPO_ROOT / "src" / "app.py"


class DummyChatAnthropic:
	def __init__(self, *args, **kwargs):
		self.args = args
		self.kwargs = kwargs

	def chat(self, message):
		return "{}"


@pytest.fixture(scope="module")
def app_module():
	"""Load the dashboard module with a mocked Anthropic client so tests can import it safely."""
	spec = importlib.util.spec_from_file_location("tested_app", APP_PATH)
	module = importlib.util.module_from_spec(spec)

	with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}, clear=False):
		with mock.patch("chatlas.ChatAnthropic", DummyChatAnthropic):
			spec.loader.exec_module(module)

	return module


@pytest.fixture
def sample_parks():
	return pd.DataFrame(
		[
			{
				"Name": "Harbour Green Park",
				"NeighbourhoodName": "Downtown",
				"Hectare": 1.2,
				"Washrooms": "Y",
				"Facilities": "Y",
				"SpecialFeatures": "N",
				"GoogleMapDest": "49.2901, -123.1207",
			},
			{
				"Name": "Sunset Beach Park",
				"NeighbourhoodName": "West End",
				"Hectare": 2.5,
				"Washrooms": "Y",
				"Facilities": "N",
				"SpecialFeatures": "Y",
				"GoogleMapDest": "49.2800, -123.1400",
			},
			{
				"Name": "Kits Beach Park",
				"NeighbourhoodName": "Kitsilano",
				"Hectare": 3.0,
				"Washrooms": "N",
				"Facilities": "Y",
				"SpecialFeatures": "Y",
				"GoogleMapDest": pd.NA,
			},
		]
	)


def test_apply_dashboard_filters_combines_text_neighbourhood_and_facility_filters(app_module, sample_parks):
	"""This test verifies that the dashboard keeps only rows matching all selected filters so combined filtering does not silently return the wrong parks."""
	filtered = app_module.apply_dashboard_filters(
		sample_parks,
		search_text="harbour",
		neighbourhoods=["Downtown", "Kitsilano"],
		size_range=(0, 2),
		facilities=["Washrooms", "Facilities"],
	)

	assert filtered["Name"].tolist() == ["Harbour Green Park"]


def test_apply_dashboard_filters_uses_inclusive_hectare_boundaries(app_module, sample_parks):
	"""This test verifies that parks exactly on the slider bounds are retained because changing that boundary rule would make the dashboard disagree with its UI."""
	filtered = app_module.apply_dashboard_filters(
		sample_parks,
		size_range=(2.5, 3.0),
	)

	assert filtered["Name"].tolist() == ["Sunset Beach Park", "Kits Beach Park"]


def test_best_match_neighbourhoods_returns_unique_fuzzy_matches(app_module):
	"""This test verifies that fuzzy neighbourhood matching resolves close user input once per neighbourhood so AI-driven filtering stays tolerant without duplicating results."""
	matched = app_module.best_match_neighbourhoods(
		["Downtow", "Kitsilan", "Downtow"],
		["Downtown", "Kitsilano", "West End"],
	)

	assert matched == ["Downtown", "Kitsilano"]


def test_folium_map_skips_rows_without_coordinates(app_module, sample_parks):
	"""This test verifies that the map only renders parks with coordinates because missing-location rows should not create broken markers or invalid map HTML."""
	html = app_module.folium_map(sample_parks)

	assert "Harbour Green Park" in html
	assert "Sunset Beach Park" in html
	assert "Kits Beach Park" not in html
