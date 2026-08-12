# Loom 1: Project Walkthrough, under 3 minutes

Hi, I built a patient simulator that automatically calls the Pretty Good AI assessment line and holds a goal directed voice conversation with the agent.

The main design decision was to optimize for the thing the rubric prioritizes first, coherent voice interaction. Twilio places the real PSTN call and ConversationRelay handles speech recognition and speech synthesis. My FastAPI WebSocket receives the practice agent's speech, sends the conversation plus a scenario specific patient goal to the model, and immediately returns the patient's next spoken turn.

I created ten scenarios that cover a baseline appointment, rescheduling, cancellation with a change of mind, refill workflows, office hours, insurance uncertainty, ambiguous dates, unclear request repair, self correction, and a multi intent call. I deliberately made the simulator goal directed instead of fully scripted, because I wanted it to adapt when the practice agent asks unexpected clarifying questions.

Every call creates two artifacts. First, Twilio records the real call in dual channel audio and my callback downloads the MP3. Second, ConversationRelay gives me the spoken text, so I write a readable transcript with both speakers. When the call ends, a separate QA pass identifies only substantive bugs and explains the evidence, impact, and expected behavior.

One tradeoff I made was not directly bridging raw telephony audio to a Realtime API. That could be a strong production architecture, but for a six hour assessment it adds codec and audio transport complexity. ConversationRelay let me spend the time on conversation quality, test design, and iteration. The first hardening steps I would add are WebSocket signature validation, latency metrics, and an explicit scenario completion state machine.

# Loom 2: AI Debugging Demo

Record a real debugging session. Do not pretend a prewritten bug happened. A good structure is:

1. Run one scenario and show the error or poor behavior.
2. Paste only the relevant traceback or transcript excerpt into the AI.
3. Ask: "Identify the smallest likely root cause. Do not rewrite the whole project. Tell me what evidence would confirm it."
4. After checking the evidence, ask: "Patch only the affected function and explain the tradeoff."
5. Apply the patch, rerun the same scenario, and compare the before and after result.

Useful real issues to debug if they occur: duplicate partial transcripts, latency from waiting for a full model response, TwiML attribute errors, recording callback timing, or the patient agent failing to steer back to its goal.
