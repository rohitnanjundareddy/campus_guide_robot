"""
Misty Enhanced Interactive Tour Guide
With engaging dialogue, multiple interaction points, AND non-verbal gestures
Single listening thread that pauses during robot speech
"""

from time import sleep
import time
import base64
import google.generativeai as genai
import tempfile
import os
from datetime import datetime
import json
import threading
import queue
from openai import OpenAI
from mistyPy.Robot import Robot


# ========================================================================
# ENHANCED TOUR GUIDE WITH GESTURES
# ========================================================================

class EnhancedMistyTourGuide:
    def __init__(self, misty_ip, gemini_api_key, openai_api_key):
        """Initialize Enhanced Tour Guide"""
        print("🔧 Initializing Misty...")

        # Use mistyPy Robot SDK
        self.misty = Robot(misty_ip)
        self.misty_ip = misty_ip
        self.gemini_api_key = gemini_api_key

        # Single listening thread
        self.listening_active = False
        self.listening_thread = None
        self.audio_counter = 0

        # Tour state flags
        self.start_tour = False
        self.destination_confirmed = False
        self.lets_start_confirmed = False
        self.waiting_for_snack_answer = False
        self.waiting_for_interest_answer = False

        # User responses storage
        self.user_snack_preference = None
        self.user_interest = None

        self.transcript_tilldate = []

        # Current location context
        self.current_location = "start"

        # Configure APIs
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.client = OpenAI(api_key=openai_api_key)

        print("✅ Enhanced Tour Guide initialized")

    # ========================================================================
    # MOVEMENT & GESTURE FUNCTIONS
    # ========================================================================

    def drive_forward(self, seconds=2.0, speed=120):
        """Drive straight forward"""
        print(f"🚗 Driving forward for {seconds}s at speed {speed}")
        ms = int(seconds * 1000)
        self.misty.drive_time(speed, 0, ms)
        time.sleep(seconds + 0.1)

    def turn_left_degrees(self, angle_degrees, speed=40):
        """Turn left by angle"""
        print(f"↰ Turning left {angle_degrees}°")
        DEGREES_PER_SEC_AT_40 = 90.0
        deg_per_sec = DEGREES_PER_SEC_AT_40 * (speed / 40.0)
        duration = angle_degrees / deg_per_sec
        ms = int(duration * 1000)
        self.misty.drive_time(0, speed, ms)
        time.sleep(duration + 0.1)

    def turn_right_degrees(self, angle_degrees, speed=40):
        """Turn right by angle"""
        print(f"↱ Turning right {angle_degrees}°")
        DEGREES_PER_SEC_AT_40 = 90.0
        deg_per_sec = DEGREES_PER_SEC_AT_40 * (speed / 40.0)
        duration = angle_degrees / deg_per_sec
        ms = int(duration * 1000)
        self.misty.drive_time(0, -speed, ms)
        time.sleep(duration + 0.1)

    def wave(self, times=3):
        """Wave arms"""
        print(f"👋 Waving {times} times")
        for i in range(times):
            self.misty.move_arms(70, 70, 100, 100)
            time.sleep(0.5)
            self.misty.move_arms(30, 30, 100, 100)
            time.sleep(0.5)
        self.misty.move_arms(0, 0, 50, 50)

    # ========== NON-VERBAL GESTURE FUNCTIONS ==========

    def head_center(self):
        """Reset head to center position"""
        print("📍 Centering head")
        self.misty.move_head(pitch=0, roll=0, yaw=0, velocity=100)

    def head_tilt_listening(self):
        """Tilt head to show listening - curious/attentive"""
        print("👂 Head tilt: listening mode")
        self.misty.move_head(pitch=10, roll=15, yaw=0, velocity=100)

    def head_move_up(self):
        """Move head up - curious/attentive"""
        print("👂 Head move up: listening mode")
        self.misty.move_head(pitch=-25, roll=15, yaw=0, velocity=100)

    def head_look_left(self):
        """Look to the left"""
        print("👀 Looking left")
        self.misty.move_head(pitch=0, roll=0, yaw=40, velocity=100)

    def head_look_right(self):
        """Look to the right"""
        print("👀 Looking right")
        self.misty.move_head(pitch=0, roll=0, yaw=-40, velocity=100)

    def point_left(self):
        """Point left arm to the left"""
        print("👈 Pointing left")
        self.misty.move_arms(leftArmPosition=-20, rightArmPosition=0,
                             leftArmVelocity=80, rightArmVelocity=50)
        time.sleep(1.5)
        self.misty.move_arms(0, 0, 50, 50)

    def point_right(self):
        """Point right arm to the right"""
        print("👉 Pointing right")
        self.misty.move_arms(leftArmPosition=0, rightArmPosition=-30,
                             leftArmVelocity=50, rightArmVelocity=100)
        time.sleep(1.5)
        self.misty.move_arms(0, 0, 50, 50)

    def gesture_ahead(self):
        """Gesture forward with both arms"""
        print("🫴 Gesturing ahead")
        self.misty.move_arms(45, 45, 80, 80)
        time.sleep(1.0)
        self.misty.move_arms(0, 0, 50, 50)

    # ========================================================================
    # WAVE HI FUNCTIONS
    # ========================================================================

    def wave_hi(self):
        """Wave hello gesture"""
        print("👋 Waving hi!")
        self.misty.move_arm("right", position=-90, velocity=50)
        time.sleep(0.5)

        for _ in range(3):
            self.misty.move_arm("right", position=-70, velocity=80)
            time.sleep(0.3)
            self.misty.move_arm("right", position=-90, velocity=80)
            time.sleep(0.3)

        self.misty.move_arm("right", position=0, velocity=50)

    def say_hi_with_wave(self):
        """Complete greeting with wave, expression, and sound"""
        print("🎉 Performing full greeting!")
        self.misty.display_image("e_Joy.jpg")
        self.misty.change_led(red=0, green=255, blue=0)
        self.misty.play_audio("s_Acceptance.wav")
        self.wave_hi()

    # ========================================================================
    # SPEAKING FUNCTION - PAUSES LISTENING
    # ========================================================================

    def speak(self, text):
        """Speak text and pause listening during speech"""
        print(f"\n🎙️ SPEAKING: '{text}'")

        # PAUSE LISTENING
        was_listening = self.listening_active
        if was_listening:

            print("   🔇 PAUSING listening for speech ")
            self.listening_active = False
            time.sleep(0.6)  # Let current recording complete
            print("   🔇 PAUSING listening for speech after  sleep")

        # SPEAK
        self.misty.speak(text)
        self.transcript_tilldate.append(f"robot: {text}")

        # Calculate speech duration
        speech_duration = len(text) * 0.05 + 2.5
        time.sleep(speech_duration)

        # RESUME LISTENING
        if was_listening:
            time.sleep(0.5)  # Extra buffer before resuming
            self.listening_active = True
            print("   🎧 RESUMING listening")

        print("   ✅ Speech complete\n")

    # ========================================================================
    # LISTENING THREAD
    # ========================================================================

    def _continuous_listening_loop(self):
        """Continuous listening and transcription - pauses when listening_active is False"""
        print("🎧 Listening thread STARTED")
        CHUNK_DURATION = 3

        while True:
            try:
                # Check if listening is active
                if not self.listening_active:
                    time.sleep(0.2)
                    continue

                self.audio_counter += 1
                audio_name = f"chunk_{self.audio_counter}.wav"

                # Record audio
                self.misty.start_recording_audio(audio_name)
                time.sleep(CHUNK_DURATION)
                self.misty.stop_recording_audio()
                time.sleep(0.3)

                # Download and transcribe
                resp = self.misty.get_audio_file(audio_name)
                if resp and resp.status_code == 200:
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                    temp_file.write(resp.content)
                    temp_file.close()
                    audio_path = temp_file.name

                    user_speech = self._transcribe(audio_path)
                    os.remove(audio_path)

                    if user_speech:
                        print(f"\n👂 HEARD: '{user_speech}'")
                        self.transcript_tilldate.append(f"user: {user_speech}")
                        user_lower = user_speech.lower()

                        # ===== INTERACTION FLOW =====

                        # Hello detection
                        if not self.destination_confirmed and any(word in user_lower for word in ["hello", "hi", "hey"]):
                            print("   🎯 HELLO detected!")
                            self.say_hi_with_wave()
                            self.head_tilt_listening()
                            self.head_center()
                            self.head_move_up()
                            self.speak("So, where would you like me to take you today?")
                            self.transcript_tilldate.append(f"robot: So, where would you like me to take you today?")
                            continue

                        # Destination selection
                        if not self.destination_confirmed:
                            if "sandbox" in user_lower:
                                print("   🎯 SANDBOX destination selected!")
                                self.destination_confirmed = True
                                self.gesture_ahead()
                                self.speak("The sandbox! Excellent choice! That's where all the cool robot testing happens. When you're ready to begin our adventure, just say let's go and we'll roll!")
                                self.transcript_tilldate.append(f"robo: So, The sandbox! Excellent choice! That's where all the cool robot testing happens. When you're ready to begin our adventure, just say let's go and we'll roll!")
                                continue

                        # Let's start trigger
                        if self.destination_confirmed and not self.lets_start_confirmed:
                            if "let's start" in user_lower or "lets start" in user_lower or "start" in user_lower or "go" in user_lower:
                                print("   🎯 LET'S START confirmed!")
                                self.lets_start_confirmed = True
                                self.start_tour = True
                                continue

                        # Snack preference response
                        if self.waiting_for_snack_answer:
                            print("   🎯 Received snack preference!")
                            self.user_snack_preference = user_speech
                            self.waiting_for_snack_answer = False
                            self.head_center()
                            snack_response = self._generate_snack_response(user_speech)
                            self.speak(snack_response)
                            continue

                        # Interest response
                        if self.waiting_for_interest_answer:
                            print("   🎯 Received field of interest!")
                            self.user_interest = user_speech
                            self.waiting_for_interest_answer = False
                            self.head_center()
                            interest_response = self._generate_interest_response(user_speech)
                            self.speak(interest_response)
                            continue

                        # General conversation
                        if len(user_speech.split()) > 2:
                            gpt_response = self._get_gpt_response(user_speech, self.transcript_tilldate)
                            print(f"   💬 Responding: '{gpt_response[:50]}...'")
                            self.speak(gpt_response)

            except Exception as e:
                print(f"⚠️ Listening error: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(1)

    def _transcribe(self, audio_path):
        """Transcribe audio using Google Speech API"""
        try:
            with open(audio_path, "rb") as f:
                audio_content = base64.b64encode(f.read()).decode('utf-8')

            url = f"https://speech.googleapis.com/v1/speech:recognize?key={self.gemini_api_key}"
            data = {
                "config": {
                    "encoding": "LINEAR16",
                    "languageCode": "en-US"
                },
                "audio": {"content": audio_content}
            }

            import requests
            response = requests.post(url, json=data)
            if response.status_code == 200:
                results = response.json()
                transcript = ""
                for result in results.get("results", []):
                    transcript += result["alternatives"][0]["transcript"]
                return transcript.strip()
            else:
                print(f"   ⚠️ Transcription API error: {response.status_code}")
        except Exception as e:
            print(f"   ⚠️ Transcription error: {e}")
        return None

    def _generate_snack_response(self, snack_preference):
        """Generate fun response about user's snack preference"""
        try:
            prompt = f"""You are Corrie, a friendly tour guide robot. The user just told you their favorite snack when they're busy is: "{snack_preference}"

Generate a SHORT, fun, enthusiastic response (1-2 sentences) that:
- Shows you relate to their choice
- Makes a light joke or fun comment about it
- Keeps the energy positive
- Do NOT use the word "Joe" in your response

Response:"""

            response = self.client.chat.completions.create(
                model="gpt-5.1-chat-latest",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except:
            return "Oh nice choice! I'd grab that too if I had hands!"

    def _generate_interest_response(self, interest):
        """Generate response about user's field of interest"""
        try:
            prompt = f"""You are Corrie, a tour guide robot. The user just told you their field of interest is: "{interest}"

Generate a SHORT, engaging response (1-2 sentences) that:
- Shows excitement about their interest
- Makes a brief connection to robotics or the lab
- Encourages their passion

Response:"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except:
            return "That's fantastic! We definitely have some exciting projects related to that here!"

    def _get_gpt_response(self, user_speech, transcriptions):
        """Get intelligent response from GPT"""
        try:
            location_info = {
                "start": "at the starting point",
                "moving_1": "moving through the hallway",
                "pantry": "near the pantry",
                "robotics_class": "near the robotics classroom",
                "reception": "at the reception area",
                "posters": "at the research poster display",
                "moving_final": "heading to the sandbox",
                "sandbox": "at the sandbox in the UIC Engineering Innovation Center"
            }

            context = location_info.get(self.current_location, "on tour")

            prompt = f"""You are Corrie, a tour guide robot currently {context}.

Visitor said: "{user_speech}"
Chat history: "{transcriptions}"
Give a SHORT, friendly response (1-2 sentences max).
Be helpful and conversational. Don't respond with hello or any greeting unless it is beginning of the conversation.
Detect whether the new message is robot self-echo by comparing with the last 2–3 outputs; if it matches robot speech/logs return '', otherwise give a normal human-focused response.
Response:"""

            response = self.client.chat.completions.create(
                model="gpt-5.1-chat-latest",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content

        except Exception as e:
            print(f"⚠️ GPT error: {e}")
            return "That's interesting! Let me continue showing you around."

    def start_listening_thread(self):
        """Start listening thread"""
        if not self.listening_active:
            self.listening_active = True
            self.listening_thread = threading.Thread(target=self._continuous_listening_loop)
            self.listening_thread.daemon = True
            self.listening_thread.start()
            print("✅ Listening thread started")

    def stop_listening_thread(self):
        """Stop listening thread"""
        self.listening_active = False
        if self.listening_thread:
            self.listening_thread.join(timeout=3)

    # ========================================================================
    # GREETING AND INITIALIZATION
    # ========================================================================

    def wait_for_tour_start(self):
        """Wait for complete interaction flow before tour starts"""
        print("\n" + "=" * 70)
        print("WAITING FOR INTERACTION FLOW")
        print("=" * 70)
        print("Step 1: Say 'hello' to activate")
        print("Step 2: Say destination (sandbox)")
        print("Step 3: Say 'let's start' to begin tour")
        print("=" * 70)

        self.speak("Hola! I'm Corrie, your tiny robot guide! How can I help you?")

        print("\n⏳ Waiting for interaction flow to complete...")
        while not self.start_tour:
            sleep(0.5)

        print("\n✅✅✅ TOUR IS STARTING NOW! ✅✅✅\n")
        self.head_center()
        self.speak("Fantastic! Let's begin our tour to the sandbox!")
        # time.sleep(2)
        return True

    # ========================================================================
    # EXECUTE ENHANCED INTERACTIVE TOUR WITH GESTURES
    # ========================================================================

    def execute_tour(self):
        """Execute tour with multiple engaging interaction points AND gestures"""
        print("\n" + "=" * 70)
        print("🎬 STARTING ENHANCED INTERACTIVE TOUR WITH GESTURES")
        print("=" * 70)

        # ===== MOVEMENT 1: Initial straight movement =====
        print("\n🚗 MOVING FORWARD - Initial segment")
        self.current_location = "moving_1"

        self.head_center()
        self.speak("Alright, here we go! Follow me down this hallway.")
        self.transcript_tilldate.append({f"role: robot: Alright, here we go! Follow me down this hallway."})

        self.gesture_ahead()
        self.drive_forward(5.0, speed=100)

        # ===== STOP 1: PANTRY (LEFT SIDE) =====
        print("\n📍 STOP 1: PANTRY")
        self.current_location = "pantry"

        self.misty.drive_time(0, 50, 2250)
        self.head_look_left()
        self.speak("Okay, on my left here, this is our pantry! It's basically snack central and the social hub of our building.")
        self.transcript_tilldate.append({f"role: robot: Okay, on my left here, this is our pantry! It's basically snack central and the social hub of our building."})

        time.sleep(1)

        self.head_tilt_listening()
        self.speak("Speaking of snacks, what do you like to grab when you're busy working or studying?")
        self.transcript_tilldate.append({f"role: robot: Speaking of snacks, what do you like to grab when you're busy working or studying?"})

        self.waiting_for_snack_answer = True
        print("   ⏳ Waiting for snack answer...")
        self.misty.drive_time(0, -50, 2250)
        while self.waiting_for_snack_answer:
            sleep(0.5)

        # time.sleep(1)

        # ===== MOVEMENT 2: Continue forward =====
        print("\n🚗 MOVING FORWARD - Second segment")
        self.head_center()
        self.speak("Let's keep moving forward!")
        self.transcript_tilldate.append(
            {f"role: robot: Let's keep moving forward!"})
        self.drive_forward(20, speed=100)
        self.drive_forward(4, speed=40)

        # ===== STOP 3: RECEPTION =====
        print("\n📍 STOP 3: RECEPTION")
        self.current_location = "reception"

        self.head_look_right()
        self.misty.drive_time(0, -45, 2250)
        self.speak("And here on my right is our reception desk! This is where Enrique usually holds down the fort.")
        self.transcript_tilldate.append(
            {f"role: robot: And here on my right is our reception desk! This is where Enrique usually holds down the fort."})
        
        # time.sleep(1)

        self.point_right()
        self.speak("If you ever need help finding a room, or just want a friendly chat, Enrique's your guy. He probably knows more about this building than the architects who designed it!")
        self.transcript_tilldate.append(
            {
                f"role: robot: If you ever need help finding a room, or just want a friendly chat, Enrique's your guy. He probably knows more about this building than the architects who designed it!"})
        self.misty.drive_time(0, 45, 2250)
        # time.sleep(1)

        # ===== MOVEMENT 3: Continue forward =====
        print("\n🚗 MOVING FORWARD - Third segment")
        self.head_center()
        self.speak("Onward we go!")
        self.transcript_tilldate.append(
            {
                f"role: robot:Onward we go!"})
        self.drive_forward(8, speed=100)

        # ===== TURNING POINT =====
        print("\n↱ TURNING RIGHT - 90 degrees")
        self.speak("Alright, now we're going to make a right turn here.")
        self.transcript_tilldate.append(
            {
                f"role: robot:Alright, now we're going to make a right turn here."})
        turn_ninety_ms = 4500
        self.misty.drive_time(0, -45, turn_ninety_ms)
        # time.sleep(8)
        self.drive_forward(6, speed=100)

        # ===== STOP 4: RESEARCH POSTERS =====
        print("\n📍 STOP 4: RESEARCH POSTERS")
        self.current_location = "posters"

        self.head_look_left()
        self.misty.drive_time(0, 45, 2250)
        # self.speak("On our left, these are research posters from the robotics lab.")

        self.point_left()
        self.speak("Check this out of your left! Professor Joe Michaelis' poster about getting humans to like learning with social robots. He's such a cool professor that even we robots signed up for his class and the students just think it's their idea!")
        self.transcript_tilldate.append(
            {
                f"role: robot:Check this out of your left! Professor Joe Michaelis' poster about getting humans to like learning with social robots. He's such a cool professor that even we robots signed up for his class and the students just think it's their idea!"})
        # time.sleep(0.5)
        self.misty.drive_time(0, -45, 2250)

        # self.misty.drive_time(0, 45, 2250)
        # time.sleep(5)

        # ===== FINAL MOVEMENT =====
        print("\n🚗 MOVING TO SANDBOX")
        self.current_location = "moving_final"

        self.head_center()
        self.speak("Almost there! The sandbox is just ahead.")
        self.transcript_tilldate.append(
            {
                f"role: robot:Almost there! The sandbox is just ahead."})
        self.gesture_ahead()
        self.drive_forward(23, speed=100)

        # ===== FINAL STOP: SANDBOX =====
        print("\n📍 FINAL DESTINATION: SANDBOX")
        self.current_location = "sandbox"
        self.misty.drive_time(0, 45, 4500)
        self.speak("And here we are! Welcome to the sandbox!")
        self.transcript_tilldate.append(
            {
                f"role: robot:And here we are! Welcome to the sandbox!"})
        time.sleep(1)

        # ===== CONCLUSION =====
        # self.speak("Well, that concludes our tour! I hope you enjoyed learning about our facility. Thanks for rolling with me today!")
        # time.sleep(1)

        self.wave(3)

        self.speak("See you around! Beep boop!")
        self.transcript_tilldate.append(
            {
                f"role: robot:See you around! Beep boop!"})

        print("\n" + "=" * 70)
        print("✅ TOUR COMPLETE!")
        print("=" * 70)

    # ========================================================================
    # MAIN RUNNER
    # ========================================================================

    def run(self):
        """Run complete enhanced tour"""
        print("\n" + "=" * 70)
        print("🤖 CORRIE ENHANCED INTERACTIVE TOUR GUIDE 🤖")
        print("=" * 70)

        try:
            print("🚀 Starting listening thread...")
            self.start_listening_thread()
            time.sleep(1)

            self.wait_for_tour_start()
            self.execute_tour()

        except KeyboardInterrupt:
            print("\n\n⚠️ Interrupted by user")
        except Exception as e:
            print(f"\n\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("\n🛑 Shutting down...")
            self.head_center()
            self.misty.move_arms(0, 0, 50, 50)
            self.stop_listening_thread()
            print("✅ System shutdown complete")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    MISTY_IP = "192.168.0.92"

    GOOGLE_API_KEY = ""
    OPENAI_API_KEY = ""

    tour = EnhancedMistyTourGuide(MISTY_IP, GOOGLE_API_KEY, OPENAI_API_KEY)
    tour.run()