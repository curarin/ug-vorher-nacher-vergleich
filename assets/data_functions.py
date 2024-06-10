import streamlit as st
import duckdb
from datetime import datetime, timedelta
import altair as alt

def calculate_dates(date_current_iteration, max_date):
    start_date = datetime.strptime(date_current_iteration, "%Y-%m-%d").date()
    delta_days = (start_date - max_date).days
    delta_days *= -1
                    
    comparison_start_date = start_date - timedelta(days=delta_days)
    comparison_start_date = comparison_start_date - timedelta(days=-1)
    comparison_end_date = max_date - timedelta(days=delta_days)
    start_date = start_date + timedelta(days=1)

    return start_date, comparison_start_date, comparison_end_date, delta_days

def calculate_total(df):
    con = duckdb.connect()
    df_calculations = con.sql(
        """
        with source as (
                    select
                        date,
                        url,
                        query,
                        clicks,
                        impressions,
                        position,
                        tag
                    from
                        df
                ),
        group_data as (
            select
                tag,
                sum(clicks) as sum_clicks
            from
                source
            group by
                tag
        )
        select * from group_data
        """
    ).df()
    con.close()

    prior_clicks = df_calculations[df_calculations['tag'] == 'prior']['sum_clicks']
    post_clicks = df_calculations[df_calculations['tag'] == 'after']['sum_clicks']
    if prior_clicks.empty:
        sum_clicks_prior = 0
    else:
        sum_clicks_prior = prior_clicks.sum()

    if post_clicks.empty:
        sum_clicks_post = 0
    else:
        sum_clicks_post = post_clicks.sum()

    # sum_clicks_prior = df_calculations[df_calculations['tag'] == 'prior']['sum_clicks'].values[0]
    # sum_clicks_post = df_calculations[df_calculations['tag'] == 'after']['sum_clicks'].values[0]

    diff = int(sum_clicks_post) - int(sum_clicks_prior)
    
    
    return sum_clicks_prior, sum_clicks_post, diff

def calculate_differences(df):
    con = duckdb.connect()
    df_calculations = con.sql(
        """
        with source as (
            select
                date,
                url,
                query,
                clicks,
                impressions,
                position,
                tag
            from
                df
        ),
        group_data_prior as (
            select
                query,
                sum(clicks) as sum_clicks_prior,
                sum(impressions) as sum_impr_prior,
                avg(position) as avg_pos_prior
            from
                source
            where
                tag = 'prior'
            group by
                query
        ),
        group_data_post as (
            select
                query,
                sum(clicks) as sum_clicks_post,
                sum(impressions) as sum_impr_post,
                avg(position) as avg_pos_post
            from
                source
            where
                tag = 'after'
            group by
                query
        ),
        join_data as (
            select
                prior.query,
                sum_clicks_prior,
                sum_clicks_post,
                (sum_clicks_post - sum_clicks_prior) as clicks_diff,
                sum_impr_prior,
                sum_impr_post,
                (sum_impr_post - sum_impr_prior) as impr_diff,
                avg_pos_prior,
                avg_pos_post,
                (avg_pos_prior - avg_pos_post)*-1 as ranking_diff
            from
                group_data_prior as prior
            full join
                group_data_post as post
            on
                prior.query = post.query
                
        )
        select
            query,
            sum_clicks_prior,
            sum_clicks_post,
            clicks_diff,
            sum_impr_prior,
            sum_impr_post,
            impr_diff,
            round(avg_pos_prior, 2) as avg_pos_prior,
            round(avg_pos_post, 2) as avg_pos_post,
            round(ranking_diff, 2) as ranking_diff
        from join_data
        where
            query is not null
        order by
            clicks_diff desc
        

        """
    ).df()
    con.close()
    sorted_df = df_calculations.sort_values(by=["sum_clicks_post", "sum_impr_post"], ascending=[False, False])

    if sorted_df.empty:
        top_keyword_by_clicks = None
    else:
        top_keyword_by_clicks = sorted_df.iloc[0]["query"]
    
    return df_calculations, top_keyword_by_clicks

def visualize_clicks(df):
    con = duckdb.connect()
    url = df["url"][0]
    df_clicks_over_time = con.sql(
        """
        with source as (
            select
                        STRFTIME(date, '%Y-%m-%d') as date,
                        url,
                        query,
                        clicks,
                        impressions,
                        position,
                        tag
            from
                        df
        ),
        group_data as (
            select
                tag,
                date,
                sum(clicks) as clicks
            from
                source
            group by
                date,
                tag
        )
        select * from group_data

            
        """
    ).df()
    con.close()

    if not df_clicks_over_time.empty:
        color_scale = alt.Scale(
            domain=["after", "prior"],
            range=["#014d4e", "#F33A6A"]
        )
        chart = alt.Chart(df_clicks_over_time).mark_line().encode(
            x=alt.X("date:T", title="Date", timeUnit='yearmonthdate', axis=alt.Axis(format="%m-%d")),
            y=alt.Y("clicks:Q", title="Clicks per Day"),
            color=alt.Color("tag:N", scale=color_scale, legend=alt.Legend(title="Zeitpunkt der Optimierung"))
        ).properties(
            width=700,
            height=400,
            title=f"Clicks over time | '{url}'"
        ).interactive()

        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning(f"ℹ No data for {url}.")
    return None

def visualize_ranking_topquery(df, top_query):
    url = df["url"][0]
    con = duckdb.connect()
    df_clicks_over_time = con.sql(
        f"""
        with source as (
            select
                STRFTIME(date, '%Y-%m-%d') as date,
                url,
                query,
                clicks,
                impressions,
                position,
                tag
            from
                df
            where
                query = '{top_query}'
        ),
        group_data as (
            select
                tag,
                date,
                avg(position) as position
            from
                source
            group by
                date,
                tag
        )
        select * from group_data
        """
    ).df()
    con.close()

    if not df_clicks_over_time.empty:
        color_scale = alt.Scale(
            domain=["after", "prior"],
            range=["#014d4e", "#F33A6A"]
        )
        chart = alt.Chart(df_clicks_over_time).mark_line().encode(
            x=alt.X("date:T", title="Date", timeUnit='yearmonthdate', axis=alt.Axis(format="%m-%d")),
            y=alt.Y("position:Q", title="Avg. Position per Day", scale=alt.Scale(reverse=True)),
            color=alt.Color("tag:N", scale=color_scale, legend=alt.Legend(title="Zeitpunkt der Optimierung"))
        ).properties(
            width=700,
            height=400,
            title=f"Position over time for top query '{top_query}' | '{url}'"
        ).interactive()

        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning(f"ℹ No data for {url}.")
    return None

    