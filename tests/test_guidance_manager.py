from guidance import manager


def test_scan_guidance():
    output = "Open ports on localhost: 22, 80"
    hint = manager.generate("scan localhost", output)
    assert "Open ports found" in hint
    assert "22" in hint and "80" in hint


def test_recon_guidance():
    out = "results saved to scan_logs/test.json"
    hint = manager.generate("sniper 1.1.1.1", out)
    assert "scan_logs/test.json" in hint
