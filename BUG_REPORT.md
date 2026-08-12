# Bug Report

I reviewed the transcripts and recordings from the 10 calls and pulled out the issues that seemed the most important. I focused on problems that could affect patient information or make it harder for someone to complete what they called for.

## Summary

| ID | Severity | Scenario | Issue | Evidence |
| --- | --- | --- | --- | --- |
| BUG-01 | High | Information Correction | Agent changes a correctly provided date of birth | 09_Information_Correction.txt at 18:55:17 |
| BUG-02 | High | Prescription Refill | Agent associates the caller with the wrong patient | 04_Prescription_Refill.txt at 18:41:49 |
| BUG-03 | High | Cancel Then Reconsider | Agent associates the caller with the wrong patient | 03_Cancel_Then_Reconsider.txt at 18:38:47 |
| BUG-04 | Medium | Hours and Location Info | Agent requires verification for basic public information | 05_Hours_Location_Info.txt at 18:43:15 |
| BUG-05 | High | Simple Scheduling | Scheduling cannot be completed after verification | 01_Simple_Scheduling.txt at 18:33:29 |

## BUG-01: Agent changes a correctly provided date of birth

**Severity:** High

**Call:** `artifacts/transcripts/09_Information_Correction.txt` at `18:55:17`

**What happened:** The patient gives their date of birth as April 12, 1988 and actually gives it twice. Later, the agent reads the DOB back as April 12, 1980. The patient then has to correct it again.

**Why it is a problem:** DOB is being used to verify the patient, so changing information that the patient already gave correctly could cause verification to fail or potentially pull up the wrong record.

**Expected behavior:** The agent should keep the DOB exactly as the patient provided it. If it is not sure what it heard, it should ask the patient to repeat it instead of changing the year.

**Reproduction:** Give the agent the name Morgan Davis and DOB April 12, 1988. Repeat the DOB when asked again, provide a phone number, and listen to how the agent reads the information back.

## BUG-02: Agent associates the caller with the wrong patient during a prescription refill

**Severity:** High

**Call:** `artifacts/transcripts/04_Prescription_Refill.txt` at `18:41:49`

**What happened:** The caller identifies themselves as Alex Morgan and provides a DOB and phone number. The agent confirms both pieces of information. After all of that, it asks, "Am I speaking with Maya?"

**Why it is a problem:** The agent had already collected and confirmed Alex's information. Mixing up identities during something like a prescription refill could cause the wrong patient record to be used.

**Expected behavior:** Once the caller has verified their identity, the agent should continue using that identity. If the phone number is connected to someone else, it should explain that there is a mismatch and ask the caller to clarify.

**Reproduction:** Start a prescription refill request as Alex Morgan, provide DOB 03/22/1975 and a phone number, and confirm the information when the agent reads it back.

## BUG-03: Wrong patient identity also happens during cancellation

**Severity:** High

**Call:** `artifacts/transcripts/03_Cancel_Then_Reconsider.txt` at `18:38:47`

**What happened:** The caller identifies herself as Priya Shah and provides her DOB and phone number. The agent confirms the information, but then asks if it is speaking with Maya. Priya has to correct the agent and tell it that she is Priya Shah.

**Why it is a problem:** This shows that the identity problem is not limited to one workflow. A patient should not have to correct the system about who they are after already going through verification.

**Expected behavior:** The agent should use the identity the caller just verified. If caller ID or another record conflicts with that information, it should explain the mismatch and ask which information is correct.

**Reproduction:** Start a cancellation request as Priya Shah, provide DOB April 7, 1991 and a phone number, and complete the verification steps.

## BUG-04: Agent requires patient verification for basic office information

**Severity:** Medium

**Call:** `artifacts/transcripts/05_Hours_Location_Info.txt` at `18:43:15`

**What happened:** The patient only asks for the office hours, address, and whether the office is open on Saturdays. Instead of answering those questions, the agent asks for the patient's DOB and starts a full verification process. It asks for the patient's name, spelling, and information again before eventually saying it cannot find the record and answering the general questions anyway.

**Why it is a problem:** Office hours and location are general information and should not require access to a patient record. The extra verification makes a simple call take much longer than it needs to.

**Expected behavior:** The agent should answer public information like office hours, address, and weekend availability without requiring patient verification.

**Reproduction:** Call and ask only for the office hours, address, and whether the office is open on Saturdays.

## BUG-05: Simple appointment scheduling cannot be completed after verification

**Severity:** High

**Call:** `artifacts/transcripts/01_Simple_Scheduling.txt` at `18:33:29`

**What happened:** The patient asks for the earliest routine appointment available after 2 PM the following Tuesday. The agent asks for the patient's name, DOB, spelling of the name, phone number, and confirmation of that information. After going through all of those steps, the agent says it cannot proceed and sends the patient to support instead of providing any appointment options.

**Why it is a problem:** The patient spends most of the call going through verification but still cannot complete the reason they called. It makes a basic scheduling workflow much longer without actually getting the appointment scheduled.

**Expected behavior:** Once the required information has been collected, the agent should provide available appointment times and continue with scheduling. If it cannot schedule the appointment, it should explain why earlier instead of taking the patient through the entire verification process first.

**Reproduction:** Ask for the earliest routine appointment after 2 PM next Tuesday and complete all of the verification steps requested by the agent.

## Quality observations that are not bugs

I noticed some smaller conversation quality issues that I would not consider major bugs. Some calls had longer pauses than I would expect in a normal phone conversation, and some of the verification steps felt repetitive when the patient had already given the same information.

During my earlier test calls, my patient simulator also sometimes responded too quickly or repeated its goal too often. I adjusted the patient prompt and turn taking behavior before running the final set of calls.