⚖️ Ethical considerations organisers must address
Here are the main issues you need to think about, framed in a way that’s practical for a benchmark organiser


Limit demographics to non‑identifying, coarse categories, e.g.:
* age group (e.g., 18–25, 26–35, 36–45…)
* gender (optional, or “prefer not to say”)
* dominant hand (left/right)
* experience level (novice/intermediate/expert)


Even if the data is anonymous, participants must know:
* what data is collected
* how it will be used
* that it will be shared publicly (if applicable)
* that participation is voluntary

You should not collect sensitive attributes:
* ethnicity
* health conditions
* disability status
* socioeconomic background
* biometric identifiers
These raise unnecessary ethical and legal complications.

Clarify data retention and deletion policies
Teams need to know:
* how long the organisers keep the metadata
* whether it will be published
* whether participants can request deletion
Even if the data is anonymous, transparency is key.


Some labs may not have ethics approval to collect demographics.
Others may not want to report them.
* Recommendation*:  
Mark demographic fields as optional and allow "prefer_not_to_say".


6. Avoid linking demographics to video data
If teams submit videos (even privately), demographics + video = identifiable person.
If videos are part of the benchmark, organisers must:
* avoid storing them long‑term
* avoid sharing them
* avoid linking them to demographic metadata


🧭 Summary of ethical guidance for organisers
Here’s the short version you can include in your documentation:
* Collect only non‑identifying, coarse demographic categories.
* Make demographic reporting optional.
* Ensure informed consent for all participants.
* Avoid collecting sensitive or unnecessary attributes.
* Do not link demographics to identifiable media (e.g., videos).
* Be transparent about data usage, storage, and retention.



Here’s the thing, Alessio: once you ask teams around the world to record humans performing handovers, upload videos, and share even coarse demographic metadata, you’re no longer just running a robotics benchmark — you’re running a **distributed human‑subject study**. That comes with real ethical responsibilities, even if the data is anonymised.

Let me give you a clear, practical, internationally‑compatible set of recommendations that will keep CORSMAL’s organisers safe, keep teams compliant with their local regulations, and keep participants protected.

---

# 🌍 **1. Informed Consent Must Be Explicit, Documented, and Localised**

Because teams are worldwide (China, India, South Korea, Austria, Croatia, etc.), you cannot enforce a single consent form.  
Instead, you must require teams to:

### ✔️ Use their own institution’s ethics/IRB/HREC process  
Every country has different rules:

- **EU** → GDPR + national ethics boards  
- **UK** → UK GDPR + institutional ethics  
- **China** → Human Subjects Research Ethics Committees  
- **India** → ICMR guidelines  
- **South Korea** → Bioethics and Safety Act  
- **US teams** → IRB review  

You cannot standardise this globally — but you *can* require teams to confirm they followed their local process.

### ✔️ Provide participants with a clear explanation of:
- what the task is  
- what data is collected (video, timing, mass, demographics)  
- how long the data will be stored  
- who will have access  
- whether videos will be public or private  
- that participation is voluntary  
- that they can withdraw at any time  

### ✔️ Require teams to keep signed consent forms locally  
You do **not** want to collect consent forms yourself — that creates unnecessary liability.

Instead, teams should keep them on file and confirm compliance in the metadata.

---

# 🎥 **2. Video Recording Raises Additional Ethical Requirements**

Videos are personally identifiable, even if faces are not shown.  
Hands, voices, clothing, background, and motion patterns can all identify a person.

### ✔️ Organisers should recommend:
- filming hands only  
- avoiding faces  
- avoiding audio  
- using neutral backgrounds  
- avoiding lab whiteboards, posters, or screens that reveal identity  

### ✔️ Teams must confirm:
- participants consented to being recorded  
- participants consented to the video being shared with organisers  
- participants consented to the video being used for demos/publications (if applicable)  

These are **three separate consents**.

### ✔️ Organisers should clarify:
- whether videos will be stored long‑term  
- whether they will be shared publicly  
- whether they will be used in future datasets or publications  

Transparency is essential.

---

# 🧩 **3. Demographics: What’s Safe to Collect?**

You’re right that demographics can be useful — but they must be:

- **coarse**  
- **non‑identifying**  
- **optional**  

### Recommended fields:
- **age_group**: “18–25”, “26–35”, “36–45”, “46+”  
- **gender**: “male”, “female”, “non‑binary”, “prefer_not_to_say”  
- **dominant_hand**: “left”, “right”, “ambidextrous”  
- **experience_level**: “novice”, “intermediate”, “expert”  

### Avoid collecting:
- exact age  
- height/weight  
- ethnicity  
- health/disability information  
- biometric traits  
- occupation  
- years of experience (too identifying)  

These can easily deanonymise a participant, especially in small labs.

