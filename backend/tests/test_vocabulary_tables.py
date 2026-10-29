"""Routes, species and endpoint categories are validated against the cached tables."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.models.protocol import ProtocolParameters, coerce_route_list
from app.services import vocabulary


@pytest.fixture(autouse=True)
def _reset():
    vocabulary.clear_applications()
    yield
    vocabulary.clear_applications()


def test_without_tables_values_pass_through():
    assert coerce_route_list(["oral", "aquatic-waterborne"]) == ["oral", "aquatic-waterborne"]
    assert ProtocolParameters(species="dog", endpoint_category="whatever").species == "dog"


def test_routes_follow_the_table():
    vocabulary.set_slugs("routes", ["oral", "aquatic-waterborne"])
    assert coerce_route_list(["dermal", "aquatic-waterborne", "oral"]) == [
        "aquatic-waterborne",
        "oral",
    ]


def test_species_follow_the_table_and_keep_markers():
    vocabulary.set_slugs("species", ["rat", "dog"])
    assert ProtocolParameters(species="dog").species == "dog"
    assert ProtocolParameters(species="in_vitro").species == "in_vitro"
    with pytest.raises(ValidationError):
        ProtocolParameters(species="rhinoceros")


def test_endpoint_category_follows_the_table_through_aliases():
    vocabulary.set_slugs("endpoints", ["acute-systemic-toxicity", "skin-irritation"])
    assert ProtocolParameters(endpoint_category="acute_toxicity").endpoint_category == "acute_toxicity"
    with pytest.raises(ValidationError):
        ProtocolParameters(endpoint_category="made_up")
