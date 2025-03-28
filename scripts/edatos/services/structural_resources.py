
from edatos.utils.urn import split_urn

def urn_to_url(base_url, urn):
    prefix, agency_id, item_scheme_id, version, resource_id = split_urn(urn, True)

    base_url += '/v1.0'
    if prefix == 'urn:sdmx:org.sdmx.infomodel.base.Agency':
        return f"{base_url}/agencyschemes/{agency_id}/{item_scheme_id}/{version}/agencies/{resource_id}.json"
    else:
        raise ValueError("Resource type is not supported")


def extract_organisation_info(organisation):
    if 'contacts' in organisation and 'contact' in organisation['contacts'] and organisation['contacts']['contact']:
        contact = organisation['contacts']['contact'][0]
    else:
        raise ValueError("No contact found in organisation", organisation)

    organisation_url = contact['urls'][0] if 'urls' in contact and contact['urls'] else ''
    return contact['name'], organisation_url, organisation['id']