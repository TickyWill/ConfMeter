"""Module of functions for the merge of employees information with the contributions list 
of the Institute to conferences taking care of:

- Correction of spelling of authors names if the extracted data from HAL
- Creation of list of Institute authors with selected attributes;
- Creation of full reference for each contribution;
- Creation of contributions hash-ID

"""

__all__ = ['read_merged_data',
           'recursive_year_search',
           'save_merged_data',
           'set_merge_paths',
          ]


# Standard Library imports
import warnings
from pathlib import Path

# 3rd party imports
import pandas as pd

# Local inports
import cmfuncts.conf_globals as cm_cg
import cmfuncts.employees_globals as cm_eg
from cmfuncts.build_employees import adapt_search_depth
from cmfuncts.build_employees import read_hal_employees_data
from cmfuncts.conf_extract import read_conf_extract
from cmfuncts.useful_functs import capitalize_name
from cmfuncts.useful_functs import standardize_name


def _build_all_authors_list(authors_init):
    sep = "."
    authors_list = []
    for author in authors_init.split(","):
        names_list = author.split(" ")
        first_name = names_list[0]
        last_name = " ".join(names_list[1:])
        if sep in first_name:
            first_name_list = [x + sep for x in first_name.split(sep)[:-1]]
            if len(first_name_list)>=2:
                first_name_initiales = "-".join(first_name_list)
            else:
                first_name_initiales = first_name_list[0]
        else:
            first_name_initiales = first_name[0] + "."
        authors_list.append(" ".join([first_name_initiales, last_name]))
    new_authors = ", ".join(authors_list)
    return new_authors


def _build_corr_authors(init_authors, init_author, new_author):
    authors_list = []
    for author in init_authors.split(","):
        if author.lower()==init_author:
            authors_list.append(new_author)
        else:
            authors_list.append(author)
    authors = ",".join(authors_list)
    return authors


def _build_corr_author(ortho_empl_name):
    names_list = []
    for name in ortho_empl_name.split(" "):
        names_list.append(capitalize_name(name))
    author = " ".join(names_list)
    return author


def _save_names_corr_data(confmeter_path, corpus_year, conf_df):
    """Saves, for a corpus year, the HAL conferences data after 
    check of author-names spelling.

    Args:
        confmeter_path (path): The full path to the working folder.
        corpus_year (str): 4 digits year of the corpus.
        conf_df (dataframe): The conferences data to save.
    """
    # Setting useful aliases
    hal_corpus_alias = cm_cg.CM_ARCHI['corpus_folder']
    corr_file_base_alias = cm_cg.CM_ARCHI['hal_corr_file_base']

    # Setting specific file name
    corr_file = corpus_year + corr_file_base_alias

    # Setting specific paths
    year_cmf_path = confmeter_path / Path(corpus_year)
    hal_corpus_path = year_cmf_path / Path(hal_corpus_alias)
    corr_file_path = hal_corpus_path / Path(corr_file)

    # Saving the modifyed data
    conf_df.to_excel(corr_file_path, index=False)