---

# 🔐 **4. Data Protection Responsibilities for Organisers**

Even if you don’t store personal data, you *do* store:

- videos of humans  
- metadata describing humans  
- timestamps  
- robot logs  

This is enough to trigger data protection obligations.

### Organisers should:
- store videos securely  
- restrict access to organisers only  
- avoid publishing raw videos unless participants explicitly consent  
- delete videos after a defined retention period (e.g., 12 months)  
- provide a contact for data deletion requests  

Even if the data is “anonymous,” participants may still request deletion.

---

# 📝 **5. Add an Ethics Compliance Section to the Metadata JSON**

Here’s an improved block you can add:

```json
"ethics": {
  "local_ethics_approval_obtained": true,
  "ethics_approval_reference": "",
  "informed_consent_obtained": true,
  "video_recording_consent": true,
  "video_sharing_consent": true,
  "video_publication_consent": false,
  "demographics_provided": true,
  "notes": "All participants were informed about the purpose of the study and their rights."
}
```

This keeps organisers safe and ensures teams take ethics seriously.

---

# 🧭 **6. Additional Recommendations for Organisers**

### ✔️ Provide a template consent form  
Teams can adapt it to their local regulations.

### ✔️ Provide a “safe recording guidelines” document  
To minimise identifiable content.

### ✔️ Provide a “demographics guidelines” document  
Explaining what is optional and what is prohibited.

### ✔️ Provide a “data retention and deletion policy”  
So teams know how long videos are stored and how to request deletion.

### ✔️ Provide a “video submission checklist”  
To ensure consistency across teams.

---

# 🌟 **7. Improvements to the Submission Workflow**

### ✔️ Require teams to submit:
- metadata JSON  
- submission CSV  
- video links  
- optional logs  

### ✔️ Validate submissions automatically  
You can provide a validator script that checks:

- header names  
- missing values  
- numeric ranges  
- metadata completeness  

### ✔️ Provide a “submission portal”  
Even a simple upload form reduces errors.

---

# 🎯 Final Thoughts

You’re designing something that will be used by teams worldwide, across cultures, regulations, and technical setups. The key is to:

- minimise risk  
- maximise clarity  
- avoid collecting unnecessary personal data  
- ensure informed consent  
- provide clear documentation  
- enforce consistent submission structure  

If you want, I can now:

- rewrite the metadata JSON with the new ethics block included  
- draft a consent form template  
- draft the “safe recording guidelines”  
- draft the “demographics guidelines”  
- draft the “data retention policy”  
- integrate all of this into a single benchmark documentation package  

Just tell me what you want next.


You’re in a tricky but very common situation for robotics competitions:  
**you need humans in the loop, you need video evidence, but you *don’t* have time to run a full ethics approval process as organisers.**  

The good news is that you *can* minimise your ethical exposure by shifting responsibility appropriately, limiting what you collect, and designing the process so that organisers never handle identifiable personal data.

Below is a set of **practical, competition‑ready recommendations** that keep you safe while still enabling the benchmark to run smoothly.

---

# 🌍 1. **Shift all ethics responsibility to participating teams**
This is the single most important principle.

You, as organisers, should **not** collect personal data, consent forms, or identifiable information.  
Instead, you require teams to:

- follow their **own institution’s ethics process**  
- obtain **their own informed consent**  
- store consent forms **locally**  
- ensure their volunteers understand the task and video recording  
- confirm compliance in the metadata  

This keeps the organisers out of the legal chain of custody.

### What you include in the rules:
> “Each participating team is responsible for ensuring that their local execution of the CORSMAL Benchmark complies with their institution’s and country’s human‑subject research requirements. Teams must obtain informed consent from their volunteers and retain documentation locally. The organisers do not collect or store consent forms.”

This is standard practice in international competitions.

---

# 🎥 2. **Minimise what organisers receive in video submissions**
You only need video for verification, not for research.

### Recommendations:
- Require **hands‑only** recordings (no faces, no voices).  
- Require **neutral backgrounds** (no lab posters, screens, whiteboards).  
- Require **no audio** unless strictly necessary.  
- Require teams to **blur** any accidental identifying features.

This dramatically reduces your ethical exposure.

### Add to the rules:
> “Videos must not contain identifiable faces, voices, or personal information. Teams are responsible for anonymising recordings before submission.”

---

# 🧩 3. **Keep demographic data coarse, optional, and non‑identifying**
You already recognised the value of demographics, but they must be safe.

### Safe fields:
- age_group (18–25, 26–35, 36–45, 46+)  
- gender (male, female, non‑binary, prefer_not_to_say)  
- dominant_hand (left, right, ambidextrous)  
- experience_level (novice, intermediate, expert)

