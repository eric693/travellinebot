# 🤖 LINE Bot 智能旅遊客服系統

一個功能完整的 LINE Bot，專為宿霧旅遊代理商設計，提供智能行程推薦、自動客服回覆和完整的旅遊諮詢服務。

## 🌟 主要功能

### 1. 智能行程推薦
- **AI 對話式客服**：理解自然語言，如「我想看鯨鯊」、「想要刺激的行程」
- **個人化推薦**：根據用戶偏好智能推薦最適合的行程
- **完整行程資料庫**：18個精心設計的旅遊行程

### 2. 自動客服系統
- **即時回覆**：保險、跳傘、伴手禮、導遊等常見問題
- **行程代碼查詢**：輸入 S1、C1、N3 等代碼查看詳細資訊
- **拼團活動**：輸入 joiner 獲取拼團報名連結

### 3. 智能歡迎系統
- **新成員歡迎**：自動歡迎新加入的群組成員
- **報到引導**：指導新成員完成報到手續

## 📋 行程代碼列表

| 代碼 | 行程名稱 | 天數 | 價格範圍 (PHP) | 特色 |
|------|----------|------|----------------|------|
| **C1** | 資生堂跳島一日遊 | 1日 | 2,500-4,300 | 經典跳島，適合初次遊客 |
| **S1** | 宿霧鯨鯊兩日遊 | 2日 | 7,750-10,050 | 鯨鯊+朔溪，最熱門 |
| **S4A** | 鯨鯊一日遊（輕鬆版） | 1日 | 4,500-5,800 | 鯨鯊+半程朔溪 |
| **N3** | 媽媽島兩日遊 | 2日 | 6,800-12,900 | 網美必去，白沙洲 |
| **B1** | 薄荷一日遊 | 1日 | 4,200-5,600 | 巧克力山+眼鏡猴 |
| **S2** | 朔溪一日遊 | 1日 | 3,800-5,800 | 刺激冒險體驗 |
| **C2** | 市區一日遊 | 1日 | 1,600-3,400 | 文化歷史，最便宜 |
| **S8** | 墨寶一日遊 | 1日 | 2,200-4,500 | 沙丁魚風暴 |

*完整18個行程代碼請參考程式碼*

## 🛠 技術架構

- **Backend**: Python Flask
- **LINE API**: LINE Bot SDK
- **AI 功能**: 自然語言處理 + 意圖識別
- **部署**: ngrok tunnel + screen sessions

## 🚀 快速開始

### 1. 設定 LINE Bot

1. 前往 [LINE Developers](https://developers.line.biz/)
2. 創建新的 Provider 和 Channel
3. 取得以下資訊：
   - `Channel Secret`
   - `Channel Access Token`

### 2. 配置程式

編輯 `grouplinebot.py`，更新以下資訊：

```python
# 更新為您的 LINE Bot 資訊
LINE_CHANNEL_SECRET = 'your_channel_secret_here'
LINE_CHANNEL_ACCESS_TOKEN = 'your_channel_access_token_here'
GROUP_ID = 'your_group_id_here'  # 可選
```

### 3. 運行系統

#### 方法一：手動部署

```bash
# 1. 啟動 LINE Bot
screen -dmS linebot bash -c "python3 grouplinebot.py"

# 2. 啟動 ngrok
screen -dmS ngrok bash -c "ngrok http 5001"

# 3. 獲取 Webhook URL
curl -s http://localhost:4040/api/tunnels | grep '"public_url".*https'
```

### 4. 設定 Webhook

1. 複製 ngrok 提供的 HTTPS URL
2. 在 LINE Developers Console 設定 Webhook URL：
   ```
   https://your-ngrok-url.ngrok.io/callback
   ```
3. 啟用 Webhook

## 📱 使用方式

### 客戶可以這樣與 Bot 互動：

#### 🗣 自然對話
```
用戶: "我想看鯨鯊"
Bot: 根據您的需求，我為您推薦這幾個超棒的行程：
     🌟 1. 【S1】宿霧鯨鯊兩日遊...
```

#### 🔢 行程代碼查詢
```
用戶: "S1"
Bot: 🌊 【S1】宿霧鯨鯊兩日遊行程
     📍 行程景點/活動：
     • 歐斯陸鯨鯊浮潛 Oslob...
```

#### 🤔 常見問題
```
用戶: "保險"
Bot: 🔔 關於保險的說明：
     我們旅遊行程中所使用的車輛與船隻...
```

#### 👥 拼團活動
```
用戶: "joiner"
Bot: 🔥 iOutback Agency 澳貝客遊學 週末拼團活動 🔥
     📌 報名傳送門 👉 https://forms.gle/...
```

## 🎯 智能推薦示例

Bot 可以理解各種自然語言需求：

| 用戶輸入 | Bot 理解 | 推薦結果 |
|----------|----------|----------|
| "想要刺激的" | 冒險偏好 | S1, S2, S4 |
| "預算有限" | 價格敏感 | C2, S8 |
| "適合拍照" | 網美需求 | N3, N4 |
| "第一次來宿霧" | 新手友好 | C1, S4A, B1 |
| "兩天一夜" | 時間偏好 | S1, N3, B2 |

## 🔧 管理指令

### 檢查運行狀態
```bash
# 查看 screen sessions
screen -ls

# 查看進程
ps aux | grep -E "(grouplinebot|ngrok)"

# 查看日誌
tail -f nohup.out
```

### 進入 screen sessions
```bash
# 進入 LINE Bot session
screen -r linebot

# 進入 ngrok session  
screen -r ngrok

# 離開 screen (不關閉)
Ctrl+A, D
```

### 重啟服務
```bash
# 停止所有服務
pkill -f grouplinebot.py
pkill -f ngrok

# 重新啟動
nohup python3 grouplinebot.py &
```

## 🛡 故障排除

### 常見問題

1. **Bot 沒有回應**
   ```bash
   # 檢查進程是否運行
   ps aux | grep grouplinebot
   
   # 檢查端口是否被佔用
   netstat -tlnp | grep :5001
   ```

2. **ngrok 連線問題**
   ```bash
   # 檢查 ngrok 狀態
   curl http://localhost:4040/api/tunnels
   
   # 重啟 ngrok
   pkill ngrok
   screen -dmS ngrok bash -c "ngrok http 5001"
   ```

3. **Webhook 驗證失敗**
   - 確認 Channel Secret 和 Access Token 正確
   - 檢查 Webhook URL 是否使用 HTTPS
   - 確認 `/callback` 路徑正確

### 日誌查看
```bash
# 即時查看日誌
tail -f nohup.out

# 查看最近的錯誤
grep -i error nohup.out | tail -10
```

