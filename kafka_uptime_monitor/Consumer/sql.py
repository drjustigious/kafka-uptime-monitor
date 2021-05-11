

def create_table(table_name, columns):
    """
    Returns the SQL required to create a table with the given name and columns.
    'columns' should be a list of strings describing each column's name and type:

    create_table("uptime_stats", ["num integer", "name varchar"])

    The table will also have a serial integer primary key called 'id'.
    """
    columns_string = ", ".join(columns)
    sql = "CREATE TABLE IF NOT EXISTS {} (id serial PRIMARY KEY, {});".format(
        table_name,
        columns_string
    )
    return sql


def update(table_name, column_value_pairs):
    """
    Returns the SQL for inserting the given data into the given table.
    'column_value_pairs' should be an iterable of 2-tuples.
    """
    columns = []
    values = []
    for pair in column_value_pairs:
        columns.append(pair[0])
        values.append(pair[1])

    columns_string = ", ".join(columns)
    s_values = len(values)*["%s"]
    values_string = ", ".join(s_values)

    sql = "INSERT INTO {} ({}) VALUES ({})".format(
        table_name,
        columns_string,
        values_string
    )

    return sql, values