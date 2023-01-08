import logging
from typing import List
from dataclasses import asdict

from extract import extract_cards, extract_card_sides, extract_tabs_sides, extract_tabs
from formatters import format_tabs, format_tab_group
from tab_swapping import get_swapped_tabs
from text_to_html import tabs_to_html
from card_error import CardError, validate_card_data, are_clozes_in_card
import card_types as Types

from logger import expressive_debug

# NOTE: if changes are made to the cards' HTML/CSS/JS, you also want to look into cards_specific_wrappers' functions

logger = logging.getLogger(__name__)


# TODO: turn behaviour configs to kwargs
def markdown_to_anki(markdown: Types.MDString, interactive=False, fast_forward=False):
    cards = extract_cards(markdown)

    if cards[0]:
        logger.info(f"📦 Found {len(cards)} cards to process...")
    else:
        raise CardError("No cards were found...")

    processed_cards = []
    processed_cards_with_cloze = []
    failed_cards = []
    aborted_cards = 0
    successful_cards = 0

    for index, card in enumerate(cards):
        try:  # Handle CardErrors
            card_sides = extract_card_sides(card)

            card_data: Types.CardWithSwap = {
                "front": {
                    "left_tabs": [],
                    "left_tabs_swap": [],
                    "right_tabs": [],
                    "right_tabs_swap": []
                },
                "back": {
                    "left_tabs": [],
                    "left_tabs_swap": [],
                    "right_tabs": [],
                    "right_tabs_swap": []
                }
            }

            for side, side_content in asdict(card_sides).items():
                tabs_sides = extract_tabs_sides(side_content)

                for tab_side, tab_side_content in tabs_sides.items():
                    if not tab_side_content:  # Non-empty tab side
                        continue
                    tabs_info = extract_tabs(tab_side_content)
                    html_tabs = tabs_to_html(tabs_info["tabs"])
                    formatted_tabs = format_tabs(html_tabs)

                    card_data[side][tab_side] = formatted_tabs
                    card_data[side][f"{tab_side}_swap"] = tabs_info["tabs_to_swap"]

            validate_card_data(card_data)

            card_with_swapped_tabs = get_swapped_tabs(card_data)

            formatted_card = {
                "front": "",
                "back": ""
            }

            for side in asdict(card_sides).keys():
                formatted_card[side] += format_tab_group(card_with_swapped_tabs[side]["left_tabs"])
                formatted_card[side] += format_tab_group(card_with_swapped_tabs[side]["right_tabs"])

            if are_clozes_in_card(formatted_card):
                processed_cards_with_cloze.append(formatted_card)
            else:
                processed_cards.append(formatted_card)
            successful_cards += 1

        except CardError as error:
            if fast_forward:
                logger.error(f"{error}")
                logger.info(f"❌ Failed to process the card number {index + 1}...")
                aborted_cards += 1
                failed_cards.append(f"❌ ERROR ❌ - {error}\n{card}")
                continue
            elif interactive:
                logger.info(f"\n📔 This is the card that created the error:📔\n{card}\n\n(see card above)")
                logger.error(error)

                user_input = input("❓ Would you like to abort this card and continue? (y/N)\n>>> ").lower()
                if user_input == "y" or user_input == "yes":
                    logger.info(f"❌ Failed to process the card number {index + 1}...")
                    aborted_cards += 1
                    failed_cards.append(f"❌ ERROR ❌ - {error}\n{card}")
                    continue
            raise error
        logger.info(f"✅ Finished processing the card number {index + 1}!")

    return {
        "cards": processed_cards,
        "cards_with_clozes": processed_cards_with_cloze,
        "failed_cards": failed_cards,
        "number_of_successful": successful_cards,
        "number_of_failed": aborted_cards
    }
