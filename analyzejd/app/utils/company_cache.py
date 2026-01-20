# Simple in-memory cache for now
# Later → Redis / DB

_company_cache = {}

def get_company_from_cache(company_name: str):
    return _company_cache.get(company_name.lower())

def save_company_to_cache(company_name: str, data: dict):
    _company_cache[company_name.lower()] = data
