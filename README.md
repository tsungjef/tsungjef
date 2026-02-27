# LocalAI + n8n 會議記錄 AI 應用程式

這個範例專案提供一個可在本機執行的會議記錄自動化流程：

1. 上傳會議錄音（或逐字稿）。
2. 用 LocalAI 的 Whisper 模型做語音轉文字（可選）。
3. 用 LocalAI 的 LLM 產生：
   - 會議摘要
   - 決議事項
   - 待辦事項（Owner / Deadline）
   - 風險與追蹤重點
4. 透過 n8n 將結果寫入 Notion、Google Docs、Email 或 Slack。

---

## 架構說明

- **n8n**：負責流程編排（Trigger、HTTP Request、Function、通知整合）
- **LocalAI**：OpenAI 相容 API，提供本機 LLM / Whisper 服務
- **模型檔案**：放在 `./models`
- **Prompt 模板**：放在 `./prompts`

```text
[Webhook / Manual Trigger]
        ↓
 [取得錄音檔 or 逐字稿]
        ↓
 [Whisper 轉寫（可選）]
        ↓
 [LLM 摘要 + 任務結構化]
        ↓
 [格式化成 Markdown/JSON]
        ↓
 [寫入 Notion/Slack/Email]
```

---

## 快速開始

## 1) 先決條件

- Docker + Docker Compose
- 至少 8GB RAM（建議 16GB 以上）
- 如果你要跑較大模型，請準備 GPU 與對應 runtime

## 2) 啟動服務

```bash
docker compose up -d
```

啟動後可用：

- n8n: `http://localhost:5678`
- LocalAI: `http://localhost:8080/v1`

## 3) 準備模型

把模型放到 `./models`，例如：

- `models/ggml-model-q4_k_m.gguf`（聊天/摘要模型）
- `models/whisper-base.bin`（語音轉文字模型）

> LocalAI 支援多種模型格式，請依你下載的模型調整設定。

## 4) 匯入 n8n workflow

1. 開啟 n8n。
2. Import workflow。
3. 匯入 `workflows/meeting-minutes.json`。
4. 設定 `LOCALAI_BASE_URL`（預設 `http://localai:8080/v1`）。

## 5) 測試流程

- 用 Manual Trigger 執行
- 在 `transcript` 欄位貼上會議逐字稿
- 觀察 `summary_json` 輸出

---

## n8n 內的 LocalAI 呼叫範例

### Chat Completions（摘要）

- URL: `{{ $env.LOCALAI_BASE_URL || 'http://localai:8080/v1' }}/chat/completions`
- Method: `POST`
- Headers: `Content-Type: application/json`
- Body:

```json
{
  "model": "meeting-llm",
  "temperature": 0.2,
  "messages": [
    {"role": "system", "content": "你是專業會議助理，輸出 JSON"},
    {"role": "user", "content": "{{ $json.transcript }}"}
  ]
}
```

### Audio Transcriptions（語音轉文字，可選）

- URL: `{{ $env.LOCALAI_BASE_URL || 'http://localai:8080/v1' }}/audio/transcriptions`
- Method: `POST (multipart/form-data)`
- 欄位：
  - `file`: binary 音檔
  - `model`: `whisper-1`

---

## 輸出格式建議（JSON）

建議 LLM 最終輸出固定 schema，方便後續自動化：

```json
{
  "title": "會議標題",
  "summary": "三到五行摘要",
  "decisions": ["決議1", "決議2"],
  "action_items": [
    {
      "task": "要做什麼",
      "owner": "負責人",
      "deadline": "YYYY-MM-DD"
    }
  ],
  "risks": ["風險1"],
  "follow_up": ["下次會議追蹤項目"]
}
```

---

## 建議 Prompt 策略

- System Prompt 請求「只輸出 JSON，不要額外文字」。
- 要求 Action items 必填 owner/deadline，若缺資料則標示 `"unknown"`。
- 先摘要再結構化：可提高穩定性。
- 如逐字稿很長，先切段摘要，再做最終合併。

可參考：`prompts/meeting-system-prompt.txt`

---

## 常見問題

### 1) LocalAI 回應很慢

- 換小一點的 GGUF 模型
- 降低 max tokens
- 先做關鍵段落摘要，再整份彙總

### 2) 輸出 JSON 格式常壞掉

- 把 schema 直接放進 prompt
- 在 n8n 加入「JSON Parse + fallback 修復」節點
- temperature 降到 `0.1 ~ 0.3`

### 3) 中文品質不穩

- 選擇中文表現較好的模型
- 在 System Prompt 明確要求「繁體中文」

---

## 下一步可以加的功能

- 行事曆整合（自動排 follow-up）
- RAG（結合公司知識庫）
- 多語言會議翻譯
- 自動寄送會議紀要與待辦追蹤提醒

如果你要，我可以下一步直接幫你把 `meeting-minutes.json` 擴充成：
- Webhook 收音檔
- Whisper 轉寫
- 產生 Markdown 會議紀要
- 自動發 Slack + 寫 Notion
