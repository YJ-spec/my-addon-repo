# CurieJet Integration 安裝與設定指南

以下是安裝與啟動 CurieJet Integration 的完整步驟，請依照順序操作。

---

## 1. 安裝 Mosquitto broker

1. 打開 Home Assistant 主介面。
2. 點擊左側「設定」→「附加元件、備份與資料存取」。
3. 在「附加元件商店」搜尋 `Mosquitto broker`。
4. 點擊安裝。
5. 安裝完成後**不要馬上啟動**，先繼續下一步設定。

---

## 2. 設定 Mosquitto broker

1. 在 Mosquitto broker 的設定頁面，找到 `配置 (Configuration)`。
2. 修改設定內容如下：

    ```yaml
    logins: []
    require_certificate: false
    certfile: fullchain.pem
    keyfile: privkey.pem
    customize:
      active: true
      folder: mosquitto
    ```

✅ **特別注意**：`customize.active` 必須設為 `true`，才能正確載入橋接設定。

3. 儲存設定後，回到「資訊」頁面。
4. 點擊「啟動」。

---

## 3. 啟用 MQTT Discovery 功能

1. 在 Home Assistant 左側選單，點擊「設定」→「裝置與服務」。
2. 在整合（Integrations）頁面點擊右下角「新增整合」。
3. 搜尋 `MQTT`。
4. 選擇 `MQTT` 並安裝。
5. 安裝後，進入 MQTT 整合設定，確認以下選項：
    - `啟用自動發現 (Enable discovery)` ✅ 開啟
    - Broker 填寫：`core-mosquitto`
    - Port：`1883`
    - 帳號密碼：如果有設定，請填入；否則留空。

6. 儲存設定。

---

## 4. 安裝 CurieJet Integration 插件

1. 打開 Home Assistant 主介面。
2. 點擊左側「設定」→「附加元件、備份與資料存取」。
3. 在「附加元件商店」右上角點「⋮ → 儲存庫」。
4. 新增插件儲存庫網址：

    ```
    https://github.com/YJ-spec/my-addon-repo
    ```

5. 找到 `CurieJet Integration` 插件並安裝。
6. 安裝後，進入插件設定頁面，設定以下參數：

    | 項目 | 說明 |
    |:---|:---|
    | mqtt_topics | 填入 `+/+/data,+/+/control`（預設值） |
    | mqtt_broker | 填入 `core-mosquitto` |
    | mqtt_port | 填入 `1883` |
    | mqtt_username | 若 Mosquitto 有設定帳號，請填入 |
    | mqtt_password | 若 Mosquitto 有設定密碼，請填入 |
    | HA_LONG_LIVED_TOKEN | 可選，若需要與 HA API 整合可填入 Token |

7. 儲存設定。
8. 啟動 CurieJet Integration 插件。

---

## 5. 最後檢查

- 確認 `/share/mosquitto/` 資料夾內有 `external_bridge.conf` 檔案（插件啟動時自動產生）。
- 確認 Home Assistant `MQTT` 整合已啟用且可用。
- 確認 Mosquitto broker 已正常啟動且讀取到 `/share/mosquitto/` 的設定。

---

# 🎉 完成！

當 CurieJet 裝置上線並透過 MQTT 發送訊息時，  
Home Assistant 將會自動偵測並新增裝置與感測器！

---
