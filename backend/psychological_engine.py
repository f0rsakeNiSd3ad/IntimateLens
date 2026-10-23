import re
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from models import ChatMessage, TimelineEvent, GottmanAnalysis

class PsychologicalEngine:
    """
    On-Device Psychological Framework Engine for Relationship Telemetry.
    Implements:
    - Gottman Method: Four Horsemen (Criticism, Contempt, Defensiveness, Stonewalling)
    - Gottman 5:1 Positivity-to-Negativity Affect Ratio (SPAFF)
    - Response Time & Work-Hour Autonomy Telemetry (9 AM - 5 PM protection)
    - Context-Aware De-escalation & Logistical Courtesy Handling
    - Attachment Theory: Anxious (Pursuer) vs. Avoidant (Distancer) Linguistic Dynamics
    - Adaptive Output Mapping: Bifurcates between 'Healthy/Bonding' and 'Crisis/Repair'
    """

    # 1. Criticism: Character assassination & globalizing blame
    # Specifically targets negative absolutes while protecting positive praise ("you always make me smile")
    CRITICISM_PATTERNS = [
        r"\b(you always (assume|think the worst|forget|ruin|ignore|mess up|complain|disappoint|judge|criticize|blame|yell|snap|act like|leave|make me feel bad|attack|jump to))\b",
        r"\b(you never (listen|care|help|remember|understand|support|apologize|try|show up|change|appreciate))\b",
        r"\b(why do you always (have to|ruin|start|make it about))\b",
        r"\b(you can never (just|admit|listen|be supportive|handle))\b",
        r"\b(it'?s (always|all) your fault|you ruin everything|you ruined it)\b",
        r"\b(you'?re (so )?(selfish|lazy|childish|careless|inconsiderate|immature|dramatic|toxic|narcissistic))\b",
        r"\b(you are (so )?(selfish|lazy|childish|careless|inconsiderate|immature|dramatic|toxic|narcissistic))\b",
        r"\b(why can'?t you (just|ever) (listen|be normal|act right|care))\b",
        r"\b(what is wrong with you|you have no idea how to be)\b",
        r"\b(tum hamesha (yahi karte ho|galti karte ho|ladte ho|chillate ho))\b",
        r"\b(kabhi meri baat nahi sunte|sab tumhari galti|har baar yahi natak)\b",
        r"\b(tum (bahut )?(matlabi|dramebaaz|pagal|chhoti soch|irresponsible) ho)\b",
    ]

    # Positive absolutes that must NEVER be flagged as criticism
    POSITIVE_ABSOLUTE_PATTERNS = [
        r"\byou always (make me (smile|laugh|happy)|look|know how to|support|help|encourage|give|love|take care|bring|inspire|know)\b",
        r"\byou never (fail to|disappoint when|let me down)\b",
        r"\bevery single time (we (meet|talk|hang|see)|i see you|we are together)\b",
    ]

    # 2. Contempt: Moral superiority, sneering, mocking, cynicism, hostility (#1 predictor of relationship failure)
    CONTEMPT_PATTERNS = [
        r"\b(pathetic|disgusting|worthless|loser|idiot|moron|stupid|clown|trash)\b",
        r"\b(useless|lazy|poor baby|like a child|acting like a child|such a child|like your dad|like your mother|like your mom)\b",
        r"\b(waste of space|waste of time|total waste|waste)\b",
        r"\b(sick of you|tired of your face|shut up|get lost|get a life|grow up)\b",
        r"\b(you're a joke|what a joke|do you want an award|rolling my eyes)\b",
        r"\b(you're impossible|clueless|embarrassing|disgrace)\b",
        r"\b(bakwas|chup kar|chup|kutta|kamina|giri hui|dimag kharab|aukat)\b",
        r"\b(dramabaaz|dramebaaz|overacting|apna shakal dekha hai)\b",
        r"[🙄😒🤡🤮🖕]",
    ]

    # 3. Defensiveness: Victimhood, cross-complaining, deflection, denying responsibility
    # Detects righteous indignation, cross-complaining, and victimhood postures
    DEFENSIVENESS_PATTERNS = [
        r"\b(not my fault|it'?s not my fault|i did nothing wrong|what did i do wrong)\b",
        r"\b(what about you|you did the same thing|look who'?s talking|you started it)\b",
        r"\b(i only did (that|it) because you|you made me (do|say))\b",
        r"\b(stop attacking me|stop blaming me|stop accusing me|why are you always on my case)\b",
        r"\b(you'?re overreacting|making a big deal out of nothing|making a scene)\b",
        r"\b(sorry but you|i'?m sorry but you (started|did|pushed))\b",
        r"\b(but sure|i'?m the bad guy|im the bad guy|make me (out to be )?(the|a) (bad guy|villain)|always my fault|blame me)\b",
        r"\b(you never appreciate|after everything i (do|did)|i work hard|working to pay|i do everything)\b",
        r"\b(meri galti nahi|maine kya kiya tha|tumne bhi to wahi kiya|tumne pehle shuru kiya)\b",
        r"\b(overreact mat karo|faltu me blame mat karo|maine to bas tumhare bolne par kiya)\b",
    ]

    # 4. Affection, Fondness, Admiration & Collaborative Connection Bids
    # Encompasses explicit love, daily care, shared humor, appreciation, and collaborative planning
    # Standalone 'baby' removed to prevent false positives with sarcastic or demeaning phrases ("poor baby")
    AFFECTION_PATTERNS = [
        r"\b(love you|i love you|miss you|so proud of you|adore you|cherish you)\b",
        r"\b(sweetheart|babe|darling|honey|cutie|my love|handsome|gorgeous|beautiful)\b",
        r"\b(my baby|hey baby|love you baby|thanks baby|night baby|morning baby)\b",
        r"\b(thank you|thanks so much|really appreciate|grateful for you|means so much|means a lot)\b",
        r"\b(thinking of you|hope you have a great|how was your day|take care|sleep well|good morning|good night|sweet dreams|drive safe)\b",
        r"\b(sounds (great|good|awesome|perfect|fun)|can'?t wait|looking forward to|excited to see you|love that)\b",
        r"\b(haha|hahaha|lol|lmao|rofl|so funny|hilarious)\b",
        r"\b(jaan|babu|shona|merijaan|pyaar|bohot pyaar|shukriya|shabash)\b",
        r"[❤️💖💕🥰😘😍🤗✨😊😄🎉👍👏🙌]"
    ]

    # 5. Genuine Conflict Repair Attempts: Apologies and concessions during disputes
    REPAIR_PATTERNS = [
        r"\b(i'm sorry|i am sorry|my bad|i apologize|please forgive me)\b",
        r"\b(you'?re right|i see your point|i understand why you|let'?s start over)\b",
        r"\b(i don'?t want to fight|can we calm down|let'?s take a breath|i hear you)\b",
        r"\b(i shouldn'?t have said that|let me rephrase|can we hug|peace)\b",
        r"\b(maaf kar do|sorry yaar|galti ho gayi|ladayi nahi karni|maaf karna)\b",
        r"[🥺🙏🕊️🤝]"
    ]

    # 6. Anxious Attachment (Pursuer): Urgency, reassurance-seeking, hypervigilance
    ANXIOUS_PATTERNS = [
        r"\b(are you mad at me|are you angry|did i do something wrong)\b",
        r"\b(why are you ignoring me|why aren'?t you answering|please reply)\b",
        r"\b(do you (even )?(still )?love me|do you even care|answer me)\b",
        r"\b(hello\?+|where are you\?+|talk to me|say something)\b",
        r"\b(naraz ho kya|reply kyu nahi|kya hua baat kyu nahi|batao na)\b",
    ]

    # 7. Avoidant Attachment (Distancer): Deactivation, minimizing, emotional distancing
    AVOIDANT_PATTERNS = [
        r"\b(you'?re making a big deal out of nothing|stop being dramatic)\b",
        r"\b(i don'?t have time for this drama|calm down|chill|too much drama)\b",
        r"\b(stop overthinking|you'?re crazy|not dealing with this)\b",
        r"\b(it is what it is|let it go|forget it|not in the mood)\b",
        r"\b(drame mat karo|chhoti baat ka batangad|dimag mat khao)\b",
    ]

    @staticmethod
    def parse_msg_datetime(ts_str: Optional[str]) -> Optional[datetime]:
        """Parses various chat export timestamp formats into a datetime object."""
        if not ts_str:
            return None
        cleaned = ts_str.strip().strip("[]").replace("\u202f", " ").replace("\xa0", " ")
        formats = [
            "%d/%m/%Y, %H:%M:%S",
            "%m/%d/%Y, %H:%M:%S",
            "%d/%m/%Y, %I:%M:%S %p",
            "%m/%d/%Y, %I:%M:%S %p",
            "%d/%m/%Y, %H:%M",
            "%m/%d/%Y, %H:%M",
            "%d/%m/%Y, %I:%M %p",
            "%m/%d/%Y, %I:%M %p",
            "%d/%m/%y, %I:%M %p",
            "%m/%d/%y, %I:%M %p",
            "%d/%m/%y, %H:%M",
            "%m/%d/%y, %H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%H:%M:%S",
            "%H:%M",
            "%I:%M %p",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(cleaned, fmt)
            except (ValueError, TypeError):
                continue
        return None

    @staticmethod
    def is_logistical_apology(text: str) -> bool:
        """
        Identifies courteous logistical apologies (work meetings, missed calls, delays)
        rather than Gottman conflict de-escalation attempts after a fight.
        """
        lower = text.lower()
        logistical_phrases = [
            r"\b(sorry|apologies|my bad)[,.]?\s*(i\s+)?(was|just|missed|in a meeting|at work|busy|working|driving|traffic|eating|sleeping|couldn'?t answer)\b",
            r"\b(sorry|apologies|my bad)[,.]?\s*(for (the )?delay|late reply|didn'?t see|about the wait)\b",
            r"\b(missed your call|phone was on silent|caught in traffic|stuck in a meeting|running late|late reply)\b",
            r"\bsorry\b.*?\b(meeting|traffic|driving|work|call|delay|busy)\b",
        ]
        return any(re.search(pat, lower) for pat in logistical_phrases)

    @staticmethod
    def is_stonewalling(text: str, prev_msg: Optional[ChatMessage], recent_conflict: bool = False) -> bool:
        """
        Strict, context-aware stonewalling detector.
        Identifies emotional shutdown, withdrawal, and hostile disengagement.
        Everyday agreements ('ok', 'fine', 'cool', 'theek hai') are NEVER stonewalling.
        """
        lower = text.lower().strip()

        # Collaborative phrases containing 'whatever' are NOT stonewalling
        if re.search(r"\bwhatever (you (want|prefer|like|think|decide)|works|is best|is good|sounds good)\b", lower):
            return False

        # Direct stonewalling and withdrawal phrases (anywhere in message)
        stonewalling_phrases = [
            r"\b(leave me alone|not doing this|i'?m not doing this|done talking|i'?m done talking)\b",
            r"\b(shut down|shutting down|talk to the wall|don'?t talk to me|stop talking to me)\b",
            r"\b(i'?m out|im out|not dealing with this|can'?t deal with you|not listening)\b",
            r"\b(chup kar|mujhe baat nahi karni|dimag mat khao|khatam karo)\b",
        ]
        for pat in stonewalling_phrases:
            if re.search(pat, lower):
                return True

        # Dismissive words: 'whatever', 'idc', 'idk', 'bye', 'don't care'
        cold_words = {"whatever", "idc", "idk", "bye", "don't care", "dont care", "k"}
        cleaned_words = [w.strip(".,!?:;") for w in lower.split()]
        has_cold_word = (lower.rstrip(".!?") in cold_words) or any(w in cold_words for w in cleaned_words if len(cleaned_words) <= 3)

        if has_cold_word:
            # If following active tension or conflict, dismissive whatever is classic stonewalling
            if recent_conflict:
                return True
            if prev_msg:
                prev_lower = prev_msg.message.lower()
                is_emotional_context = (
                    len(prev_msg.message.split()) >= 3 or
                    any(w in prev_lower for w in ["feel", "why", "talk", "listen", "matter", "hurt", "angry", "upset", "please", "seriously", "useless", "lazy", "always", "never", "hate", "you"])
                )
                if is_emotional_context:
                    return True

        return False

    def _match_any(self, patterns: List[str], text: str) -> bool:
        lower = text.lower()
        for pat in patterns:
            if re.search(pat, lower, re.IGNORECASE):
                return True
        return False

    def analyze_conversation(self, messages: List[ChatMessage]) -> Dict[str, Any]:
        """
        Executes complete psychological telemetry on conversation turns with strict
        false-positive suppression and contextual response-time filtering.
        """
        if not messages:
            return self._empty_result()

        speakers = list(dict.fromkeys(m.sender for m in messages if m.sender and m.sender != "Unknown"))
        speaker_a = speakers[0] if len(speakers) > 0 else "Person A"
        speaker_b = speakers[1] if len(speakers) > 1 else "Person B"

        # Per-speaker tracking
        stats = {
            speaker_a: {"words": 0, "msgs": 0, "criticism": 0, "contempt": 0, "defensiveness": 0, "stonewalling": 0, "affection": 0, "repairs": 0, "anxious": 0, "avoidant": 0},
            speaker_b: {"words": 0, "msgs": 0, "criticism": 0, "contempt": 0, "defensiveness": 0, "stonewalling": 0, "affection": 0, "repairs": 0, "anxious": 0, "avoidant": 0},
        }

        timeline_events: List[TimelineEvent] = []
        positive_events_count = 0
        negative_events_count = 0
        total_repairs = 0
        accepted_repairs = 0
        message_history: List[Dict[str, Any]] = []

        # Turn-by-turn conversational analysis
        for idx, msg in enumerate(messages):
            sender = msg.sender if msg.sender in stats else (speaker_a if idx % 2 == 0 else speaker_b)
            text = msg.message
            word_count = len(text.split())
            stats[sender]["words"] += word_count
            stats[sender]["msgs"] += 1

            prev_msg = messages[idx - 1] if idx > 0 else None
            next_msg = messages[idx + 1] if idx + 1 < len(messages) else None
            dt_curr = self.parse_msg_datetime(msg.timestamp)

            # -------------------------------------------------------------
            # LOOKBACK STATE TRACKER: Contextual Tension & Sentiment
            # A Gottman "Repair Attempt" or "De-escalation" can ONLY exist
            # if there was a preceding negative event (conflict, criticism,
            # contempt, defensiveness, stonewalling) within the last 3-5 msgs
            # (or within the last 60 minutes).
            # -------------------------------------------------------------
            recent_conflict = False
            neg_recent_count = 0
            pos_recent_count = 0

            # Inspect up to 5 preceding turns in reverse order
            for past in reversed(message_history[max(0, idx - 5):idx]):
                if dt_curr and past.get("datetime"):
                    gap_mins = (dt_curr - past["datetime"]).total_seconds() / 60.0
                    # If the tension was more than 60 minutes ago, it has cooled down
                    if gap_mins > 60.0:
                        continue
                if past.get("is_conflict"):
                    recent_conflict = True
                    neg_recent_count += 1
                if past.get("is_positive"):
                    pos_recent_count += 1

            recent_sentiment = "negative" if neg_recent_count > pos_recent_count else ("positive" if pos_recent_count > 0 else "neutral")

            # 1. Response-Time Logic (9 AM - 5 PM Protection)
            if prev_msg:
                dt_prev = self.parse_msg_datetime(prev_msg.timestamp)
                if dt_curr and dt_prev:
                    time_gap_hours = (dt_curr - dt_prev).total_seconds() / 3600.0
                    start_hour = dt_prev.hour
                    is_work_hours = (9 <= start_hour < 17)
                    # Gaps during work hours (9 AM - 5 PM) are normal daytime autonomy: NEVER flag as apathy/disconnection
                    if not is_work_hours and time_gap_hours >= 4.0 and (18 <= start_hour <= 23):
                        # Flag only if prior message was an unresolved conflict or distress bid
                        if self._match_any(self.ANXIOUS_PATTERNS + self.CRITICISM_PATTERNS, prev_msg.message):
                            timeline_events.append(TimelineEvent(
                                timestamp=msg.timestamp or f"Turn #{idx+1}",
                                speaker=sender,
                                message=f"[Delayed response: {int(time_gap_hours)}h after evening conflict]",
                                sentiment_impact=-25,
                                label="Evening Communication Latency"
                            ))

            # 2. Check for Logistical Courtesy vs Conflict Repair
            is_logistical = self.is_logistical_apology(text)

            # 3. Criticism Check (protects positive absolutes)
            is_positive_absolute = self._match_any(self.POSITIVE_ABSOLUTE_PATTERNS, text)
            has_criticism = False
            if not is_positive_absolute:
                has_criticism = self._match_any(self.CRITICISM_PATTERNS, text)

            # 4. Other Gottman Markers
            has_contempt = self._match_any(self.CONTEMPT_PATTERNS, text)
            has_defensiveness = self._match_any(self.DEFENSIVENESS_PATTERNS, text)
            has_stonewalling = self.is_stonewalling(text, prev_msg, recent_conflict=recent_conflict)

            # 5. Attachment Tendencies
            has_anxious = self._match_any(self.ANXIOUS_PATTERNS, text) or (text.count("?") >= 3 and word_count < 10)
            has_avoidant = self._match_any(self.AVOIDANT_PATTERNS, text)

            # -------------------------------------------------------------
            # 6. Sarcasm / Contempt Override & Affection Bids
            # Gottman Rule: Contempt, insults ("useless", "poor baby"), and
            # criticism strictly OVERRIDE affection keywords.
            # -------------------------------------------------------------
            is_repair_candidate = self._match_any(self.REPAIR_PATTERNS, text) and not is_logistical

            has_repair = False
            has_affection = False

            if has_contempt or has_criticism:
                # Contempt / Criticism / Sarcasm strictly overrides any affection patterns
                has_affection = False
                has_repair = False
            elif is_repair_candidate and (recent_conflict or recent_sentiment == "negative"):
                # Active conflict context: Genuine Gottman Repair Attempt
                has_repair = True
                has_affection = False
            else:
                # Peaceful / Neutral context: Greetings, compliments, and courteous apologies
                has_repair = False
                has_affection = bool(
                    self._match_any(self.AFFECTION_PATTERNS, text) or
                    is_positive_absolute or
                    is_logistical or
                    is_repair_candidate
                )

            # Record occurrences in timeline (mutually exclusive)
            if has_criticism:
                stats[sender]["criticism"] += 1
                negative_events_count += 1
                timeline_events.append(TimelineEvent(
                    timestamp=msg.timestamp or f"Turn #{idx+1}",
                    speaker=sender,
                    message=text[:120],
                    sentiment_impact=-45,
                    label="Gottman Marker: Criticism & Global Blame"
                ))

            if has_contempt:
                stats[sender]["contempt"] += 1
                negative_events_count += 2  # Contempt is doubly corrosive
                timeline_events.append(TimelineEvent(
                    timestamp=msg.timestamp or f"Turn #{idx+1}",
                    speaker=sender,
                    message=text[:120],
                    sentiment_impact=-75,
                    label="Critical Marker: Contempt & Disdain"
                ))

            if has_defensiveness:
                stats[sender]["defensiveness"] += 1
                negative_events_count += 1
                timeline_events.append(TimelineEvent(
                    timestamp=msg.timestamp or f"Turn #{idx+1}",
                    speaker=sender,
                    message=text[:120],
                    sentiment_impact=-35,
                    label="Gottman Marker: Defensiveness & Deflection"
                ))

            if has_stonewalling:
                stats[sender]["stonewalling"] += 1
                negative_events_count += 1
                timeline_events.append(TimelineEvent(
                    timestamp=msg.timestamp or f"Turn #{idx+1}",
                    speaker=sender,
                    message=text[:120],
                    sentiment_impact=-40,
                    label="Gottman Marker: Stonewalling & Shutdown"
                ))

            repair_accepted = False
            if has_repair:
                stats[sender]["repairs"] += 1
                total_repairs += 1
                if next_msg:
                    next_text_lower = next_msg.message.lower()
                    if any(term in next_text_lower for term in ["thank", "okay", "ok", "fine", "hug", "love", "sorry", "appreciate", "agree", "alright", "no worries", "all good", "don't worry"]):
                        repair_accepted = True
                        accepted_repairs += 1

                if repair_accepted:
                    positive_events_count += 1
                    timeline_events.append(TimelineEvent(
                        timestamp=msg.timestamp or f"Turn #{idx+1}",
                        speaker=sender,
                        message=text[:120],
                        sentiment_impact=+60,
                        label="Successful Repair Attempt"
                    ))
                else:
                    timeline_events.append(TimelineEvent(
                        timestamp=msg.timestamp or f"Turn #{idx+1}",
                        speaker=sender,
                        message=text[:120],
                        sentiment_impact=+20,
                        label="De-escalation / Repair Attempt"
                    ))
            elif has_affection:
                stats[sender]["affection"] += 1
                positive_events_count += 1
                if not (has_criticism or has_contempt):
                    timeline_events.append(TimelineEvent(
                        timestamp=msg.timestamp or f"Turn #{idx+1}",
                        speaker=sender,
                        message=text[:120],
                        sentiment_impact=+55,
                        label="Bid for Connection & Affection"
                    ))

            if has_anxious:
                stats[sender]["anxious"] += 1

            if has_avoidant:
                stats[sender]["avoidant"] += 1

            # Update history tracker for subsequent message lookback
            is_this_conflict = bool(has_criticism or has_contempt or has_defensiveness or has_stonewalling)
            is_this_positive = bool(has_affection or (has_repair and repair_accepted))
            message_history.append({
                "idx": idx,
                "datetime": dt_curr,
                "is_conflict": is_this_conflict,
                "is_positive": is_this_positive
            })

        # Calculate Gottman Composite Scores (0 to 100 scale)
        total_msgs = max(len(messages), 1)
        tot_crit = stats[speaker_a]["criticism"] + stats[speaker_b]["criticism"]
        tot_cont = stats[speaker_a]["contempt"] + stats[speaker_b]["contempt"]
        tot_def = stats[speaker_a]["defensiveness"] + stats[speaker_b]["defensiveness"]
        tot_stone = stats[speaker_a]["stonewalling"] + stats[speaker_b]["stonewalling"]

        def calc_horseman_score(count, weight=1.0):
            if count == 0:
                return 0
            density = count / total_msgs
            raw_score = 35 + (density * 100 * weight)
            return min(100, int(raw_score))

        criticism_score = calc_horseman_score(tot_crit, 1.2)
        contempt_score = calc_horseman_score(tot_cont, 1.5)  # Contempt is the #1 predictor of relationship failure
        defensiveness_score = calc_horseman_score(tot_def, 1.2)
        stonewalling_score = calc_horseman_score(tot_stone, 1.2)

        # Positivity-to-Negativity Ratio (Gottman 5:1 metric)
        if negative_events_count == 0:
            ratio = 10.0 if positive_events_count > 0 else 5.0
        else:
            ratio = round(positive_events_count / max(negative_events_count, 1), 1)

        # Affection Levels per Person (Four Horsemen heavily deduct affection)
        def calc_person_affection(speaker):
            sp_data = stats[speaker]
            msgs = max(sp_data["msgs"], 1)
            crit = sp_data["criticism"]
            cont = sp_data["contempt"]
            defe = sp_data["defensiveness"]
            stone = sp_data["stonewalling"]
            aff = sp_data["affection"]

            total_horsemen = crit + cont + defe + stone
            if total_horsemen > 0:
                # Contempt carries a 30 pt deduction; criticism/defensiveness/stonewalling carry 22 pts each
                penalty = (cont * 30) + (crit * 22) + (defe * 22) + (stone * 22)
                base = 35 + int((aff / msgs) * 35)
                score = base - penalty
                return max(5, min(95, score))
            else:
                pos_ratio = aff / msgs
                score = 55 + int(pos_ratio * 40)
                return max(15, min(98, score))

        person_a_aff = calc_person_affection(speaker_a)
        person_b_aff = calc_person_affection(speaker_b)

        # Overall Toxicity (Strict zero-floor when no toxic markers are present)
        total_negative_markers = tot_crit + tot_cont + tot_def + tot_stone
        if total_negative_markers == 0:
            toxicity_score = max(0, min(8, 8 - min(positive_events_count, 8)))
        else:
            toxicity_raw = (contempt_score * 0.40) + (criticism_score * 0.25) + (defensiveness_score * 0.20) + (stonewalling_score * 0.15)
            # Severe conflict multipliers
            horsemen_types = sum(1 for s in [criticism_score, contempt_score, defensiveness_score, stonewalling_score] if s > 0)
            if horsemen_types >= 3:
                toxicity_raw += 20  # Compounding multi-horsemen penalty
            if tot_cont > 0:
                toxicity_raw += 15  # Contempt active poison penalty
            if ratio < 1.0:
                toxicity_raw += 15  # Negative affect dominance
            toxicity_score = int(max(0, min(100, toxicity_raw)))

        # Attachment Styles
        def determine_attachment(sp):
            anx = stats[sp]["anxious"]
            avd = stats[sp]["avoidant"]
            if anx > avd and anx >= 2:
                return "Anxious-Preoccupied (Pursuer tendency: hypervigilant check-ins, urgency for reassurance)"
            elif avd > anx and avd >= 2:
                return "Dismissive-Avoidant (Distancer tendency: deactivating, emotional minimization, withdrawal)"
            elif anx >= 2 and avd >= 2:
                return "Fearful-Avoidant (Disorganized: oscillating between seeking intimacy and pulling away)"
            return "Secure / Regulated (Communicates feelings directly without chronic protest or avoidance)"

        # Clinical Red Flags
        red_flags: List[str] = []
        if contempt_score > 0 or tot_cont > 0:
            red_flags.append(f"Severe Contempt Detected ({contempt_score}/100): Expressions of disgust, sarcasm, or mockery ('useless', 'poor baby') violate baseline relational safety.")
        if criticism_score >= 35:
            red_flags.append(f"Globalized Character Attacks ({criticism_score}/100): Disagreements frequently cross from specific requests into generalized blame ('you always', 'you never').")
        if stonewalling_score >= 30:
            red_flags.append(f"Emotional Stonewalling ({stonewalling_score}/100): One or both partners engage in monosyllabic shutdown or disengagement during conflict.")
        if defensiveness_score >= 30:
            red_flags.append(f"Chronic Defensiveness ({defensiveness_score}/100): Relational bids are met with counter-attacks, cross-complaining, or victimhood postures ('but sure, I'm the bad guy').")
        if ratio < 1.0 and total_negative_markers > 0:
            red_flags.append(f"Negative Affect Imbalance: The positive-to-negative interaction ratio is {ratio}:1, below the Gottman 5:1 stability threshold.")
        failed_repairs_count = total_repairs - accepted_repairs
        if total_repairs > 0 and failed_repairs_count > 0 and (accepted_repairs / total_repairs < 0.4):
            red_flags.append("Failed De-escalation: Attempts to apologize or de-escalate during tension were predominantly rebuffed or ignored.")

        # Clinical Green Flags
        green_flags: List[str] = []
        if person_a_aff >= 55 and person_b_aff >= 55:
            green_flags.append("Bidirectional Affection: Both partners frequently initiate bids for warmth, validation, and emotional connection.")
        if contempt_score == 0 and tot_cont == 0:
            green_flags.append("Mutual Respect: Sarcasm, sneering, and moral superiority are absent, preserving baseline safety.")
        if total_repairs > 0 and (accepted_repairs / total_repairs) >= 0.6:
            green_flags.append(f"Resilient Repair Capacity: {int((accepted_repairs / total_repairs) * 100)}% of de-escalation gestures were successfully received.")
        if ratio >= 4.0:
            green_flags.append(f"Abundant Positivity Buffer: Maintains a healthy ratio of {ratio}:1 positive interactions, providing emotional insulation.")
        if not green_flags:
            green_flags.append("Both participants maintain ongoing communication despite tension.")

        # Verdict Determination (Now supports 'Healthy' for secure, low-friction conversations)
        if toxicity_score <= 25 and contempt_score == 0 and criticism_score <= 20 and ratio >= 2.5:
            verdict = "Healthy"
        elif toxicity_score <= 50 and contempt_score < 35:
            verdict = "Repairable"
        elif toxicity_score <= 70 or contempt_score >= 35:
            verdict = "Critical"
        else:
            verdict = "Recommend Ending"

        # Generate Adaptive Blueprint (Routes to Healthy/Bonding OR Crisis/Repair)
        repair_blueprint = self._generate_repair_blueprint(
            criticism=criticism_score,
            contempt=contempt_score,
            defensiveness=defensiveness_score,
            stonewalling=stonewalling_score,
            toxicity_score=toxicity_score,
            ratio=ratio,
            speaker_a=speaker_a,
            speaker_b=speaker_b,
            stats=stats,
            style_a=determine_attachment(speaker_a),
            style_b=determine_attachment(speaker_b),
            total_repairs=total_repairs,
            accepted_repairs=accepted_repairs,
            verdict=verdict
        )

        # Build Actionable Advice mapped to the Blueprint
        advice = []
        if repair_blueprint["blueprint_type"] == "healthy_bond":
            advice.append(f"STRENGTH OF YOUR BOND: {repair_blueprint['brutal_truth_summary']}")
            advice.append(f"GROWTH PATH: {repair_blueprint['hopeful_path_summary']}")
            for person in repair_blueprint.get("person_diagnostics", []):
                advice.append(f"HABIT FOR {person['name'].upper()}: {person['action_plan']}")
            for proto in repair_blueprint.get("protocols", []):
                advice.append(f"{proto['title'].upper()}: {proto['action']} Try: \"{proto['script']}\"")
        else:
            advice.append(f"BRUTAL TRUTH: {repair_blueprint['brutal_truth_summary']}")
            advice.append(f"HOPEFUL PATH: {repair_blueprint['hopeful_path_summary']}")
            for person in repair_blueprint.get("person_diagnostics", []):
                advice.append(f"FOCUS FOR {person['name'].upper()}: {person['action_plan']}")
            for proto in repair_blueprint.get("protocols", []):
                advice.append(f"{proto['title'].upper()}: {proto['action']} Script to use: \"{proto['script']}\"")

        notes = (
            f"SPAFF Ratio: {ratio}:1. "
            f"Repairs: {accepted_repairs}/{total_repairs} accepted. "
            f"{speaker_a} style: {determine_attachment(speaker_a)}. "
            f"{speaker_b} style: {determine_attachment(speaker_b)}."
        )

        # Sort timeline events chronologically (up to 12 most salient)
        timeline_events = sorted(timeline_events, key=lambda x: x.timestamp)[:12]

        return {
            "toxicity_score": toxicity_score,
            "affection_levels": {
                "person_a": person_a_aff,
                "person_b": person_b_aff,
                speaker_a: person_a_aff,
                speaker_b: person_b_aff
            },
            "speaker_a": speaker_a,
            "speaker_b": speaker_b,
            "key_red_flags": red_flags if red_flags else ["Zero toxic communication patterns detected; interactions are constructive and secure."],
            "key_green_flags": green_flags,
            "verdict": verdict,
            "actionable_advice": advice,
            "gottman_breakdown": {
                "criticism_score": criticism_score,
                "contempt_score": contempt_score,
                "defensiveness_score": defensiveness_score,
                "stonewalling_score": stonewalling_score,
                "notes": notes
            },
            "timeline_events": [ev.model_dump() for ev in timeline_events],
            "repair_blueprint": repair_blueprint
        }

    def _generate_repair_blueprint(
        self,
        criticism: int,
        contempt: int,
        defensiveness: int,
        stonewalling: int,
        toxicity_score: int,
        ratio: float,
        speaker_a: str,
        speaker_b: str,
        stats: Dict[str, Dict[str, int]],
        style_a: str,
        style_b: str,
        total_repairs: int,
        accepted_repairs: int,
        verdict: str
    ) -> Dict[str, Any]:
        """
        Generates either:
        A) 'healthy_bond': Relationship Vitality & Proactive Connection Blueprint (for healthy chats)
        B) 'crisis_repair': Hopeful yet Brutally Honest Repair Blueprint (for conflict/crisis chats)
        """
        is_healthy = (verdict == "Healthy") or (toxicity_score <= 25 and contempt == 0 and criticism <= 20 and ratio >= 2.0)

        # ----------------------------------------------------
        # BRANCH A: HEALTHY & THRIVING RELATIONSHIP BLUEPRINT
        # ----------------------------------------------------
        if is_healthy:
            blueprint_type = "healthy_bond"
            headline = "Relationship Vitality & Connection Blueprint"

            bond_strength = (
                f"THE STRENGTH OF YOUR BOND: Baseline fondness, mutual respect, and emotional responsiveness between "
                f"{speaker_a} and {speaker_b} are exceptionally strong. Your conversation demonstrates a secure emotional connection "
                f"characterized by warmth, humor, and easy collaboration. Rather than resorting to character blame, contempt, or "
                f"defensiveness, your communication pattern fosters a calm, supportive environment where both partners feel valued."
            )

            growth_path = (
                f"THE PATH FORWARD (Cultivating Long-Term Vitality): You have established a resilient emotional foundation with an "
                f"abundant positivity buffer ({ratio}:1). In healthy relationships, the goal is intentional enrichment—maintaining "
                f"curiosity about each other's dreams, continuing everyday micro-bids for connection, and intentionally celebrating "
                f"shared wins to keep romantic vitality high."
            )

            def analyze_healthy_partner(sp: str, other: str, style: str) -> Dict[str, Any]:
                sp_stats = stats.get(sp, {})
                aff = sp_stats.get("affection", 0)
                return {
                    "name": sp,
                    "attachment_style": style,
                    "primary_issues": [
                        f"Maintains healthy, non-defensive communication boundaries with {other}.",
                        f"Demonstrates consistent emotional attunement and respectful engagement."
                    ],
                    "strengths": [
                        f"Regularly initiates bids for connection, humor, or logistical coordination ({aff} positive interactions).",
                        f"Consistently avoids contemptuous, sneering, or dismissive language toward {other}.",
                        f"Maintains dependable daytime and evening communication rhythms."
                    ],
                    "action_plan": (
                        f"Continue nurturing your emotional bond with {other} through unprompted daily appreciations "
                        f"and shared curiosity about their passions and personal goals."
                    )
                }

            person_diagnostics = [
                analyze_healthy_partner(speaker_a, speaker_b, style_a),
                analyze_healthy_partner(speaker_b, speaker_a, style_b)
            ]

            # Proactive Gottman Connection Rituals (Sound Relationship House)
            protocols = [
                {
                    "title": "The Daily Stress-Reducing Debrief",
                    "principle": "Empathy Before Advice (Gottman Magic 5 Hours)",
                    "action": f"Spend 15 minutes each evening debriefing each other's outside stressors without attempting to solve them or offer unsolicited critiques.",
                    "script": "How was the most challenging part of your day? Tell me about it—I'm in your corner.",
                    "rule": "Validate your partner's emotions before offering solutions or advice."
                },
                {
                    "title": "The Weekly State of the Union & Appreciation Ritual",
                    "principle": "Fondness & Admiration Building",
                    "action": f"Once a week, share five specific things you noticed and appreciated about each other before discussing logistics, schedules, or household chores.",
                    "script": "One thing you did this week that made me feel deeply loved and supported was [specific moment].",
                    "rule": "Express gratitude for who your partner is, not just what they did for you."
                },
                {
                    "title": "The 6-Second Reunion & Parting Habit",
                    "principle": "Micro-Bids for Physical & Emotional Connection",
                    "action": f"When parting in the morning or reuniting in the evening, engage in an intentional, unhurried 6-second physical embrace or warm greeting.",
                    "script": "I'm so glad to see you. How are you feeling right now?",
                    "rule": "Put down mobile devices and make eye contact during greetings and farewells."
                },
                {
                    "title": "Creating Shared Meaning & Joint Dreams Ritual",
                    "principle": "Shared Meaning System",
                    "action": f"Dedicate regular time between {speaker_a} and {speaker_b} to explore mutual aspirations, future trips, creative goals, and shared values.",
                    "script": "What is a dream or adventure you'd love for us to pursue together over the next year?",
                    "rule": "Support each other's personal aspirations as a shared team victory."
                }
            ]

            return {
                "blueprint_type": blueprint_type,
                "headline": headline,
                "brutal_truth_summary": bond_strength,
                "hopeful_path_summary": growth_path,
                "person_diagnostics": person_diagnostics,
                "protocols": protocols
            }

        # ----------------------------------------------------
        # BRANCH B: CRISIS / REPAIR RELATIONSHIP BLUEPRINT
        # ----------------------------------------------------
        blueprint_type = "crisis_repair"
        headline = "Relationship Repair Blueprint"

        def analyze_conflict_partner(sp: str, other: str, style: str) -> Dict[str, Any]:
            sp_stats = stats.get(sp, {})
            crit = sp_stats.get("criticism", 0)
            cont = sp_stats.get("contempt", 0)
            defe = sp_stats.get("defensiveness", 0)
            stone = sp_stats.get("stonewalling", 0)
            aff = sp_stats.get("affection", 0)
            rep = sp_stats.get("repairs", 0)
            anx = sp_stats.get("anxious", 0)
            avd = sp_stats.get("avoidant", 0)

            issues: List[str] = []
            if cont > 0:
                issues.append(f"Exhibiting Contempt & Disdain ({cont} instance{'s' if cont > 1 else ''}): Employs condescending, mocking, or sarcastic language that directly erodes emotional safety and humiliates {other}.")
            if crit > 0:
                issues.append(f"Globalized Character Attacks ({crit} instance{'s' if crit > 1 else ''}): Generalizes grievances into permanent personality defects ('you always', 'you never') instead of stating vulnerability.")
            if stone > 0:
                issues.append(f"Emotional Stonewalling & Shutdown ({stone} instance{'s' if stone > 1 else ''}): Retreats into icy silence, disengagement, or monosyllabic brush-offs ('k', 'whatever'), leaving {other} stranded in emotional panic.")
            if defe > 0:
                issues.append(f"Defensive Deflection & Posturing ({defe} instance{'s' if defe > 1 else ''}): Counter-attacks, makes excuses, or plays the victim when {other} raises an issue instead of validating their feelings.")
            if anx >= 2 and cont == 0 and crit == 0:
                issues.append(f"Anxious Escalation & Over-Pursuit: Interprets brief delays as emotional abandonment, bombarding {other} with frantic messages and demanding instant reassurance.")
            if avd >= 2 and stone == 0:
                issues.append(f"Avoidant Minimization: Shies away from emotional depth, downplaying {other}'s feelings to avoid vulnerability.")
            if not issues:
                issues.append(f"Displays regulated self-control during disputes, with no chronic toxic markers detected.")

            strengths: List[str] = []
            if aff > 0:
                strengths.append(f"Actively initiates warmth, affection, or bids for connection ({aff} positive bid{'s' if aff > 1 else ''}).")
            if rep > 0:
                strengths.append(f"Shows de-escalation maturity by initiating apologies or de-escalation gestures ({rep} repair attempt{'s' if rep > 1 else ''}).")
            if cont == 0:
                strengths.append(f"Maintains fundamental respect and refuses to use derogatory or contemptuous language toward {other}.")
            if not strengths:
                strengths.append(f"Demonstrates commitment by remaining in the dialogue despite relational tension.")

            if cont > 0:
                action_plan = f"{sp} must institute a zero-tolerance ban on sarcasm, eye-rolling, and mockery. When feeling frustrated with {other}, pause and name your core hurt instead of weaponizing disdain."
            elif crit > 0:
                action_plan = f"{sp} must adopt the Gentle Start-up protocol: replace 'You always' or 'Why do you' with 'I feel...' followed by a neutral description of the event and a specific, positive request."
            elif stone > 0:
                action_plan = f"{sp} must stop using silence as a weapon or shield. When flooded, say: 'I need a 20-minute breather, and I promise to return at [exact time] so we can talk calmly.' Never leave {other} in an emotional vacuum."
            elif defe > 0:
                action_plan = f"{sp} must implement the 2% Ownership Rule: before giving excuses or counter-attacking, acknowledge and validate at least 2% of truth in {other}'s grievance without saying 'BUT'."
            elif anx >= 2:
                action_plan = f"{sp} must practice physiological self-soothing: when {other} is slow to respond, wait 20 minutes before texting again, remembering that space is not abandonment."
            else:
                action_plan = f"{sp} should continue proactively building emotional safety by offering genuine, unprompted daily appreciations."

            return {
                "name": sp,
                "attachment_style": style,
                "primary_issues": issues,
                "strengths": strengths,
                "action_plan": action_plan
            }

        person_diagnostics = [
            analyze_conflict_partner(speaker_a, speaker_b, style_a),
            analyze_conflict_partner(speaker_b, speaker_a, style_b)
        ]

        crit_a = stats.get(speaker_a, {}).get("criticism", 0)
        crit_b = stats.get(speaker_b, {}).get("criticism", 0)
        stone_a = stats.get(speaker_a, {}).get("stonewalling", 0)
        stone_b = stats.get(speaker_b, {}).get("stonewalling", 0)
        cont_a = stats.get(speaker_a, {}).get("contempt", 0)
        cont_b = stats.get(speaker_b, {}).get("contempt", 0)
        defe_a = stats.get(speaker_a, {}).get("defensiveness", 0)
        defe_b = stats.get(speaker_b, {}).get("defensiveness", 0)

        brutal_truths = []
        if cont_a > 0 or cont_b > 0:
            cont_users = []
            if cont_a > 0:
                cont_users.append(f"{speaker_a} ({cont_a}x)")
            if cont_b > 0:
                cont_users.append(f"{speaker_b} ({cont_b}x)")
            brutal_truths.append(
                f"Contempt is actively poisoning this relationship, driven by {' and '.join(cont_users)}. Sarcasm, sneering, and eye-rolling phrases are not harmless banter—they are acts of psychological punishment. Love cannot survive when one partner looks down on the other from a moral pedestal."
            )

        if (crit_a > 0 and stone_b > 0) or (crit_b > 0 and stone_a > 0):
            pursuer = speaker_a if crit_a >= crit_b else speaker_b
            withdrawer = speaker_b if pursuer == speaker_a else speaker_a
            brutal_truths.append(
                f"{speaker_a} and {speaker_b} are caught in a classic Pursuer-Distancer spiral: {pursuer} unleashes character criticism ('you always', 'you never') when feeling neglected, which causes {withdrawer} to stonewall and shut down behind cold dismissals ('whatever', 'k'). That icy withdrawal then triggers panic in {pursuer}, who attacks even harder. Both of you are defending your egos while starving each other of emotional safety."
            )
        elif crit_a > 0 or crit_b > 0:
            crit_users = []
            if crit_a > 0:
                crit_users.append(f"{speaker_a} ({crit_a}x)")
            if crit_b > 0:
                crit_users.append(f"{speaker_b} ({crit_b}x)")
            brutal_truths.append(
                f"Conversations are turning into courtroom blame sessions driven by globalized character attacks from {' and '.join(crit_users)}. Attacking your partner's integrity forces them into defensive battle instead of listening to your pain."
            )

        if defe_a > 0 or defe_b > 0:
            defe_users = []
            if defe_a > 0:
                defe_users.append(f"{speaker_a} ({defe_a}x)")
            if defe_b > 0:
                defe_users.append(f"{speaker_b} ({defe_b}x)")
            brutal_truths.append(
                f"Accountability is repeatedly deflected through defensive justifications from {' and '.join(defe_users)}. Every time feedback is met with counter-attacks or excuses, genuine emotional repair is sabotaged."
            )

        total_markers = crit_a + crit_b + cont_a + cont_b + defe_a + defe_b + stone_a + stone_b
        if ratio < 2.0 and total_markers > 0:
            brutal_truths.append(
                f"The emotional bank account between {speaker_a} and {speaker_b} is critically depleted ({ratio}:1 positive-to-negative ratio). You cannot expect a relationship to withstand intense friction without consistent daily deposits of warmth, gratitude, and reassurance."
            )

        if not brutal_truths:
            brutal_truths.append(
                f"While baseline affection exists between {speaker_a} and {speaker_b}, subtle defensiveness and unexpressed resentments are slowly eroding your emotional safety if left unaddressed."
            )

        brutal_truth_summary = " ".join(brutal_truths)

        hopeful_path_summary = (
            f"Here is the profound reason for hope: The heated friction between {speaker_a} and {speaker_b} is not evidence that love is dead—it proves that both of you still care deeply enough to be hurt. The opposite of love is not anger; it is apathy. The emotional energy currently fueling your arguments can be immediately harnessed into passionate connection the moment both of you agree to lower your armor. Couples who master structured repair frequently forge deeper intimacy than couples who never disagree."
        )

        protocols = [
            {
                "title": "The 20-Minute Co-Regulation Ceasefire",
                "principle": "Physiological Self-Soothing (Antidote to Stonewalling & Flooding)",
                "action": f"When emotional friction spikes between {speaker_a} and {speaker_b}, either partner must call an immediate 20-minute pause. Do not pursue, multi-text, or slam doors.",
                "script": "I love you, but my nervous system is flooded right now and I don't want to say something hurtful. I need a 20-minute breather. I promise to return at [exact time] so we can talk calmly.",
                "rule": "The partner calling the timeout MUST be the one who initiates resuming at the promised time."
            },
            {
                "title": "The 2% Ownership Rule",
                "principle": "Taking Responsibility (Antidote to Defensiveness)",
                "action": f"In your next dispute between {speaker_a} and {speaker_b}, resist litigating the past. Even if your partner's complaint feels 98% exaggerated, find the 2% of truth in it and validate it first.",
                "script": "You are right about [specific action/omission]. I can see how that felt dismissive, and I own my part in that.",
                "rule": "Never follow up an apology with 'BUT you did...' That instantly erases the repair."
            },
            {
                "title": "The Gentle Start-up Protocol",
                "principle": "Softened Initiation (Antidote to Criticism)",
                "action": f"Ban accusatory 'You always' and 'Why do you' openings between {speaker_a} and {speaker_b}. State your raw emotion, describe the objective event neutrally, and state a positive need.",
                "script": "I feel [anxious / overwhelmed / lonely] about [specific neutral situation], and what I really need right now is [clear, positive request].",
                "rule": "State what you DO want, not what you DON'T want."
            },
            {
                "title": "The 14-Day Appreciation Transfusion",
                "principle": "Rebuilding the Gottman 5:1 Affect Ratio",
                "action": f"Commit to a 14-day zero-mockery contract between {speaker_a} and {speaker_b}. Every morning, unprovoked, send your partner one specific appreciation before discussing chores, work, or problems.",
                "script": "Hey, I noticed how hard you worked on [specific thing] yesterday. I really admire your dedication, and I am grateful for you.",
                "rule": "Appreciations must be specific to past actions, not generic compliments."
            }
        ]

        if "Anxious" in style_a or "Anxious" in style_b or "Avoidant" in style_a or "Avoidant" in style_b:
            pursuer_name = speaker_a if "Anxious" in style_a else speaker_b
            distancer_name = speaker_b if pursuer_name == speaker_a else speaker_a
            protocols.append({
                "title": "The Anxious-Avoidant Detente",
                "principle": "De-escalating the Pursuer-Distancer Loop",
                "action": f"For {pursuer_name}: Stop multi-texting and demanding immediate resolution; your barrage triggers emotional engulfment. For {distancer_name}: Stop using silence as a weapon; give verbal reassurance before stepping away.",
                "script": f"For {distancer_name}: 'I am not abandoning you or our bond. I just need 45 minutes to process, and I will text you at [time].' / For {pursuer_name}: 'I hear you need space. I will let you breathe and wait for your text.'",
                "rule": "Safety is created when distance is negotiated with a clock rather than an indefinite wall."
            })

        return {
            "blueprint_type": blueprint_type,
            "headline": headline,
            "brutal_truth_summary": brutal_truth_summary,
            "hopeful_path_summary": hopeful_path_summary,
            "person_diagnostics": person_diagnostics,
            "protocols": protocols
        }

    def _empty_result(self) -> Dict[str, Any]:
        return {
            "toxicity_score": 0,
            "affection_levels": {"person_a": 50, "person_b": 50},
            "speaker_a": "Person A",
            "speaker_b": "Person B",
            "key_red_flags": ["No conversation content available for analysis."],
            "key_green_flags": ["Dialogue is empty."],
            "verdict": "Healthy",
            "actionable_advice": ["Upload a chat export with active message history to generate metrics."],
            "gottman_breakdown": {
                "criticism_score": 0,
                "contempt_score": 0,
                "defensiveness_score": 0,
                "stonewalling_score": 0,
                "notes": "Empty transcript."
            },
            "timeline_events": [],
            "repair_blueprint": None
        }
