import streamlit as st
import assets.bigquery as bigquery_functions
from datetime import datetime, date, timedelta
from assets.bigquery import (
    get_max_date,
    get_data_per_url,
    dry_run_all_queries,
    calculate_bq_cost
)
from assets.data_functions import (
    calculate_differences,
    visualize_clicks,
    visualize_ranking_topquery,
    calculate_dates,
    calculate_total
)

def process_input(input_text):
    url_date_dict = {}
    lines = input_text.strip().split('\n')
    for line in lines:
        if line:
            try:
                url, date = line.split(' - ')
                url_date_dict[url] = date
            except ValueError:
                st.error(f"Line format incorrect: {line}")
    return url_date_dict

def performance_change(domain_wanted):

    st.title("Performance Change Comparison")
    above_the_fold1, above_the_fold2 = st.columns(2)
    with above_the_fold1:
        st.markdown("### Instructions")
        st.markdown("* Insert various URLs including the date of optimization and receive information on performance changes")
        st.markdown("* The periods are calculated on the basis of the optimization date. The exact same period before the optimization is used as a comparison.")
        st.markdown("* Input format looks like this -->")
        st.markdown("* Keep an eye on the costs. Periods should not be longer than 1-2 months maximum.")
    with above_the_fold2:
        st.image("screenshot.png")

    st.divider()
    st.markdown("### Provide Information")

    with st.form(key="input_field_performance_change"):
        keep_going_bool = False
        col1, col2 = st.columns(2)
        with col1:
            urls_and_date = st.text_area("Enter URL-Date pairs - one per line. Format wanted: 'URL - DATE'. Example: 'https://www.urlaubsguru.de/last-minute/side/ - 2024-05-05'")
        with col2:
            submit_value = st.form_submit_button(label="🤝 Calculate cost")
            if submit_value:
                url_date_dict = process_input(urls_and_date)
                max_date = get_max_date(domain_wanted)
                cost_list = []
                for url, date in url_date_dict.items():
                    start_date, comparison_start_date, comparison_end_date, delta_days = calculate_dates(date_current_iteration=date, max_date=max_date)
                    cost = dry_run_all_queries(domain_wanted=domain_wanted, comp_start_date=comparison_start_date, start_date=start_date, max_date=max_date, url=url)
                    cost_list.append(cost)
                calculate_bq_cost(cost_list)

            keep_going_bool = st.form_submit_button("✅ Just do it")
    if keep_going_bool == True:
            st.divider()
            url_date_dict = process_input(urls_and_date)
            max_date = get_max_date(domain_wanted)
            for url, date in url_date_dict.items():
                    start_date, comparison_start_date, comparison_end_date, delta_days = calculate_dates(date_current_iteration=date, max_date=max_date)
                    df = get_data_per_url(domain_wanted=domain_wanted, comp_start_date=comparison_start_date, start_date=start_date, max_date=max_date, url=url)
                    st.write(url)
                    st.write(df)
                    if not df.empty:
                        sum_clicks_prior, sum_clicks_post, sum_clicks_diff = calculate_total(df)
                        df_differences, top_keyword_by_clicks = calculate_differences(df)

                        st.markdown("#### Data Overview")
                        st.markdown(f"* {url}  ")
                        st.markdown(f"* Optimized on {comparison_end_date} ({delta_days} of data after update).")
                        st.markdown(f"* Total Clicks Difference is {sum_clicks_diff} ({sum_clicks_prior} vs. {sum_clicks_post}).")
                        st.write(df_differences)
                        visualize_clicks(df)
                        visualize_ranking_topquery(df, top_keyword_by_clicks)
                    else:
                        st.warning(f"No data for {url}")
                    st.divider()
