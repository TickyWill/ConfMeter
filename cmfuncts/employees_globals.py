"""Module setting globals specific to employees database management.

"""

__all__ = ['CATEGORIES_DIC',
           'EMPLOYEES_ADD_COLS',
           'EMPLOYEES_ARCHI',
           'EMPLOYEES_COL_TYPES',
           'EMPLOYEES_CONVERTERS_DIC',
           'EMPLOYEES_USEFUL_COLS',
           'EXT_DOCS_USEFUL_COLS',
           'QUALIFICATION_DIC',
           'SEARCH_DEPTH',
           'STATUS_DIC',
           'TEMP_COLS',
          ]

# 3rd party imports
import bmfuncts.employees_globals as bm_eg


SEARCH_DEPTH = bm_eg.SEARCH_DEPTH

EMPLOYEES_ARCHI = bm_eg.EMPLOYEES_ARCHI

EMPLOYEES_ARCHI["hal_employees_file_name"] = "Hal_" + EMPLOYEES_ARCHI["employees_file_name"]

EMPLOYEES_USEFUL_COLS = bm_eg.EMPLOYEES_USEFUL_COLS

EMPLOYEES_ADD_COLS = bm_eg.EMPLOYEES_ADD_COLS

EMPLOYEES_COL_TYPES = bm_eg.EMPLOYEES_COL_TYPES

EMPLOYEES_CONVERTERS_DIC = bm_eg.EMPLOYEES_CONVERTERS_DIC

EXT_DOCS_USEFUL_COLS = bm_eg.EXT_DOCS_USEFUL_COL_LIST

TEMP_COLS = {"merge_author": "Join co-author"}

CATEGORIES_DIC = bm_eg.CATEGORIES_DIC

STATUS_DIC = bm_eg.STATUS_DIC

QUALIFICATION_DIC = bm_eg.QUALIFICATION_DIC
