"""Module of functions for building the employees data compatible with authors infos in HAL.

"""

__all__ = ['adapt_search_depth',
           'read_hal_employees_data',
           'set_empl_paths',
           'update_hal_employees_data',
          ]


# Standard Library imports
from pathlib import Path

# 3rd party imports
import pandas as pd

# Local imports
import cmfuncts.employees_globals as cm_eg
from cmfuncts.format_files import add_sheets_to_workbook
from cmfuncts.useful_functs import capitalize_name


def set_empl_paths(wf_root_path):
    """Sets the parameters of employees-data files.

    Args:
        wf_root_path (path): The full path to the root folder where \
        the folder of Institute parameters is located.
    Returns:
        (tup): (The list composed of the full path (path) to the folder  \
        where are located the two files of the original and adapted \
        employees data and of the full paths (path) to these two files, \
        the list of the names (str) of these two files).
    """
    # Setting specific aliases
    empl_root_alias = cm_eg.EMPLOYEES_ARCHI["root"]
    empl_folder_name_alias = cm_eg.EMPLOYEES_ARCHI["all_years_employees"]
    empl_file_name_alias = cm_eg.EMPLOYEES_ARCHI["employees_file_name"]
    hal_empl_file_name_alias = cm_eg.EMPLOYEES_ARCHI["hal_employees_file_name"]

    # Setting useful paths
    empl_root_path = wf_root_path / Path(empl_root_alias)
    empl_folder_path = empl_root_path / Path(empl_folder_name_alias)
    all_empl_path = empl_folder_path / Path(empl_file_name_alias)
    hal_all_empl_path = empl_folder_path / Path(hal_empl_file_name_alias)

    # Setting the retrun lists
    filenames_list = [empl_file_name_alias, hal_empl_file_name_alias]
    paths_list = [empl_folder_path, all_empl_path, hal_all_empl_path]
    
    return paths_list, filenames_list


def update_hal_employees_data(wf_root_path, progress_callback=None):
    """Adapts the existing employees data for the application by adding 
    a column of full_names.

    The updated data are saved as a multisheet xlsx file with 
    one sheet per year through the `add_sheets_to_workbook` function 
    imported from  the `cmfuncts.format_files` module.
    
    Args:
        wf_root_path (path): The full path to the root folder where \
        the folder of Institute parameters is located.
        progress_callback (function): Function for updating ProgressBar \
        tkinter widget status (default = None).
    Returns:
        (tup): (Status (bool) of the employees-data update (True, if employees \
        data have been updated; False, if employees data are empty), \
        the data (dict) keyed by year and valued by adapted employees data \
        (dataframe) for the year).
    """
    # Setting specific column aliases
    first_name_col_alias = cm_eg.EMPLOYEES_USEFUL_COLS['first_name']
    last_name_col_alias = cm_eg.EMPLOYEES_USEFUL_COLS['name']
    fullname_col_alias = cm_eg.EMPLOYEES_ADD_COLS['employee_full_name']
    empl_use_cols_alias = cm_eg.EMPLOYEES_USEFUL_COLS.values()
    empl_add_cols_alias = cm_eg.EMPLOYEES_ADD_COLS.values()

    # Setting useful paths
    paths_list, _ = set_empl_paths(wf_root_path)
    _, all_empl_path, hal_all_empl_path = paths_list

    if progress_callback:
        progress_callback(10)

    # Getting employees df
    print("\nReading existing employees data of all years...")
    cols_list = list(empl_use_cols_alias) + list(empl_add_cols_alias)
    all_empl_dict = pd.read_excel(all_empl_path,
                                  sheet_name=None,
                                  dtype=cm_eg.EMPLOYEES_COL_TYPES,
                                  usecols=cols_list,
                                  converters=cm_eg.EMPLOYEES_CONVERTERS_DIC)
    years_to_update = list(all_empl_dict.keys())
    steps_nb = int(len(years_to_update))

    if steps_nb:
        print("\nAddapting employees data by adding a column of full_names...")
        print(f"    years to addapt: {years_to_update[0]} to {years_to_update[-1]}")

        if progress_callback:
            progress_bar = 20
            final_progress_bar = 100
            progress_callback(progress_bar)
            progress_step = (final_progress_bar - progress_bar) / steps_nb

        # Setting effectif full name with first name and last name
        sheet_init = True
        hal_all_empl_dict = {}
        for year in years_to_update:
            year_empl_df = all_empl_dict[str(year)].copy()
            hal_year_empl_df = pd.DataFrame()
            for _,row in year_empl_df.iterrows():
                first_name_cap = capitalize_name(row[first_name_col_alias])
                last_name_cap = capitalize_name(row[last_name_col_alias])
                row[fullname_col_alias] = first_name_cap + " " + last_name_cap
                hal_year_empl_df = pd.concat([hal_year_empl_df, row.to_frame().T])
            sheet_name = str(year)
            if sheet_init:
                hal_year_empl_df.to_excel(hal_all_empl_path, sheet_name=sheet_name,
                                               index=False)
                sheet_init = False
            else:
                add_sheets_to_workbook(hal_all_empl_path, hal_year_empl_df, sheet_name)
            hal_all_empl_dict[year] = hal_year_empl_df
            print(f"    addapted year  : {year}", end="\r")

            if progress_callback:
                progress_bar += progress_step
                progress_callback(progress_bar)
        print("\nEmployees data addapted")
        update_empl_status = True
    else:
        print("\nEmployees data are empty")
        update_empl_status = False
    return update_empl_status, hal_all_empl_dict


