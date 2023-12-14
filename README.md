# ACM-SIST website backend

# Setup
```commandline
git clone https://github.com/kishor1445/acm-website-backend
cd acm-website-backend
pip install -r requirements.txt
```
create a file called `.env` and set the below env variables
```
MAIL_SERVER="smtp.gmail.com"
MAIL_USER=Enter Your Username
MAIL_PASS=Enter Your Password
```
**NOTE:** MAIL_PASS is not your gmail password instead it's an App Password. check out this [link](https://support.google.com/mail/answer/185833?hl=en)

# Run
To run the server:
```commandline
uvicorn app.main:app
```
