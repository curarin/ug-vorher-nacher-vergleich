import streamlit as st
from datetime import datetime
import json
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd
from assets.constants import (
    get_query,
    determine_timerange,
    get_country_code,
    get_bq_table
)

data = {
    "type": "service_account",
    "project_id": st.secrets["service_account"]["project_id"],
    "private_key_id": st.secrets["service_account"]["private_key_id"],
    "private_key": st.secrets["service_account"]["private_key"],
    "client_email": st.secrets["service_account"]["client_email"],
    "client_id": st.secrets["service_account"]["client_id"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": st.secrets["service_account"]["client_x509_cert_url"],
    "universe_domain": "googleapis.com"
}

service_account_json = json.dumps(data, indent=4)
service_account_info = json.loads(service_account_json)
credentials = service_account.Credentials.from_service_account_info(service_account_info)
client = bigquery.Client(credentials=credentials)


@st.cache_resource
def get_max_date(domain_wanted):
    bq_table = get_bq_table(domain_wanted)
    df = client.query(query=f"select max(data_date) as date from {bq_table} where data_date >= date_sub(current_date(), interval 4 day) and query like '%guru%' group by data_date order by data_date desc").to_dataframe()
    max_date = df["date"][0]
    return max_date

@st.cache_resource
def get_data_per_url(domain_wanted, comp_start_date, start_date, max_date, url):
    bq_table = get_bq_table(domain_wanted)
    country_value = get_country_code(domain_wanted)
    query_get_data_per_url = get_query(bq_table, country_value, url, comp_start_date)
    df = client.query(query=query_get_data_per_url).to_dataframe()
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        df["date"] = df["date"].dt.date
        df = df.sort_values(by='date')
        df["clicks"] = df["clicks"].astype(int)
        df["impressions"] = df["impressions"].astype(int)
        df["position"] = df["position"].astype(float)
        df["tag"] = df.apply(lambda row: determine_timerange(row, start_date), axis=1)
        
    else:
        columns = ['date', 'url', 'query', 'clicks', 'impressions', 'position', 'tag']
        df = pd.DataFrame(columns=columns)
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        df["clicks"] = df["clicks"].astype(pd.Int64Dtype())
        df["impressions"] = df["impressions"].astype(pd.Int64Dtype())
        df["position"] = df["position"].astype(float)
    return df

def dry_run_all_queries(domain_wanted, comp_start_date, start_date, max_date, url):
    bq_table = get_bq_table(domain_wanted)
    country_value = get_country_code(domain_wanted)
    query_get_data_per_url = get_query(bq_table, country_value, url, comp_start_date)
    job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    query_job = client.query((query_get_data_per_url), job_config=job_config)
    gb_processed = query_job.total_bytes_processed/1000000000
    return gb_processed

def calculate_bq_cost(gb_processed_as_list):
    total_gb = sum(gb_processed_as_list)
    price_per_gb = 0.00681774884
    price_total = total_gb*price_per_gb
    price_total_rounded = round(price_total, 4)
    total_gb_rounded = round(total_gb, 2)
    st.error(f"Estimated cost: {price_total_rounded}€ for {total_gb_rounded} GB of data. Do you REALLY want to pay the price?")





