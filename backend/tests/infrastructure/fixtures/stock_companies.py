"""Stock companies fixture - loads organ_name.json."""
from backend.tests.infrastructure.utils.data_loader import load_json_file


def load_companies(limit=None):
    """Load company data from organ_name.json.
    
    Returns list of companies with schema:
    {
        "symbol": "VCB",
        "organ_name": "Ngân hàng...",
        "icb_name2": "Dịch vụ tài chính",
        "icb_name3": "Ngân hàng",
        "icb_name4": "Ngân hàng",
        "com_type_code": "NH",
        "icb_code1": "8000",
        "icb_code2": "8300",
        "icb_code3": "8350",
        "icb_code4": "8355"
    }
    """
    companies = load_json_file("organ_name.json")
    
    if limit:
        return companies[:limit]
    
    return companies


def get_company_by_symbol(symbol):
    """Get company by symbol."""
    companies = load_companies()
    for company in companies:
        if company['symbol'] == symbol:
            return company
    return None
