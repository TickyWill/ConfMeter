"""Module of useful functions for setting columns names of data.
"""

__all__ = ['build_col_conversion_dic',
          ]


# Local imports
import cmfuncts.conf_globals as cm_cg

def build_hal_col_conversion_dic(org_tup):
    """Builds a dict for setting the final column names 
    given the initial column names of the data.

    Args:
        org_tup (tup): The tuple of the organization structure \
        of the Institute.
    Returns:
        (dict): The dict for renaming the columns of the data \
        of the Institute contributions to conferences.
    """

    # Setting institute parameters
    dpt_label_dict = org_tup[1]
    dpt_col_list   = list(dpt_label_dict.keys())
    
    # Colonnes à ajouter          
    #"Liste ordonnée de tous les auteurs"                                 

    init_cm_cols_list = sum([[cm_cg.HASH_COL['hash_id'],
                              cm_cg.CONF_COLS['pub_id'],
                              cm_cg.CONF_COLS['pub_year'],
                              cm_cg.CONF_COLS['conf_year'],
                              cm_cg.CONF_COLS['conf_date'],
                              cm_cg.CONF_COLS['first_author'],
                              cm_cg.CONF_ADD_COLS['inst_authors'],                              
                              cm_cg.CONF_COLS['authors'],
                              cm_cg.CONF_COLS['title'],
                              cm_cg.CONF_COLS['conf_name'],   
                              cm_cg.CONF_COLS['doctype'],
                              cm_cg.CONF_COLS['doi'],
                              cm_cg.CONF_ADD_COLS['full_ref'],
                              cm_cg.CONF_COLS['town'],
                              cm_cg.CONF_COLS['country'],
                             ],
                             dpt_col_list,
                             [cm_cg.CONF_COLS['commitee'],
                              cm_cg.CONF_COLS['proceedings'],
                              cm_cg.CONF_COLS['url'],
                             ],
                            ], [])

    final_cm_cols_list = sum([[cm_cg.HASH_COL['hash_id'],
                               cm_cg.CONF_COLS['pub_id'],
                               cm_cg.CONF_COLS['pub_year'],
                               cm_cg.CONF_COLS['conf_year'],
                               'Date de conférence',
                               cm_cg.CONF_COLS['first_author'],
                               cm_cg.CONF_ADD_COLS['inst_authors'],                              
                               cm_cg.CONF_ADD_COLS['all_authors'],
                               'Titre',
                               'Conférence',   
                               cm_cg.CONF_COLS['doctype'],
                               cm_cg.CONF_COLS['doi'],
                               cm_cg.CONF_ADD_COLS['full_ref'],
                               cm_cg.CONF_COLS['town'],
                               cm_cg.CONF_COLS['country'],
                              ],
                               dpt_col_list,
                              ["Comité de lecture",
                               "Actes de conférence",
                               cm_cg.CONF_COLS['url'],
                              ]
                             ], [])

    cols_rename_dict = dict(zip(init_cm_cols_list, final_cm_cols_list))

    return cols_rename_dict
