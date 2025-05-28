"""Module of functions for the consolidation of the conferences-list 
in terms of:

- selecting conferences data from the extraction from HAL;
- ...

"""

__all__ = ['read_hal_extract',
           'save_hal_conf',
           'set_country_iso_dict',
           'set_hal_to_conf',
          ]


# Standard library imports
from pathlib import Path

# 3rd party imports
import BiblioParsing as bp
import pandas as pd

# Local imports
import cmfuncts.conf_globals as cg


def set_country_iso_dict():
    """Sets a data of iso code per country.

    Returns:
        (dict): Data keyyed by the country code and valued by \
        the country name in English.
    """
    # Setting useful aliases
    country_iso_file_alias = cg.CM_ARCHI['country_iso_file']
    country_sheet_alias = cg.CM_ARCHI['country_iso_sheet']   # "Base"
    country_cols_alias = cg.CM_ARCHI['country_iso_usecols']  # ["Code", "English name"]
    
    # Setting specific paths independant from corpus_year
    config_folder_path = Path(__file__).parent / Path(cg.CONFIG_FOLDER)
    country_iso_file_path = config_folder_path / Path(country_iso_file_alias)

    # Building ISO code-country dict
    code_country_df= pd.read_excel(country_iso_file_path,
                                   sheet_name=country_sheet_alias,
                                   usecols=country_cols_alias)
    code_col, name_col = country_cols_alias
    code_country_dict = dict(zip(code_country_df[code_col],
                                 code_country_df[name_col]))

    return code_country_dict


def read_hal_extract(confmeter_path, corpus_year):
    """Gets selected data resulting from the HAL extraction 
    for all types of documents.

    The columns selected from the HAL extraction data are defined 
    by the values of the 'HAL_USE_COLS' global.

    Args:
        confmeter_path (path): The full path to the working folder.
        corpus_year (str): 4 digits year of the corpus.
    Returns:
        (dataframe): The data selected from the HAL extraction.
    """
    # Setting useful aliases
    hal_corpus = cg.CM_ARCHI['corpus']
    full_file_base_alias = cg.CM_ARCHI['hal_full_file_base']

    # Setting specific filename dependent on corpus_year
    year_full_file = corpus_year + full_file_base_alias
    
    # Setting useful paths
    year_cmf_path = confmeter_path / Path(corpus_year)
    hal_corpus_path = year_cmf_path / Path(hal_corpus)
    hal_full_file_path = hal_corpus_path / Path(year_full_file)

    # Reading the file resulting from the HAL extraction
    hal_full_df = pd.read_excel(hal_full_file_path, usecols=cg.HAL_USE_COLS.values())

    return hal_full_df


def set_hal_to_conf(confmeter_path, corpus_year):
    """Builts clean data of conferences from the HAL extraction data 
    for a corpus year.

    Useful data are built from the original data resulting from the 
    HAL extraction. 
    The final columns of the bulit data are defined by the values 
    of the 'CONF_COLS' global.

    Args:
        confmeter_path (path): The full path to the working folder.
        corpus_year (str): 4 digits year of the corpus.
    Returns:
        (dataframe): The built data.
    """
    # Setting useful aliases
    unknown_alias = bp.UNKNOWN
    authors_alias = cg.HAL_USE_COLS['authors']               # 'Auteurs'
    pub_date_alias = cg.HAL_USE_COLS['pub_date']             # "Date de publication"
    conf_date_alias = cg.HAL_USE_COLS['conf_date']           # "Date de conference"
    pub_id_alias = cg.CONF_COLS['pub_id']                    # 'Pub_id'
    auth_idx_alias = cg.CONF_COLS['author_idx']              # 'Idx_author'
    co_auth_alias = cg.CONF_COLS['co_author']                # 'Co_auteur' => 'Co_author'
    country_alias = cg.CONF_COLS['country']                  # "Pays"
    first_author_alias = cg.CONF_COLS['first_author']        # "Premier auteur"
    conf_year_alias = cg.CONF_COLS['conf_year']              # "Année de conférence"
    pub_year_alias = cg.CONF_COLS['pub_year']                # "Année de publication"
    doctype_alias = cg.CONF_COLS['doctype']                  # "Type de document"
    
    # Getting ISO code-country to convert the country code
    # into the country name in the HAL extraction data
    code_country_dict = set_country_iso_dict()

    # Reading the file resulting from the HAL extraction
    hal_full_df = read_hal_extract(confmeter_path, corpus_year)

    # Selecting communications and posters to build the conferences df
    hal_conf_df = hal_full_df[hal_full_df[doctype_alias].isin(cg.CONF_TYPES)]

    # Cleaning the conferences df
    clean_hal_conf_df = hal_conf_df.copy()
    clean_hal_conf_df.fillna(0, inplace=True)
    clean_hal_conf_df.replace(to_replace=0, value=unknown_alias, inplace=True)
    clean_hal_conf_df.reindex()

    # Adding useful columns to the conferences df 
    new_hal_conf_df = pd.DataFrame(columns=cg.HAL_USE_COLS.values())
    pub_id = 0
    for _, row in clean_hal_conf_df.iterrows():
        row[pub_id_alias] = pub_id
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
    final_hal_conf_df = new_hal_conf_df[cg.CONF_COLS.values()]
    
    return final_hal_conf_df


def save_hal_conf(confmeter_path, corpus_year, hal_conf_df):
    """Saves the clean HAL conferences data for a corpus year.

    Args:
        confmeter_path (path): The full path to the working folder.
        corpus_year (str): 4 digits year of the corpus.
        hal_conf_df (dataframe): The data to save.
    """

    # Setting useful aliases
    hal_corpus = cg.CM_ARCHI['corpus']
    conf_file_base_alias = cg.CM_ARCHI['hal_conf_file_base']
    country_iso_file_alias = cg.CM_ARCHI['country_iso_file']

    # Setting specific filename dependent on year_select
    year_conf_file = corpus_year + conf_file_base_alias

    # Setting specific paths dependent on year_select
    year_cmf_path = confmeter_path / Path(corpus_year)
    hal_corpus_path = year_cmf_path / Path(hal_corpus)
    hal_conf_file_path = hal_corpus_path / Path(year_conf_file)

    hal_conf_df.to_excel(hal_conf_file_path, index=False)
    