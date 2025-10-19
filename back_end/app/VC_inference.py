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
current_dir = os.path.dirname(os.path.abspath(__file__))
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

def create_tts_fn(model, hps, speaker_ids, model_name):
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

        audio_dir = os.path.join(current_dir, 'audio_files')
        os.makedirs(audio_dir, exist_ok=True)

        create_empty_wav(os.path.join(audio_dir, f'{model_name}{str(mark)}.wav')) # add
        filename = os.path.join(audio_dir, f'{model_name}{str(mark)}.wav')  # 定義文件名 add
        sf.write(filename, audio, hps.data.sampling_rate)  # 將音頻寫入文件 add

        return "Success", filename # add
        # return "Success", (hps.data.sampling_rate, audio)

    return tts_fn

tts_fn = None


def load_vc_model(model_name):
    global tts_fn
    config_path = os.path.join(current_dir, 'VITS_files', 'OUTPUT_MODEL', model_name, 'finetune_speaker.json')
    model_path = os.path.join(current_dir, 'VITS_files', 'OUTPUT_MODEL', model_name, 'G_latest.pth')
    hps = utils.get_hparams_from_file(config_path) # get hparams from config file ( finetune_speaker.json )
    net_g = SynthesizerTrn( # 載入模型
        len(hps.symbols),
        hps.data.filter_length // 2 + 1,
        hps.train.segment_size // hps.data.hop_length,
        n_speakers=hps.data.n_speakers,
        **hps.model).to(device)
    _ = net_g.eval()
    _ = utils.load_checkpoint(model_path, net_g, None)
    speaker_ids = hps.speakers
    speakers = list(hps.speakers.keys())
    tts_fn = create_tts_fn(net_g, hps, speaker_ids, model_name)
    tts_fn("初始化中", model_name, "简体中文", 1, "_init") # 先跑一次

def vc_fn(text, mark, model_name):
    global tts_fn
    filename = tts_fn(text, model_name, "简体中文", 1, mark)
    print(filename)




