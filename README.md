# USER FLASK RESTFUL API #
A simple Python Flask application to demostrate a user model API, where users are created with certain fields using pure RESTFul call methods, the user retrive a token allow it's own deletion. This could be for example used for a user to delete his/her own personal data as long the passwrod matches the one during creation.

## INSTALLATION AND FLASK SETUP INSTRUCTION ##
1) Using python install the requirements by running the command:
```bash
pip install requirements.txt
```
1) Start the FLASK API:
```bash
python app.py
```
---
### USING THE RESTFUL API

To communicate to the API service just submit request to http://localhost/user/, the sample request to the User resource are listed below for the API:

__Example POST Request__
```json
{
	"username": "user",
	"password": "password",
	"email": "user@host.com"
}
```

__Example POST Response__
```json
{
	"date": "29/07/2020:16:43:00.000"
}
```

__Example GET Request__
```json
{
	"username": "user", 
	"password": "password"
}
```

__Example GET Response__
```json
{
	"token": "24f5bfcffbe7adddb079ce5221ff4c410ff5e3f6"
}
```

__Example DELETE Request__
```json
{
	"token": "24f5bfcffbe7adddb079ce5221ff4c410ff5e3f6"
}
```

__Example DELETE Response__
```json
{
	"username": "user"
}
```
---     

### Requirements 

---
__Plattform:__

+ python3
+ python3-pip
+ python3-setuptools

__Python specific requiremnts:__

+ flask
+ flask_sqlalchemy 
+ email_validator
+ password-strength
---

## Support Information. ##

* Author: Daniel Hung.
* Location: Manchester UK.
* email: danihuso@hotmal.com