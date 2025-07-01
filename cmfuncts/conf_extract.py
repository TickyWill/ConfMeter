"""Module of functions for the cleaning the extracted data from HAL  
in terms of:

- Extracting all publications of the Institute from HAL database;
- Keeping only the contributions to conferences from the extracted data;
- Setting the country name in place of the country code.

"""

__all__ = ['read_conf_extract',
           'set_extract_paths',
           'set_hal_to_conf',
          ]


# Standard library imports
from pathlib import Path

# 3rd party imports
import HalApyJson as haj
import pandas as pd

# Local imports
import cmfuncts.conf_globals as cm_cg


def _set_country_iso_dict():
    """Sets a data of iso code per country.

    Returns:
        (dict): Data keyyed by the country code and valued by \
        the country name in English.
    """
    # Setting useful aliases
    country_iso_file_alias = cm_cg.CM_ARCHI['country_iso_file']
    country_sheet_alias = cm_cg.CM_ARCHI['country_iso_sheet']   # "Base"
    country_cols_alias = cm_cg.CM_ARCHI['country_iso_usecols']  # ["Code", "English name"]
    
    # Setting specific paths independant from corpus_year
    config_folder_path = Path(__file__).parent / Path(cm_cg.CONFIG_FOLDER)
    country_iso_file_path = config_folder_path / Path(country_iso_file_alias)

    # Building ISO code-country dict
    code_country_df= pd.read_excel(country_iso_file_path,
                                   sheet_name=country_sheet_alias,
                                   usecols=country_cols_alias)
    code_col, name_col = country_cols_alias
    code_country_dict = dict(zip(code_country_df[code_col],
                                 code_country_df[name_col]))

    return code_country_dict


def set_extract_paths(wf_path, corpus_year):
    """Sets the parameters of the extraction files from the HAL database.

    Args:
        wf_path (path): The full path to the working folder.
        corpus_year (str): 4 digits year of the corpus.
    Returns:
        (tup): (The list composed of the full path (path) to the folder  \
        where are located the two files of the original and adapted \
        employees data and of the full paths (path) to these two files, \
        the list of the names (str) of these two files).
    """
    # Setting useful aliases
    hal_corpus_alias = cm_cg.CM_ARCHI['corpus_folder']
    full_file_base_alias = cm_cg.CM_ARCHI['hal_full_file_base']
    conf_file_base_alias = cm_cg.CM_ARCHI['hal_conf_file_base']

    # Setting specific file names dependent on corpus_year
    year_full_file = corpus_year + full_file_base_alias
    year_conf_file = corpus_year + conf_file_base_alias

    # Setting specific paths dependent on corpus_year
    year_wf_path = wf_path / Path(corpus_year)
    hal_corpus_path = year_wf_path / Path(hal_corpus_alias)
    full_file_path = hal_corpus_path / Path(year_full_file)
    conf_file_path = hal_corpus_path / Path(year_conf_file)

    # Setting the return lists
    filenames_list = [year_full_file, year_conf_file]
    paths_list = [hal_corpus_path, full_file_path, conf_file_path]

    return paths_list,filenames_list


def _save_hal_data(wf_path, corpus_year, hal_full_df, hal_conf_df):
    """Saves the full HAL data and the clean HAL conferences data 
    for a corpus year.

    Args:
        wf_path (path): The full path to the working folder.
        corpus_year (str): 4 digits year of the corpus.
        hal_full_df (dataframe): The full data to save.
        hal_conf_df (dataframe): The conferences data to save.
    """
    # Setting useful aliases
    hal_corpus_alias = cm_cg.CM_ARCHI['corpus_folder']
    full_file_base_alias = cm_cg.CM_ARCHI['hal_full_file_base']
    conf_file_base_alias = cm_cg.CM_ARCHI['hal_conf_file_base']

    # Setting specific file names dependent on corpus_year
    year_full_file = corpus_year + full_file_base_alias
    year_conf_file = corpus_year + conf_file_base_alias

    # Setting specific paths dependent on corpus_year
    year_wf_path = wf_path / Path(corpus_year)
    hal_corpus_path = year_wf_path / Path(hal_corpus_alias)
    full_file_path = hal_corpus_path / Path(year_full_file)
    conf_file_path = hal_corpus_path / Path(year_conf_file)

    # Saving the data
    hal_full_df.to_excel(full_file_path, index=False)
    hal_conf_df.to_excel(conf_file_path, index=False)

    return year_full_file, year_conf_file, hal_corpus_path


