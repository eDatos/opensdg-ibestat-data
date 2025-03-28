# We'll initialize previous_indicator and next_indicator based on two things:
# - Order of the indicators in the file
# - Whether the indicator is complete and published
def setup_indicators_navigation(indicators):

    navigable_indicators = {
        key: value
        for key, value in indicators.items()
        if value.get('reporting_status') == 'complete' and value.get('published')
    }

    navigable_indicator_keys = list(navigable_indicators.keys())
    for i, key in enumerate(navigable_indicator_keys):
        
        indicators[key]['previous_indicator'] = navigable_indicator_keys[i - 1] if i > 0 else None
        indicators[key]['next_indicator'] = navigable_indicator_keys[i + 1] if i < len(navigable_indicator_keys) - 1 else None

    return indicators