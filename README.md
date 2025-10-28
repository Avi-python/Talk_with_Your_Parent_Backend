# 啟動方式

1. git clone this repo
2. switch to Talk_with_Your_Parent_Backend dir, and build an venv `python -m venv venv` 
3. enter into venv, and install dependencies `pip install -r requirements.txt`
4. manually install torch dependencies:
```sh
pip install torch==1.13.1+cu116 torchaudio==0.13.1+cu116 torchvision==0.14.1+cu116 \
  --extra-index-url https://download.pytorch.org/whl/cu116
```
5. create `OUTPUT_MODEL` dir in `/back_end/app/VITS_files`
6. check the path in VC_inference.py
7. build monotonic_align
```sh
cd to VITS_files
git clone https://github.com/resemble-ai/monotonic_align.git
cd monotonic_align
python setup.py build_ext --inplace
```
8. create .env file under /back_end dir (follow the .env.example)
9. if you don't have a openai api key, go to **openai playground** and create one. Then copy the api key and paste to the .env file. (you must add some credits to your account)
10. Run migrateions (If it is first run)
```sh
python manage.py makemigrations
python manage.py migrate
``` 
11. run server
```sh
python manage.py runserver
```
12. follow the setup and create super user
13. enter into the manage page:`http://localhost:8000/admin/
14. create new **personality** (name, description => 角色的描述，可以用我們之前提出的 10 項特徵, image = avatar)
15. create a new dir under OUTPUT_MODEL (**the name of the dir must equal to personality.name**)
16. put the `finetune_speaker.json` and `G_latest.pth` under the folder created in step 15. 
17. DONE, now run with the frontend (frontend has a login page, you can enter with superuser's gmail/pwd or create a new user and login with that user)