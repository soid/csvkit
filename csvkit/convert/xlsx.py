#!/usr/bin/env python

from cStringIO import StringIO
import datetime
from types import NoneType

from openpyxl.reader.excel import load_workbook

from csvkit import table

def normalize_empty(values, **kwargs):
    """
    Normalize a column which contains only empty cells.
    """
    return None, [None] * len(values)

def normalize_unicode(values, **kwargs):
    """
    Normalize a column of text cells.
    """
    return unicode, [unicode(v) if v else None for v in values]

def normalize_ints(values, **kwargs):
    """
    Normalize a column of integer cells.
    """
    return int, values 

def normalize_floats(values, **kwargs):
    """
    Normalize a column of float cells.
    """
    return float, [float(v) for v in values]

def normalize_datetimes(values, **kwargs):
    """
    Normalize a column of datetime cells.
    """
    return datetime.datetime, values

def normalize_dates(values, **kwargs):
    """
    Normalize a column of date cells.
    """
    return datetime.date, values 

def normalize_booleans(values, **kwargs):
    """
    Normalize a column of boolean cells.
    """
    return bool, [bool(v) if v != '' else None for v in values] 

# TODO
NORMALIZERS = {
    unicode: normalize_unicode,
    datetime.datetime: normalize_datetimes,
    datetime.date: normalize_dates,
    bool: normalize_booleans,
    int: normalize_ints,
    float: normalize_floats,
    NoneType: normalize_empty
}

def determine_column_type(types):
    """
    Determine the correct type for a column from a list of cell types.
    """
    types_set = set(types)
    types_set.discard(NoneType)

    if len(types_set) == 2:
        if types_set == set([int, float]):
            return float
        elif types_set == set([datetime.datetime, datetime.date]):
            return datetime.datetime

    # Normalize mixed types to text
    if len(types_set) > 1:
        return unicode

    try:
        return types_set.pop()
    except KeyError:
        return NoneType 

def xlsx2csv(f, **kwargs):
    """
    Convert an Excel .xlsx file to csv.
    """
    book = load_workbook(f)
    sheet = book.get_active_sheet()

    tab = table.Table() 

    for i, column in enumerate(sheet.columns):
        # Trim headers
        column_name = column[0].value

        # Empty column name? Truncate remaining data
        if not column_name:
            break

        values = [c.value for c in column[1:]]
        types = [type(v) for v in values]

        column_type = determine_column_type(types)
        t, normal_values = NORMALIZERS[column_type](values)

        column = table.Column(i, column_name, normal_values, normal_type=t)
        tab.append(column)

    o = StringIO()
    output = tab.to_csv(o)
    output = o.getvalue()
    o.close()

    return output 