def adapt_search_depth(corpus_year, hal_all_empl_dict):
    # Setting specific aliase    
    search_depth_init_alias = cm_eg.SEARCH_DEPTH
    
    # Identifying available years in employees data
    empl_available_years = [int(x) for x in list(hal_all_empl_dict.keys())]

    # Building required years list for initial search depth given the corpus year
    required_years = [int(corpus_year) - i for i in range(int(search_depth_init_alias))]

    # Building available years in the employees data among the required ones to search
    empl_use_years = list(set(empl_available_years).intersection(set(required_years)))
    empl_use_keys = [str(year) for year in empl_use_years]
    empl_use_keys.reverse()

    # Adapting search_depth for the given corpus year
    corpus_search_depth = min(int(search_depth_init_alias), len(empl_use_years))   
    return corpus_search_depth, empl_use_keys

def read_hal_employees_data(wf_root_path):
    """Sets Institute employees data by year.

    The search depth and the list of available years of employees data 
    are adapted to the corpus year.

    Args:
        wf_root_path (path): The full path to the root folder where \
        the folder of Institute parameters is located.
    Returns:
        (tup): (employees data (dict keyed by years (str) and valued by employees data \
        of the year (df)), adapted search depth (int), adapted list of available years (str) \
        of employees data).    
    """
    # Setting specific aliases
    fullname_col_alias = cm_eg.EMPLOYEES_ADD_COLS['employee_full_name']
    empl_use_cols_alias = cm_eg.EMPLOYEES_USEFUL_COLS.values()
    empl_add_cols_alias = cm_eg.EMPLOYEES_ADD_COLS.values()

    # Setting useful paths
    paths_list, _ = set_empl_paths(wf_root_path)
    hal_all_empl_path = paths_list[-1]

    # Getting employees df
    hal_cols_list = list(empl_use_cols_alias) + list(empl_add_cols_alias) \
                    + [fullname_col_alias]
    hal_all_empl_dict = pd.read_excel(hal_all_empl_path,
                                      sheet_name = None,
                                      dtype = cm_eg.EMPLOYEES_COL_TYPES,
                                      usecols = hal_cols_list,
                                      converters=cm_eg.EMPLOYEES_CONVERTERS_DIC)
    return hal_all_empl_dict
