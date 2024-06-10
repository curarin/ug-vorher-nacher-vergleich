
def get_query(bq_table, country_value, url, comp_start_date):
    query = f"""
        with source_data as (
            select
                data_date as date,
                url,
                query,
                sum(clicks) as clicks,
                sum(impressions) as impressions,
                sum(sum_position)/sum(impressions) + 1 as position
            from
                {bq_table}
            where
                url = '{url}'
                and data_date >= '{comp_start_date}'
                and country = '{country_value}'
                and query is not null
                and impressions > 5
            group by
                data_date,
                url,
                query
        )
    select * from source_data
    """
    return query

def get_bq_table(domain_wanted):
    domain_mapping = {
        "Germany": "seo-datawarehouse-379113.searchconsole.searchdata_url_impression",
        "Austria": "seo-datawarehouse-379113.searchconsole_UG_AT.searchdata_url_impression",
        "Switzerland": "seo-datawarehouse-379113.searchconsole_HG_CH.searchdata_url_impression",
        "Netherlands": "seo-datawarehouse-379113.searchconsole_HG_NL.searchdata_url_impression",
        "Spain": "seo-datawarehouse-379113.searchconsole_HG_ES.searchdata_url_impression"
    }
    bq_table = domain_mapping.get(domain_wanted, None)
    return bq_table

def get_country_code(domain_wanted):
    country_mapping = {
        "Germany": "deu",
        "Austria": "aut",
        "Switzerland": "che",
        "Netherlands": "nl",
        "Spain": "esp"
    }
    country_code = country_mapping.get(domain_wanted, None)
    return country_code

def determine_timerange(row, start_date):
    if row["date"] >= start_date:
        return "after"
    else:
        return "prior"