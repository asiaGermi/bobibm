"""
Data Loader Module for Financial Risk Management System
Phase 2: Data Layer Implementation

This module provides data access functions for the HI-Small_Trans.csv dataset
with LRU caching, transaction queries, and statistical analysis.

Dataset Structure (HI-Small_Trans.csv):
- Timestamp: Transaction timestamp (YYYY/MM/DD HH:MM format)
- From Bank: Source bank ID
- Account (From): Source account ID
- To Bank: Destination bank ID
- Account (To): Destination account ID
- Amount Received: Amount received in destination currency
- Receiving Currency: Currency of received amount
- Amount Paid: Amount paid in source currency
- Payment Currency: Currency of paid amount
- Payment Format: Type of payment (Cheque, Reinvestment, etc.)
- Is Laundering: Binary flag (0=legitimate, 1=laundering)

Transaction Key: Composite key of (Timestamp, From Account)
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta

import pandas as pd
import numpy as np


# Constants
DEFAULT_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "raw" / "HI-Small_Trans.csv"
CACHE_SIZE = 1  # Only cache the main dataset once


class DataLoaderError(Exception):
    """Base exception for data loader errors"""
    pass


class DataNotFoundError(DataLoaderError):
    """Raised when data file is not found"""
    pass


class InvalidTransactionKeyError(DataLoaderError):
    """Raised when transaction key is invalid"""
    pass


@lru_cache(maxsize=CACHE_SIZE)
def load_dataset(data_path: Optional[str] = None) -> pd.DataFrame:
    """
    Load the HI-Small_Trans.csv dataset with LRU caching.
    
    This function loads the dataset once and caches it in memory for subsequent calls.
    The cache ensures the CSV is only read from disk once during the application lifecycle.
    
    Args:
        data_path: Optional path to the CSV file. If None, uses default path.
        
    Returns:
        pd.DataFrame: Complete transaction dataset with all columns
        
    Raises:
        DataNotFoundError: If the CSV file is not found
        DataLoaderError: If there's an error reading the CSV
        
    Example:
        >>> df = load_dataset()
        >>> print(df.shape)
        (1000000, 11)
    """
    if data_path is None:
        data_path = str(DEFAULT_DATA_PATH)
    
    if not os.path.exists(data_path):
        raise DataNotFoundError(f"Dataset not found at path: {data_path}")
    
    try:
        # Read CSV with appropriate data types
        df = pd.read_csv(
            data_path,
            parse_dates=['Timestamp'],
            date_format='%Y/%m/%d %H:%M'
        )
        
        # Rename columns to be more Python-friendly (remove spaces)
        df.columns = [
            'timestamp',
            'from_bank',
            'from_account',
            'to_bank',
            'to_account',
            'amount_received',
            'receiving_currency',
            'amount_paid',
            'payment_currency',
            'payment_format',
            'is_laundering'
        ]
        
        # Ensure proper data types
        df['from_account'] = df['from_account'].astype(str)
        df['to_account'] = df['to_account'].astype(str)
        df['from_bank'] = df['from_bank'].astype(str)
        df['to_bank'] = df['to_bank'].astype(str)
        df['is_laundering'] = df['is_laundering'].astype(int)
        
        return df
        
    except Exception as e:
        raise DataLoaderError(f"Error loading dataset: {str(e)}")


def get_transactions_by_account(account_id: str, data_path: Optional[str] = None) -> pd.DataFrame:
    """
    Retrieve all transactions for a specific account (both sent and received).
    
    Args:
        account_id: The account ID to filter transactions
        data_path: Optional path to the CSV file
        
    Returns:
        pd.DataFrame: All transactions involving the specified account
        
    Raises:
        DataLoaderError: If there's an error loading data
        
    Example:
        >>> transactions = get_transactions_by_account("8000EBD30")
        >>> print(f"Found {len(transactions)} transactions")
    """
    df = load_dataset(data_path)
    
    # Filter transactions where account is either sender or receiver
    mask = (df['from_account'] == str(account_id)) | (df['to_account'] == str(account_id))
    result = df[mask].copy()
    
    # Sort by timestamp descending (most recent first)
    result = result.sort_values('timestamp', ascending=False)
    
    return result


def get_transactions_by_bank(bank_id: str, data_path: Optional[str] = None) -> pd.DataFrame:
    """
    Retrieve all transactions for a specific bank (both sent and received).
    
    Args:
        bank_id: The bank ID to filter transactions
        data_path: Optional path to the CSV file
        
    Returns:
        pd.DataFrame: All transactions involving the specified bank
        
    Raises:
        DataLoaderError: If there's an error loading data
        
    Example:
        >>> transactions = get_transactions_by_bank("010")
        >>> print(f"Bank 010 has {len(transactions)} transactions")
    """
    df = load_dataset(data_path)
    
    # Filter transactions where bank is either sender or receiver
    mask = (df['from_bank'] == str(bank_id)) | (df['to_bank'] == str(bank_id))
    result = df[mask].copy()
    
    # Sort by timestamp descending (most recent first)
    result = result.sort_values('timestamp', ascending=False)
    
    return result


def get_transaction_by_key(
    timestamp: str,
    from_account: str,
    data_path: Optional[str] = None
) -> Dict:
    """
    Retrieve a specific transaction by its composite key (timestamp + from_account).
    
    The transaction key is a composite of timestamp and from_account, which uniquely
    identifies a transaction in the dataset.
    
    Args:
        timestamp: Transaction timestamp (ISO format or 'YYYY/MM/DD HH:MM')
        from_account: Source account ID
        data_path: Optional path to the CSV file
        
    Returns:
        dict: Transaction data as a dictionary, or empty dict if not found
        
    Raises:
        InvalidTransactionKeyError: If timestamp format is invalid
        DataLoaderError: If there's an error loading data
        
    Example:
        >>> tx = get_transaction_by_key("2022/09/01 00:20", "8000EBD30")
        >>> print(tx['amount_paid'])
        3697.34
    """
    df = load_dataset(data_path)
    
    # Parse timestamp to ensure consistent format
    try:
        if 'T' in timestamp:  # ISO format
            ts = pd.to_datetime(timestamp)
        else:  # Original format
            ts = pd.to_datetime(timestamp, format='%Y/%m/%d %H:%M')
    except Exception as e:
        raise InvalidTransactionKeyError(f"Invalid timestamp format: {timestamp}. Error: {str(e)}")
    
    # Filter by composite key
    mask = (df['timestamp'] == ts) & (df['from_account'] == str(from_account))
    result = df[mask]
    
    if len(result) == 0:
        return {}
    
    # Return first match as dictionary
    return result.iloc[0].to_dict()


def get_account_history(
    account_id: str,
    days_back: int = 30,
    data_path: Optional[str] = None
) -> Dict:
    """
    Get account transaction history with statistical analysis.
    
    Retrieves transactions for the specified account within the given time window
    and calculates comprehensive statistics.
    
    Args:
        account_id: The account ID to analyze
        days_back: Number of days to look back (default: 30)
        data_path: Optional path to the CSV file
        
    Returns:
        dict: Dictionary containing:
            - account_id: The account ID
            - period_days: Number of days analyzed
            - transactions: List of transaction dictionaries
            - statistics: Dict with statistical metrics including:
                - total_transactions: Total number of transactions
                - sent_count: Number of outgoing transactions
                - received_count: Number of incoming transactions
                - total_sent: Total amount sent
                - total_received: Total amount received
                - net_flow: Net cash flow (received - sent)
                - avg_transaction_amount: Average transaction amount
                - median_transaction_amount: Median transaction amount
                - std_transaction_amount: Standard deviation of amounts
                - max_transaction: Largest transaction amount
                - min_transaction: Smallest transaction amount
                - laundering_count: Number of flagged transactions
                - laundering_percentage: Percentage of flagged transactions
                - unique_counterparties: Number of unique accounts interacted with
                - payment_formats: Distribution of payment types
                
    Raises:
        DataLoaderError: If there's an error loading data
        
    Example:
        >>> history = get_account_history("8000EBD30", days_back=30)
        >>> print(f"Total transactions: {history['statistics']['total_transactions']}")
        >>> print(f"Net flow: ${history['statistics']['net_flow']:.2f}")
    """
    df = load_dataset(data_path)
    
    # Calculate date range
    max_date = df['timestamp'].max()
    start_date = max_date - timedelta(days=days_back)
    
    # Filter transactions for this account within date range
    mask = (
        ((df['from_account'] == str(account_id)) | (df['to_account'] == str(account_id))) &
        (df['timestamp'] >= start_date)
    )
    account_txs = df[mask].copy()
    
    # Separate sent and received transactions
    sent_txs = account_txs[account_txs['from_account'] == str(account_id)]
    received_txs = account_txs[account_txs['to_account'] == str(account_id)]
    
    # Calculate statistics
    statistics = {
        'total_transactions': len(account_txs),
        'sent_count': len(sent_txs),
        'received_count': len(received_txs),
        'total_sent': float(sent_txs['amount_paid'].sum()) if len(sent_txs) > 0 else 0.0,
        'total_received': float(received_txs['amount_received'].sum()) if len(received_txs) > 0 else 0.0,
        'net_flow': 0.0,
        'avg_transaction_amount': 0.0,
        'median_transaction_amount': 0.0,
        'std_transaction_amount': 0.0,
        'max_transaction': 0.0,
        'min_transaction': 0.0,
        'laundering_count': int(account_txs['is_laundering'].sum()),
        'laundering_percentage': 0.0,
        'unique_counterparties': 0,
        'payment_formats': {}
    }
    
    # Calculate derived statistics
    if len(account_txs) > 0:
        statistics['net_flow'] = statistics['total_received'] - statistics['total_sent']
        
        # Use amount_paid for sent, amount_received for received
        all_amounts = pd.concat([
            sent_txs['amount_paid'],
            received_txs['amount_received']
        ])
        
        statistics['avg_transaction_amount'] = float(all_amounts.mean())
        statistics['median_transaction_amount'] = float(all_amounts.median())
        statistics['std_transaction_amount'] = float(all_amounts.std())
        statistics['max_transaction'] = float(all_amounts.max())
        statistics['min_transaction'] = float(all_amounts.min())
        statistics['laundering_percentage'] = (statistics['laundering_count'] / len(account_txs)) * 100
        
        # Count unique counterparties
        counterparties = set()
        counterparties.update(sent_txs['to_account'].unique())
        counterparties.update(received_txs['from_account'].unique())
        counterparties.discard(str(account_id))  # Remove self
        statistics['unique_counterparties'] = len(counterparties)
        
        # Payment format distribution
        payment_formats = account_txs['payment_format'].value_counts().to_dict()
        statistics['payment_formats'] = payment_formats
    
    # Convert transactions to list of dictionaries
    transactions = account_txs.sort_values('timestamp', ascending=False).to_dict('records')
    
    return {
        'account_id': account_id,
        'period_days': days_back,
        'date_range': {
            'start': start_date.isoformat(),
            'end': max_date.isoformat()
        },
        'transactions': transactions,
        'statistics': statistics
    }


def get_transaction_sample(n: int = 100, data_path: Optional[str] = None) -> pd.DataFrame:
    """
    Get a random sample of transactions from the dataset.
    
    Useful for testing, analysis, and demonstration purposes.
    
    Args:
        n: Number of transactions to sample (default: 100)
        data_path: Optional path to the CSV file
        
    Returns:
        pd.DataFrame: Random sample of n transactions
        
    Raises:
        DataLoaderError: If there's an error loading data
        ValueError: If n is less than 1 or greater than dataset size
        
    Example:
        >>> sample = get_transaction_sample(n=50)
        >>> print(f"Sampled {len(sample)} transactions")
    """
    df = load_dataset(data_path)
    
    if n < 1:
        raise ValueError("Sample size must be at least 1")
    
    if n > len(df):
        raise ValueError(f"Sample size {n} exceeds dataset size {len(df)}")
    
    # Return random sample
    return df.sample(n=n, random_state=None).sort_values('timestamp', ascending=False)


# Utility functions for data validation and info

def get_dataset_info(data_path: Optional[str] = None) -> Dict:
    """
    Get summary information about the dataset.
    
    Args:
        data_path: Optional path to the CSV file
        
    Returns:
        dict: Dataset information including size, date range, and basic statistics
    """
    df = load_dataset(data_path)
    
    return {
        'total_transactions': len(df),
        'date_range': {
            'start': df['timestamp'].min().isoformat(),
            'end': df['timestamp'].max().isoformat()
        },
        'unique_accounts': len(set(df['from_account'].unique()) | set(df['to_account'].unique())),
        'unique_banks': len(set(df['from_bank'].unique()) | set(df['to_bank'].unique())),
        'total_volume': float(df['amount_paid'].sum()),
        'laundering_transactions': int(df['is_laundering'].sum()),
        'laundering_percentage': float((df['is_laundering'].sum() / len(df)) * 100),
        'currencies': df['payment_currency'].unique().tolist(),
        'payment_formats': df['payment_format'].unique().tolist()
    }


def clear_cache():
    """
    Clear the LRU cache for the dataset loader.
    
    Use this function if you need to reload the dataset from disk,
    for example after the CSV file has been updated.
    """
    load_dataset.cache_clear()

# Made with Bob
