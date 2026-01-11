"""Pydantic schemas for financial statements domain."""

from datetime import date
from typing import Optional

from pydantic import BaseModel


class IncomeStatementResponse(BaseModel):
    """Income statement response schema."""

    date: date
    symbol: str
    reported_currency: Optional[str] = None
    cik: Optional[str] = None
    filling_date: Optional[date] = None
    accepted_date: Optional[date] = None
    calendar_year: Optional[str] = None
    period: Optional[str] = None
    revenue: Optional[float] = None
    cost_of_revenue: Optional[float] = None
    gross_profit: Optional[float] = None
    gross_profit_ratio: Optional[float] = None
    research_and_development_expenses: Optional[float] = None
    general_and_administrative_expenses: Optional[float] = None
    selling_and_marketing_expenses: Optional[float] = None
    selling_general_and_administrative_expenses: Optional[float] = None
    other_expenses: Optional[float] = None
    operating_expenses: Optional[float] = None
    cost_and_expenses: Optional[float] = None
    interest_income: Optional[float] = None
    interest_expense: Optional[float] = None
    depreciation_and_amortization: Optional[float] = None
    ebitda: Optional[float] = None
    ebitda_ratio: Optional[float] = None
    operating_income: Optional[float] = None
    operating_income_ratio: Optional[float] = None
    total_other_income_expenses_net: Optional[float] = None
    income_before_tax: Optional[float] = None
    income_before_tax_ratio: Optional[float] = None
    income_tax_expense: Optional[float] = None
    net_income: Optional[float] = None
    net_income_ratio: Optional[float] = None
    eps: Optional[float] = None
    eps_diluted: Optional[float] = None
    weighted_average_shs_out: Optional[float] = None
    weighted_average_shs_out_dil: Optional[float] = None
    link: Optional[str] = None
    final_link: Optional[str] = None

    class Config:
        from_attributes = True


class BalanceSheetResponse(BaseModel):
    """Balance sheet response schema."""

    date: date
    symbol: str
    reported_currency: Optional[str] = None
    cik: Optional[str] = None
    filling_date: Optional[date] = None
    accepted_date: Optional[date] = None
    calendar_year: Optional[str] = None
    period: Optional[str] = None
    cash_and_cash_equivalents: Optional[float] = None
    short_term_investments: Optional[float] = None
    cash_and_short_term_investments: Optional[float] = None
    net_receivables: Optional[float] = None
    inventory: Optional[float] = None
    other_current_assets: Optional[float] = None
    total_current_assets: Optional[float] = None
    property_plant_equipment_net: Optional[float] = None
    goodwill: Optional[float] = None
    intangible_assets: Optional[float] = None
    goodwill_and_intangible_assets: Optional[float] = None
    long_term_investments: Optional[float] = None
    tax_assets: Optional[float] = None
    other_non_current_assets: Optional[float] = None
    total_non_current_assets: Optional[float] = None
    other_assets: Optional[float] = None
    total_assets: Optional[float] = None
    account_payables: Optional[float] = None
    short_term_debt: Optional[float] = None
    tax_payables: Optional[float] = None
    deferred_revenue: Optional[float] = None
    other_current_liabilities: Optional[float] = None
    total_current_liabilities: Optional[float] = None
    long_term_debt: Optional[float] = None
    deferred_revenue_non_current: Optional[float] = None
    deferred_tax_liabilities_non_current: Optional[float] = None
    other_non_current_liabilities: Optional[float] = None
    total_non_current_liabilities: Optional[float] = None
    other_liabilities: Optional[float] = None
    capital_lease_obligations: Optional[float] = None
    total_liabilities: Optional[float] = None
    preferred_stock: Optional[float] = None
    common_stock: Optional[float] = None
    retained_earnings: Optional[float] = None
    accumulated_other_comprehensive_income_loss: Optional[float] = None
    other_total_stockholders_equity: Optional[float] = None
    total_stockholders_equity: Optional[float] = None
    total_equity: Optional[float] = None
    total_liabilities_and_stockholders_equity: Optional[float] = None
    minority_interest: Optional[float] = None
    total_liabilities_and_total_equity: Optional[float] = None
    total_investments: Optional[float] = None
    total_debt: Optional[float] = None
    net_debt: Optional[float] = None
    link: Optional[str] = None
    final_link: Optional[str] = None

    class Config:
        from_attributes = True


class CashFlowStatementResponse(BaseModel):
    """Cash flow statement response schema."""

    date: date
    symbol: str
    reported_currency: Optional[str] = None
    cik: Optional[str] = None
    filling_date: Optional[date] = None
    accepted_date: Optional[date] = None
    calendar_year: Optional[str] = None
    period: Optional[str] = None
    net_income: Optional[float] = None
    depreciation_and_amortization: Optional[float] = None
    deferred_income_tax: Optional[float] = None
    stock_based_compensation: Optional[float] = None
    change_in_working_capital: Optional[float] = None
    accounts_receivables: Optional[float] = None
    inventory: Optional[float] = None
    accounts_payables: Optional[float] = None
    other_working_capital: Optional[float] = None
    other_non_cash_items: Optional[float] = None
    net_cash_provided_by_operating_activities: Optional[float] = None
    investments_in_property_plant_and_equipment: Optional[float] = None
    acquisitions_net: Optional[float] = None
    purchases_of_investments: Optional[float] = None
    sales_maturities_of_investments: Optional[float] = None
    other_investing_activities: Optional[float] = None
    net_cash_used_for_investing_activities: Optional[float] = None
    debt_repayment: Optional[float] = None
    common_stock_issued: Optional[float] = None
    common_stock_repurchased: Optional[float] = None
    dividends_paid: Optional[float] = None
    other_financing_activities: Optional[float] = None
    net_cash_used_provided_by_financing_activities: Optional[float] = None
    effect_of_forex_changes_on_cash: Optional[float] = None
    net_change_in_cash: Optional[float] = None
    cash_at_end_of_period: Optional[float] = None
    cash_at_beginning_of_period: Optional[float] = None
    operating_cash_flow: Optional[float] = None
    capital_expenditure: Optional[float] = None
    free_cash_flow: Optional[float] = None
    link: Optional[str] = None
    final_link: Optional[str] = None

    class Config:
        from_attributes = True
