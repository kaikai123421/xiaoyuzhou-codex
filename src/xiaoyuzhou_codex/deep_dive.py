from collections.abc import Callable


class TranscriptResolver:
    def __init__(self, *, fetch_text: Callable[[str], str], transcribe_audio: Callable[[str], str]):
        self.fetch_text = fetch_text
        self.transcribe_audio = transcribe_audio

    def resolve(self, transcript_url: str | None, audio_url: str | None) -> str:
        if transcript_url:
            transcript = self.fetch_text(transcript_url).strip()
            if transcript:
                return transcript
        if audio_url:
            transcript = self.transcribe_audio(audio_url).strip()
            if transcript:
                return transcript
        raise RuntimeError("该单集没有可用逐字稿，音频也无法转写")


def build_deep_dive_prompt(title: str, transcript: str, *, evidence_type: str = "transcript") -> str:
    labels = {
        "transcript": "发布方逐字稿",
        "captions": "可靠字幕",
        "audio-transcription": "音频转写",
        "show-notes": "节目简介与节目笔记",
    }
    if evidence_type not in labels:
        raise ValueError(f"未知证据类型：{evidence_type}")
    disclaimer = ""
    if evidence_type == "show-notes":
        disclaimer = "未核验完整音频；以下仅依据节目简介与节目笔记，不代表完整听审。\n"
    return f"""请用中文深度解读播客《{title}》。

证据来源：{labels[evidence_type]}
{disclaimer}

只能依据下方证据材料，不得编造嘉宾身份、数据、金句或结论；不确定内容必须明确标注。

按以下标题输出：
1. 执行摘要
2. 内容结构
3. 主要观点
4. 论据与案例
5. 原文金句（少量引用）
6. 值得质疑之处与反方观点
7. 可信度提示
8. 可执行建议
9. 延伸问题
10. 公众号选题价值
11. 可关联的既有知识

证据材料：
{transcript}
"""
