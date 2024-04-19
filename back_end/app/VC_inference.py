import sys

# sys.path.append("VITS_files")

import os
import numpy as np
import torch
from torch import no_grad, LongTensor
from .VITS_files import commons
# from mel_processing import spectrogram_torch
from .VITS_files import utils
from .VITS_files.models import SynthesizerTrn
# import gradio as gr
import librosa
import webbrowser
import soundfile as sf # add
import wave
import subprocess

from .VITS_files.text import text_to_sequence, _clean_text
device = "cuda:0" if torch.cuda.is_available() else "cpu"
# import logging
# logging.getLogger("PIL").setLevel(logging.WARNING)
# logging.getLogger("urllib3").setLevel(logging.WARNING)
# logging.getLogger("markdown_it").setLevel(logging.WARNING)
# logging.getLogger("httpx").setLevel(logging.WARNING)
# logging.getLogger("asyncio").setLevel(logging.WARNING)

language_marks = {
    "Japanese": "",
    "日本語": "[JA]",
    "简体中文": "[ZH]",
    "English": "[EN]",
    "Mix": "",
}
lang = ['日本語', '简体中文', 'English', 'Mix']

def create_empty_wav(filename, sample_rate=44100, num_channels=1):
    """
    Create an empty WAV file with the given filename, duration, sample rate, and number of channels.

    Args:
    - filename (str): The filename of the WAV file to create.
    - duration (float): The duration of the empty WAV file in seconds.
    - sample_rate (int): The sample rate of the WAV file (default is 44100 Hz).
    - num_channels (int): The number of audio channels (default is 1 for mono).

    Returns:
    - None
    """
    # Open the WAV file for writing
    with wave.open(filename, 'w') as wf:
        # Set parameters for the WAV file
        wf.setnchannels(num_channels)
        wf.setsampwidth(2)  # 2 bytes per sample for 16-bit audio
        wf.setframerate(sample_rate)
        wf.setnframes(int(sample_rate * 0))

def get_text(text, hps, is_symbol):
    text_norm = text_to_sequence(text, hps.symbols, [] if is_symbol else hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = LongTensor(text_norm)
    return text_norm

def create_tts_fn(model, hps, speaker_ids):
    def tts_fn(text, speaker, language, speed, mark): # 應該就是這個
        if language is not None:
            text = language_marks[language] + text + language_marks[language]
        speaker_id = speaker_ids[speaker]
        stn_tst = get_text(text, hps, False)
        with no_grad():
            x_tst = stn_tst.unsqueeze(0).to(device)
            x_tst_lengths = LongTensor([stn_tst.size(0)]).to(device)
            sid = LongTensor([speaker_id]).to(device)
            audio = model.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=.667, noise_scale_w=0.8,
                                length_scale=1.0 / speed)[0][0, 0].data.cpu().float().numpy()
        del stn_tst, x_tst, x_tst_lengths, sid

        path = "D:\\College_things\\College_Program\\Backend\\audio_files\\"

        create_empty_wav(path + f'ppp{str(mark)}.wav') # add
        filename = os.path.join(path, f'ppp{str(mark)}.wav')  # 定義文件名 add
        sf.write(filename, audio, hps.data.sampling_rate)  # 將音頻寫入文件 add

        return "Success", filename # add
        # return "Success", (hps.data.sampling_rate, audio)

    return tts_fn

hps = utils.get_hparams_from_file("D:/College_things/College_Program/Backend/back_end/app/VITS_files/OUTPUT_MODEL/finetune_speaker.json") # get hparams from config file ( finetune_speaker.json )

net_g = SynthesizerTrn( # 載入模型 
    len(hps.symbols),
    hps.data.filter_length // 2 + 1,
    hps.train.segment_size // hps.data.hop_length,
    n_speakers=hps.data.n_speakers,
    **hps.model).to(device)
_ = net_g.eval()

_ = utils.load_checkpoint("D:/College_things/College_Program/Backend/back_end/app/VITS_files/OUTPUT_MODEL/G_latest.pth", net_g, None)
speaker_ids = hps.speakers
speakers = list(hps.speakers.keys())
tts_fn = create_tts_fn(net_g, hps, speaker_ids)

def vc_fn(text, mark):
    filename = tts_fn(text, "PPP", "简体中文", 1, mark)
    print(filename)

# 先跑一次
tts_fn("初始化中", "PPP", "简体中文", 1, "_init")



