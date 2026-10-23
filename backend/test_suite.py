import io
import json
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "model_name" in data
    print("[PASS] 1. Health check endpoint")

def test_whatsapp_bracket():
    chat = """[10/10/2023, 14:30:00] Sarah: Where are you?
[10/10/2023, 14:32:00] Alex: I'm stuck in traffic, be home in 10.
[10/10/2023, 14:33:00] Sarah: Ok drive safe, love you!
[10/10/2023, 14:33:30] Alex: Love you too!"""
    files = {"file": ("whatsapp.txt", chat.encode("utf-8"), "text/plain")}
    res = client.post("/analyze", files=files, data={"user_instructions": "Couple chatting"})
    assert res.status_code == 200
    data = res.json()
    assert data["toxicity_score"] < 25
    assert data["verdict"] in ["Healthy", "Repairable"]
    assert len(data["normalized_conversation"]) == 4
    print("[PASS] 2. WhatsApp bracket format")

def test_whatsapp_dash_and_unicode_ltr():
    chat = """\u200e12/05/2023, 2:30\u202fPM - Alice: Why did you ignore my call?
12/05/2023, 2:32 PM - Bob: I was in a meeting! You always assume the worst.
12/05/2023, 2:33 PM - Alice: Whatever, don't talk to me."""
    files = {"file": ("chat.txt", chat.encode("utf-8"), "text/plain")}
    res = client.post("/analyze", files=files, data={"user_instructions": "Heated argument"})
    assert res.status_code == 200
    data = res.json()
    assert data["gottman_breakdown"]["criticism_score"] > 0
    assert len(data["timeline_events"]) > 0
    print("[PASS] 3. WhatsApp dash & Unicode LTR mark")