def _check_hal_names_spelling(wf_path, corpus_year, conf_df):
    """Replace author names in conferences data by the employee name.

    This is done when a name-spelling discrepency is given in the 
    dedicated file which name is given by 'orthograph_file_alias' 
    parameter and located in the folder of the working folder 
    which name is given by 'orphan_treat_root_alias' parameter.
    The corrected conferences data are saved through the 
    `_save_names_corr_data` internal function.

    Args:
        wf_path (path): Full path to working folder.
        conf_df (dataframe): Data of contributions to conferences \
        with one row per author where author names should be corrected.
    Returns:
        (dataframe): Publications list with one row per author where \
        spelling of author names have been corrected.
    """
    # Setting useful aliases
    orphan_treat_root_alias = cm_cg.ORPHAN_ARCHI["root"]
    orthograph_file_name_alias = cm_cg.ORPHAN_ARCHI["orthograph file"]

    # Setting useful column names (name stands for fullname)
    pub_id_alias = cm_cg.CONF_COLS['pub_id']
    pub_name_alias = cm_cg.CONF_COLS['co_author']
    first_author_alias = cm_cg.CONF_COLS['first_author']
    authors_alias = cm_cg.CONF_COLS['authors']
    ortho_pub_name_alias = cm_cg.ORTHO_COLS['pub_fullname']
    ortho_empl_name_alias = cm_cg.ORTHO_COLS['empl_fullname']

    # Setting useful path
    orphan_treat_root_path = wf_path / Path(orphan_treat_root_alias)
    ortho_path = orphan_treat_root_path / Path(orthograph_file_name_alias)

    # Reading data file targeted by 'ortho_path'
    ortho_cols_list = [ortho_pub_name_alias,
                       ortho_empl_name_alias]
    warnings.simplefilter(action='ignore', category=UserWarning)
    ortho_df = pd.read_excel(ortho_path, usecols=ortho_cols_list)

    new_conf_df = conf_df.copy()
    new_conf_df.reset_index(drop=True, inplace=True)
    new_conf_df[pub_name_alias] = new_conf_df[pub_name_alias].apply(standardize_name)
    new_conf_df[first_author_alias] = new_conf_df[first_author_alias].apply(standardize_name)
    for pub_row_num, pub_row in new_conf_df.iterrows():
        pub_id = new_conf_df.loc[pub_row_num, pub_id_alias]
        init_pub_name = new_conf_df.loc[pub_row_num, pub_name_alias].lower()
        init_first_author = new_conf_df.loc[pub_row_num, first_author_alias].lower()
        init_authors = new_conf_df.loc[pub_row_num, authors_alias]
        for ortho_row_num, ortho_row in ortho_df.iterrows():
            ortho_pub_name = ortho_df.loc[ortho_row_num, ortho_pub_name_alias].lower()
            if init_pub_name==ortho_pub_name:                
                ortho_empl_name = ortho_df.loc[ortho_row_num, ortho_empl_name_alias]
                new_pub_name = _build_corr_author(ortho_empl_name)
                new_authors = _build_corr_authors(init_authors, init_pub_name, new_pub_name)
                new_conf_df.loc[pub_row_num, pub_name_alias] = new_pub_name
                if init_first_author==init_pub_name:
                    pub_id_idxs = new_conf_df.index[new_conf_df[pub_id_alias]==pub_id]
                    new_conf_df.loc[pub_id_idxs, first_author_alias] = new_pub_name
                    new_conf_df.loc[pub_id_idxs, authors_alias] = new_authors
    new_conf_df[authors_alias] = new_conf_df[authors_alias].apply(_build_all_authors_list)

    # Saving the corrected conferences data
    _save_names_corr_data(wf_path, corpus_year, new_conf_df)
    return new_conf_df


def _add_hal_ext_docs(wf_path, init_valid_df, init_orphan_df,
                      merge_auth_col, fullname_col):
    # Setting useful aliases
    orphan_treat_root_alias = cm_cg.ORPHAN_ARCHI["root"]
    adds_file_name_alias = cm_cg.ORPHAN_ARCHI["employees adds file"]
    ext_docs_sheet_alias = cm_cg.ORPHAN_SHEET_NAMES["docs to add"]
    converters_alias = cm_eg.EMPLOYEES_CONVERTERS_DIC
    ext_docs_cols_alias = cm_eg.EXT_DOCS_USEFUL_COLS.copy()
    firstname_initials_col_alias = cm_eg.EMPLOYEES_ADD_COLS['first_name_initials']

    # Correcting useful column name
    ext_docs_cols_alias[-2] = firstname_initials_col_alias

    # Setting specific paths
    orphan_treat_root_path = wf_path / Path(orphan_treat_root_alias)
    ext_docs_path = orphan_treat_root_path / Path(adds_file_name_alias)

    # Reading of the external phd students excel file
    # using the same useful columns as init_valid_df defined by EXT_DOCS_USEFUL_COLS
    # with dates conversion through converters_alias
    # and drop of empty rows
    warnings.simplefilter(action='ignore', category=UserWarning)
    ext_docs_df = pd.read_excel(ext_docs_path,
                                sheet_name=ext_docs_sheet_alias,
                                usecols=ext_docs_cols_alias,
                                converters=converters_alias)
    ext_docs_df.dropna(how='all', inplace=True)
    ext_docs_df.reset_index(drop=True, inplace=True)
    ext_docs_df[merge_auth_col] = ext_docs_df[fullname_col].apply(lambda x:
                                                                  standardize_name(x)\
                                                                  .lower().replace("-"," "))

    valid_adds_df = init_orphan_df.merge(ext_docs_df, how='inner', on=merge_auth_col)
    new_valid_df = pd.concat([init_valid_df, valid_adds_df])
    new_valid_df.sort_values(by=["Pub_id", 'Idx_author'], inplace=True)
    to_drop_df = new_valid_df[init_orphan_df.columns]
    new_orphan_df = pd.concat([init_orphan_df, to_drop_df, to_drop_df]).drop_duplicates(keep=False)

    return new_valid_df, new_orphan_df


