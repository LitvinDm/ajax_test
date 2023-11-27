## Local Environment Installation Manual

1. Make sure you use Python 3.10. Other versions is possible

2. Create python virtual environment. Run this command inside the root
project directory:
```shell
python3 -m venv venv
```

4. Activate your virtual environment:
```shell
source ./venv/bin/activate
```

5. Install requirements 
```shell
pip install -r requirements.txt
```
6. Fill .env file in root or set environment variables
```shell
api_username=
api_password=
api_url=
api_endpoint=
app_username=
app_password=
db_host=
db_user=
db_password=
db_name=
```
7. Start application
```shell
uvicorn main:app --reload    
```