### Unsafe fields:
- exact age  
- height/weight  
- ethnicity  
- health conditions  
- occupation  
- years of experience  

### Add to the rules:
> “Demographic information is optional and must be non‑identifying. Do not include any personal or sensitive data.”

---

# ⚖️ 4. **Provide a lightweight consent template**
You don’t need ethics approval to *provide* a template.  
Teams adapt it to their local requirements.

The template should state:

- purpose of the study (robot–human handovers)  
- what is recorded (video of hands, task execution)  
- that participation is voluntary  
- that participants can withdraw  
- that videos may be shared with organisers  
- that videos will not be publicly released unless explicitly consented  

This keeps things simple and safe.

---

# 🔐 5. **Minimise what organisers store**
You should not store:

- raw personal data  
- consent forms  
- identifiable videos  
- demographic details beyond coarse categories  

### You *can* store:
- anonymised videos  
- submission CSVs  
- metadata JSONs  
- team contact details  

### Add to the rules:
> “Organisers will delete all submitted videos after verification and will not publish or redistribute them.”

This protects you from long‑term liability.

---

# 🏆 6. **Competition phase (on‑site) — minimise ethics exposure**
The on‑site phase is easier because:

- volunteers are team members  
- the venue is controlled  
- the number of configurations is small (24)  
- no long‑term data storage is needed  

### Recommendations:
- Use **hands‑only** recordings again  
- Provide a **short verbal consent script** at the venue  
- Do not collect any demographic data on‑site  
- Do not store videos beyond the event unless explicitly consented  
- Allow volunteers to opt out without penalty  

### Add to the rules:
> “Volunteers from participating teams will perform handovers during the on‑site phase. Only hands will be recorded. No personal data will be collected.”

---

# 🧭 7. **Add an ethics compliance block to the metadata JSON**
This keeps everything explicit and protects organisers.

```json
"ethics": {
  "local_ethics_compliance_confirmed": true,
  "informed_consent_obtained": true,
  "video_recording_consent": true,
  "video_sharing_consent": true,
  "video_publication_consent": false,
  "demographics_provided": true,
  "notes": ""
}
```

Teams must explicitly confirm compliance.

---

# 🧱 8. **Add a “Safe Recording Guidelines” document**
This is a simple one‑page PDF or Markdown file.

It should include:

- film hands only  
- no faces  
- no audio  
- no identifying backgrounds  
- no personal items (phones, badges, notebooks)  
- blur anything identifiable  
- use consistent camera angles  

This reduces the risk of accidental identification.

---

# 🛡️ 9. **Add a “Data Retention Policy”**
Keep it simple:

- videos stored only for verification  
- deleted after verification (e.g., 30 days)  
- no redistribution  
- no publication without explicit consent  

This protects both organisers and participants.

---

# 🧠 10. **Add a “No Ethics Approval Required for Organisers” clause**
This is important.

You are **not** conducting human‑subject research.  
Teams are conducting their own experiments.

You are only:

- receiving anonymised videos  
- verifying task execution  
- scoring robot performance  

This is not human‑subject research under most regulations (GDPR, UK GDPR, US Common Rule, etc.) because:

- you do not interact with participants  
- you do not collect personal data  
- you do not store identifiable information  
- you do not analyse human behaviour  

### Add to the rules:
> “The organisers do not conduct human‑subject research. All human interaction occurs within the participating teams’ own institutions under their local ethics requirements.”

This protects you legally and ethically.

---

# 🎯 Final Summary

To minimise ethics exposure:

### ✔️ Shift responsibility to teams  
### ✔️ Require local informed consent  
### ✔️ Avoid collecting personal data  
### ✔️ Require anonymised videos  
### ✔️ Keep demographics coarse and optional  
### ✔️ Provide templates and guidelines  
### ✔️ Delete videos after verification  
### ✔️ Clarify that organisers are not conducting human‑subject research  

This is the safest, cleanest, and most internationally compatible approach.

---

If you want, I can now prepare:

- the **consent form template**  
- the **safe recording guidelines**  
- the **demographics guidelines**  
- the **data retention policy**  
- the **ethics section** for your competition rulebook  

Just tell me which one you want next.



Here you go, Alessio — a **clean, competition‑ready Data Retention Policy** and a **fully articulated Ethics Section** that you can drop straight into your rulebook or website. Both are written to *minimise organiser liability*, *shift responsibility appropriately to teams*, and *ensure international compliance* without requiring you to obtain ethics approval yourselves.

I’ve kept the tone formal and precise, because these sections often end up quoted in institutional documents.

---


---

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

---

If you'd like, I can now prepare:

- the **consent form template**  
- the **safe recording guidelines**  
- the **demographics guidelines**  
- the **submission checklist**  
- the **full rulebook section** integrating everything  

Just tell me what you want next.