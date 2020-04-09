from pandas import DataFrame


def create_state_with_value(rows: tuple, columns: tuple, value: object) -> DataFrame:
    expected_state = DataFrame(columns=columns, index=rows)
    expected_state.fillna(value, inplace=True)
    return expected_state


def update_rows_to_value_for_column(state: DataFrame, rows: tuple, column: str, value: object) -> DataFrame:
    for row in rows:
        state.loc[row, column] = value
    return state


def update_rows_with_old_to_new_for_column(state: DataFrame, rows: tuple, column: str, old_value: object,
                                           new_value: object) -> DataFrame:
    for row in rows:
        if state.loc[row, column] == old_value:
            state.loc[row, column] = new_value

    return state
