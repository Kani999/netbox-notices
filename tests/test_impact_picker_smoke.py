"""
Smoke test: the rendered Impact form gives the user device context when picking an Interface.

Fetches the real pages through the Django test client (same HTML the browser gets after the
HTMX reload that follows picking a content type).
"""

import pytest
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

PICKER_CONFIG = {
    "notices": {
        "allowed_content_types": ["dcim.Interface", "circuits.Circuit"],
        "parent_fields": {"dcim.Interface": "device", "notices.Maintenance": "provider"},
    }
}


@pytest.fixture(autouse=True)
def picker_config(settings):
    settings.PLUGINS_CONFIG = PICKER_CONFIG


@pytest.fixture
def interface(device):
    from dcim.models import Interface

    return Interface.objects.create(device=device, name="Gi0/1", type="1000base-t")


@pytest.mark.django_db
class TestImpactPickerSmoke:
    def test_add_page_interface_target_has_selector_and_parent(self, admin_client, maintenance):
        from dcim.models import Interface

        url = reverse("plugins:notices:impact_add")
        params = {
            "event_content_type": ContentType.objects.get_for_model(maintenance).pk,
            "event_object_id": maintenance.pk,
            "target_content_type": ContentType.objects.get_for_model(Interface).pk,
        }
        response = admin_client.get(url, params)
        html = response.content.decode()

        assert response.status_code == 200
        assert 'selector="dcim.interface"' in html
        assert 'ts-parent-field="device"' in html
        assert 'selector="notices.maintenance"' in html
        assert 'ts-parent-field="provider"' in html
        assert html.count('title="Open selector"') == 2  # one button per GFK dropdown

    def test_edit_page_preselects_interface(self, admin_client, maintenance, interface):
        from notices.models import Impact

        impact = Impact.objects.create(event=maintenance, target=interface, impact="OUTAGE")
        response = admin_client.get(reverse("plugins:notices:impact_edit", args=[impact.pk]))
        html = response.content.decode()

        assert response.status_code == 200
        assert f'<option value="{interface.pk}"' in html
        assert 'ts-parent-field="device"' in html

    def test_selector_modal_for_interface_offers_device_filter(self, admin_client):
        response = admin_client.get(reverse("htmx_object_selector"), {"_model": "dcim.interface", "target": "x"})
        html = response.content.decode()

        assert response.status_code == 200
        assert 'name="device_id"' in html

    def test_post_creates_impact_on_interface(self, admin_client, maintenance, interface):
        from dcim.models import Interface

        from notices.models import Impact

        data = {
            "event_content_type": ContentType.objects.get_for_model(maintenance).pk,
            "event_choice": maintenance.pk,
            "target_content_type": ContentType.objects.get_for_model(Interface).pk,
            "target_choice": interface.pk,
            "impact": "OUTAGE",
        }
        response = admin_client.post(reverse("plugins:notices:impact_add"), data)

        assert response.status_code == 302, response.content.decode()[:500]
        assert Impact.objects.get().target == interface
