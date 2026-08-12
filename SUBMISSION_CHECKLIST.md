# Submission Checklist

## Before running the calls

1. Create the Pretty Good AI test account for product context.
2. Do not call the number shown on the product confirmation screen.
3. Configure one Twilio phone number and use that same number for every assessment call.
4. Confirm `.env` contains the assessment number `+18054398008` unchanged.
5. Confirm `curl http://localhost:8000/health` returns `{"ok":true}`.
6. Run `pytest -q`.
7. Make one baseline call with `python run.py --scenario 01_simple_schedule`.

## Evidence of iteration

1. Listen to the baseline recording.
2. Read its transcript.
3. Identify one real weakness in the patient simulator.
4. Change the smallest relevant prompt or function.
5. Rerun the same scenario.
6. Write the before and after result in `ITERATION_NOTES.md`.
7. Use this real debugging sequence in the second Loom video.

## Final call set

1. Run `python run.py --all`.
2. Verify at least ten complete conversations exist.
3. Verify each final call is a meaningful conversation, not a single question and hang up.
4. Verify there are ten MP3 recordings in `artifacts/recordings/`.
5. Verify there are ten readable TXT transcripts in `artifacts/transcripts/`.
6. Open each recording and make sure both sides are audible.
7. Match recordings to transcripts using the Twilio Call SID.

## Bug report

1. Review every file in `artifacts/bug_reports/`.
2. Reject weak or speculative findings.
3. Copy only the strongest real issues into `BUG_REPORT.md`.
4. Add the exact transcript filename and timestamp for each issue.
5. Explain what happened, why it matters, and the expected behavior.

## GitHub

1. Make the repository public.
2. Do not commit `.env` or secrets.
3. Include working Python code.
4. Include README setup and run instructions.
5. Include `ARCHITECTURE.md`.
6. Include all final transcripts.
7. Include all final MP3 recordings.
8. Include the completed `BUG_REPORT.md`.
9. Add both public Loom links to the README.

## Loom videos

1. Project walkthrough is no longer than three minutes.
2. Webcam is on.
3. Use your own voice.
4. Explain what you built and why you chose the architecture.
5. Explain at least one tradeoff.
6. Show the ten scenarios and generated artifacts.
7. Record a second video showing a real AI assisted debugging cycle.

## Submission form

1. Public GitHub repository link.
2. Public project walkthrough Loom link.
3. Public AI debugging Loom link.
4. The exact one Twilio caller number in E.164 format.
5. Double check the caller number before submitting.
