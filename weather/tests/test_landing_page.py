import pytest
from django.urls import reverse


def test_landing_page(client):
    """
    Test the landing page view to ensure it renders correctly.

    This test verifies that the landing page view returns a 200 OK status code when accessed,
    and that the template context contains the correct 'project_name' and 'author' values as expected.
    """

    # Simulate a request to the landing page URL
    url = reverse('landing-page')
    response = client.get(url)

    # Check that the response is 200 OK
    assert response.status_code == 200

    # Verify that the context contains the correct project_name and author
    assert 'project_name' in response.context
    assert response.context['project_name'] == 'Weather API'
    assert 'author' in response.context
    assert response.context['author'] == 'Ali Tahir'

    # also, verify that the correct template was used to render the landing page
    assert 'weather/landing_page.html' in [t.name for t in response.templates]
