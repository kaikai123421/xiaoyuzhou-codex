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
        raise RuntimeError("璇ュ崟闆嗘病鏈夊彲鐢ㄩ€愬瓧绋匡紝闊抽涔熸棤娉曡浆鍐?)


def build_deep_dive_prompt(title: str, transcript: str, *, evidence_type: str = "transcript") -> str:
    labels = {
        "transcript": "鍙戝竷鏂归€愬瓧绋?,
        "captions": "鍙潬瀛楀箷",
        "audio-transcription": "闊抽杞啓",
        "show-notes": "鑺傜洰绠€浠嬩笌鑺傜洰绗旇",
    }
    if evidence_type not in labels:
        raise ValueError(f"鏈煡璇佹嵁绫诲瀷锛歿evidence_type}")
    disclaimer = ""
    if evidence_type == "show-notes":
        disclaimer = "鏈牳楠屽畬鏁撮煶棰戯紱浠ヤ笅浠呬緷鎹妭鐩畝浠嬩笌鑺傜洰绗旇锛屼笉浠ｈ〃瀹屾暣鍚銆俓n"
    return f"""璇风敤涓枃娣卞害瑙ｈ鎾銆妠title}銆嬨€?
璇佹嵁鏉ユ簮锛歿labels[evidence_type]}
{disclaimer}

鍙兘渚濇嵁涓嬫柟璇佹嵁鏉愭枡锛屼笉寰楃紪閫犲槈瀹捐韩浠姐€佹暟鎹€侀噾鍙ユ垨缁撹锛涗笉纭畾鍐呭蹇呴』鏄庣‘鏍囨敞銆?
鎸変互涓嬫爣棰樿緭鍑猴細
1. 鎵ц鎽樿
2. 鍐呭缁撴瀯
3. 涓昏瑙傜偣
4. 璁烘嵁涓庢渚?5. 鍘熸枃閲戝彞锛堝皯閲忓紩鐢級
6. 鍊煎緱璐ㄧ枒涔嬪涓庡弽鏂硅鐐?7. 鍙俊搴︽彁绀?8. 鍙墽琛屽缓璁?9. 寤朵几闂
10. 鍏紬鍙烽€夐浠峰€?11. 鍙叧鑱旂殑鏃㈡湁鐭ヨ瘑

璇佹嵁鏉愭枡锛?{transcript}
"""