def set_merge_paths(wf_path, corpus_year):
    """Sets the parameters of the files resulting from merge of data of 
    the contributions to conferences with the data of employees.

    Args:
        wf_path (path): The full path to the working folder.
        corpus_year (str): 4 digits year of the corpus.
    Returns:
        (tup): (The list composed of the full path (path) to the folder  \
        where are located the two files generated by the merge \
        and of the full paths (path) to these two files, \
        the list of the names (str) of these two files).
    """
    # Setting useful aliases
    conf_empl_folder_alias = cm_cg.CM_ARCHI['conf_empl_folder']
    valid_file_alias = cm_cg.CM_ARCHI['valid_authors']
    orphan_file_alias = cm_cg.CM_ARCHI['orphan_authors']

    # Setting specific paths
    year_cmf_path = wf_path / Path(corpus_year)
    conf_empl_folder_path = year_cmf_path / Path(conf_empl_folder_alias)
    valid_file_path = conf_empl_folder_path / Path(valid_file_alias)
    orphan_file_path = conf_empl_folder_path / Path(orphan_file_alias)

    # Setting the return lists
    filenames_list = [valid_file_alias, orphan_file_alias]
    paths_list = [conf_empl_folder_path, valid_file_path, orphan_file_path]

    return paths_list, filenames_list


def save_merged_data(wf_path, corpus_year, valid_df,
                     orphan_df=pd.DataFrame(), step=None):
    """Saves, for a corpus year, the lists of contributions to conferences 
    with one row per Institute-affiliated author, either merged with 
    employees data or not found in employees data.

    Args:
        wf_path (path): The full path to the working folder.
        corpus_year (str): 4 digits year of the corpus.
        valid_df (dataframe): The list of contributions to conferences \
        with one row per Institute-affiliated author merged with \
        employees data.
        orphan_df (dataframe): The optional list of conferences with \
        one row per Institute-affiliated author not found in employees \
        data (default=empty dataframe).
        step (str): The optional modification name of the merged data \
        (default=None).
    """
    paths_list, filenames_list = set_merge_paths(wf_path, corpus_year)
    conf_empl_folder_path, valid_file_path, orphan_file_path = paths_list
    valid_file_name, _ = filenames_list
    
    if step:
        # Setting specific 'valid' file name
        valid_file_name = step + valid_file_name

        # Setting specific 'valid' paths
        valid_file_path = conf_empl_folder_path / Path(valid_file_name)

    # Saving the 'valid' data
    valid_df.to_excel(valid_file_path, index=False)
    
    if not orphan_df.empty:
        # Saving the 'orphan' data
        orphan_df.to_excel(orphan_file_path, index=False)


def _year_search(wf_path, dfs_list, cols_list, first_step):
    """Searches for the author affiliated to the institute in the 
    employees data of the year.
    
    This is done through the `pandas.DataFrame.merge` function applied 
    on the 'merge_auth_col' column common to the employees data 
    and the contributions-to-conferences data. 
    The conferences data out of the merge are the data for which 
    no employee is found. These data are kept in a specific dataframe. 
    For the first year search, the external PhD students are added 
    as employees of the Institute through the `_add_hal_ext_docs` 
    internal function.

    Args:
        dfs_list (list): [The employees data of the year (dataframe), \
        The merged data with the employees data of the next year (dataframe), \
        The out of merge data of the next year (dataframe)].
        cols_list (list): The list of the useful columns names.
        first_step (bool): The status of the search, true for the first search \
        year at which the the external PhD students are added.
    Returns:
        (tup): (The updated merged data with the employees data of the year (dataframe), \
        The updated out of merge data of the year (dataframe)).
    """
    pub_id_col, auth_idx_col, fullname_col, merge_auth_col = cols_list
    empl_df, valid_df, orphan_df = dfs_list 

    # Merging with employees data
    empl_df[merge_auth_col] = empl_df[fullname_col].apply(lambda x:
                                                          standardize_name(x)\
                                                          .lower().replace("-"," "))                

    valid_adds_df = orphan_df.merge(empl_df, how='inner', on=merge_auth_col)
    valid_df = pd.concat([valid_df, valid_adds_df])
    valid_df.sort_values(by=[pub_id_col, auth_idx_col], inplace=True)
    to_drop_df = valid_df[orphan_df.columns]
    orphan_df = pd.concat([orphan_df, to_drop_df, to_drop_df]).drop_duplicates(keep=False)

    if first_step:
        # Merging with external PhD students data
        valid_df, orphan_df = _add_hal_ext_docs(wf_path, valid_df, orphan_df,
                                                merge_auth_col, fullname_col)

    return valid_df, orphan_df


