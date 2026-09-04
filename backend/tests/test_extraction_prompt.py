import json

from app.adapters.llm import ExtractionError, _raw_experiments_from_payload
from app.services.extraction import enrich_raw_experiments


def test_experiments_payload_parses_multi_experiment_response():
    payload = {
        "experiments": [
            {
                "study_type": "acute toxicity LD50 study",
                "route": ["oral", "intraperitoneal"],
                "application": "basic-research",
                "procedure_text": "Single-dose acute toxicity LD50 study.",
                "species": "rat",
                "animal_counts": {"female": None, "male": 60, "total": None, "per_group": None},
                "regulatory": True,
                "notes": None,
            },
            {
                "study_type": "28-day subacute repeated-dose oral toxicity study",
                "route": ["oral"],
                "application": "basic-research",
                "procedure_text": "28-day repeated-dose oral toxicity study.",
                "species": "rat",
                "animal_counts": {"female": None, "male": 20, "total": None, "per_group": None},
                "regulatory": True,
                "notes": "28-day repeated-dose design has no matching endpoint_category.",
            },
        ]
    }

    raw_results = _raw_experiments_from_payload(payload)
    assert not isinstance(raw_results, ExtractionError)
    results = enrich_raw_experiments(raw_results)
    assert len(results) == 2
    assert results[0].endpoint_category == "acute_toxicity"
    assert results[0].raw.animal_counts is not None
    assert results[0].raw.animal_counts.male == 60
    assert results[1].endpoint_category is None
    assert results[1].raw.animal_counts is not None
    assert results[1].raw.animal_counts.male == 20
    assert results[1].raw.notes is not None


def test_empty_experiments_array_returns_actionable_error():
    result = _raw_experiments_from_payload(
        {"experiments": []},
        raw_response='{"experiments": []}',
    )
    assert isinstance(result, ExtractionError)
    assert result.reason == "empty_experiments_array"
    assert "empty experiments array" in result.message.lower()
    assert result.raw_response is not None


def test_invalid_experiment_items_include_raw_response():
    result = _raw_experiments_from_payload(
        {"experiments": [{"route": ["oral"]}]},
        raw_response='{"experiments": [{"route": ["oral"]}]}',
    )
    assert isinstance(result, ExtractionError)
    assert result.reason == "no_valid_experiment_items"
    assert result.message.startswith("AI model call returned an invalid response:")
    assert "route" in result.message
    assert "route" in (result.raw_response or "")


def test_null_route_array_coerces_to_none():
    result = _raw_experiments_from_payload(
        {
            "experiments": [
                {
                    "study_type": "UV photocarcinogenesis study",
                    "route": [None],
                    "application": "basic-research",
                    "procedure_text": "Chronic UV exposure in mice.",
                    "species": "mouse",
                }
            ]
        }
    )
    assert not isinstance(result, ExtractionError)
    assert result[0].route is None


def test_string_null_route_array_coerces_to_none():
    result = _raw_experiments_from_payload(
        {
            "experiments": [
                {
                    "study_type": "UV photocarcinogenesis study",
                    "route": ["null"],
                    "application": "basic-research",
                    "procedure_text": "Chronic UV exposure in mice.",
                    "species": "mouse",
                }
            ]
        }
    )
    assert not isinstance(result, ExtractionError)
    assert result[0].route is None


def test_mixed_route_array_drops_null_markers():
    result = _raw_experiments_from_payload(
        {
            "experiments": [
                {
                    "study_type": "acute toxicity LD50 study",
                    "route": ["oral", "null"],
                    "application": "basic-research",
                    "procedure_text": "LD50 study in rats.",
                    "species": "rat",
                }
            ]
        }
    )
    assert not isinstance(result, ExtractionError)
    assert result[0].route == ["oral"]


def test_string_route_coerces_to_single_item_array():
    result = _raw_experiments_from_payload(
        {
            "experiments": [
                {
                    "study_type": "inhalation toxicity study of carbon black in rats",
                    "route": "inhalation",
                    "route_evidence": (
                        "rats in the exposure group were exposed to CB in the "
                        "nose-only inhalation chamber"
                    ),
                    "route_confidence": "high",
                    "application": "regulatory-use",
                    "procedure_text": (
                        "Rats were exposed to carbon black aerosol nose-only "
                        "for 6 hrs/day for 90 days"
                    ),
                    "species": "rat",
                    "animal_counts": {
                        "female": None,
                        "male": 32,
                        "total": 32,
                        "per_group": 16,
                    },
                    "regulatory": True,
                }
            ]
        }
    )
    assert not isinstance(result, ExtractionError)
    assert result[0].route == ["inhalation"]
    assert result[0].species == "rat"


def test_null_application_defaults_to_basic_research():
    result = _raw_experiments_from_payload(
        {
            "experiments": [
                {
                    "study_type": "acute toxicity LD50 study",
                    "route": ["oral"],
                    "application": None,
                    "procedure_text": "LD50 study in rats.",
                    "species": "rat",
                    "animal_counts": {"male": 60},
                    "regulatory": True,
                }
            ]
        }
    )
    assert not isinstance(result, ExtractionError)
    assert result[0].application == "basic-research"


def test_guard_response_returns_error():
    result = _raw_experiments_from_payload(
        {"experiments": [], "error": "No protocol detected"}
    )
    assert isinstance(result, ExtractionError)
    assert result.message == "No protocol detected"
    assert result.reason == "guard_response"


