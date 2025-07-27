import argparse
import math
import string
import struct
import wave

SAMPLE_RATE = 44100  # Hertz
NOTE_SCALE = [
    261.63,  # C4
    293.66,  # D4
    329.63,  # E4
    349.23,  # F4
    392.00,  # G4
    440.00,  # A4
    493.88,  # B4
]

LETTER_TO_FREQ = {
    letter: NOTE_SCALE[i % len(NOTE_SCALE)] * (2 ** (i // len(NOTE_SCALE)))
    for i, letter in enumerate(string.ascii_lowercase)
}

def letter_wave(freq, duration=0.4):
    """Generate a list of samples for a sine wave of given frequency."""
    samples = []
    total = int(SAMPLE_RATE * duration)
    for i in range(total):
        value = 0.5 * math.sin(2 * math.pi * freq * i / SAMPLE_RATE)
        samples.append(value)
    return samples


def word_to_wave(word, output_file):
    """Convert the word into a simple tune saved as a wave file."""
    word = word.lower()
    samples = []
    for letter in word:
        freq = LETTER_TO_FREQ.get(letter)
        if freq:
            samples.extend(letter_wave(freq))
    with wave.open(output_file, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit audio
        wf.setframerate(SAMPLE_RATE)
        for s in samples:
            wf.writeframes(struct.pack("<h", int(s * 32767)))


def main():
    parser = argparse.ArgumentParser(description="Convert an English word to a simple music file.")
    parser.add_argument("word", help="The word to convert")
    parser.add_argument("-o", "--output", default="word.wav", help="Output wav filename")
    args = parser.parse_args()
    word_to_wave(args.word, args.output)
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
