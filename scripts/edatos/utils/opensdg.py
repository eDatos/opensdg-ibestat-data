# We'll initialize previous_indicator and next_indicator based on two things:
# - Order of the indicators in the file
# - Whether the indicator is complete and published
from edatos.services.statistical_resources import generate_indicator_sort_order


def setup_indicators_navigation(indicators):

    navigable_indicators = {
        key: value
        for key, value in indicators.items()
        if value.get('reporting_status') == 'complete' and value.get('published')
    }

    sorted_navigable_indicator_keys = sorted(navigable_indicators.keys(), key=generate_indicator_sort_order)    
    for i, key in enumerate(sorted_navigable_indicator_keys):        
        indicators[key]['previous_indicator'] = sorted_navigable_indicator_keys[i - 1] if i > 0 else None
        indicators[key]['next_indicator'] = sorted_navigable_indicator_keys[i + 1] if i < len(sorted_navigable_indicator_keys) - 1 else None

    return indicators