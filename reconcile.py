#This file contains the logic for identifying whether or not the balances reconcile, and reporting the cummulative discrepancy, as well as the specific days the mismatches emerged.
def valid_input(transactions, balance):
    """
    A function that informs the user if the input files are valid, i.e indicates an invalid input if the sizes of transactions and balances don't match, or if either contains a date that the other does not.

    Args:
        transactions (dict): A dict of transaction amounts (positive for deposits, negative for withdrawals) for each date.
        balance (dict): A dict of reported balances (date, balance) into a dict.
    
    Returns:
        bool: True if the input files are valid, False otherwise.
        str: A message indicating the reason for invalid input, or an empty string if the input is valid.
    """
    error_str = ""
    error_bool = True

    for date in transactions:
        if date not in balance:
            error_str += " The date {date} is present in the transactions file but not in the balances file.".format(date=date)
            error_bool = False

    for date in balance:
        if date not in transactions:
            error_str += " The date {date} is present in the balance file but not in the transactions file.".format(date=date)
            error_bool = False
            
    return error_bool, error_str

def compute_expected_balance(transactions):
    """
    Computes the expected balance based on the list of transactions.
    
    Args:
        transactions (dict): A dict of transaction amounts (positive for deposits, negative for withdrawals) for each date.
        
    Returns:
        dict: The expected balance for each day after applying all transactions for each day
    """
    expected_balance = {}
    running = 0
    for date in sorted(transactions):
        running += transactions[date]
        expected_balance[date] = running
    return expected_balance

def compute_discrepancy(expected_balance, actual_balance):
    """
    Computes the discrepancy between the expected balance and the actual balance for each day.
    
    Args:
        expected_balance (dict): The expected balance for each day after applying all transactions for each day
        actual_balance (dict): The actual balance reported for each day.

    Returns:
        dict: A dictionary containing the cumulative discrepancy for each day.
    """
    cumulative_discrepancy = {}
    for date in expected_balance:
        expected = expected_balance[date]
        actual = actual_balance.get(date, 0)  # Default to 0 if the date is not in actual_balance
        discrepancy = expected - actual
        cumulative_discrepancy[date] = discrepancy
    
    return cumulative_discrepancy

def flag_significant_days(cumulative_discrepancy):
    """
    Flags the days where the discrepancy increases or decreases from the previous day.
    
    Args:
        cumulative_discrepancy (dict): A dictionary containing the cumulative discrepancy for each day.
        
    Returns:
        dict: A dictionary of dates where the discrepancy is significant , along with the delta value of the discrepancy.
    """
    significant_days = {}
    previous_discrepancy = None
    
    for date in sorted(cumulative_discrepancy.keys()):
        current_discrepancy = cumulative_discrepancy[date]
        
        if previous_discrepancy is not None:
            delta = current_discrepancy - previous_discrepancy
            if delta != 0:
                significant_days[date] = delta
        
        previous_discrepancy = current_discrepancy
    
    return significant_days

def summarize_day(date, significant_days):
    """
    Summarizes the mismatch on a specific date.
    
    Args:
        date (str): The date the user wants to summarize.
        significant_days (dict): A dictionary of dates where the discrepancy is significant, along with the delta value of the discrepancy.
        
    Returns:
        str: A summary string of the requested date.
    """
    if not date in significant_days:
        return "No significant discrepancies found."
    
    else:
        delta = significant_days[date]
        if delta > 0:
            return f"On {date}, the discrepancy increased by {delta}."            
        else:
            return f"On {date}, the discrepancy decreased by {abs(delta)}."