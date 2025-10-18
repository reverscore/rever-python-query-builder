from sqlalchemy import asc, desc

common_supported_filters = {
    'site_id',
    'country_codes',
    'tag_ids',
    'site_group_ids',
    'tag_group_ids',
}

order_mapping = {
    'asc': asc,
    'desc': desc,
}
