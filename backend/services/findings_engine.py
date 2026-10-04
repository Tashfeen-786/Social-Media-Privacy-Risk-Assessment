"""
findings_engine.py
------------------
Turns detected risk flags into explainable privacy findings.

Every finding contains:
    category, severity, finding, explanation, recommended_action

Findings are purely defensive and educational. They describe *exposure*,
never how to exploit it.
"""

from typing import Any, Dict, List

from backend.models.categories import CATEGORIES

SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}


def _f(category, severity, finding, explanation, action, priority):
    return {"category": category, "severity": severity, "finding": finding,
            "explanation": explanation, "action": action, "priority": priority}


# finding_type -> metadata
FINDING_CATALOG: Dict[str, Dict[str, str]] = {
    # ---------------- Profile ------------------------------------------
    "public_profile": _f(
        "profile_exposure", "HIGH", "Profile is publicly visible",
        "A fully public profile lets anyone, including automated collectors, read "
        "your identity details and posts.",
        "Restrict your profile audience to connections only.", "IMPORTANT"),
    "public_profile_photo": _f(
        "profile_exposure", "MEDIUM", "Profile photo publicly visible",
        "Public profile photos are commonly copied to build impersonating accounts.",
        "Limit profile-photo visibility and enable profile-picture guard if available.",
        "GOOD PRACTICE"),
    "public_friend_list": _f(
        "profile_exposure", "MEDIUM", "Friends / followers list is public",
        "A public connection list reveals your social graph and makes impersonation "
        "attempts more believable.",
        "Set your friends / followers list to 'Only me' or 'Friends'.", "IMPORTANT"),
    "search_engine_indexed": _f(
        "profile_exposure", "MEDIUM", "Profile discoverable through search engines",
        "Search-engine indexing expands your digital footprint beyond the platform.",
        "Disable 'allow search engines outside the platform to link to your profile'.",
        "GOOD PRACTICE"),
    "activity_status_visible": _f(
        "profile_exposure", "LOW", "Activity status / last-seen visible",
        "Presence indicators reveal when you are online and can expose daily rhythms.",
        "Turn off activity status / last-seen indicators.", "GOOD PRACTICE"),

    # ---------------- Personal information ------------------------------
    "public_phone": _f(
        "personal_information", "CRITICAL", "Public phone number",
        "A publicly visible phone number can be used for spam, smishing and "
        "account-recovery abuse attempts.",
        "Limit phone-number visibility to 'Only me'.", "IMMEDIATE"),
    "public_email": _f(
        "personal_information", "HIGH", "Public e-mail address",
        "A public e-mail address increases phishing and credential-stuffing targeting.",
        "Hide your e-mail address from your public profile.", "IMMEDIATE"),
    "public_birthday": _f(
        "personal_information", "HIGH", "Public full birth date",
        "Full date of birth is a common identity-verification data point and supports "
        "identity fraud.",
        "Show only day/month, or hide the birth date entirely.", "IMMEDIATE"),
    "public_workplace": _f(
        "personal_information", "MEDIUM", "Workplace publicly visible",
        "Employer details make business-themed pretexting messages more convincing.",
        "Limit workplace visibility to connections.", "GOOD PRACTICE"),
    "public_education": _f(
        "personal_information", "LOW", "Education details publicly visible",
        "School / college details are frequently used as security-question answers.",
        "Restrict education details and never use them as security answers.",
        "GOOD PRACTICE"),
    "public_family": _f(
        "personal_information", "MEDIUM", "Family / relationship details public",
        "Named relatives are commonly referenced in 'emergency' scam messages to "
        "build trust.",
        "Hide family relationships and relationship status from public view.", "IMPORTANT"),

    # ---------------- Location -------------------------------------------
    "public_location": _f(
        "location_exposure", "HIGH", "Public location / home city",
        "Publicly visible location narrows you down geographically and supports "
        "localised scams.",
        "Limit current-city and hometown visibility.", "IMPORTANT"),
    "realtime_location": _f(
        "location_exposure", "CRITICAL", "Real-time location sharing / live check-ins",
        "Real-time location sharing can increase immediate location exposure and also "
        "signals absence from home.",
        "Review location-sharing settings and avoid unnecessary real-time location "
        "broadcasts; post after you leave.", "IMMEDIATE"),
    "travel_plans": _f(
        "location_exposure", "HIGH", "Travel plans posted publicly",
        "Announcing trips in advance signals that your home is empty and your routine "
        "has changed.",
        "Share trip content after returning and keep it to a limited audience.", "IMPORTANT"),
    "photo_geotags": _f(
        "location_exposure", "MEDIUM", "Automatic photo geotagging enabled",
        "Geotags attach precise coordinates to ordinary photos.",
        "Disable location tagging in the camera and platform settings.", "IMPORTANT"),
    "home_visible_photos": _f(
        "location_exposure", "MEDIUM", "Photos reveal home / street details",
        "House numbers, street signs and building fronts identify your residence "
        "without any metadata.",
        "Review and remove photos that show identifiable home details.", "GOOD PRACTICE"),
    "live_location_sharing": _f(
        "location_exposure", "HIGH", "Live location shared beyond close circle",
        "Continuous location sharing with a wide audience creates a long-term "
        "movement profile.",
        "Restrict live-location sharing to a small trusted list and set an expiry.",
        "IMMEDIATE"),
    "exif_not_stripped": _f(
        "location_exposure", "HIGH", "Photo metadata (EXIF) not removed before upload",
        "EXIF can embed camera/device identity, capture timestamps and GPS coordinates "
        "inside ordinary photos.",
        "Strip EXIF metadata before uploading, or use the local metadata viewer to "
        "create a sanitised copy.", "IMPORTANT"),

    # ---------------- Content --------------------------------------------
    "public_posts": _f(
        "content_exposure", "HIGH", "Posts are public by default",
        "Public posting makes every future post part of your permanent public footprint.",
        "Change the default post audience to 'Friends' and limit past posts.", "IMPORTANT"),
    "old_posts_not_reviewed": _f(
        "content_exposure", "MEDIUM", "Old public posts never reviewed",
        "Historic posts often contain contact details, addresses and context you would "
        "not publish today.",
        "Use the platform's bulk 'limit past posts' tool and review old content.",
        "IMPORTANT"),
    "document_photos": _f(
        "content_exposure", "CRITICAL", "Photos of documents / tickets posted",
        "Documents, tickets and IDs contain identifiers usable for identity fraud.",
        "Remove such posts and never publish document images.", "IMMEDIATE"),
    "routine_exposure": _f(
        "content_exposure", "MEDIUM", "Daily routine is inferable from posts",
        "Regular timing patterns reveal predictable physical movements (routine trails).",
        "Vary what you share and avoid posting fixed schedules publicly.", "GOOD PRACTICE"),
    "workplace_media": _f(
        "content_exposure", "HIGH", "Workplace / school badges, IDs or room details posted",
        "Badges, desks, floor and room numbers disclose physical access context about "
        "your workplace or school.",
        "Avoid posting badge, ID or entry details; keep work updates generic.", "IMPORTANT"),
    "child_media_public": _f(
        "content_exposure", "CRITICAL", "Photos/videos of children are publicly visible",
        "Publicly visible media of minors can be copied, re-contextualised and used to "
        "identify or approach a child.",
        "Make the account private or restrict the audience, and remove/blur children's "
        "faces in public media.", "IMMEDIATE"),
    "child_posts_public": _f(
        "content_exposure", "HIGH", "Posts mentioning children are publicly visible",
        "Details about a minor's activities and milestones build a public profile of "
        "someone who cannot consent.",
        "Limit the audience of posts that reference minors.", "IMMEDIATE"),
    "child_school_public": _f(
        "content_exposure", "CRITICAL", "School information involving minors is public",
        "School names, timings and routes combine into a predictable physical pattern "
        "for a child.",
        "Remove school identifiers, uniforms, timings and route details from public posts.",
        "IMMEDIATE"),

    # ---------------- Connections -----------------------------------------
    "unknown_connections": _f(
        "connection_risk", "HIGH", "Unknown connection requests accepted",
        "Unverified connections gain access to friends-only content and are a common "
        "first step in social-engineering attempts.",
        "Verify unfamiliar profiles before accepting; when in doubt, decline.", "IMMEDIATE"),
    "no_request_verification": _f(
        "connection_risk", "MEDIUM", "Connection requests not verified",
        "Without checking mutual contacts or account age, fake profiles are hard to spot.",
        "Check mutual friends, account age and post history before accepting.", "IMPORTANT"),
    "connections_not_reviewed": _f(
        "connection_risk", "LOW", "Connection list never reviewed",
        "Old or dormant connections may have been taken over.",
        "Periodically review and remove unknown or inactive connections.", "GOOD PRACTICE"),
    "open_dm": _f(
        "connection_risk", "MEDIUM", "Direct messages open to everyone",
        "Open inboxes are the main delivery channel for phishing and scam messages.",
        "Restrict message requests to connections or filter unknown senders.", "IMPORTANT"),
    "impersonation_seen": _f(
        "connection_risk", "HIGH", "Impersonating account observed",
        "Cloned profiles are used to contact your connections while pretending to be you.",
        "Report the duplicate account and warn your connections.", "IMMEDIATE"),

    # ---------------- Tagging ---------------------------------------------
    "tag_review_disabled": _f(
        "tagging_risk", "HIGH", "Tag review disabled",
        "Without tag review, others can attach your identity to content you never approved.",
        "Enable tag review where available.", "IMPORTANT"),
    "open_tagging": _f(
        "tagging_risk", "MEDIUM", "Anyone can tag you",
        "Open tagging lets strangers place your name on public content.",
        "Limit who can tag you to connections only.", "IMPORTANT"),
    "public_tagged_posts": _f(
        "tagging_risk", "MEDIUM", "Tagged posts publicly visible",
        "Tagged content you do not control becomes part of your public footprint.",
        "Limit the audience of posts you are tagged in.", "GOOD PRACTICE"),
    "open_mentions": _f(
        "tagging_risk", "LOW", "Unknown accounts can mention you",
        "Mentions from unknown accounts can associate your profile with unwanted content.",
        "Restrict who can @mention you to people you follow.", "GOOD PRACTICE"),

    # ---------------- Account security -------------------------------------
    "mfa_disabled": _f(
        "account_security", "CRITICAL", "Multi-factor authentication disabled",
        "Without MFA, a single leaked or guessed password is enough to take over the "
        "account, which then also exposes private content.",
        "Enable multi-factor authentication using the strongest supported method "
        "(authenticator app or security key).", "IMMEDIATE"),
    "login_alerts_disabled": _f(
        "account_security", "HIGH", "Login alerts disabled",
        "Login alerts are the fastest way to detect an unauthorised sign-in.",
        "Enable login / unrecognised-device alerts.", "IMPORTANT"),
    "password_reuse": _f(
        "account_security", "CRITICAL", "Password re-use reported",
        "Re-used passwords allow one unrelated website breach to affect your "
        "social-media account.",
        "Use a unique password per site, stored in a password manager.", "IMMEDIATE"),
    "sessions_not_reviewed": _f(
        "account_security", "MEDIUM", "Active sessions never reviewed",
        "Forgotten sessions on old devices remain logged in indefinitely.",
        "Review active sessions and sign out unknown devices.", "IMPORTANT"),
    "no_recovery_setup": _f(
        "account_security", "MEDIUM", "Account recovery not reviewed",
        "Without valid recovery options you may permanently lose access after an incident.",
        "Configure and review backup codes and a recovery contact.", "GOOD PRACTICE"),
    "no_password_manager": _f(
        "account_security", "LOW", "No password manager / weak password hygiene",
        "Memorised passwords tend to be short, patterned and re-used.",
        "Adopt a reputable password manager and generate unique passwords.", "GOOD PRACTICE"),

    # ---------------- Third-party apps ---------------------------------------
    "apps_not_reviewed": _f(
        "third_party_risk", "HIGH", "Third-party applications not reviewed",
        "Connected apps keep API access to your profile data long after you stop using "
        "them, breaking least privilege.",
        "Review and revoke unnecessary application access.", "IMPORTANT"),
    "social_login_used": _f(
        "third_party_risk", "MEDIUM", "Social login used widely",
        "Using one social account everywhere concentrates risk in a single identity "
        "provider.",
        "Prefer separate accounts with unique passwords for important services.",
        "GOOD PRACTICE"),
    "unused_apps_present": _f(
        "third_party_risk", "MEDIUM", "Unused app integrations still connected",
        "Dormant integrations violate least privilege and expand the attack surface.",
        "Remove integrations you no longer use.", "IMPORTANT"),
    "permissions_not_checked": _f(
        "third_party_risk", "LOW", "App permissions not reviewed before authorising",
        "Apps often request far more data than they need.",
        "Read requested scopes and grant the minimum required.", "GOOD PRACTICE"),

    # ---------------- Social engineering --------------------------------------
    "suspicious_links": _f(
        "social_engineering", "CRITICAL", "Links from unknown senders are clicked",
        "Unexpected links are the most common delivery route for credential-phishing "
        "pages.",
        "Do not open unexpected links; navigate to the site manually instead.", "IMMEDIATE"),
    "low_phishing_awareness": _f(
        "social_engineering", "HIGH", "Low phishing-recognition confidence",
        "Recognising pretexting and fake-support messages is the primary human control "
        "against social engineering.",
        "Complete a short phishing-awareness module and review the checklist.", "IMPORTANT"),
    "otp_shared": _f(
        "social_engineering", "CRITICAL", "Verification code (OTP) shared previously",
        "One-time codes are the last barrier protecting the account; sharing one "
        "defeats MFA entirely.",
        "Never share verification codes with anyone, including 'support'.", "IMMEDIATE"),
    "scam_engagement": _f(
        "social_engineering", "HIGH", "Engagement with giveaway / urgency scams",
        "Responding marks the account as reactive and invites further targeting.",
        "Ignore and report prize / urgency messages; never share personal details in DMs.",
        "IMPORTANT"),
    "no_out_of_band_verification": _f(
        "social_engineering", "MEDIUM", "Unusual requests not verified out-of-band",
        "Compromised accounts are used to message their own contacts.",
        "Confirm unusual requests by phone or in person before acting.", "IMPORTANT"),

    # ---------------- Digital footprint -----------------------------------------
    "footprint_unknown": _f(
        "digital_footprint", "MEDIUM", "Digital footprint never self-audited",
        "You cannot reduce exposure you have never measured.",
        "Search your own name and review what is publicly visible.", "IMPORTANT"),
    "abandoned_accounts": _f(
        "digital_footprint", "HIGH", "Abandoned public accounts still exist",
        "Unused accounts keep old data public and are rarely monitored for takeover.",
        "Close or secure unused accounts and delete their public content.", "IMPORTANT"),
    "privacy_settings_not_reviewed": _f(
        "digital_footprint", "HIGH", "Weak / unreviewed privacy settings",
        "Platforms change defaults over time; unreviewed settings drift towards more "
        "exposure.",
        "Run the platform privacy check-up at least every six months.", "IMPORTANT"),
    "handle_reuse": _f(
        "digital_footprint", "MEDIUM", "Same username re-used across platforms",
        "A unique handle links all your accounts into one correlated profile, which is "
        "the basis of handle-correlation risk.",
        "Use different handles for personal and public-facing accounts.", "GOOD PRACTICE"),
    "link_aggregator": _f(
        "digital_footprint", "MEDIUM", "Public link-in-bio aggregator in use",
        "Aggregator pages conveniently group all your identities for anyone who finds one.",
        "Review what the aggregator exposes and remove sensitive or personal links.",
        "IMPORTANT"),
    "linked_docs_pii": _f(
        "digital_footprint", "HIGH", "Linked pages / documents may contain personal details",
        "Public documents, spreadsheets and repositories frequently leak e-mail "
        "addresses, phone numbers and other identifiers.",
        "Review linked documents and repositories for contact details, secrets and "
        ".env files before sharing them.", "IMMEDIATE"),
    "tracker_awareness_low": _f(
        "digital_footprint", "LOW", "Third-party trackers on linked sites unknown",
        "Sites linked from your profile may load analytics or advertising trackers that "
        "profile your visitors and, by association, you.",
        "Check which third-party scripts your linked sites load and reduce them.",
        "GOOD PRACTICE"),
    "no_privacy_notice": _f(
        "digital_footprint", "LOW", "Linked personal site has no privacy / cookie notice",
        "A site you control that collects visitor data without notice is itself a "
        "privacy shortcoming.",
        "Add a short privacy and cookie notice to your personal site.", "GOOD PRACTICE"),
}


def generate_privacy_findings(features: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return the list of triggered findings, most severe first."""
    findings: List[Dict[str, Any]] = []
    for finding_type, triggered in features["flags"].items():
        if not triggered:
            continue
        meta = FINDING_CATALOG.get(finding_type)
        if not meta:
            continue
        findings.append({
            "finding_type": finding_type,
            "category": meta["category"],
            "category_label": CATEGORIES[meta["category"]],
            "severity": meta["severity"],
            "finding": meta["finding"],
            "explanation": meta["explanation"],
            "recommended_action": meta["action"],
        })
    findings.sort(key=lambda f: (SEVERITY_ORDER[f["severity"]], f["finding"]))
    return findings


__all__ = ["generate_privacy_findings", "FINDING_CATALOG", "SEVERITY_ORDER"]
