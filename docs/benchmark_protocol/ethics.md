# 🧭 **ETHICS SECTION (for CORSMAL Competition Track)**

## **1. Overview**
The CORSMAL Competition Track involves human–robot handovers performed by volunteers recruited by participating teams (qualification phase) and by volunteers from other teams (competition phase). Although humans are involved in the execution of the benchmark, the organisers do **not** conduct human‑subject research and do **not** interact with participants directly.

All human interaction occurs within the participating teams’ own institutions or at the competition venue.

---

## **2. Ethical Responsibilities of Participating Teams**
Each team is fully responsible for ensuring that their local execution of the benchmark complies with:
- their institution’s ethics or IRB/HREC requirements  
- their country’s human‑subject research regulations  
- informed consent standards  
- data protection laws (e.g., GDPR, UK GDPR, CCPA, PIPL, etc.)

Teams must:
- obtain informed consent from all volunteers  
- explain the purpose of the task and the nature of the recordings  
- inform volunteers that participation is voluntary and can be withdrawn  
- anonymise all recordings before submission  
- retain consent documentation locally  

The organisers do **not** collect or store consent forms.

---

## **3. Informed Consent Requirements**
Teams must ensure that volunteers understand:
- the purpose of the handover task  
- that their hands will be recorded on video  
- that videos will be shared with organisers for verification  
- that videos will not be published without explicit consent  
- that they may withdraw at any time  
- that no personal data will be collected or stored  

A lightweight consent template will be provided for teams to adapt to their local regulations.

---

## **4. Anonymisation Requirements**
To minimise ethical and legal risks, teams must ensure that:
- only hands are visible in the recordings  
- no faces, voices, or identifying features appear  
- backgrounds do not reveal personal or institutional information  
- any accidental identifying content is blurred before submission  

Failure to anonymise recordings may result in disqualification.

---

## **5. Demographic Information**
Teams may optionally provide **coarse, non‑identifying demographics** for each volunteer:
- age group (e.g., 18–25, 26–35, 36–45, 46+)  
- gender (male, female, non‑binary, prefer_not_to_say)  
- dominant hand (left, right, ambidextrous)  
- experience level (novice, intermediate, expert)

Teams must **not** provide:
- exact age  
- ethnicity  
- health information  
- biometric data  
- occupation  
- any sensitive or identifying attributes  

Demographic data is used only for aggregate analysis and reproducibility.

---

## **6. Ethics for the On‑Site Competition Phase**
During the on‑site phase:
- volunteers are members of participating teams  
- only hands will be recorded  
- no personal data will be collected  
- no demographic data will be requested  
- a short verbal consent script will be used  
- videos will be anonymised and deleted after verification  

This phase does not constitute human‑subject research.

---

## **7. Organisers’ Ethical Position**
The organisers:
- do not conduct human‑subject research  
- do not collect personal data  
- do not store identifiable information  
- do not analyse human behaviour  
- only verify robot performance and task execution  

All ethical responsibility for human participation lies with the participating teams.

---

## **8. Compliance Confirmation**
Teams must confirm in their metadata JSON:

- `local_ethics_compliance_confirmed`  
- `informed_consent_obtained`  
- `video_recording_consent`  
- `video_sharing_consent`  
- `video_publication_consent` (optional)  
- `demographics_provided`  

This confirmation is required for a valid submission.
