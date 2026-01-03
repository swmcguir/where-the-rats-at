"""Response time and equity metrics calculations."""

import pandas as pd
import numpy as np
from typing import Dict, Optional


def calculate_ward_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate response time metrics by ward.

    Args:
        df: DataFrame with rodent complaints (must have 'ward', 'response_days', 'status')

    Returns:
        DataFrame with metrics per ward
    """
    # Filter to completed complaints with valid response times
    completed = df[
        (df['status'].str.contains('Completed', case=False, na=False)) &
        (df['response_days'].notna()) &
        (df['response_days'] > 0)
    ].copy()

    # Group by ward and calculate metrics
    metrics = completed.groupby('ward').agg(
        total_complaints=('sr_number', 'count'),
        median_response=('response_days', 'median'),
        mean_response=('response_days', 'mean'),
        p90_response=('response_days', lambda x: np.percentile(x, 90)),
        min_response=('response_days', 'min'),
        max_response=('response_days', 'max'),
        std_response=('response_days', 'std')
    ).reset_index()

    # Calculate completion rate
    all_by_ward = df.groupby('ward').size().reset_index(name='all_complaints')
    completed_by_ward = completed.groupby('ward').size().reset_index(name='completed')

    rates = all_by_ward.merge(completed_by_ward, on='ward', how='left')
    rates['completed'] = rates['completed'].fillna(0)
    rates['completion_rate'] = (rates['completed'] / rates['all_complaints'] * 100).round(1)

    # Merge with metrics
    metrics = metrics.merge(rates[['ward', 'completion_rate', 'all_complaints']], on='ward', how='left')

    # Rank by median response time (1 = fastest)
    metrics['rank'] = metrics['median_response'].rank(method='min').astype(int)

    # Calculate city-wide median for comparison
    city_median = completed['response_days'].median()
    metrics['vs_city_median'] = ((metrics['median_response'] - city_median) / city_median * 100).round(1)

    # Sort by rank
    metrics = metrics.sort_values('rank')

    return metrics


def calculate_ward_grades(metrics: pd.DataFrame,
                          min_complaints_threshold: int = 800) -> pd.DataFrame:
    """Add letter grades using MULTI-FACTOR scoring (v5 - percentile-based).

    Five factors weighted by priority, scored using percentile ranking:
    - Median Response (30%): Core speed metric
    - Volume Factor (25%): Credit for handling high workload
    - P90 Response (20%): Worst-case scenario handling
    - Consistency (15%): Low variance = reliable service
    - Completion Rate (10%): Basic effectiveness

    Args:
        metrics: DataFrame from calculate_ward_metrics()
        min_complaints_threshold: Threshold for low sample size flag

    Returns:
        DataFrame with 'grade' column and factor scores added
    """
    metrics = metrics.copy()

    # Flag wards with low sample size (informational only)
    metrics['low_sample_size'] = metrics['total_complaints'] < min_complaints_threshold

    n = len(metrics)

    def percentile_score(series, ascending=True):
        """Convert values to percentile-based scores (20-100 range).

        Best performer gets 100, worst gets 20.
        """
        if ascending:  # Lower is better (response time, std dev)
            ranks = series.rank(ascending=True, method='average')
        else:  # Higher is better (volume, completion)
            ranks = series.rank(ascending=False, method='average')

        # Convert rank to 20-100 score
        # Rank 1 (best) = 100, Rank n (worst) = 20
        scores = 100 - ((ranks - 1) / max(n - 1, 1)) * 80
        return scores

    # 1. Speed Score (30%) - lower median response is better
    metrics['speed_score'] = percentile_score(metrics['median_response'], ascending=True)

    # 2. Volume Score (25%) - higher volume handled = better
    metrics['volume_score'] = percentile_score(metrics['total_complaints'], ascending=False)

    # 3. P90 Score (20%) - lower P90 is better (no long waits)
    metrics['p90_score'] = percentile_score(metrics['p90_response'], ascending=True)

    # 4. Consistency Score (15%) - lower std dev is better
    metrics['consistency_score'] = percentile_score(metrics['std_response'], ascending=True)

    # 5. Completion Score (10%) - higher completion rate is better
    metrics['completion_score'] = percentile_score(metrics['completion_rate'], ascending=False)

    # Calculate weighted final score
    metrics['final_score'] = (
        metrics['speed_score'] * 0.30 +
        metrics['volume_score'] * 0.25 +
        metrics['p90_score'] * 0.20 +
        metrics['consistency_score'] * 0.15 +
        metrics['completion_score'] * 0.10
    )

    # Assign grade based on final score
    # A: 80+, B: 65-79, C: 50-64, D: 35-49, F: <35
    def assign_grade(score):
        if score >= 80:
            return 'A'
        elif score >= 65:
            return 'B'
        elif score >= 50:
            return 'C'
        elif score >= 35:
            return 'D'
        else:
            return 'F'

    metrics['grade'] = metrics['final_score'].apply(assign_grade)

    # Keep for backwards compatibility
    metrics['adjusted_response'] = metrics['median_response']
    metrics['volume_adjustment'] = 1.0
    metrics['response_score'] = metrics['speed_score']  # Alias

    # Add grade color for visualization
    grade_colors = {
        'A': '#22c55e',  # Green
        'B': '#84cc16',  # Lime
        'C': '#eab308',  # Yellow
        'D': '#f97316',  # Orange
        'F': '#ef4444'   # Red
    }
    metrics['grade_color'] = metrics['grade'].map(grade_colors)

    return metrics


def calculate_monthly_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate monthly complaint volume and response time trends.

    Args:
        df: DataFrame with rodent complaints

    Returns:
        DataFrame with monthly aggregates
    """
    df = df.copy()
    df['month'] = df['created_date'].dt.to_period('M')

    monthly = df.groupby('month').agg(
        complaint_count=('sr_number', 'count'),
        median_response=('response_days', 'median'),
        mean_response=('response_days', 'mean')
    ).reset_index()

    monthly['month'] = monthly['month'].dt.to_timestamp()

    return monthly


