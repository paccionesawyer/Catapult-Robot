import random
import time

import speech_recognition as sr

class SpeechRecognizer:
    
    def __init__(self):
        # create recognizer and mic instances
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # adjust the recognizer sensitivity to ambient noise and record audio
        # from the microphone
        with self.microphone as source:
            print("Adjusting Recognizer for Ambient Noise")
            self.recognizer.adjust_for_ambient_noise(source)
            self.audio = self.recognizer.listen(source)

        self.passWords = ["ball"]

    def recognize_speech_from_mic(self):
        """Transcribe speech from recorded from `microphone`.

        Returns a dictionary with three keys:
        "success": a boolean indicating whether or not the API request was
                    successful
        "error":   `None` if no error occured, otherwise a string containing
                    an error message if the API could not be reached or
                    speech was unrecognizable
        "transcription": `None` if speech could not be transcribed,
                    otherwise a string containing the transcribed text
        """
        print("trying to recognize speech")
        # check that recognizer and microphone arguments are appropriate type
        if not isinstance(self.recognizer, sr.Recognizer):
            raise TypeError("`recognizer` must be `Recognizer` instance")

        if not isinstance(self.microphone, sr.Microphone):
            raise TypeError("`microphone` must be `Microphone` instance")

        # set up the response object
        response = {
            "success": True,
            "error": None,
            "transcription": None
        }

        
        with self.microphone as source:
            audio = self.recognizer.listen(source)

        # try recognizing the speech in the recording
        # if a RequestError or UnknownValueError exception is caught,
        #     update the response object accordingly
        try:
            response["transcription"] = self.recognizer.recognize_google(audio)
        except sr.RequestError:
            # API was unreachable or unresponsive
            response["success"] = False
            response["error"] = "API unavailable"
        except sr.UnknownValueError:
            # speech was unintelligible
            response["error"] = "Unable to recognize speech"

        return response

    def checkResponse(self, response):
        if response in self.passWords:
            return True

if __name__ == "__main__":
    test = SpeechRecognizer()
    response = test.recognize_speech_from_mic()
    print(response)