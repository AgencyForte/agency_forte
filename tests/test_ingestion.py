import pytest
import requests
import polars as pl
from insuretra_pipeline.config import DATASETS, get_settings
from insuretra_pipeline.socrata import fetch_dataset_rows

@pytest.mark.network
def test_socrata_authentication_and_rate_limiting():
    """Test Case 1.1: Socrata API Authentication and Rate-Limiting Check"""
    settings = get_settings()
    
    # We test one of the datasets, e.g. 'agencies'
    dataset = DATASETS["agencies"]
    url = f"https://data.texas.gov/resource/{dataset.resource_id}.csv"
    
    headers = {}
    if settings.socrata_app_token:
        headers["X-App-Token"] = settings.socrata_app_token

    # Just fetch limit 1 to check auth/headers
    response = requests.get(url, params={"$limit": 1}, headers=headers)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Optionally verify X-App-Token-Status or rate limiting headers if token is present
    # Usually X-Socrata-Region or X-RateLimit-Remaining exist
    assert "X-Socrata-Region" in response.headers or "X-App-Token-Status" in response.headers

@pytest.mark.network
def test_source_schema_mapping_and_accessibility():
    """Test Case 1.2: Source Schema Mapping and Row Accessibility"""
    settings = get_settings()
    
    # Test 'agencies'
    dataset_agencies = DATASETS["agencies"]
    df_agencies = fetch_dataset_rows(dataset_agencies, settings.socrata_app_token)
    assert not df_agencies.is_empty()
    assert "License number" in df_agencies.columns or "NPN" in df_agencies.columns
    
    # Test 'relationships'
    dataset_rels = DATASETS["relationships"]
    df_rels = fetch_dataset_rows(dataset_rels, settings.socrata_app_token)
    assert not df_rels.is_empty()
    assert "Associated licensee NPN" in df_rels.columns
    
    # Test 'agent_appointments'
    dataset_agents = DATASETS["agent_appointments"]
    df_agents = fetch_dataset_rows(dataset_agents, settings.socrata_app_token)
    assert not df_agents.is_empty()
    assert "NAIC ID" in df_agents.columns
    assert "Agent NPN" in df_agents.columns
