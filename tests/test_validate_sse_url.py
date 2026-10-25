"""Unit tests for core.mcp_client.validate_sse_url (SSRF guard)."""
import unittest

from core.mcp_client import validate_sse_url


class ValidateSseUrlTest(unittest.TestCase):
    def test_public_url_passes(self):
        # example.com is guaranteed-public (IANA reserved documentation
        # domain) and resolves to public addresses.
        validate_sse_url("https://example.com/sse")  # must not raise
        validate_sse_url("http://example.com:8080/sse")

    def test_public_ip_literal_passes(self):
        validate_sse_url("http://93.184.216.34/sse")  # example.com's historic IP

    def test_cloud_metadata_blocked(self):
        with self.assertRaises(ValueError):
            validate_sse_url("http://169.254.169.254/latest/meta-data/")

    def test_localhost_blocked(self):
        with self.assertRaises(ValueError):
            validate_sse_url("http://localhost:8501/sse")
        with self.assertRaises(ValueError):
            validate_sse_url("https://localhost/sse")
        with self.assertRaises(ValueError):
            validate_sse_url("http://foo.localhost/sse")

    def test_loopback_ip_blocked(self):
        with self.assertRaises(ValueError):
            validate_sse_url("http://127.0.0.1:8080/sse")
        with self.assertRaises(ValueError):
            validate_sse_url("http://127.0.0.42/sse")
        with self.assertRaises(ValueError):
            validate_sse_url("http://[::1]:8080/sse")

    def test_private_ranges_blocked(self):
        for url in (
            "http://10.0.0.1/sse",
            "http://10.255.255.255/sse",
            "http://172.16.0.1/sse",
            "http://172.31.255.255/sse",
            "http://192.168.1.1/sse",
            "http://192.168.254.254/sse",
            "http://[fe80::1]/sse",
            "http://[fd00::1]/sse",
        ):
            with self.assertRaises(ValueError, msg=url):
                validate_sse_url(url)

    def test_ftp_scheme_blocked(self):
        with self.assertRaises(ValueError):
            validate_sse_url("ftp://example.com/sse")
        with self.assertRaises(ValueError):
            validate_sse_url("file:///etc/passwd")
        with self.assertRaises(ValueError):
            validate_sse_url("gopher://127.0.0.1/")

    def test_no_host_blocked(self):
        with self.assertRaises(ValueError):
            validate_sse_url("http:///sse")


if __name__ == "__main__":
    unittest.main()
