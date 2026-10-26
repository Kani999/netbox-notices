"""
Django system checks for the notices plugin.

Currently checks that every entry in ``allowed_content_types`` has a Site
resolver registered. Without one, impacts targeting that content type silently
have an empty ``sites`` cache and won't appear in site/region/location
filters — a class of bug worth catching at startup rather than at query time.
"""

from django.apps import apps
from django.core.checks import Warning, register

from .resolvers import SITE_RESOLVERS
from .utils import get_allowed_content_types, get_parent_fields, parent_field_for


@register()
def check_resolver_coverage(app_configs, **kwargs):
    """W001: warn for allowed content types missing a Site resolver."""
    warnings = []
    registered = {k.lower() for k in SITE_RESOLVERS}
    for ct_string in get_allowed_content_types():
        if ct_string.lower() not in registered:
            warnings.append(
                Warning(
                    f"No site resolver registered for allowed content type {ct_string!r}.",
                    hint=(
                        "Impacts targeting this type will have empty Impact.sites and won't appear "
                        "in site/region/location filters. Register one via "
                        "notices.resolvers.register_site_resolver, and add a matching signal "
                        "handler in notices.signals so the cache stays fresh when the target's "
                        "site changes."
                    ),
                    id="notices.W001",
                )
            )
    return warnings


@register()
def check_parent_fields(app_configs, **kwargs):
    """W002: warn for `parent_fields` entries that name a missing model or a non-ForeignKey field."""
    warnings = []
    for label, field_name in get_parent_fields().items():
        try:
            model = apps.get_model(label)
        except (LookupError, ValueError):
            model = None
        if model is None or parent_field_for(model) != field_name:
            warnings.append(
                Warning(
                    f"Ignoring parent_fields entry {label!r}: {field_name!r}.",
                    hint="The key must be an installed 'app_label.ModelName' and the value a ForeignKey on it.",
                    id="notices.W002",
                )
            )
    return warnings