def test_bovine_species_coerces_to_other():
    result = _raw_experiments_from_payload(
        {
            "experiments": [
                {
                    "study_type": "ex vivo eye irritation test",
                    "route": ["ocular"],
                    "application": "basic-research",
                    "procedure_text": "Ex vivo bovine cornea perfusion.",
                    "species": "bovine",
                }
            ]
        }
    )
    assert not isinstance(result, ExtractionError)
    assert result[0].species == "other"


def test_per_field_confidence_parsed():
    result = _raw_experiments_from_payload(
        {
            "experiments": [
                {
                    "study_type": "acute toxicity LD50 study",
                    "route": ["oral"],
                    "route_confidence": "high",
                    "application": "basic-research",
                    "application_confidence": "medium",
                    "procedure_text": "LD50 study in rats.",
                    "species": "rat",
                    "species_confidence": "high",
                }
            ]
        }
    )
    assert not isinstance(result, ExtractionError)
    assert result[0].route_confidence == "high"
    assert result[0].application_confidence == "medium"
    assert result[0].species_confidence == "high"


def test_parse_json_payload_extracts_object_from_leading_prose():
    from app.adapters.llm import _parse_json_payload

    raw = (
        'We are given a protocol description. Here is the JSON:\n'
        '{"experiments": [{"study_type": "acute toxicity LD50 study", "route": ["oral"], '
        '"application": "basic-research", "procedure_text": "LD50 study", "species": "rat", '
        '"regulatory": true, "notes": null}]}'
    )
    payload = _parse_json_payload(raw)
    assert payload["experiments"][0]["study_type"] == "acute toxicity LD50 study"


def test_build_extraction_prompt_injects_protocol_text():
    from app.prompts.extraction import build_extraction_prompt

    prompt = build_extraction_prompt("Acute toxicity LD50 study in rats.")
    assert "Acute toxicity LD50 study in rats." in prompt
    assert '"experiments"' in prompt
    assert "study_type" in prompt
    assert "MAX 15 WORDS" in prompt
    assert "MAX 5 WORDS" in prompt
    assert "Do not quote entire paragraphs" in prompt
    assert "route_confidence" in prompt
    assert "substance-to-tissue contact" in prompt
    assert "EVEIT" in prompt
    assert "per-field confidence" in prompt
    assert "Do NOT include a top-level" in prompt


def test_parse_json_payload_repairs_truncated_unterminated_string():
    from app.adapters.llm import _parse_json_payload

    raw = (
        '{"experiments": [{"study_type": "acute toxicity LD50 study", "route": ["oral"], '
        '"route_evidence": "administered EO p.o. by gastric tube", '
        '"study_domain": "general'
    )
    payload = _parse_json_payload(raw)
    assert isinstance(payload, dict)
    assert payload["experiments"][0]["study_domain"] == "general"


def test_parse_json_payload_repairs_truncated_mid_evidence_field():
    from app.adapters.llm import _parse_json_payload

    raw = (
        '{"experiments": [{"study_type": "genotoxicity battery", "route": ["oral"], '
        '"route_evidence": "treated by gavage", "study_domain": null, '
        '"procedure_text": "Gavage dosing study.", '
        '"procedure_text_evidence": "treated by gavage'
    )
    payload = _parse_json_payload(raw)
    experiment = payload["experiments"][0]
    assert experiment["procedure_text_evidence"] == "treated by gavage"
    assert experiment["study_type"] == "genotoxicity battery"


def test_parse_json_payload_repairs_truncated_after_property_comma():
    from app.adapters.llm import _parse_json_payload

    raw = (
        '{"experiments": [{"study_type": "reproductive toxicity study", "route": ["oral"], '
        '"route_evidence": "mixed into NIH-07M diet", "application": "regulatory-use",'
    )
    payload = _parse_json_payload(raw)
    experiment = payload["experiments"][0]
    assert experiment["application"] == "regulatory-use"
    assert experiment["route"] == ["oral"]


def test_parse_json_payload_repairs_truncated_nested_object():
    from app.adapters.llm import _parse_json_payload

    raw = (
        '{"experiments": [{"study_type": "subacute toxicity study", "route": ["oral"], '
        '"species": "rat", "animal_counts": {"female": null, "male": 20,'
    )
    payload = _parse_json_payload(raw)
    experiment = payload["experiments"][0]
    assert experiment["animal_counts"]["male"] == 20


def test_parse_json_payload_repairs_missing_opening_brace():
    from app.adapters.llm import _parse_json_payload

    raw = (
        'experiments": [{"study_type": "acute toxicity LD50 study", "route": ["oral"], '
        '"application": "basic-research", "procedure_text": "LD50 study", '
        '"species": "rat", "animal_counts": {"total": 60}, "regulatory": true, '
        '"notes": null}]}'
    )
    payload = _parse_json_payload(raw)
    assert isinstance(payload, dict)
    assert len(payload["experiments"]) == 1

    raw_results = _raw_experiments_from_payload(payload)
    assert not isinstance(raw_results, ExtractionError)
    results = enrich_raw_experiments(raw_results)
    assert results[0].endpoint_category == "acute_toxicity"


def test_legacy_payload_maps_endpoint_category_to_study_type():
    payload = {
        "experiments": [
            {
                "endpoint_category": "genotoxicity",
                "route": ["oral"],
                "application": "regulatory-use",
                "procedure_text": "Comet assay battery",
                "species": "rat",
                "n_animals": 5,
                "regulatory": None,
                "notes": None,
            }
        ]
    }
    raw_results = _raw_experiments_from_payload(payload)
    assert not isinstance(raw_results, ExtractionError)
    results = enrich_raw_experiments(raw_results)
    assert results[0].endpoint_category == "genotoxicity"
    assert results[0].raw.animal_counts is not None
    assert results[0].raw.animal_counts.total == 5