def set_hal_to_conf(institute, wf_path, corpus_year, progress_callback=None):
    """Builts clean data of Institute contributions to conferences 
    from the HAL extraction data for a corpus year.

    The data are extracted from HAL database through the 
    `build_hal_df_from_api` function of the `HalToJson` 
    package imported as 'haj'. 
    Then, the conferences data are built from the original data 
    resulting from the HAL extraction. In particular, the country 
    code is replaced by the country name using the 'code_country_dict' 
    dict built through the `_set_country_iso_dict` internal function.
    The final columns of the built data are defined by the values 
    of the 'CONF_COLS' global. 
    Finally, the built data are saved as xlsx files.

    Args:
        institute (str): The name of the Institute.
        wf_path (path): The full path to the working folder.
        corpus_year (str): 4 digits year of the corpus.
        progress_callback (function): Function for updating ProgressBar \
        tkinter widget status (default = None).
    Returns:
        (dataframe): The built data.
    """
    # Setting useful aliases
    unknown_alias = cm_cg.INDISPONIBLE
    authors_alias = cm_cg.HAL_USE_COLS['authors']         # 'Auteurs'
    pub_date_alias = cm_cg.HAL_USE_COLS['pub_date']       # "Date de publication"
    conf_date_alias = cm_cg.HAL_USE_COLS['conf_date']     # "Date de conference"
    pub_id_alias = cm_cg.CONF_COLS['pub_id']              # 'Pub_id'
    auth_idx_alias = cm_cg.CONF_COLS['author_idx']        # 'Idx_author'
    co_auth_alias = cm_cg.CONF_COLS['co_author']          # 'Co_auteur' => 'Co_author'
    town_alias = cm_cg.CONF_COLS['town']                  # "Ville"
    country_alias = cm_cg.CONF_COLS['country']            # "Pays"
    first_author_alias = cm_cg.CONF_COLS['first_author']  # "Premier auteur"
    conf_year_alias = cm_cg.CONF_COLS['conf_year']        # "Année de conférence"
    pub_year_alias = cm_cg.CONF_COLS['pub_year']          # "Année de publication"
    doctype_alias = cm_cg.CONF_COLS['doctype']            # "Type de document"
    full_ref_alias = cm_cg.HAL_USE_COLS['full_ref']       # "01"

    # Extracting the HAL corpus
    hal_full_df = haj.build_hal_df_from_api(corpus_year, institute.lower())   
    if progress_callback:
        progress_callback(20)
    

    # Selecting communications and posters to build the conferences data
    init_hal_conf_df = hal_full_df[hal_full_df[doctype_alias].isin(cm_cg.CONF_TYPES)]

    # Cleaning the conferences data
    clean_hal_conf_df = init_hal_conf_df.copy()
    clean_hal_conf_df.replace(to_replace="NA", value=unknown_alias,
                              inplace=True)
    clean_hal_conf_df.reindex()
    
    # Getting ISO code-country to convert the country code
    # into the country name in the conferences data
    code_country_dict = _set_country_iso_dict()
      
    steps_nb = int(len(clean_hal_conf_df))    
    if steps_nb:    
        if progress_callback:
            progress_bar = 40
            progress_callback(progress_bar)
            final_progress_bar = 90
            progress_step = (final_progress_bar - progress_bar) / steps_nb

    # Adding useful columns to the conferences data 
    new_hal_conf_df = pd.DataFrame(columns=cm_cg.HAL_USE_COLS.values())
    pub_id = 0
    for _, row in clean_hal_conf_df.iterrows():
        row[pub_id_alias] = pub_id
        row[town_alias] = row[full_ref_alias].split(", ")[-2].split("(")[0]
        country_iso = str(row[country_alias]).upper()
        row[country_alias] = code_country_dict[country_iso]
        authors_list = row[authors_alias].split(",")
        auth_id = 0
        for author in authors_list:
            row[auth_idx_alias] = auth_id
            row[co_auth_alias] = author
            row[first_author_alias] = authors_list[0]
            row[conf_year_alias] = row[conf_date_alias][0:4]
            row[pub_year_alias] = row[pub_date_alias][0:4]
            new_hal_conf_df = pd.concat([new_hal_conf_df, row.to_frame().T])
            auth_id += 1
        pub_id += 1
        if progress_callback:
            progress_bar += progress_step
            progress_callback(progress_bar)
    hal_conf_df = new_hal_conf_df[cm_cg.CONF_COLS.values()]

    # Setting useful paths
    paths_list, _ = set_extract_paths(wf_path, corpus_year)
    _, full_file_path, conf_file_path = paths_list

    # Saving the full data and the conferences data
    hal_full_df.to_excel(full_file_path, index=False)
    hal_conf_df.to_excel(conf_file_path, index=False)    
    if progress_callback:
        progress_callback(100)

    return hal_conf_df


def read_conf_extract(wf_path, corpus_year):
    """Gets the data of the contributions to conferences resulting 
    from the HAL extraction.

    The columns selected from the HAL extraction data are defined 
    by the values of the 'HAL_USE_COLS' global.

    Args:
        wf_path (path): The full path to the working folder.
        corpus_year (str): 4 digits year of the corpus.
    Returns:
        (dataframe): The data selected from the HAL extraction.
    """
    # Setting useful paths
    paths_list, _ =set_extract_paths(wf_path, corpus_year)
    _, _, conf_file_path = paths_list

    # Reading the file resulting from the HAL extraction
    conf_df = pd.read_excel(conf_file_path, usecols=cm_cg.CONF_COLS.values())

    return conf_df