def test_instagram_format():
    chat = """John (12/05/2023, 18:00): Hey, did you see the movie?
Emily (12/05/2023, 18:05): Yes! It was incredible, thanks for recommending it.
John (12/05/2023, 18:06): Anytime, glad you liked it!"""
    files = {"file": ("instagram.txt", chat.encode("utf-8"), "text/plain")}
    res = client.post("/analyze", files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["affection_levels"]["person_a"] >= 50
    assert data["verdict"] in ["Healthy", "Repairable"]
    print("[PASS] 4. Instagram export format")

def test_json_format():
    json_data = [
        {"sender": "David", "text": "Are we still meeting tonight?", "timestamp": "19:00"},
        {"sender": "Emma", "text": "Yes, absolutely! Can't wait to see you.", "timestamp": "19:02"},
        {"sender": "David", "text": "Me too :)", "timestamp": "19:03"}
    ]
    files = {"file": ("chat.json", json.dumps(json_data).encode("utf-8"), "application/json")}
    res = client.post("/analyze", files=files)
    assert res.status_code == 200
    data = res.json()
    assert len(data["normalized_conversation"]) == 3
    print("[PASS] 5. JSON export format")

def test_multiline_continuation():
    chat = """[10/10/2023, 14:00] Alice: First line of thought.
And here is the second line of the same thought without timestamp.
[10/10/2023, 14:05] Bob: Understood completely."""
    files = {"file": ("multiline.txt", chat.encode("utf-8"), "text/plain")}
    res = client.post("/analyze", files=files)
    assert res.status_code == 200
    data = res.json()
    assert len(data["normalized_conversation"]) == 2
    assert "second line" in data["normalized_conversation"][0]["original_text"]
    print("[PASS] 6. Multiline message continuation")

def test_latin1_encoding():
    chat = "[10/10/2023, 14:00] Renee: Cafe tonight?\n[10/10/2023, 14:05] Bob: Oui!"
    files = {"file": ("latin1.txt", chat.encode("latin-1"), "text/plain")}
    res = client.post("/analyze", files=files)
    assert res.status_code == 200
    data = res.json()
    assert len(data["normalized_conversation"]) == 2
    print("[PASS] 7. Latin-1 text encoding")

def test_invalid_file_extension():
    files = {"file": ("data.pdf", b"dummy pdf content", "application/pdf")}
    res = client.post("/analyze", files=files)
    assert res.status_code == 400
    assert "Unsupported file type" in res.json()["detail"]
    print("[PASS] 8. Invalid file extension rejection")

def test_empty_chat_rejection():
    files = {"file": ("empty.txt", b"\n\n   \n", "text/plain")}
    res = client.post("/analyze", files=files)
    assert res.status_code == 400
    assert "No messages found" in res.json()["detail"]
    print("[PASS] 9. Empty chat rejection")

def test_direct_json_endpoint():
    req = {
        "chat_text": "Alex: You never do dishes.\nSam: Not true, I did them yesterday.",
        "user_instructions": "Chore dispute"
    }
    res = client.post("/analyze/json", json=req)
    assert res.status_code == 200
    data = res.json()
    assert "criticism_score" in data["gottman_breakdown"]
    assert len(data["actionable_advice"]) > 0
    print("[PASS] 10. Direct JSON endpoint")

def test_repair_blueprint():
    chat = """[10/10/2023, 14:00] Alice: You are so pathetic and useless, I can't stand you.
[10/10/2023, 14:01] Bob: Whatever, you always nag.
[10/10/2023, 14:02] Alice: I'm sorry, that was mean of me. Can we talk?
[10/10/2023, 14:03] Bob: Okay, I appreciate that. Thanks."""
    files = {"file": ("conflict.txt", chat.encode("utf-8"), "text/plain")}
    res = client.post("/analyze", files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["speaker_a"] == "Alice"
    assert data["speaker_b"] == "Bob"
    assert "Alice" in data["affection_levels"]
    assert "Bob" in data["affection_levels"]
    
    assert "repair_blueprint" in data
    blueprint = data["repair_blueprint"]
    assert blueprint is not None
    assert "brutal_truth_summary" in blueprint and len(blueprint["brutal_truth_summary"]) > 0
    assert "Alice" in blueprint["brutal_truth_summary"] or "Bob" in blueprint["brutal_truth_summary"]
    assert "hopeful_path_summary" in blueprint and len(blueprint["hopeful_path_summary"]) > 0
    assert "Alice" in blueprint["hopeful_path_summary"] and "Bob" in blueprint["hopeful_path_summary"]
    
    # Verify Person Diagnostics
    assert "person_diagnostics" in blueprint and len(blueprint["person_diagnostics"]) == 2
    names = [p["name"] for p in blueprint["person_diagnostics"]]
    assert "Alice" in names and "Bob" in names
    for p in blueprint["person_diagnostics"]:
        assert len(p["primary_issues"]) > 0
        assert len(p["action_plan"]) > 0

    assert "protocols" in blueprint and len(blueprint["protocols"]) >= 4
    for proto in blueprint["protocols"]:
        assert "title" in proto
        assert "principle" in proto
        assert "action" in proto
        assert "script" in proto
        assert "rule" in proto
    print("[PASS] 11. Relationship Repair Blueprint & Person Diagnostics verification")

def test_healthy_chat_with_work_gap():
    chat = """[12/10/2023, 10:00:00] Maya: Good morning! Hope your presentation goes well today.
[12/10/2023, 12:35:00] Leo: Hey! Sorry for the delay, was wrapped up in meetings all morning. It went great though!
[12/10/2023, 12:36:15] Maya: So proud of you! You always know your stuff.
[12/10/2023, 12:37:00] Leo: Thanks love! Actually, do you want to grab dinner tonight?
[12/10/2023, 12:38:00] Maya: I'd love to, but I might be 15 mins late getting home from the studio.
[12/10/2023, 12:39:00] Leo: Ok cool, no problem at all. Take your time!
[12/10/2023, 12:40:00] Maya: Perfect, see you at 7pm! Love you."""
    files = {"file": ("healthy_chat.txt", chat.encode("utf-8"), "text/plain")}
    res = client.post("/analyze", files=files, data={"user_instructions": "Couple planning dinner"})
    assert res.status_code == 200
    data = res.json()

    # 1. Verification of False Positive Elimination
    assert data["verdict"] == "Healthy"
    assert data["toxicity_score"] <= 15
    assert data["gottman_breakdown"]["criticism_score"] == 0
    assert data["gottman_breakdown"]["contempt_score"] == 0
    assert data["gottman_breakdown"]["defensiveness_score"] == 0
    assert data["gottman_breakdown"]["stonewalling_score"] == 0

    # 2. Response Time Logic: 2.5 hr gap during 10 AM - 12:35 PM work hours must NOT trigger apathy or disconnection
    for flag in data["key_red_flags"]:
        assert "apathy" not in flag.lower()
        assert "disconnection" not in flag.lower()
        assert "defensiveness" not in flag.lower()

    # 3. Output Mapping: Healthy Relationship Template
    blueprint = data["repair_blueprint"]
    assert blueprint["blueprint_type"] == "healthy_bond"
    assert blueprint["headline"] == "Relationship Vitality & Connection Blueprint"
    assert "THE STRENGTH OF YOUR BOND" in blueprint["brutal_truth_summary"]
    assert "THE PATH FORWARD" in blueprint["hopeful_path_summary"]
    assert len(blueprint["person_diagnostics"]) == 2
    assert data["speaker_a"] in ["Maya", "Leo"]
    assert data["speaker_b"] in ["Maya", "Leo"]
    print("[PASS] 12. Healthy chat with work gap & weak keyword false-positive immunity verification")

def test_repair_attempt_context_and_greeting_mutual_exclusivity():
    chat = """[14/10/2023, 08:30:00] Chris: Good morning beautiful ☀️
[14/10/2023, 08:31:00] Taylor: Good morning handsome! Have a wonderful day.
[14/10/2023, 11:45:00] Chris: Did you hear back from the plumber?
[14/10/2023, 13:30:00] Taylor: Sorry, was in a meeting! Yes, they are coming tomorrow at 10am.
[14/10/2023, 13:32:00] Chris: Perfect, thank you love!"""
    files = {"file": ("peaceful_chat.txt", chat.encode("utf-8"), "text/plain")}
    res = client.post("/analyze", files=files)
    assert res.status_code == 200
    data = res.json()

    # Bug 1 Verification: No "Failed De-escalation" red flag without preceding tension
    for flag in data["key_red_flags"]:
        assert "failed de-escalation" not in flag.lower()

    # Bug 2 Verification: "Good morning beautiful ☀️" must ONLY be "Bid for Connection & Affection"
    # and NEVER "De-escalation / Repair Attempt"
    morning_events = [ev for ev in data["timeline_events"] if "beautiful" in ev["message"].lower()]
    assert len(morning_events) == 1
    assert morning_events[0]["label"] == "Bid for Connection & Affection"

    # Verify "Sorry, was in a meeting!" without tension is NOT a Repair Attempt
    meeting_events = [ev for ev in data["timeline_events"] if "meeting" in ev["message"].lower()]
    for ev in meeting_events:
        assert ev["label"] != "De-escalation / Repair Attempt"
        assert ev["label"] != "Successful Repair Attempt"

    # Verify notes reflect 0/0 repairs because there was zero conflict
    assert "Repairs: 0/0 accepted" in data["gottman_breakdown"]["notes"]

    # Part B: Genuine conflict where repair IS attempted and REBUFFED -> MUST trigger "Failed De-escalation"
    conflict_fail_chat = """[14/10/2023, 19:00:00] Alice: You always embarrass me in front of our friends!
[14/10/2023, 19:01:00] Bob: Stop attacking me, you ruin every single party!
[14/10/2023, 19:02:00] Alice: I'm sorry, that was mean of me. Can we talk calmly?
[14/10/2023, 19:03:00] Bob: Shut up, get lost."""
    files_conflict = {"file": ("conflict_fail.txt", conflict_fail_chat.encode("utf-8"), "text/plain")}
    res_conflict = client.post("/analyze", files=files_conflict)
    assert res_conflict.status_code == 200
    data_conflict = res_conflict.json()

    # Preceding conflict existed -> Alice's message MUST be recognized as a Repair Attempt
    repair_events = [ev for ev in data_conflict["timeline_events"] if "sorry" in ev["message"].lower()]
    assert len(repair_events) == 1
    assert repair_events[0]["label"] == "De-escalation / Repair Attempt"
    # And it must be mutually exclusive (not also labeled as affection)
    assert not any(ev["label"] == "Bid for Connection & Affection" and "sorry" in ev["message"].lower() for ev in data_conflict["timeline_events"])

    # Because Bob rejected Alice's repair, Failed De-escalation red flag MUST trigger
    assert any("failed de-escalation" in flag.lower() for flag in data_conflict["key_red_flags"])
    print("[PASS] 13. Context-aware Repair Attempts & Greeting Mutual Exclusivity verification")

def test_contempt_defensiveness_stonewalling_and_affection_override():
    chat = """[15/10/2023, 19:00:00] Maya: Oh, poor baby... God, you're so useless
[15/10/2023, 19:01:00] Leo: I'm working to pay for this house, but sure, I'm the bad guy
[15/10/2023, 19:02:00] Maya: You always leave everything to me, you're so lazy
[15/10/2023, 19:03:00] Leo: Whatever, leave me alone. I'm not doing this."""
    files = {"file": ("toxic_conflict.txt", chat.encode("utf-8"), "text/plain")}
    res = client.post("/analyze", files=files)
    assert res.status_code == 200
    data = res.json()

    # 1. Contempt detection: Sarcastic "poor baby... useless" must be Contempt, NOT Affection
    maya_insult_events = [ev for ev in data["timeline_events"] if "useless" in ev["message"].lower()]
    assert len(maya_insult_events) >= 1
    assert any("contempt" in ev["label"].lower() for ev in maya_insult_events)
    assert not any("affection" in ev["label"].lower() for ev in maya_insult_events)
    assert data["gottman_breakdown"]["contempt_score"] > 50

    # 2. Defensiveness detection: Leo's victimhood ("but sure, I'm the bad guy")
    assert data["gottman_breakdown"]["defensiveness_score"] > 50

    # 3. Stonewalling detection: Leo's shutdown ("Whatever, leave me alone. I'm not doing this.")
    assert data["gottman_breakdown"]["stonewalling_score"] > 50

    # 4. Mutual Respect FAILED in Green Flags
    assert not any("mutual respect" in flag.lower() for flag in data["key_green_flags"])

    # 5. Affection and Toxicity Recalibration: Affection < 20%, Toxicity > 75
    assert data["affection_levels"]["Maya"] < 20
    assert data["affection_levels"]["Leo"] < 20
    assert data["toxicity_score"] > 75
    print("[PASS] 14. Contempt, Defensiveness, Stonewalling & Affection Override verification")

if __name__ == "__main__":
    test_health()
    test_whatsapp_bracket()
    test_whatsapp_dash_and_unicode_ltr()
    test_instagram_format()
    test_json_format()
    test_multiline_continuation()
    test_latin1_encoding()
    test_invalid_file_extension()
    test_empty_chat_rejection()
    test_direct_json_endpoint()
    test_repair_blueprint()
    test_healthy_chat_with_work_gap()
    test_repair_attempt_context_and_greeting_mutual_exclusivity()
    test_contempt_defensiveness_stonewalling_and_affection_override()
    print("\n==========================================")
    print("ALL 14 RIGOROUS TESTS COMPLETED SUCCESSFULLY!")
    print("==========================================")


