#!/usr/bin/env python3
"""Generate Nature Remo device-extension (BLE) macro XMLs for Yamaha SR-B20A.

Reverse-engineered from SoundBar Remote 2.50 (com.yamaha.ac.SBRemote):
- Service (advertised):  945ca2b0-852c-4ab8-b654-354df41c2795
- Write char:            0c50e7fa-594c-408b-a8d455b53b884b7c08  (WRITE_TYPE_NO_RESPONSE -> WRITE_COMMAND)
- Notify char:           5cafe9de-e7b0-4e0b-8fb9-2da91a7ae3ed  (app enables notify at connect; not needed per macro)
- Raw command table: wy enum (smali wy.smali) + volume-set [0x41, level 0-50] (hf3.smali BLE path)
- Framing (pg0.g): CC AA LEN PAYLOAD... CHECKSUM, CHECKSUM = (-(LEN + sum(bytes))) & 0xFF
"""
import os

SVC = "945ca2b0-852c-4ab8-b654-354df41c2795"
CHR = "0c50e7fa-594c-408b-a8d455b53b884b7c08"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sr-b20a")
RAW = "https://github.com/eraiza0816/sr-b20a-remo-macros/blob/main/sr-b20a"

CMDS = {  # name: (raw payload bytes, description)
    "power_on": ([0x40, 0x78, 0x7E], "Power ON"),
    "power_standby": ([0x40, 0x78, 0x7F], "Power STANDBY"),
    "input_tv": ([0x40, 0x78, 0xDF], "Input TV"),
    "input_optical": ([0x40, 0x78, 0x49], "Input Optical"),
    "input_bluetooth": ([0x40, 0x78, 0x29], "Input Bluetooth"),
    "input_hdmi": ([0x40, 0x78, 0x4A], "Input HDMI"),
    "input_analog": ([0x40, 0x78, 0xD1], "Input Analog"),
    "mute_on": ([0x40, 0x7E, 0xA2], "Mute ON"),
    "mute_off": ([0x40, 0x7E, 0xA3], "Mute OFF"),
    "volume_up": ([0x40, 0x78, 0x1E], "Volume +1"),
    "volume_down": ([0x40, 0x78, 0x1F], "Volume -1"),
    "clear_voice_on": ([0x40, 0x7E, 0x80], "Clear Voice ON"),
    "clear_voice_off": ([0x40, 0x7E, 0x82], "Clear Voice OFF"),
    "bass_ext_on": ([0x40, 0x78, 0x6E], "Bass Extension ON"),
    "bass_ext_off": ([0x40, 0x78, 0x6F], "Bass Extension OFF"),
    "surround_3d": ([0x40, 0x78, 0xC9], "3D Surround"),
    "surround_mode": ([0x40, 0x78, 0xB4], "Surround"),
    "surround_stereo": ([0x40, 0x78, 0x50], "Stereo"),
    "program_movie": ([0x40, 0x78, 0xD9], "Program Movie"),
    "program_game": ([0x40, 0x78, 0xDC], "Program Game"),
    "program_music": ([0x40, 0x78, 0xDA], "Program Music"),
    "program_standard": ([0x40, 0x7E, 0xF1], "Program Standard/TV"),
    "program_sport": ([0x40, 0x7E, 0xDB], "Program Sports"),
    "subwoofer_up": ([0x40, 0x78, 0x4C], "Subwoofer +1"),
    "subwoofer_down": ([0x40, 0x78, 0x4D], "Subwoofer -1"),
    "bass_up": ([0x40, 0x78, 0x53], "Tone Bass +1"),
    "bass_down": ([0x40, 0x78, 0x54], "Tone Bass -1"),
    "treble_up": ([0x40, 0x78, 0x55], "Tone Treble +1"),
    "treble_down": ([0x40, 0x78, 0x56], "Tone Treble -1"),
    "dimmer_bright": ([0x51, 0x00], "Dimmer Bright"),
    "dimmer_dark": ([0x51, 0x01], "Dimmer Dark"),
    "dimmer_off": ([0x51, 0x02], "Dimmer Off"),
}
# volume presets 0-50 step 5: raw = [0x41, level]
for lv in range(0, 51, 5):
    CMDS[f"volume_{lv:02d}"] = ([0x41, lv], f"Volume = {lv}")

TPL = """<macro name="{name}" icon="PLAY">
   <assert-service description="Ensure Yamaha soundbar service" uuid="{svc}">
      <assert-characteristic description="Ensure write characteristic" uuid="{chr}">
         <property name="WRITE_WITHOUT_RESPONSE" requirement="MANDATORY"/>
      </assert-characteristic>
   </assert-service>
   <write description="{desc}" characteristic-uuid="{chr}" service-uuid="{svc}" value="{val}" type="WRITE_COMMAND"/>
</macro>
"""


def frame(payload):
    s = len(payload) + sum(payload)
    chk = ((~s) + 1) & 0xFF
    return bytes([0xCC, 0xAA, len(payload)] + list(payload) + [chk])


rows = []
for name, (payload, desc) in CMDS.items():
    framed = frame(payload)
    val = "".join("%02X" % b for b in framed)
    with open(os.path.join(OUT, name + ".xml"), "w") as f:
        f.write(TPL.format(name=name, desc=desc, svc=SVC, chr=CHR, val=val))
    rows.append(f"| {name} | {desc} | `{val}` | {RAW}/{name}.xml |")

with open(os.path.join(OUT, "COMMANDS.md"), "w") as f:
    f.write("# YAMAHA SR-B20A BLE macros\n\n")
    f.write("service `945ca2b0-852c-4ab8-b654-354df41c2795`, write char "
            "`0c50e7fa-594c-408b-a8d455b53b884b7c08`, `WRITE_COMMAND`.\n\n")
    f.write("| file | function | framed write value | raw URL for Remo |\n|---|---|---|---|\n")
    f.write("\n".join(rows) + "\n")

print(f"wrote {len(CMDS)} xml + COMMANDS.md to {OUT}")
