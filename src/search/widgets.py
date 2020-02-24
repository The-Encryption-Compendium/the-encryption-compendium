"""
Custom widgets for the search app.
"""

from encryption_compendium.widgets import IconTextInput


class SearchInput(IconTextInput):
    """
    Custom TextInput widget for search bars.
    """

    icon_name = "search"
    placeholder = "Search..."
