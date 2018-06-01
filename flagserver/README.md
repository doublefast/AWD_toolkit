# flagserver

## run
```
python2/3 main.py
```
## submit flag
### GET method
http://127.0.0.1:62088/flag/Flag_In_Here  
http://127.0.0.1:62088/flag/Flag_In_Here/Ip_In_Here

use in Gamebox
```
#retry -t 2 ,timeout -T 2,https --no-check-certificat
wget -O- -q -T 2 -t 2 http://127.0.0.1:62088/flag/`cat flag`

#retry --retry 2 ,timeout -m 2,https -k
curl -m 2 --retry 2 -s http://127.0.0.1:62088/flag/`cat flag`
```


### POST method
/flag  Postdata: flag=Flag_In_Here  
/flag  Postdata: flag=Flag_In_Here&ip=Ip_In_Here  
/flagx  Postdata: Flag_In_Here  

use in Gamebox

```
wget -O- -q -T 2 -t 2 --post-data flag=`cat flag` http://127.0.0.1:62088/flag
curl -d flag=`cat flag` http://127.0.0.1:62088/flag

wget -O- -q -T 2 -t 2 --post-file flag http://127.0.0.1:62088/flagx
cat flag |curl -d @- -m 2 --retry 2 -s http://127.0.0.1:62088/flagx
curl -d @flag -m 2 --retry 2 -s http://127.0.0.1:62088/flagx

```

## Show flag
HTML  http://127.0.0.1:62088/static/givemeflag/index.html

json  http://127.0.0.1:62088/showflagjson

## Clear Data
```
rm -f db.db
```