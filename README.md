## 1. 建立基本環境
1. pyenv
2. install Django

## 2. 加入認證 app ( authentication )

### 下載相關依賴
1. pip install cors-header
2. pip install djangorestframework djangorestframework_simplejwt
3. 配置 settings
   1. cors-header 要加 'corsheaders.middleware.CorsMiddleware' middleware client 才會給過

### 編輯文件
1. urls.py
2. models.py
3. serializers.py
4. views.py

### streamlizatoin
- curl test :
```bash
curl -X POST http://localhost:8000/app/openai/ -H "Content-Type:application/json" --data-binary "{\"params\": {\"messages\": \"my name is daniel handsome boy\"}}"
```

## 3. 加入 文本生成 ( langchain )

我原本是使用一般的 OPENAI module，後來改成使用 langchain，因為比較方便可以使用
  
- history
- system msg

1. 載入 langchain module
2. 另外要使用 `from lanchain_openai import ChatOpenAI`，而非 `from langchain.chat_models import ChatOpenAI` ，因為版本過了（淘汰）。

## 4. 加入 tts ( VITS-fast-fine-tuning )

按照 VITS reop LOCAL.md 前五步驟

1. Clone this repository;
2. Run `pip install -r requirements.txt`;
    可以不載 gradio
3. Install GPU version PyTorch: (Make sure you have CUDA 11.6 or 11.7 installed)
    ```console
    # CUDA 11.6 (選這個)
    pip install torch==1.13.1+cu116 torchvision==0.14.1+cu116 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cu116
    # CUDA 11.7
    pip install torch==1.13.1+cu117 torchvision==0.14.1+cu117 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cu117
   ```
4. Install necessary libraries for dealing video data:
    ```console
   pip install imageio==2.4.1
   pip install moviepy
   ```
5. Build monotonic align (necessary for training)
    ```console
    cd monotonic_align
    mkdir monotonic_align
    python setup.py build_ext --inplace
    cd ..
    ```

6. 創 OUTPUT_MODEL dir，這個不一定要這個名字，但同時 VC_inference.py 裡面的 default 參數也需要改
   更改讀入 OUTPUT_MODEL 的方式，使用絕對路徑
7. 輸出音頻的位置只需要改變裡面 filepath 即可
8. 只留 VC_inference.py 在外面，剩下的檔案全部放在新增的 VITS_files 裡面
   更改 import 方式如下面 error 1. 所說
   

### 會遇到的 error
1. 載入目錄的問題，會出現 no module name ...
   要全部使用 `from . import`，如果是要載入特定檔案、目錄 `from .<directory>.<file> import ...`
   所也有些它給的檔案 => module.py models.py text 等等裡面有些都要改成這樣的方式

## 4. 前後端的傳送對話文字和語音
新打一個 api -> audio_file 專門要求語音檔案，所以就會由前端來控制傳送，後段只負責產生語音和等待要求。

### 尚未測試有效功能
- 如果前端要的時候卻還沒有出現語音，前端請求會延遲最多 5 秒，超過就 404。

## 5. 偵測上下文量

自製一個計算 token 的 function，可以在超過一定量的時候刪掉
- 雖然 gpt 4 的容忍值可已到 32000 token，但我還是停在 2000 就好，因為還要考慮 system prompt。
- 新開 api for 
  - 計算對應使用者 tokens 數量，並回傳是否超過上限
  - 清除 memory

### 分開 memory
我會使用登入的使用者來區別不同人，進而創建不同 conversations
- 發現的 feature
  - 如果使用同一個 chrome 瀏覽器帳號，可能是因為 localstorage 的關係，使用者會相同。

## 6. 限制聊天人數
- 使用 users_conversation_tokens.length 以表示當前聊天的人數
- 使用 timer 去偵測如果一個人待在頁面太久都沒有動，就要將他從 users_conversation_tokens 移出
- client access openai api 要先去看 users_conversation_tokens 裡面有沒有它
  - 如果沒有它，並且 users_conversation_tokens.length < 10 就可以聊天，並且新增一個它的 entry。
  - 如果沒有它，並且 users_conversation_tokens.length >= 10 就必須排隊等待 
    - 需要維護一個等待佇列
  - 如果發現有它，那代表重複登入了，block 掉
    - TODO : 需要顯示警告訊息
- 要調整 openai api，如果 access 的使用者發現沒有在 users_conversation_tokens 裡面，就要擋下來回報 404，讓使用者刷新頁面重新去等待
  - 用在
    - detect 使用者頁面放太久沒有說話
  - TODO : 在前端 router 那邊需要再 beforeRoute 去檢查 to and from
    - 如果 to 來自 /Chat，帶表他要進入聊天頁面，因此就需要 access 後端 api 去確認我是否可以排進去
    - 如果 from 來自 /Chat，帶表他要離開聊天室，因此就需要 access 後端 api 刪掉 entry
    - 如果是 reload，就讓他重新進入等待頁面
- 需要再開一個 api 用來 set users_conversation_tokens，當被允許進入的時候要使用這個來設定，以免被 openai api 擋下來。

### bug

- DONE : 當我將 user 從後端踢出 user_conversation_tokens，他還是可以進來，即便有其他人並且連線是滿的，可能是因為沒有刪除完整，也可能會出現使用者已經在聊天室裡面的情況出現。

# 之後打開方式
1. copy repo
2. 建立一個新的 venv ( name: pyvenv )
3. pip install -r requirements.txt
4. 

