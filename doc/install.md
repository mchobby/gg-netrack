# Prerequisite

Need for python 2.7 on Raspberry Pi 3.

# Install 

Install PIP

```
sudo apt-get install pip
```

install psycopg2

```
sudo apt-get install python-psycopg2
```

# Configuration

 # Create ini file

```
cp netrack.ini.sample netrack.ini
nano netrack.ini
```
Fill in the fields with the needed connection data

Database connectivity canbe tested with
```
python db-test.py
```

 # Disable Screen Blanking

```
sudo nano /etc/rc.local
```

add the instruction

```
setterm -blank 0
```

 # Tuning font size on the screen

The font size on the screen is very small and not convenient for
monitoring

```
sudo nano /etc/default/console-setup
```

change the FONTFACE and FONTSIZE parameters

```
FONTFACE="Terminus"
FONTSIZE="14x28"
