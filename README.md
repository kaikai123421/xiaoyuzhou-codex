# xiaoyuzhou-codex

涓€涓?RSS 浼樺厛銆佷互灏忓畤瀹欎负鏀跺惉鍏ュ彛鐨勬挱瀹㈤浄杈撅細姣忓ぉ绛涢€変腑鑻辨枃浼樿川鑺傜洰锛屽彂閫佷腑鏂囬涔︽棩鎶ワ紝骞舵敮鎸佸洖澶嶁€滄繁鎸?2銆?鈥濄€?
## 鍔熻兘

- 杩借釜鍏紑 RSS锛屼繚鐣欏皬瀹囧畽鑺傜洰閾炬帴銆?- 鎸?AI/绉戞妧銆佸晢涓氭姇璧勩€佸績鐞嗚鐭ャ€佸仴搴风瀛﹀拰浜虹墿璁胯皥璇勫垎銆?- 姣忓ぉ绮鹃€?5鈥? 鏈燂紝涓嶈冻鏃跺畞缂烘瘚婊ャ€?- 瑙ｆ瀽椋炰功涓殑娣辨寲涓庡亸濂藉弽棣堟寚浠ゃ€?- 浼樺厛浣跨敤鍙戝竷鏂归€愬瓧绋匡紝鍐嶆寜璁稿彲杞啓闊抽銆?- 鎻愪緵鍙畨瑁呯殑 Codex skill 鍜?GitHub Actions 瀹氭椂妯℃澘銆?
## 鏈湴璇曠敤

闇€瑕?Python 3.11 鎴栨洿楂樼増鏈細

```powershell
python -m pip install -e .
Copy-Item config/config.example.json config/config.json
Copy-Item config/private.example.json private/config.json
xyz-codex check-sources
xyz-codex daily
```

鎶婄ず渚嬭闃呭拰椋炰功鍗犱綅淇℃伅鏇挎崲涓鸿嚜宸辩殑閰嶇疆銆俙private/`銆佺湡瀹為厤缃€佺姸鎬佸拰鎶ュ憡榛樿涓嶄細杩涘叆 Git銆?
## 鍛戒护

- `check-sources`锛氭鏌?RSS 鍙敤鎬с€?- `daily`锛氱敓鎴愭棩鎶ュ苟鎸夐厤缃彂閫侀涔︺€?- `daily --dry-run`锛氬彧棰勮锛屼笉鍐欏叆鐘舵€佹垨鍙戦€佹秷鎭€?- `process-commands`锛氬鐞嗛涔﹀洖澶嶃€?- `deep-dive`锛氭牴鎹€愬瓧绋裤€佸瓧骞曘€侀煶棰戣浆鍐欐垨鑺傜洰绗旇鐢熸垚甯﹁瘉鎹爣绛剧殑娣辨寲鎻愮ず銆?- `discover`锛氳緭鍑哄緟浜哄伐瀹℃牳鐨勫€欓€夎妭鐩€?
## 鑷姩杩愯

浠撳簱宸ヤ綔娴佸湪鍖椾含鏃堕棿 08:00 杩愯鏃ユ姤锛屽苟姣忓皬鏃跺鐞嗕竴娆￠涔︽寚浠ゃ€傞厤缃?GitHub Secrets锛?
- `PUBLIC_CONFIG_JSON`锛氱湡瀹炲叕寮€閰嶇疆鍐呭銆?- `PRIVATE_CONFIG_JSON`锛氶涔﹀強鍙€夎浆鍐欐湇鍔＄殑绉佸瘑閰嶇疆銆?
鐘舵€侀€氳繃 GitHub Actions 缂撳瓨璺ㄨ繍琛屼繚瀛樸€傛洿鎺ㄨ崘浣跨敤 Codex 鑷姩浠诲姟璋冪敤 `skills/xiaoyuzhou-podcast-radar`锛屼互渚垮畬鎴愯涔夋憳瑕佸拰椋炰功鐭ヨ瘑搴撳綊妗ｃ€?
## 瀹夊叏杈圭晫

椤圭洰涓嶈皟鐢ㄥ皬瀹囧畽绉佹湁鎺ュ彛锛屼笉缁曡繃浠樿垂鎴栬闂帶鍒讹紝涓嶆妸鑺傜洰绠€浠嬪啋鍏呭畬鏁村惉鍙栫粨鏋溿€傚尰鐤椼€佸績鐞嗗強鎶曡祫淇℃伅浠呬綔淇℃伅鍙傝€冦€?
## License

MIT

