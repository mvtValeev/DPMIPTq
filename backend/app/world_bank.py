import wbdata
import pandas as pd

def fetch_world_bank_data(
    countries: list[str],
    indicators: dict[str, str],
    start_year: int,
    end_year: int
) -> pd.DataFrame:
    # формируем диапазон дат для WB API
    date_range = (str(start_year), str(end_year))
    import wbdata
    # загружаем данные с правильным параметром parse_dates
    df = wbdata.get_dataframe(
        indicators,
        country=countries,
        date=date_range,
        parse_dates=True
    )

    # сбрасываем индекс, переименовываем колонки
    df = df.reset_index().rename(columns={"country": "страна", "date": "год"})
    df["country"] = df["country"].str.lower().str.strip()
    # переводим год из datetime в целое

    return df


