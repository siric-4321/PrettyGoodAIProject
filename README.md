# Pretty Good AI Voice Patient Simulator

For the Pretty Good AI AI Engineering Challenge, I built a Python voice agent that calls the assessment line and acts like a real patient interacting with the practice's AI receptionist.

The goal was not just to run scripted test cases. I wanted the patient agent to actually listen to what the receptionist said, respond naturally, and continue steering the conversation toward the goal of each scenario. The system records every call, saves both sides of the conversation as a transcript, and analyzes the completed call for potential issues.

## What I Built

The simulator:

* Calls only the Pretty Good AI assessment number, `+1-805-439-8008`
* Runs 10 different patient scenarios
* Uses Twilio ConversationRelay for the phone conversation, speech recognition, and speech synthesis
* Uses an OpenAI model to generate the patient's responses based on the conversation
* Records both sides of every call
* Saves the recordings as MP3 files
* Creates readable transcripts for each call
* Runs a post call analysis to help identify possible issues
* Hard locks the destination number so the runner cannot accidentally call another number

## How It Works

The system starts with `run.py`, which creates an outbound call through Twilio.

When the call connects, Twilio requests the `/voice` endpoint from my FastAPI server. That endpoint returns TwiML that connects the call to the `/ws` WebSocket using ConversationRelay.

ConversationRelay handles the speech recognition and speech synthesis. When the receptionist speaks, its speech is sent to my WebSocket as a prompt. `PatientAgent` receives that message along with the recent conversation and the instructions for the current scenario.

The OpenAI model then generates a short patient response. That response is sent back through ConversationRelay and spoken over the phone.

While the conversation is happening, `Transcript` records both the patient and receptionist turns. Twilio separately records the actual call and sends the recording back to `/recording-status` when it is ready.

After the conversation ends, `analyzer.py` reviews the transcript for possible QA issues.

I included more detail about my design decisions and tradeoffs in `ARCHITECTURE.md`.

## Setup

### 1. Requirements

You will need:

* Python 3.12 or later
* A Twilio account with a voice capable phone number
* An OpenAI API key
* ngrok or another HTTPS/WSS tunnel

Twilio ConversationRelay also needs to be enabled for the Twilio account.

### 2. Create the environment

```bash
python -m venv .venv