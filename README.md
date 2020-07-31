# USER FLASK RESTFUL API #
A simple Python Flask application to demostrate a user model API, where users are created with certain fields using pure RESTFul call methods, the user retrive a token allow it's own deletion. This could be for example used for a user to delete his/her own personal data as long the passwrod matches the one during creation.

## FLASK INSTALLATION, SETUP, AND RUN INSTRUCTIONS ##
1) Using python install the requirements by running the command:
```bash
pip install requirements.txt
```
2) Start database:
```bash
flask initdb
```
3) Start Flask RESTFul API:
```bash
flask run
```
---
### USING THE RESTFUL API

To communicate to the API service just submit request to http://localhost/user/, the sample request to the User resource are listed below for the API:

__Example POST Request [create a user]__
```json
{
	"username": "user",
	"password": "password",
	"email": "user@host.com"
}
```

__Example POST Response [create a user]__
```json
{
	"date": "29/07/2020:16:43:00.000"
}
```

__Example GET Request [get user auth token]__
```json
{
	"username": "user", 
	"password": "password"
}
```

__Example GET Response [get user auth token]__
```json
{
	"token": "24f5bfcffbe7adddb079ce5221ff4c410ff5e3f6"
}
```

__Example DELETE Request [delete a user]__
```json
{
	"token": "24f5bfcffbe7adddb079ce5221ff4c410ff5e3f6"
}
```

__Example DELETE Response [delete a user]__
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

+ password_strength
+ flask_sqlalchemy 
+ flask 
+ passlib
+ jwt
---

## Support Information. ##

* Author: Daniel Hung.
* Location: Manchester UK.
* email: danihuso@hotmal.com