# Forked from org.siemac.edatos.core.common.util.shared.UrnUtils

def split_urn(urn, is_version_mandatory):
    parts = urn.split('=')
    if len(parts) != 2:
        raise ValueError("URN format is incorrect")
    prefix, urn_without_prefix = parts
    agency_id, item_scheme_id, version, resource_id = split_urn_without_prefix_item(urn_without_prefix, is_version_mandatory)
    return [prefix, agency_id, item_scheme_id, version, resource_id]

def split_urn_without_prefix_item(universal_identifier, is_version_mandatory):
    """
    Splits a URN without a prefix item into its components: agencyID, itemSchemeID, version, and resourceID.

    :param universal_identifier: The URN to split.
    :param is_version_mandatory: Boolean indicating if the version is mandatory.
    :return: A list containing [agencyID, itemSchemeID, version, resourceID].
    """
    COLON = ":"
    LEFT_PARENTHESIS = "("
    RIGHT_PARENTHESIS = ")"
    DOT = "."

    # Extract components
    agency_id = universal_identifier.split(COLON, 1)[0]
    item_scheme_id = universal_identifier.split(COLON)[-1].split(LEFT_PARENTHESIS)[0] if LEFT_PARENTHESIS in universal_identifier else None
    version = universal_identifier.split(LEFT_PARENTHESIS)[-1].split(RIGHT_PARENTHESIS)[0] if LEFT_PARENTHESIS in universal_identifier and RIGHT_PARENTHESIS in universal_identifier else None
    resource_id = universal_identifier.split(RIGHT_PARENTHESIS + DOT)[-1] if RIGHT_PARENTHESIS + DOT in universal_identifier else None

    # Handle case where itemSchemeID is None and version is not mandatory
    if item_scheme_id is None and not is_version_mandatory:
        item_scheme_id = universal_identifier.split(COLON)[-1]

    return [agency_id, item_scheme_id, version, resource_id]
