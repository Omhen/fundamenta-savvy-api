"""Mapper functions for calculating company metrics from financial data."""

from datetime import date, timedelta, datetime
from typing import List, Optional, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models import (
    CompanyMetrics,
    CompanyProfile,
    Quote,
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    Dividend,
)


def safe_divide(numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
    """Safely divide two numbers, returning None if division is not possible."""
    if numerator is None or denominator is None or denominator == 0:
        return None
    return numerator / denominator


def get_ttm_income_statements(session: Session, symbol: str) -> List[IncomeStatement]:
    """Get the last 4 quarterly income statements for TTM calculations."""
    return (
        session.query(IncomeStatement)
        .filter(IncomeStatement.symbol == symbol)
        .filter(IncomeStatement.period.ilike("Q%"))
        .order_by(desc(IncomeStatement.date))
        .limit(4)
        .all()
    )


def get_ttm_balance_sheets(session: Session, symbol: str) -> List[BalanceSheet]:
    """Get the last 4 quarterly balance sheets."""
    return (
        session.query(BalanceSheet)
        .filter(BalanceSheet.symbol == symbol)
        .filter(BalanceSheet.period.ilike("Q%"))
        .order_by(desc(BalanceSheet.date))
        .limit(4)
        .all()
    )


def get_ttm_cash_flows(session: Session, symbol: str) -> List[CashFlowStatement]:
    """Get the last 4 quarterly cash flow statements for TTM calculations."""
    return (
        session.query(CashFlowStatement)
        .filter(CashFlowStatement.symbol == symbol)
        .filter(CashFlowStatement.period.ilike("Q%"))
        .order_by(desc(CashFlowStatement.date))
        .limit(4)
        .all()
    )


def get_latest_quote(session: Session, symbol: str) -> Optional[Quote]:
    """Get the latest quote for a symbol."""
    return (
        session.query(Quote)
        .filter(Quote.symbol == symbol)
        .order_by(desc(Quote.timestamp))
        .first()
    )


def get_company_profile(session: Session, symbol: str) -> Optional[CompanyProfile]:
    """Get company profile for a symbol."""
    return (
        session.query(CompanyProfile)
        .filter(CompanyProfile.symbol == symbol)
        .first()
    )


def get_dividend_history(session: Session, symbol: str) -> List[Dividend]:
    """Get dividend history for the specified number of years."""
    return (
        session.query(Dividend)
        .filter(Dividend.symbol == symbol)
        .order_by(desc(Dividend.date))
        .all()
    )


def sum_ttm(values: List[Optional[float]]) -> Optional[float]:
    """Sum values for TTM calculation, returning None if any value is None."""
    if not values or len(values) < 4:
        return None
    non_none_values = [v for v in values if v is not None]
    if len(non_none_values) < 4:
        return None
    return sum(non_none_values[:4])


def calculate_pe_ratio(
    quote: Optional[Quote],
    income_statements: List[IncomeStatement]
) -> Optional[float]:
    """
    Calculate P/E ratio.
    Formula: Price / EPS (TTM)
    """
    if not quote or not quote.price:
        return None

    ttm_eps = sum_ttm([stmt.eps for stmt in income_statements])
    return safe_divide(quote.price, ttm_eps)


def calculate_pb_ratio(
    quote: Optional[Quote],
    balance_sheets: List[BalanceSheet]
) -> Optional[float]:
    """
    Calculate P/B ratio.
    Formula: Market Cap / Book Value (Total assets - intangible assets - total liabilities)
    """
    if not quote or not quote.market_cap or not balance_sheets:
        return None

    # Use most recent balance sheet equity
    latest_bs = balance_sheets[0] if balance_sheets else None
    if not latest_bs or not latest_bs.total_stockholders_equity:
        return None

    book_value = latest_bs.total_assets - latest_bs.intangible_assets - latest_bs.total_liabilities
    return safe_divide(quote.market_cap, book_value)


def calculate_ps_ratio(
    quote: Optional[Quote],
    income_statements: List[IncomeStatement]
) -> Optional[float]:
    """
    Calculate P/S ratio.
    Formula: Market Cap / Revenue (TTM)
    """
    if not quote or not quote.market_cap:
        return None

    ttm_revenue = sum_ttm([stmt.revenue for stmt in income_statements])
    return safe_divide(quote.market_cap, ttm_revenue)


def calculate_enterprise_value(
    quote: Optional[Quote],
    balance_sheet: Optional[BalanceSheet]
) -> Optional[float]:
    """
    Calculate Enterprise Value.
    Formula: Market Cap + Total Debt - Cash and Cash Equivalents
    """
    if not quote or not quote.market_cap or not balance_sheet:
        return None

    total_debt = balance_sheet.total_debt or 0
    cash = balance_sheet.cash_and_cash_equivalents or 0

    return quote.market_cap + total_debt - cash


def calculate_ev_ebitda_ratio(
    quote: Optional[Quote],
    balance_sheets: List[BalanceSheet],
    income_statements: List[IncomeStatement]
) -> Optional[float]:
    """
    Calculate EV/EBITDA ratio.
    Formula: Enterprise Value / EBITDA (TTM)
    """
    if not balance_sheets:
        return None

    ev = calculate_enterprise_value(quote, balance_sheets[0])
    if ev is None:
        return None

    ttm_ebitda = sum_ttm([stmt.ebitda for stmt in income_statements])
    return safe_divide(ev, ttm_ebitda)


def calculate_ev_fcf_ratio(
    quote: Optional[Quote],
    balance_sheets: List[BalanceSheet],
    cash_flows: List[CashFlowStatement]
) -> Optional[float]:
    """
    Calculate EV/FCF ratio.
    Formula: Enterprise Value / Free Cash Flow (TTM)
    """
    if not balance_sheets:
        return None

    ev = calculate_enterprise_value(quote, balance_sheets[0])
    if ev is None:
        return None

    ttm_fcf = sum_ttm([stmt.free_cash_flow for stmt in cash_flows])
    return safe_divide(ev, ttm_fcf)


def calculate_copm(
    income_statements: List[IncomeStatement]
) -> Optional[float]:
    """
    Calculate Cash Operating Profit Margin (COPM) aka EBITDA Margin.
    Formula: (Earnings before Interest and Tax + Depreciation + amortization) (TTM) / Revenue (TTM)
    """
    ttm_ebitda = sum_ttm([stmt.ebitda for stmt in income_statements])
    ttm_revenue = sum_ttm([stmt.revenue for stmt in income_statements])
    return safe_divide(ttm_ebitda, ttm_revenue)


def calculate_roic(
    income_statements: List[IncomeStatement],
    balance_sheets: List[BalanceSheet]
) -> Optional[float]:
    """
    Calculate Return on Invested Capital (ROIC).
    Formula: NOPAT / Invested Capital
    Where:
        NOPAT = Operating Income * (1 - Tax Rate)
        Invested Capital = Total Debt + Total Equity - Cash
    """
    if not income_statements or not balance_sheets:
        return None

    # TTM operating income
    ttm_operating_income = sum_ttm([stmt.operating_income for stmt in income_statements])
    if ttm_operating_income is None:
        return None

    # Calculate effective tax rate from most recent quarter
    latest_stmt = income_statements[0]
    if latest_stmt.income_before_tax and latest_stmt.income_before_tax != 0:
        tax_rate = safe_divide(latest_stmt.income_tax_expense, latest_stmt.income_before_tax)
        if tax_rate is None or tax_rate < 0:
            tax_rate = 0.21  # Default corporate tax rate
    else:
        tax_rate = 0.21

    nopat = ttm_operating_income * (1 - tax_rate)

    # Invested capital from most recent balance sheet
    latest_bs = balance_sheets[0]
    total_debt = latest_bs.total_debt or 0
    total_equity = latest_bs.total_stockholders_equity or 0
    cash = latest_bs.cash_and_cash_equivalents or 0

    invested_capital = total_debt + total_equity - cash
    if invested_capital <= 0:
        return None

    return safe_divide(nopat, invested_capital)


def calculate_rota(
    income_statements: List[IncomeStatement],
    balance_sheets: List[BalanceSheet]
) -> Optional[float]:
    """
    Calculate Return on Tangible Assets (ROTA).
    Formula: Net Income (TTM) / (Total Assets - Goodwill - Intangible Assets)
    """
    if not balance_sheets:
        return None

    ttm_net_income = sum_ttm([stmt.net_income for stmt in income_statements])
    if ttm_net_income is None:
        return None

    # Tangible assets from most recent balance sheet
    latest_bs = balance_sheets[0]
    total_assets = latest_bs.total_assets or 0
    goodwill = latest_bs.goodwill or 0
    intangibles = latest_bs.intangible_assets or 0

    tangible_assets = total_assets - goodwill - intangibles
    if tangible_assets <= 0:
        return None

    return safe_divide(ttm_net_income, tangible_assets)


def calculate_debt_ebitda_ratio(
    balance_sheets: List[BalanceSheet],
    income_statements: List[IncomeStatement]
) -> Optional[float]:
    """
    Calculate Debt/EBITDA ratio.
    Formula: Total Debt / EBITDA (TTM)
    """
    if not balance_sheets:
        return None

    total_debt = balance_sheets[0].total_debt
    if total_debt is None:
        return None

    ttm_ebitda = sum_ttm([stmt.ebitda for stmt in income_statements])
    return safe_divide(total_debt, ttm_ebitda)


def calculate_dividend_yield(
    dividends: List[Dividend],
    quote: Optional[Quote]
) -> Optional[float]:
    """
    Calculate dividend yield.
    Formula: Annual Dividend / Price
    """
    if not quote or not quote.price or not dividends:
        return None

    # Sum dividends from the last year
    one_year_ago = date.today() - timedelta(days=365)
    annual_dividends = sum(
        d.adj_dividend or d.dividend or 0
        for d in dividends
        if d.date and d.date >= one_year_ago
    )

    if annual_dividends == 0:
        return None

    return safe_divide(annual_dividends, quote.price)


def calculate_dividend_payout(
    cash_flows: List[CashFlowStatement],
    income_statements: List[IncomeStatement]
) -> Optional[float]:
    """
    Calculate dividend payout ratio.
    Formula: Dividends Paid (TTM) / Net Income (TTM)
    """
    ttm_dividends = sum_ttm([abs(stmt.dividends_paid or 0) for stmt in cash_flows])
    ttm_net_income = sum_ttm([stmt.net_income for stmt in income_statements])

    if ttm_dividends is None or ttm_dividends == 0:
        return None

    return safe_divide(ttm_dividends, ttm_net_income)


def calculate_dividend_growth(dividends: List[Dividend], years: int = 10) -> Optional[float]:
    """
    Calculate 10-year dividend CAGR.
    Formula: (Dividend_now / Dividend_10y_ago)^(1/10) - 1
    """
    if not dividends:
        return None

    dividend_by_year = _get_yearly_dividends(dividends)
    if len(dividend_by_year.keys()) < 2:
        return None

    years_sorted = sorted(dividend_by_year.keys(), reverse=True)

    # Need at least 10 years of data for proper CAGR
    current_year = datetime.utcnow().year
    last_year = years_sorted[0] if years_sorted[0] < current_year else years_sorted[1]
    # Find the oldest year that's roughly 10 years ago
    target_year = last_year - years

    first_year = None
    for year in years_sorted:
        if year <= target_year:
            first_year = year
            break

    if first_year is None:
        # Use the oldest available if we don't have 10 years
        first_year = years_sorted[-1]

    years_diff = last_year - first_year
    if years_diff < 1:
        return 0

    current_div = dividend_by_year[last_year]
    oldest_div = dividend_by_year[first_year]

    if oldest_div <= 0 or current_div <= 0:
        return 0

    # CAGR formula
    return (current_div / oldest_div) ** (1 / years_diff) - 1


def calculate_years_increasing_dividend(dividends: List[Dividend]) -> Optional[int]:
    """
    Calculate consecutive years of dividend increases.
    """
    if not dividends:
        return None

    dividend_by_year = _get_yearly_dividends(dividends)

    years_sorted = sorted(dividend_by_year.keys(), reverse=True)
    if len(years_sorted) < 2:
        return 0

    now_year = datetime.utcnow().year
    # if the previous year there were no dividends, there were no increases
    if now_year - 1 not in dividend_by_year:
        return 0

    consecutive_increases = 0
    for i in range(len(years_sorted) - 1):
        current_year = years_sorted[i]
        if current_year == now_year:
            continue
        prev_year = years_sorted[i + 1]

        # Check if years are consecutive
        if current_year - prev_year != 1:
            break

        if dividend_by_year[current_year] > dividend_by_year[prev_year]:
            consecutive_increases += 1
        else:
            break

    return consecutive_increases


def _get_yearly_dividends(dividends):
    # Get annual dividend totals
    dividend_by_year = {}
    for d in dividends:
        if d.date:
            year = d.date.year
            if year not in dividend_by_year:
                dividend_by_year[year] = 0
            dividend_by_year[year] += d.adj_dividend or d.dividend or 0
    return dividend_by_year


def calculate_score(pe_ratio, pb_ratio, ps_ratio, ev_ebitda_ratio, ev_fcf_ratio, copm, roic, rota, debt_ebitda_ratio,
                    dividend_yield, dividend_payout, dividend_growth_10y, years_inc_dividend) -> float:
    score: float = 0
    if pe_ratio is not None and (0 < pe_ratio < 30):
        if 8 < pe_ratio < 15:
            score += 10
        if pe_ratio <= 8:
            score += pe_ratio * 10 / 8.0
        if pe_ratio >= 15:
            score += (30 - pe_ratio) * 10 / 15.0
    if pb_ratio is not None and pb_ratio < 10:
        score += 10 if pb_ratio < 5 else 10 - (pb_ratio - 5) * 2.0
    if ps_ratio is not None and ps_ratio < 6:
        score += 10 if ps_ratio < 3 else 10 - (ps_ratio - 3) * 10 / 3.0
    if ev_ebitda_ratio is not None and ev_ebitda_ratio < 18:
        score += 10 if ev_ebitda_ratio < 12 else 10 - (ev_ebitda_ratio - 12) * 10 / 6.0
    if ev_fcf_ratio is not None and ev_fcf_ratio < 30:
        score += 10 if ev_ebitda_ratio <= 20 else 30 - ev_fcf_ratio
    if copm is not None and copm > 0:
        score += 10 if copm > 0.20 else copm * 1000 / 20
    if roic is not None and roic > 0:
        score += 10 if roic >= 0.15 else roic * 1000 / 15
    if rota is not None and rota > 0:
        score += 10 if rota >= 0.15 else rota * 1000 / 15
    if debt_ebitda_ratio is not None and debt_ebitda_ratio < 6:
        score += 10 if debt_ebitda_ratio <= 3 else 10 - (debt_ebitda_ratio - 3) * 10 / 3.0
    if dividend_yield is not None and dividend_yield > 0:
        score += 10 if dividend_yield > 0.03 else dividend_yield * 10 / 0.03
    if dividend_payout is not None and dividend_payout < 0.9:
        score += 10 if dividend_payout < 0.8 else 10 - (dividend_payout - 0.8) * 100
    if dividend_growth_10y is not None and dividend_growth_10y > 0:
        score += 10 if dividend_growth_10y > 0.07 else dividend_growth_10y * 100 / 0.07
    if years_inc_dividend is not None and years_inc_dividend > 0:
        score += 10 if years_inc_dividend > 10 else years_inc_dividend

    return score / 13  # score average of the 13 datapoints


def calculate_company_metrics(
        symbol: str,
    session: Session
) -> Optional[CompanyMetrics]:
    """
    Calculate all metrics for a company and return a CompanyMetrics model.
    """
    # Fetch all required data
    quote = get_latest_quote(session, symbol)
    profile = get_company_profile(session, symbol)
    income_statements = get_ttm_income_statements(session, symbol)
    balance_sheets = get_ttm_balance_sheets(session, symbol)
    cash_flows = get_ttm_cash_flows(session, symbol)
    dividends = get_dividend_history(session, symbol)

    pe_ratio = calculate_pe_ratio(quote, income_statements)
    pb_ratio = calculate_pb_ratio(quote, balance_sheets)
    ps_ratio = calculate_ps_ratio(quote, income_statements)
    ev_ebitda_ratio = calculate_ev_ebitda_ratio(quote, balance_sheets, income_statements)
    ev_fcf_ratio = calculate_ev_fcf_ratio(quote, balance_sheets, cash_flows)
    copm = calculate_copm(income_statements)
    roic = calculate_roic(income_statements, balance_sheets)
    rota = calculate_rota(income_statements, balance_sheets)
    debt_ebitda_ratio = calculate_debt_ebitda_ratio(balance_sheets, income_statements)
    dividend_yield = calculate_dividend_yield(dividends, quote)
    dividend_payout = calculate_dividend_payout(cash_flows, income_statements)
    dividend_growth_10y = calculate_dividend_growth(dividends, years=10)
    years_inc_dividend = calculate_years_increasing_dividend(dividends)
    score = calculate_score(
        pe_ratio,
        pb_ratio,
        ps_ratio,
        ev_ebitda_ratio,
        ev_fcf_ratio,
        copm,
        roic,
        rota,
        debt_ebitda_ratio,
        dividend_yield,
        dividend_payout,
        dividend_growth_10y,
        years_inc_dividend
    )

    # Need at least basic data to calculate metrics
    if not income_statements and not balance_sheets:
        return None

    # Calculate all metrics
    return CompanyMetrics(
        symbol=symbol,
        company_name=profile.company_name if profile else None,
        sector=profile.sector if profile else None,
        market_cap=quote.market_cap if quote else None,

        # Valuation ratios
        pe_ratio=pe_ratio,
        pb_ratio=pb_ratio,
        ps_ratio=ps_ratio,

        # Enterprise value ratios
        ev_ebitda_ratio=ev_ebitda_ratio,
        ev_fcf_ratio=ev_fcf_ratio,

        # Profitability
        copm=copm,
        roic=roic,
        rota=rota,

        # Leverage
        debt_ebitda_ratio=debt_ebitda_ratio,

        # Dividends
        dividend_yield=dividend_yield,
        dividend_payout=dividend_payout,
        dividend_growth_10y=dividend_growth_10y,
        years_increasing_dividend=years_inc_dividend,

        score=score,
    )
