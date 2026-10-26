"""
Utility functions for vendor notification plugin
"""

from django.conf import settings
from django.core.exceptions import FieldDoesNotExist

from .constants import DEFAULT_ALLOWED_CONTENT_TYPES


def get_allowed_content_types():
    """
    Get list of allowed content types from plugin config.

    Returns list from PLUGINS_CONFIG['notices']['allowed_content_types']
    or DEFAULT_ALLOWED_CONTENT_TYPES if not configured.
    """
    return settings.PLUGINS_CONFIG.get("notices", {}).get("allowed_content_types", DEFAULT_ALLOWED_CONTENT_TYPES)


def get_parent_fields():
    """
    Parent-field map from PLUGINS_CONFIG['notices']['parent_fields'] (no built-in default).

    Keys are "app_label.ModelName" (any case), values the name of a ForeignKey on that model.
    """
    configured = settings.PLUGINS_CONFIG.get("notices", {}).get("parent_fields", {})
    return {key.lower(): value for key, value in configured.items() if value}


def parent_field_for(model):
    """Name of the configured parent ForeignKey of `model`, or None if unset or invalid."""
    name = get_parent_fields().get(model._meta.label_lower)
    if not name:
        return None
    try:
        field = model._meta.get_field(name)
    except FieldDoesNotExist:
        return None
    return name if field.many_to_one else None
