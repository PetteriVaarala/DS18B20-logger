# DS18B20-logger

## Installation
```
git clone https://github.com/PetteriVaarala/DS18B20-logger.git

sudo aptitude install python-pip
sudo pip install -U pip
sudo pip install influxdb
cp DS18B20-logger.sample.conf DS18B20-logger.conf
vi DS18B20-logger.conf
crontab -e
  * * * * * ~/DS18B20-logger/DS18B20-logger.py >> ~/DS18B20-logger/DS18B20-logger.log 2>&1
```
