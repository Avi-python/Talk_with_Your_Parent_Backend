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

# 之後打開方式
1. copy repo
2. 建立一個新的 venv ( name: pyvenv )
3. pip install -r requirements.txt

