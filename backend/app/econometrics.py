import pandas as pd
import statsmodels.api as sm
from typing import List
from linearmodels.panel import PanelOLS, RandomEffects
from linearmodels.iv import IV2SLS


def perform_ols_analysis(df: pd.DataFrame, dependent_var: str, base_var: str, control_vars: List[str]):
    X = df[[base_var] + control_vars]
    X = sm.add_constant(X)
    y = df[dependent_var]
    model = sm.OLS(y, X, missing='drop').fit()
    return {
        "method": "OLS",
        "params": model.params.to_dict(),
        "pvalues": model.pvalues.to_dict(),
        "r_squared": model.rsquared,
        "summary": model.summary().as_text()
    }


def perform_2sls_analysis(df: pd.DataFrame, dependent_var: str, endog_var: str, exog_vars: List[str], instrument_vars: List[str]):
    exog = sm.add_constant(df[exog_vars])
    endog = df[endog_var]
    instr = df[instrument_vars]
    y = df[dependent_var]
    iv = IV2SLS(dependent=y, exog=exog, endog=endog, instruments=instr).fit()
    return {
        "method": "2SLS",
        "params": iv.params.to_dict(),
        "pvalues": iv.pvalues.to_dict(),
        "r_squared": iv.rsquared,
        "summary": iv.summary.as_text()
    }


def perform_fe_analysis(df: pd.DataFrame, dependent_var: str, exog_vars: List[str], entity: str, time: str):
    panel = df.set_index([entity, time])
    exog = sm.add_constant(panel[exog_vars])
    y = panel[dependent_var]
    mod = PanelOLS(y, exog, entity_effects=True).fit()
    return {
        "method": "Fixed Effects",
        "params": mod.params.to_dict(),
        "pvalues": mod.pvalues.to_dict(),
        "r_squared": mod.rsquared,
        "summary": mod.summary.as_text()
    }


def perform_re_analysis(df: pd.DataFrame, dependent_var: str, exog_vars: List[str], entity: str, time: str):
    panel = df.set_index([entity, time])
    exog = sm.add_constant(panel[exog_vars])
    y = panel[dependent_var]
    mod = RandomEffects(y, exog).fit()
    return {
        "method": "Random Effects",
        "params": mod.params.to_dict(),
        "pvalues": mod.pvalues.to_dict(),
        "r_squared": mod.rsquared,
        "summary": mod.summary.as_text()
    }


def perform_analysis(df: pd.DataFrame, method: str, **kwargs):
    """
    method: 'OLS', '2SLS', 'FE', 'RE'
    kwargs per method:
      OLS: dependent_var, base_var, control_vars
      2SLS: dependent_var, base_var (endog), control_vars (exog), instrument_vars
      FE/RE: dependent_var, exog_vars, entity, time
    """
    m = method.lower()
    if m == 'ols':
        if 'dependent_var' not in kwargs or 'base_var' not in kwargs:
            raise ValueError("OLS requires 'dependent_var' and 'base_var'")
        return perform_ols_analysis(
            df,
            kwargs['dependent_var'],
            kwargs['base_var'],
            kwargs.get('control_vars', [])
        )
    elif m == '2sls':
        for param in ['dependent_var', 'base_var', 'instrument_vars']:
            if param not in kwargs:
                raise ValueError(f"2SLS requires '{param}'")
        return perform_2sls_analysis(
            df,
            kwargs['dependent_var'],
            kwargs['base_var'],
            kwargs.get('control_vars', []),
            kwargs['instrument_vars']
        )
    elif m == 'fe':
        for param in ['dependent_var', 'exog_vars', 'entity', 'time']:
            if param not in kwargs:
                raise ValueError(f"FE requires '{param}'")
        return perform_fe_analysis(
            df,
            kwargs['dependent_var'],
            kwargs['exog_vars'],
            kwargs['entity'],
            kwargs['time']
        )
    elif m == 're':
        for param in ['dependent_var', 'exog_vars', 'entity', 'time']:
            if param not in kwargs:
                raise ValueError(f"RE requires '{param}'")
        return perform_re_analysis(
            df,
            kwargs['dependent_var'],
            kwargs['exog_vars'],
            kwargs['entity'],
            kwargs['time']
        )
    else:
        raise ValueError(f"Unknown method '{method}'")
    """
    method: 'OLS', '2SLS', 'FE', 'RE'
    kwargs per method:
      OLS: dependent_var, base_var, control_vars
      2SLS: dependent_var, base_var (endog), control_vars (exog), instrument_vars
      FE/RE: dependent_var, exog_vars, entity, time
    """
    m = method.lower()
    if m == 'ols':
        return perform_ols_analysis(
            df,
            kwargs['dependent_var'],
            kwargs['base_var'],
            kwargs.get('control_vars', [])
        )
    elif m == '2sls':
        return perform_2sls_analysis(
            df,
            kwargs['dependent_var'],
            kwargs['base_var'],
            kwargs.get('control_vars', []),
            kwargs['instrument_vars']
        )
    elif m == 'fe':
        return perform_fe_analysis(
            df,
            kwargs['dependent_var'],
            kwargs.get('exog_vars', []),
            kwargs['entity'],
            kwargs['time']
        )
    elif m == 're':
        return perform_re_analysis(
            df,
            kwargs['dependent_var'],
            kwargs.get('exog_vars', []),
            kwargs['entity'],
            kwargs['time']
        )
    else:
        raise ValueError(f"Unknown method: {method}")