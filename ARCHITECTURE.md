# Architecture

I built the system around Twilio Programmable Voice, ConversationRelay, FastAPI, and OpenAI. `run.py` starts the outbound call from my Twilio number to the Pretty Good AI assessment line. I hard coded the assessment number and also validate it in the configuration so the program cannot accidentally call a different number.

Once the call connects, Twilio sends a request to my FastAPI `/voice` endpoint. The server returns TwiML that starts ConversationRelay and connects it to my `/ws` WebSocket. ConversationRelay handles speech recognition and text to speech, while my Python code controls how the simulated patient responds.

Each test scenario has its own patient persona, goal, opening line, and edge behavior. When the receptionist speaks, the transcribed message is sent through the WebSocket to `PatientAgent`. The agent uses the scenario instructions and recent conversation history to decide what the patient should say next. I intentionally keep the responses short because during my early tests I found that longer responses made interruptions and awkward turn taking much more common.

While the call is running, I save both sides of the conversation to a transcript. Twilio also records the actual phone call and sends a callback to my server when the recording is ready, which I download as an MP3. After the call ends, I run a separate analysis over the transcript to look for possible QA issues. I still manually reviewed the transcripts and recordings before deciding which issues to include in my final bug report.

## Why I Chose This Approach

I chose ConversationRelay instead of sending raw phone audio directly to a realtime model because I wanted to spend most of the challenge working on the patient behavior and testing rather than building the audio pipeline itself.

ConversationRelay handles the speech recognition, speech synthesis, and phone audio layer for me, while I still control the actual conversation logic through the WebSocket. This also made debugging easier because I could see the receptionist's transcribed message, the patient response, and the final transcript separately.

I considered using a direct Realtime API connection, which could potentially reduce some latency and give more control over the audio. The tradeoff is that I would also have to handle more of the audio streaming, codec, timing, and transcription logic myself. For a six hour challenge, I thought ConversationRelay was the better tradeoff because it let me get to real phone calls faster and spend more time actually listening to and improving them.

My first few calls also changed how I designed the final version. The patient initially responded too early in some conversations and sometimes repeated the scenario goal too aggressively. After listening to those calls, I adjusted the turn taking logic and patient instructions and reran the scenario until the conversation was more natural. This is also why I kept the conversation history available to the patient agent instead of treating every receptionist message independently.

For a production version, I would add Twilio signature validation, authentication around operational endpoints, structured latency monitoring, and stronger handling for stored recordings. I would also replace the natural end of conversation detection with a more explicit state machine or tool based approach so the system has a clearer definition of when each scenario has actually been completed.