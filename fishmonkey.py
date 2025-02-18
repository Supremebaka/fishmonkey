import os
import re
import sys
from pydub import AudioSegment
from tkinter import filedialog, Tk

# ? Folder with your 43 sound effects
SFX_FOLDER = os.path.expanduser("~/Downloads/fishmonkey/sfx_library")

# ? Full Sound Effect Map
SFX_MAP = {
    "vine boom": "1_VineBoom.mp3",
    "air horn": "2_AirHorn.mp3",
    "bruh 3 times": "3_Bruh3Times.mp3",
    "beep sound": "4_BeepSound.mp3",
    "disc rewind": "5_DiscRewind.mp3",
    "violin": "6_Violin.mp3",
    "tension": "7_Tension.mp3",
    "bell ding": "8_BellDing.mp3",
    "cartoon sound effect": "9_CartoonSoundEffect.mp3",
    "funny fart": "10_SoundFart.mp3",
    "ka-ching money": "11_KaChingMoney.mp3",
    "dramatic": "12_Dramatic.mp3",
    "birds chirping": "13_BirdsChirping.mp3",
    "crickets": "14_Crickets.mp3",
    "horror": "15_Horror.mp3",
    "thunder": "16_Thunder.mp3",
    "typing": "17_Typing.mp3",
    "honking car": "18_HonkingCar.mp3",
    "rattlesnake": "19_RattleSnake.mp3",
    "explosion": "20_Explosion.mp3",
    "riser": "21_Riser.mp3",
    "laser": "22_Laser.mp3",
    "camera picture": "23_CameraPicture.mp3",
    "coughing": "24_Coughing.mp3",
    "dj khaled another one": "25_DJKhaledAnotherOne.mp3",
    "audience clap": "26_AudienceClap.mp3",
    "breaking glass": "27_BreakingGlass.mp3",
    "woosh": "28_Woosh.mp3",
    "heartbeat": "29_Heartbeat.mp3",
    "trombone womp womp": "30_TromboneWompWomp.mp3",
    "low tape fade": "31_LowTapeFade.mp3",
    "material girl": "32_MaterialGurl.mp3",
    "oh no sound": "33_OhNoSound.mp3",
    "science woosh": "34_ScienceWoosh.mp3",
    "sad violin": "35_SadViolin.mp3",
    "broke boy funny": "36_BrokeBoyFunny.mp3",
    "drum roll": "37_DrumRoll.mp3",
    "druski i ain't playing": "38_DruskiIAintPlayin.mp3",
    "bang low bass": "39_BangLowBass.mp3",
    "low tape fade": "40_LowTapeFade.mp3",
    "another woosh": "41_AnotherWoosh.mp3",
    "cash register ding": "42_CashRegisterDing.mp3",
    "closing chime": "43_ClosingChime.mp3",
}

def welcome_message():
    """Displays instructions for how to use ChatGPT prompt and generate an SRT file."""
    print("\n" + "="*50)
    print("? **Welcome to FishMonkey - Automatic SFX Adder!** ?")
    print("="*50)
    print("\n**How to Use:**")
    print("1? **Copy the prompt below** and paste it into ChatGPT **with your script** to generate an SRT file.\n")
    print("""**ChatGPT Prompt**:
'Hey ChatGPT, analyze my script and generate an SRT file 
with timestamps where the following 43 sound effects should be added.
Overuse the sound effects to make it catchy for a TikTok video.
The available sounds are (list below).
Ensure timestamps use the format hh:mm:ss,mmm (e.g. 00:00:02,500).'
""")
    print("2? **Save the SRT file** ChatGPT gives you.")
    print("3? **Select that SRT file** when prompted by this script.")
    print("4? **FishMonkey** will create an MP3 with SFX at the correct timestamps.\n")
    print("Press ENTER when you're ready to select your SRT file.")
    input()

def select_srt_file():
    """Opens file dialog for user to select the SRT file."""
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select SRT File",
        filetypes=[("SRT Files", "*.srt")]
    )
    return file_path

def parse_srt(srt_file):
    """
    Reads the SRT file. Each block is typically:
    
    1
    00:00:02,500 --> 00:00:05,000
    [Sound Effect: vine boom]
    """
    with open(srt_file, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    sfx_timeline = []
    timestamp_pattern = re.compile(r"(\d{2}:\d{2}:\d{2},\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2},\d{3})")
    effect_pattern = re.compile(r"\[Sound Effect:\s*(.+?)\]", re.IGNORECASE)

    i = 0
    while i < len(lines):
        # Skip blank lines or numeric lines
        if not lines[i].strip() or lines[i].strip().isdigit():
            i += 1
            continue

        # Attempt to match the timestamp line
        match_ts = timestamp_pattern.search(lines[i])
        if match_ts:
            start_ts = match_ts.group(1)  # e.g. "00:00:02,500"
            # Convert to seconds
            start_ts = start_ts.replace(",", ".")  # "00:00:02.500"
            h, m, s = start_ts.split(":")
            s = float(s)  # s might be "02.500"
            m = float(m)
            h = float(h)
            total_seconds = h*3600 + m*60 + s

            # Next line(s) might contain the effect
            if i+1 < len(lines):
                effect_line = lines[i+1].strip()
                effect_match = effect_pattern.search(effect_line)
                if effect_match:
                    effect_name = effect_match.group(1).lower().strip()
                    if effect_name in SFX_MAP:
                        sfx_timeline.append({"timestamp": total_seconds, "sfx": effect_name})

            i += 2
        else:
            i += 1

    return sfx_timeline

def process_sfx(sfx_timeline, output_audio="final_sfx_audio.mp3"):
    """
    Create a silent track based on the highest timestamp
    and overlay each sound effect at its correct position.
    """
    if not sfx_timeline:
        print("? No SFX found in the SRT file. Exiting.")
        return

    max_time = max(s["timestamp"] for s in sfx_timeline) + 5
    base_audio = AudioSegment.silent(duration=int(max_time*1000))

    for entry in sfx_timeline:
        t_ms = int(entry["timestamp"] * 1000)
        effect = entry["sfx"]
        sfx_path = os.path.join(SFX_FOLDER, SFX_MAP[effect])
        if os.path.exists(sfx_path):
            sfx_audio = AudioSegment.from_mp3(sfx_path)
            base_audio = base_audio.overlay(sfx_audio, position=t_ms)
            print(f"? Added '{effect}' at {entry['timestamp']}s")
        else:
            print(f"? Missing SFX file: {sfx_path}")

    base_audio.export(output_audio, format="mp3")
    print(f"? Final audio saved as {output_audio}")

def main():
    print("\n=== FishMonkey: SRT to MP3 SFX Adder ===\n")
    welcome_message()

    srt_file = select_srt_file()
    if not srt_file:
        print("? No SRT file selected. Exiting.")
        sys.exit(1)

    # Parse the SRT to build a timeline
    sfx_timeline = parse_srt(srt_file)

    # Create final MP3
    process_sfx(sfx_timeline, "final_sfx_audio.mp3")

if __name__ == "__main__":
    main()
