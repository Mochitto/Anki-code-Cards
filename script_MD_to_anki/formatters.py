import logging
import re
from typing import Dict, List, Tuple

import card_types as Types
from cards_specific_wrappers import wrap_tab, wrap_tab_body, wrap_tab_group, wrap_tab_label
from debug_tools import expressive_debug

logger = logging.getLogger(__name__)


def format_tabs(tabs: List[Types.HTMLTab]) -> List[Types.HTMLString]:
    formatted_tabs = [format_tab(tab) for tab in tabs]
    return formatted_tabs


def format_tab(tab: Types.HTMLTab) -> Types.HTMLString:
    tab_label = tab["tab_label"]
    tab_body = tab["tab_body"]

    wrapped_label = wrap_tab_label(tab_label)
    wrapped_body = wrap_tab_body(tab_body)

    return wrap_tab(wrapped_label, wrapped_body)


def format_tab_group(tabs_list: List[Types.HTMLString], add_over_sibling=False) -> Types.HTMLString:
    tabs = tabs_list.copy()

    if tabs:
        activated_tabs = activate_first_tab(tabs)
        joined_tabs = "".join(activated_tabs)

        tab_group = wrap_tab_group(joined_tabs, add_over_sibling)
        cleaned_tab_group = remove_newlines(tab_group)
    else:
        return ""

    return cleaned_tab_group


def activate_first_tab(tabs: List[Types.HTMLString]) -> List[Types.HTMLString]:
    new_tabs = tabs.copy()

    new_tabs[0] = re.sub(r'(class="tab)"', r'\1 tab--isactive"', new_tabs[0])
    return new_tabs


def remove_newlines(text: Types.HTMLString) -> Types.HTMLString:
    """Remove newlines from the text.
    This is needed because all the newlines INSIDE tags will become <br>, when needed.
    The remaining newlines are linked to the markdown input
    and become useless as block elements do not need them.
    """
    return re.sub(r"\n", "", text)
