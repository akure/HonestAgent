from honest_agent.ops.release_packaging import STD10G_TOOLS, verify_std10g_prerequisites


def test_std10g_gate_reports_all_required_capabilities_without_claiming_release():
    result = verify_std10g_prerequisites()
    assert set(result["tools"]) == set(STD10G_TOOLS)
    assert result["status"] in {"READY", "BLOCKED"}
    if result["status"] == "BLOCKED":
        assert result["action"] == "NO_RELEASE_EXECUTION"
        assert result["missing_tools"]
    else:
        assert result["action"] == "REQUIRES_APPROVED_TARGET_AND_CREDENTIALS"


def test_std10g_gate_is_conservative_when_any_capability_is_missing():
    result = verify_std10g_prerequisites()
    required = result["required_capabilities"]
    if result["status"] == "BLOCKED":
        assert not all(required.values())
        assert set(result["missing_tools"]).issuperset(set(STD10G_TOOLS) - set(result["tools"]))
