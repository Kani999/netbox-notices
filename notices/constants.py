"""
Constants for vendor notification plugin configuration
"""

# Default allowed content types for impact linking
DEFAULT_ALLOWED_CONTENT_TYPES = [
    "circuits.Circuit",
    "dcim.Device",
    "dcim.PowerFeed",
    "dcim.Site",
]

# Parent object shown next to each option in the Impact target/event dropdowns ("device > Gi0/1").
# Only models whose brief API serializer returns the parent work here (Device, Site, PowerFeed do not).
DEFAULT_PARENT_FIELDS = {
    "dcim.Interface": "device",
    "virtualization.VMInterface": "virtual_machine",
    "circuits.Circuit": "provider",
    "notices.Maintenance": "provider",
    "notices.Outage": "provider",
}

# Generating notifications creates, updates and deletes drafts, so it needs all three rights.
GENERATE_NOTIFICATIONS_PERMISSIONS = (
    "notices.add_preparednotification",
    "notices.change_preparednotification",
    "notices.delete_preparednotification",
)
