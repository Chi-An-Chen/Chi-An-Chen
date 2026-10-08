# 個人 README 圖卡更新

此版本使用 GitHub 帳號 `Chi-An-Chen`。`README.md` 中的 `./contributions.sh`、`./stats.sh` 是終端機風格的標題，實際更新由 Python 執行。

## 自動更新

將此目錄上傳至個人頁面 repository `Chi-An-Chen/Chi-An-Chen` 的 `main` 分支後，`.github/workflows/update-profile-art.yml` 會在每日 11:20 UTC（台灣 19:20）排程更新；也支援手動執行與 push 觸發。GitHub 的排程可能延遲，SVG 並非即時查詢。

語言圖卡使用可選的 Actions repository secret `LANGUAGES_TOKEN`：

- 有 key：讀取此帳號擁有、且 key 可存取的 public 與 private repositories。需授權所有要統計的 repositories；classic PAT 可使用 `repo`，fine-grained PAT 選取此帳號的所有 repositories 並允許 Metadata 讀取。
- 沒有 key／空值：只讀取 public repositories，圖卡標示 `PUBLIC ONLY / no key`，private 數量顯示 `—`。
- key 無效或抓取失敗：停止更新並保留既有 SVG，不會靜默切換成不完整的統計。若 key 可見的 private 數量無法由 API 核對，應確認 key 的 repository 授權範圍。

用於提交圖卡的 `GITHUB_TOKEN` 由 Actions 自動提供；它不代替讀取其他 private repositories 的 `LANGUAGES_TOKEN`。Repository 的預設 Workflow permissions 可維持 Read；此 workflow 只在更新 job 明確要求 `contents: write`。若有組織政策或 branch protection 阻止提交，需依錯誤調整該限制。

## 首次設定：建議的最小權限

1. 前往 https://github.com/settings/personal-access-tokens/new 建立 Fine-grained PAT。
2. Token name：`profile-languages-readonly`；Expiration：90 days（到期前更新 repository secret）。
3. Resource owner：`Chi-An-Chen`；Repository access：`All repositories`，以涵蓋所有目前與未來擁有的 repos。只選取個人頁面 repo 無法統計其他 private repos。
4. Repository permissions：只保留 `Metadata: Read-only`；其餘 repository 與 account 權限不啟用。GitHub 的列舉 repositories／語言統計 API 只需要 Metadata 讀取，不需要 Contents 或 Workflows 寫入權限。請優先使用此 fine-grained token，而不是具備廣泛 `repo` 權限的 classic PAT。
5. Generate token 後，直接將值存入 https://github.com/Chi-An-Chen/Chi-An-Chen/settings/secrets/actions → New repository secret。Name 必須是 `LANGUAGES_TOKEN`；Secret 欄貼上 token。不放入 Variables、程式碼、README、commit、聊天或截圖。
6. 將檔案上傳至 repo 的 `main`，確保 `.github/workflows/update-profile-art.yml` 也有上傳。
7. https://github.com/Chi-An-Chen/Chi-An-Chen/actions → Update profile art → Run workflow → main → Run workflow。
8. 等執行成功後，確認 `data/profile-data.json` 的 `username` 為 `Chi-An-Chen`、`includes_private` 為 `true`，repo 數與自己的 repo 清單一致。公開輸出只保存聚合數字；private 數量及語言加總會公開，不包含 private repo 名稱或程式碼。

## 目前 workflow 的保護

- 只在本人的 `main` 執行；沒有 `pull_request`／`pull_request_target` 觸發。
- 只用 GitHub 官方 checkout、setup-python Actions，固定完整 commit SHA；提交使用 Git，不用第三方自動提交 Action。
- `LANGUAGES_TOKEN` 只在語言統計步驟作為環境變數傳入；腳本只將它放在送往 GitHub API 的 Authorization header，不輸出或保存它。
- 提交前執行驗證：確認帳號、統計、SVG 與聚合 JSON 欄位，並檢查常見 GitHub token 格式；若發現疑似 key，僅回報檔名，不將 key 印進公開 log。只加入五個明確指定的資料／SVG 檔案。
- `.gitignore` 排除常見本機 secret 與快取檔。這不是完整的 secret scanner；上傳前仍需確認 staged files，避免將 key 寫進允許上傳的檔案。
- 不能保證任何 workflow 永遠不洩漏。能修改此 repo workflow 的人也可能利用 secret，因此只給可信任的人 write access；若 token 曾出現在公開內容，立即 revoke 並建立新 token。

排程每天約台灣 19:20 執行；GitHub Actions 高負載時可能延遲或漏跑，並不保證準點。Public repo 若 60 天沒有活動，GitHub 可能停用 schedule。此流程正常會定期提交時間戳，若停止更新仍需檢查 Actions 狀態。README 圖片可能有快取，先以 workflow 執行結果與 `generated_at` 判斷資料是否更新。

常見錯誤：HTTP 401 通常是 key 無效或到期；HTTP 403 需檢查權限與 API rate limit；private 數量不足時檢查是否選了 All repositories；提交被拒絕時檢查 `contents: write` 或分支保護。Key 到期時 workflow 會失敗並保留上一版圖卡，只有 secret 未設定或空值時才改成 public-only。

## 本機更新

在此目錄執行：

```sh
python3 -m pip install -r scripts/requirements.txt
python3 scripts/fetch_contributions.py
python3 scripts/generate_streak_svg.py
python3 scripts/render_stats_svg.py
python3 scripts/render_profile_svg.py --snapshot data/profile-data.json
python3 scripts/check_profile.py
```

最後兩行預設更新 `avi-ascii.svg` 並驗證結果。如需 private 統計，先在執行環境設定 `GH_TOKEN`；也可使用已有的 GitHub CLI 登入：

```sh
GH_TOKEN="$(gh auth token)" python3 scripts/render_profile_svg.py --snapshot data/profile-data.json
```

## 資料意義

- `avi-ascii.svg`：此帳號擁有的 repositories，包括 forks 與 archived；語言比例按各 repo 預設分支的 GitHub language bytes 加總，不代表你親自撰寫的程式碼或熟練度。`data/profile-data.json` 只保存聚合數字，不含 private repository 名稱。開發經驗文字集中在 `scripts/render_profile_svg.py` 的 `EXPERIENCES`，可自行編輯；自動更新的是 repository／語言數據。
- `contrib-heatmap.svg` 和 `stats.svg`：共用 `data/contributions.json`，從你的公開 GitHub contribution calendar 重新擷取。private contribution 數量是否包含在內，依個人頁面的「Private contributions」可見性設定；此處不使用語言統計的 key。
- 資料帳號與預期帳號不一致時，renderer 直接失敗；不再退回原作者的舊 snapshot。原本的照片與 ASCII 工具留作歷史素材，更新流程不會呼叫它們。

參考：[GitHub Actions secrets](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets)、[Repository languages API](https://docs.github.com/en/rest/repos/repos#list-repository-languages)、[Contribution visibility](https://docs.github.com/en/account-and-profile/how-tos/contribution-settings)。