def recursive_year_search(wf_root_path, wf_path, corpus_year, conf_df=pd.DataFrame(),
                          employees_dict={}, years_to_search=[], progress_callback=None):
    """Searches for the author affiliated to the institute in the 
    employees data.
    
    First, the employees data are set through the `read_hal_employees_data` 
    function imported from the `cmfuncts.build_employees` module.
    Then, the spelling of the authors names is corrected through the 
    `_check_hal_names_spelling` internal function. 
    After that, the search is done recursively on years of employees data 
    through the `_year_search` internal function. 
    The data of contributions to conferences for which no employee is found 
    are kept in a specific dataframe. 
    Finally, the two kinds of data are saved through the `save_merged_data` 
    internal function. 

    Args:
        wf_root_path (path): The full path to the root folder where \
        the folder of Institute parameters is located.
        wf_path (path): The full path to the working folder.
        corpus_year (str): 4 digits year of the corpus.
        conf_df (dataframe): The list of contributions to conferences \
        with one row per Institute-affiliated author.
        employees_dict (dict):
        empl_use_years (list):
        progress_callback (function): Function for updating ProgressBar \
        tkinter widget status (default = None).
    Returns:
        (tup): (The updated merged data with the employees data (dataframe), \
        The updated out of merge data (dataframe)).
    """
    # Setting specific aliases
    pub_id_alias = cm_cg.CONF_COLS['pub_id']                              # 'Pub_id'
    auth_idx_alias = cm_cg.CONF_COLS['author_idx']                        # 'Idx_author'
    co_auth_alias = cm_cg.CONF_COLS['co_author']                          # 'Co_auteur' => 'Co_author'
    fullname_alias = cm_eg.EMPLOYEES_ADD_COLS['employee_full_name']       # 'Employee_full_name'
    merge_auth_alias = cm_eg.TEMP_COLS["merge_author"]                    # "Join co-author"

    # Setting useful columns list
    cols_list = [pub_id_alias, auth_idx_alias, fullname_alias, merge_auth_alias]

    if not employees_dict:
        # Reading employees data
        print("\nReading employees data...")
        employees_dict = read_hal_employees_data(wf_root_path)

    # Building the search time depth of Institute co-authors among the employees data
    if not years_to_search:
        _, years_to_search = adapt_search_depth(corpus_year, hal_all_empl_dict)
    steps_nb = len(years_to_search)

    if progress_callback:
        progress_callback(15)
    
#    corpus_year_status = corpus_year in employees_dict.keys()
#    year_start = int(corpus_year)
#    if not corpus_year_status:
#        year_start = int(corpus_year)-1
#    year_stop = year_start - (search_depth - 1)
#    years_to_search = [str(i) for i in range(year_start, year_stop-1,-1)]
#    steps_nb = int(len(years_to_search))
    if steps_nb:
        if conf_df.empty:
            # reading extraction data of contributions to conferences
            print("\nReading contributions to conferences data...")
            conf_df = read_conf_extract(wf_path, corpus_year)

        # Checking author names
        conf_df = _check_hal_names_spelling(wf_path, corpus_year, conf_df)    
        print("\nName spelling in data of contributions to conferences checked.")

        # Initializing orphan data through standardization of co-authors name
        orphan_df = conf_df.copy()
        orphan_df[merge_auth_alias] = conf_df[co_auth_alias].apply(lambda x:
                                                                   standardize_name(x)\
                                                                   .lower().replace("-"," "))
        if progress_callback:
            progress_bar = 20
            final_progress_bar = 90
            progress_callback(progress_bar)
            progress_step = (final_progress_bar - progress_bar) / steps_nb

            
        print("\nSearching for authors among employees...")
        print(f"    years for search: from {years_to_search[0]} to {years_to_search[-1]}")
        valid_df = pd.DataFrame()
        first_step = True
        for year in years_to_search:
            # Merging with employees data of year
            empl_df = employees_dict[year].copy()

            dfs_list = [empl_df, valid_df, orphan_df]
            return_tup = _year_search(wf_path, dfs_list, cols_list, first_step)
            valid_df, orphan_df = return_tup
            first_step = False
            print(f"    searched year   : {year}", end="\r")

            if progress_callback:
                progress_bar += progress_step
                progress_callback(progress_bar)

        # Saving merged data
        save_merged_data(wf_path, corpus_year, valid_df, orphan_df=orphan_df)
        search_status = True
    else:
        search_status = False

    if progress_callback:
        progress_callback(100)

    return search_status, valid_df


def read_merged_data(wf_path, corpus_year):
    """Reads, for a corpus year, the lists of conferences with one row  
    per Institute-affiliated author merged with employees data.

    Args:
        wf_path (path): The full path to the working folder.
        corpus_year (str): 4 digits year of the corpus.
    Returns:
        (dataframe): The list of contributions to conferences with \
        one row per Institute-affiliated author merged with employees data.
    """
    paths_list, _ = set_merge_paths(wf_path, corpus_year)
    _, valid_file_path, _ = paths_list

    # Saving the data
    valid_df = pd.read_excel(valid_file_path)

    return valid_df
