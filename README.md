## 建立基本環境
1. pyenv
2. install Django

## 加入認證 app ( authentication )

### 下載相關依賴
1. pip install cors-header
2. pip install djangorestframework djangorestframework_simplejwt
3. 配置 settings
   1. cors-header 要加 'corsheaders.middleware.CorsMiddleware' middleware client 才會給過
   2. 

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

## 加入 tts ( VITS-fast-fine-tuning )

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

# 之後打開方式
1. copy repo
2. 建立一個新的 venv ( name: pyvenv )
3. pip install -r requirements.txt

