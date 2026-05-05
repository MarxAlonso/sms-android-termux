integraciones-test


POST
/test/sms/send
Send Sms Test

Parameters
Try it out
No parameters

Request body

application/json
Example Value
Schema
{
  "to": "string",
  "message": "string",
  "channel": "sms",
  "tenant_id": "string",
  "metadata": {
    "additionalProp1": {}
  }
}
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

GET
/test/sms/pending
Get Sms Pending


Parameters
Try it out
Name	Description
fecha
string | (string | null)
(query)
fecha
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links
integraciones

auth


POST
/auth/jwt/login
Auth:Jwt.Login

Parameters
Try it out
No parameters

Request body

application/x-www-form-urlencoded
grant_type
string | (string | null)
pattern: ^password$
username *
string
password *
string($password)
scope
string
client_id
string | (string | null)
client_secret
string | (string | null)($password)
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiOTIyMWZmYzktNjQwZi00MzcyLTg2ZDMtY2U2NDJjYmE1NjAzIiwiYXVkIjoiZmFzdGFwaS11c2VyczphdXRoIiwiZXhwIjoxNTcxNTA0MTkzfQ.M10bjOe45I5Ncu_uXvOmVV8QxnL-nZfcH96U90JaocI",
  "token_type": "bearer"
}
No links
400	
Bad Request

Media type

application/json
Examples

Bad credentials or the user is inactive.
Example Value
Schema
{
  "detail": "LOGIN_BAD_CREDENTIALS"
}
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

POST
/auth/jwt/logout
Auth:Jwt.Logout


Parameters
Try it out
No parameters

Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
401	
Missing token or inactive user.

No links

POST
/auth/register
Register:Register

Parameters
Try it out
No parameters

Request body

application/json
Example Value
Schema
{
  "email": "user@example.com",
  "password": "string",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false,
  "nombre": "string",
  "rol": "string"
}
Responses
Code	Description	Links
201	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
{
  "id": 0,
  "email": "user@example.com",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false,
  "nombre": "string",
  "rol": "string"
}
No links
400	
Bad Request

Media type

application/json
Examples

A user with this email already exists.
Example Value
Schema
{
  "detail": "REGISTER_USER_ALREADY_EXISTS"
}
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

POST
/auth/forgot-password
Reset:Forgot Password

Parameters
Try it out
No parameters

Request body

application/json
Example Value
Schema
{
  "email": "user@example.com"
}
Responses
Code	Description	Links
202	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

POST
/auth/reset-password
Reset:Reset Password

Parameters
Try it out
No parameters

Request body

application/json
Example Value
Schema
{
  "token": "string",
  "password": "string"
}
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
400	
Bad Request

Media type

application/json
Examples

Bad or expired token.
Example Value
Schema
{
  "detail": "RESET_PASSWORD_BAD_TOKEN"
}
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

POST
/auth/request-verify-token
Verify:Request-Token

Parameters
Try it out
No parameters

Request body

application/json
Example Value
Schema
{
  "email": "user@example.com"
}
Responses
Code	Description	Links
202	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]