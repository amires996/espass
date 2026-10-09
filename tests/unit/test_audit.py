from pyvault.services.security_audit import audit_credentials


def test_audit_detects_reuse_empty_and_http_without_exposing_password():
    items=[{"title":"A","password":"shared","url":"http://example.test"},
           {"title":"B","password":"shared"},{"title":"C","password":""}]
    issues=audit_credentials(items)
    labels={x["issue"] for x in issues}
    assert "Potentially reused password" in labels
    assert "Empty password" in labels
    assert "Website does not use HTTPS" in labels
    assert all("shared" not in str(issue) for issue in issues)
