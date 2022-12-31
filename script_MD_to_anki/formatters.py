import re
from typing import List

from cards_specific_wrappers import wrap_tab, wrap_tab_body, wrap_tab_label, wrap_tab_group
import card_types as CardTypes

def format_tabs(tabs: List[CardTypes.Tab]) -> List[str]:
    formatted_tabs = []
    for tab in tabs:
        html_tab = format_tab(tab)
        formatted_tabs.append(html_tab)
    return formatted_tabs

def format_tab(tab: CardTypes.Tab) -> str:
    tab_label = tab["tab_label"]
    tab_body = tab["tab_body"]

    wrapped_label = wrap_tab_label(tab_label)
    wrapped_body = wrap_tab_body(tab_body)

    finished_tab = wrap_tab(wrapped_label, wrapped_body)
    return finished_tab

def format_tab_group(tabs_list, add_over_sibling=False):
    tabs = tabs_list.copy()

    if tabs:
        activated_tabs = activate_first_tab(tabs)
        joined_tabs = "".join(activated_tabs)

        tab_group = wrap_tab_group(joined_tabs, add_over_sibling)
        cleaned_tab_group = remove_newlines(tab_group)
    else:
        return ""

    return cleaned_tab_group

def activate_first_tab(tabs):
    new_tabs = tabs.copy()

    new_tabs[0] = re.sub(r'(class="tab)"', r'\1 tab--isactive"', new_tabs[0])
    return new_tabs

def remove_newlines(text: str) -> str:
    """Remove newlines from the text.
    This is needed because all the newlines INSIDE tags will become <br>, when needed.
    The remaining newlines are linked to the markdown input
    and become useless as block elements do not need them.

    This might be a useless step depending on mistune's configuration?"""
    return re.sub(r"\n", "", text)

def clean_from_clozes(text:str) -> str:
    clozes_regex = re.compile(r"{{c(\d)::(.+?)}}")

    text_without_clozes = re.sub(clozes_regex, r"\2", text)
    
    return text_without_clozes

def inject_clozes(text: str, list_of_clozes) -> str:
    new_text = text

    for cloze in list_of_clozes:
        number = cloze[0]
        clozed_text = cloze[1]
        escaped_clozed_text = re.escape(cloze[1])

        word_regex = re.compile(fr"\b{clozed_text}\b")

        new_text = re.sub(word_regex, f"{{{{c{number}::{clozed_text}}}}}", new_text)

    return new_text