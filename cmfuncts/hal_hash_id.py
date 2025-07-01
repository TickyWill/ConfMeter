"""Module of functions for creating an ID for each publication 
that is independent of the extraction from the external databases.

"""

__all__ = ['create_hal_hash_id']


# Standard Library imports
from pathlib import Path

# 3rd party imports
import pandas as pd
from bmfuncts.create_hash_id import _my_hash
from bmfuncts.useful_functs import reorder_df

# Local imports
import cmfuncts.conf_globals as cm_cg


def save_hash_data(cm_files_path, corpus_year, hash_id_df):
    """Saves, for a corpus year, the data of hash ID per ID 
    of the contributions to conferences.

    Args:
        cm_files_path (path): The full path to the working folder.
        corpus_year (str): 4 digits year of the corpus.
        hash_id_df (dataframe): The data to save.
    Returns:
        (str): End message.
    """
    # Setting useful aliases
    conf_empl_folder_alias = cm_cg.CM_ARCHI['conf_empl_folder']
    hash_file_alias = cm_cg.CM_ARCHI['hash_id_file_name']

    # Setting specific paths
    year_cmf_path = cm_files_path / Path(corpus_year)
    conf_empl_folder_path = year_cmf_path / Path(conf_empl_folder_alias)
    hash_file_path = conf_empl_folder_path / Path(hash_file_alias)

    # Saving the data
    hash_id_df.to_excel(hash_file_path, index=False)

    hash_id_nb = len(hash_id_df)
    message = (f"\n{hash_id_nb} hash IDs of contributions to conferences created "
               f"and saved in file: \n  {hash_file_path}")
    return message


def create_hal_hash_id(cm_files_path, corpus_year, valid_df):
    """Builds data which columns are given by 'hash_id_col_alias' 
    and 'pub_id_alias' and add column with hash IDs to the data 
    of contributions to conferences.

    The content of these columns in the built data is as follows:

    - The 'hash_id_col_alias' column contains the unique hash ID \
    built for each contribution to conferences through the `_my_hash` \
    function imported from the `bmfuncts.create_hash_id` on the basis \
    of the values of 'conf_year_alias', 'conf_name_alias', 'country_alias', \
    'doctype_alias', 'title_alias' and 'authors_alias' columns.
    - The 'pub_id_alias' column contains the order number of the contribution \
    in the list of contributions to conferences.

    The built data are saved through the `save_hash_data` function of 
    the same module.

    Args:
        cm_files_path (path): The full path to the working folder.
        corpus_year (str): 4 digits year of the corpus.
        valid_df (dataframe): The list of contributions to conferences, \
        with one row per Institute-affiliated author, merged with \
        employees data.
    Returns:
        (dataframe): The updated list of contributions to conferences.        
    """
    # Setting useful aliases
    hash_id_alias = cm_cg.HASH_COL['hash_id']
    pub_id_alias = cm_cg.CONF_COLS['pub_id']                    # 'Pub_id'
    authors_alias = cm_cg.HAL_USE_COLS['authors']               # 'Auteurs'
    title_alias = cm_cg.CONF_COLS['title']                      # "Titres"
    doctype_alias = cm_cg.CONF_COLS['doctype']                  # "Type de document"
    conf_year_alias = cm_cg.CONF_COLS['conf_year']              # "Année de conférence"
    conf_name_alias = cm_cg.CONF_COLS['conf_name']              # "Conference"
    country_alias = cm_cg.CONF_COLS['country']                  # "Pays"

    # Setting useful columns list
    useful_cols = [pub_id_alias, conf_year_alias, conf_name_alias, country_alias,
                   doctype_alias, title_alias, authors_alias]

    # Concatenate de dataframes to hash
    valid_to_hash = valid_df[useful_cols].copy()

    data = []
    for row_idx, row in valid_to_hash.iterrows():
        pub_id = row[pub_id_alias]
        text   = (f"{str(row[conf_year_alias])}"
                  f"{str(row[conf_name_alias])}"
                  f"{str(row[country_alias])}"
                  f"{str(row[doctype_alias])}"
                  f"{str(row[title_alias])}"
                  f"{str(row[authors_alias])}")
        hash_id = _my_hash(text)
        data.append([hash_id, pub_id])
    hash_id_df = pd.DataFrame(data, columns=[hash_id_alias, pub_id_alias])
    hash_id_df = hash_id_df.drop_duplicates()

    # Adding column of Hash-IDs and reordering columns in valid_df
    valid_df = valid_df.merge(hash_id_df,
                              how="inner",
                              on=pub_id_alias)
    col_dict = {hash_id_alias: 0}
    valid_df = reorder_df(valid_df, col_dict)
    
    message = save_hash_data(cm_files_path, corpus_year, hash_id_df)
    print(message)

    return valid_df
