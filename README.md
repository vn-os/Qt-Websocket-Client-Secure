### Websocket Client (WS & WSS) ###
_ _ _

##### INSTALLATION #####

> $ pip3 install -r requirements.txt

##### COMMANDS #####

> Install
>
>> $ pip install -r src\main\python\requirements.txt
>>
>> $ fbs run

> Generate SSL file for both `localhost` and `127.0.0.1`
>
>> $ openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes -keyout local.pem -out local.pem -subj "/CN=localhost" -addext "subjectAltName=IP:127.0.0.1"

##### SCREENSHOTS #####

![](screenshots/1.PNG)
![](screenshots/2.PNG)
![](screenshots/3.PNG)

_ _ _

Website: http://vic.onl/