def calculate_seasonal_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate seasonal patterns (which months have most rats).

    Args:
        df: DataFrame with rodent complaints

    Returns:
        DataFrame with monthly averages across all years
    """
    df = df.copy()
    df['month_num'] = df['created_date'].dt.month
    df['month_name'] = df['created_date'].dt.month_name()

    # Average complaints per month across all years
    seasonal = df.groupby(['month_num', 'month_name']).agg(
        avg_complaints=('sr_number', 'count')
    ).reset_index()

    # Normalize by number of years in dataset
    years = df['created_date'].dt.year.nunique()
    seasonal['avg_complaints'] = (seasonal['avg_complaints'] / years).round(0)

    seasonal = seasonal.sort_values('month_num')

    return seasonal


def get_city_summary(df: pd.DataFrame) -> Dict:
    """Get city-wide summary statistics.

    Args:
        df: DataFrame with rodent complaints

    Returns:
        Dict with summary stats
    """
    completed = df[
        (df['status'].str.contains('Completed', case=False, na=False)) &
        (df['response_days'].notna()) &
        (df['response_days'] > 0)
    ]

    return {
        'total_complaints': len(df),
        'completed_complaints': len(completed),
        'completion_rate': round(len(completed) / len(df) * 100, 1) if len(df) > 0 else 0,
        'median_response_days': round(completed['response_days'].median(), 1) if len(completed) > 0 else None,
        'mean_response_days': round(completed['response_days'].mean(), 1) if len(completed) > 0 else None,
        'wards_with_data': df['ward'].nunique(),
        'date_range': {
            'start': df['created_date'].min(),
            'end': df['created_date'].max()
        }
    }


# Quick test
if __name__ == "__main__":
    from data.fetch import fetch_rodent_complaints

    print("Fetching data...")
    df = fetch_rodent_complaints(days_back=365)
    print(f"Loaded {len(df)} complaints")

    print("\nCity Summary:")
    summary = get_city_summary(df)
    for key, value in summary.items():
        print(f"  {key}: {value}")

    print("\nWard Metrics (top 10 fastest):")
    metrics = calculate_ward_metrics(df)
    metrics = calculate_ward_grades(metrics)
    print(metrics[['ward', 'median_response', 'rank', 'grade', 'total_complaints']].head(10))

    print("\nWard Metrics (bottom 5 slowest):")
    print(metrics[['ward', 'median_response', 'rank', 'grade', 'total_complaints']].tail(5))
