"""Module of useful functions for setting columns names of data.
"""

__all__ = ['build_col_conversion_dic',
          ]


# Local imports
import cmfuncts.conf_globals as cg

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

    init_cm_cols_list = sum([[cg.HASH_COL['hash_id'],
                              cg.CONF_COLS['pub_id'],
                              cg.CONF_COLS['pub_year'],
                              cg.CONF_COLS['conf_year'],
                              cg.CONF_COLS['conf_date'],
                              cg.CONF_COLS['first_author'],
                              cg.CONF_ADD_COLS['inst_authors'],                              
                              cg.CONF_COLS['authors'],
                              cg.CONF_COLS['title'],
                              cg.CONF_COLS['conf_name'],   
                              cg.CONF_COLS['doctype'],
                              cg.CONF_COLS['doi'],
                              cg.CONF_ADD_COLS['full_ref'],
                              cg.CONF_COLS['town'],
                              cg.CONF_COLS['country'],
                             ],
                             dpt_col_list,
                             [cg.CONF_COLS['commitee'],
                              cg.CONF_COLS['proceedings'],
                              cg.CONF_COLS['url'],
                             ],
                            ], [])

    final_cm_cols_list = sum([[cg.HASH_COL['hash_id'],
                               cg.CONF_COLS['pub_id'],
                               cg.CONF_COLS['pub_year'],
                               cg.CONF_COLS['conf_year'],
                               'Date de conférence',
                               cg.CONF_COLS['first_author'],
                               cg.CONF_ADD_COLS['inst_authors'],                              
                               cg.CONF_ADD_COLS['all_authors'],
                               'Titre',
                               'Conférence',   
                               cg.CONF_COLS['doctype'],
                               cg.CONF_COLS['doi'],
                               cg.CONF_ADD_COLS['full_ref'],
                               cg.CONF_COLS['town'],
                               cg.CONF_COLS['country'],
                              ],
                               dpt_col_list,
                              ["Comité de lecture",
                               "Actes de conférence",
                               cg.CONF_COLS['url'],
                              ]
                             ], [])

    cols_rename_dict = dict(zip(init_cm_cols_list, final_cm_cols_list))

    return cols_rename_dict
