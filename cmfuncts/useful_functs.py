"""Module of useful functions used by several modules of package `cmfuncts`.

"""

__all__ = ['capitalize_name',
           'create_cm_archi',
           'standardize_name',
          ]


# 3rd party imports
import BiblioParsing as bp
from bmfuncts.useful_functs import create_folder


def capitalize_name(name):
    """ Capitalizes each word in a text representing a name.
    
    All words are capitalized including those separated by a minus symbol.

    Args:
        name (str): The text to be modified.
    Returns:
     (str): The modifyed text.
    """
    name_space_split = name.split(" ")
    name_cap_list = []
    for sub_name in name_space_split:
        sub_name_minus_split = [x.capitalize() for x in sub_name.split("-")]
        sub_name_cap = "-".join(sub_name_minus_split)
        name_cap_list.append(sub_name_cap)
    name_cap = " ".join(name_cap_list)
    return name_cap


def standardize_name(name):
    """Removes accentuated characters.

    This done through the `remove_special_symbol` function imported 
    from the `BiblioParsing` package imported as bp.

    Args:
        name (str): The text to be modified.
    Returns:
     (str): The modifyed text.
     """
    new_name = bp.remove_special_symbol(name, only_ascii=True, strip=True)
    return new_name


def create_cm_archi(wf_path, corpus_year_folder, verbose=False):
    """Creates a corpus folder with the required architecture.

    It uses the global "CM_ARCHI" for the names of the sub_folders 
    and the `create_folder` function imported from 
    the `bmfuncts.useful_functs` module.

    Args:
        wf_path (path): The full path of the working folder.
        corpus_year_folder (str): The name of the folder of the corpus.
        verbose (bool): Optional status of prints (default = False).
    Returns:
        (str): End message recalling the corpus-year architecture created.
    """
    # Setting useful alias
    archi_alias = cg.CM_ARCHI

    # Creating architecture for corpus-year working-folder
    corpus_year_folder_path = create_folder(wf_path, corpus_year_folder, verbose=verbose)
    _ = create_folder(corpus_year_folder_path, archi_alias["corpus_folder"], verbose=verbose)
    _ = create_folder(corpus_year_folder_path, archi_alias["conf_empl_folder"], verbose=verbose)
    _ = create_folder(corpus_year_folder_path, archi_alias["final_results_folder"], verbose=verbose)

    message = f"Architecture created for {corpus_year_folder} folder"
    return message