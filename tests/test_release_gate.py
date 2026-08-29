from honest_agent.ops.release_gate import evaluate_release_gate


ALL_PASS = {blocker: "PASS" for blocker in ("B-1", "B-2", "B-3", "B-4", "B-5", "B-6")}


def test_release_gate_requires_all_blockers_and_risk_acceptance():
    result = evaluate_release_gate(ALL_PASS)
    assert result.decision == "NO-GO"
    assert result.blockers == ()
    result = evaluate_release_gate(ALL_PASS, residual_risk_accepted=True)
    assert result.decision == "GO"


def test_release_gate_does_not_infer_missing_or_partial_evidence_as_pass():
    result = evaluate_release_gate({"B-1": "PASS", "B-2": "PARTIAL"}, residual_risk_accepted=True)
    assert result.decision == "NO-GO"
    assert "B-2" in result.blockers
    assert "B-3" in result.blockers


def test_release_gate_allows_explicitly_scoped_conditional_pilot():
    result = evaluate_release_gate({**ALL_PASS, "B-4": "PARTIAL"}, conditional_pilot=True)
    assert result.decision == "CONDITIONAL PILOT"
    assert result.blockers == ("B-4",)


def test_release_gate_rejects_unknown_evidence_state():
    result = evaluate_release_gate({**ALL_PASS, "B-7": "DONE"}, residual_risk_accepted=True)
    assert result.decision == "NO-GO"
    assert "B-7" in result.blockers
