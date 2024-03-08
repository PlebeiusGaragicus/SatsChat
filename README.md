these are old instructions and will no longer work.

---

## `apt-update` and install prerequesties

```sh
apt-get update
apt-get upgrade -y

apt-get install -y git curl python3-venv python3-pip redis-server pkg-config

# pkg-config required for python sepsecp256k1 library, and therefore bolt11 library

```

## Configure Redis database
```sh
# ensure it's working
systemctl status redis-server
redis-cli ping

# TODO - configure it!
# nano /etc/redis/redis.conf
# systemctl restart redis-server

# enable
systemctl enable redis-server

```

## install cloudflared
```sh
# ensure you choose the debian install commands
```


## change root PS1 to show completion...
```sh
echo 'export PS1="\n\[\e[1;35m\]<\[\e[1;31m\]\u\[\e[1;35m\]> \[\e[1;34m\]\h\[\e[1;35m\] [\w] \[\e[1;36m\]\$ \[\e[0m\]\n"' >> ~/.bashrc
```



## Create a non-`root` user

```sh
adduser satoshi
usermod -aG sudo satoshi
```

Then, log out of `root` and log in as this user

```sh
# signal that we are non-root
echo 'export PS1="\n\[\e[1;35m\](\[\e[1;31m\]\u\[\e[1;35m\]@\[\e[1;34m\]\h\[\e[1;35m\]) [\w] \[\e[33;3m\]\A\[\e[0m\] \[\e[1;36m\]\$ \[\e[0m\]\n"' >> ~/.bashrc

# log out and in again...
```

## clone the repo

```sh
git clone https://github.com/PlebeiusGaragicus/satschat.git
cd satschat
```

## configure the Python virtual environment

```sh
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## create the `.env` file with API keys

```sh
cat << EOF > .env
OPENAI_API_KEY=
GEMINI_API_KEY=
MISTRAL_API_KEY=
EOF

nano .env
```

Copy and paste in any API keys you have.

## setup a `systemd` service to launch the application

Note: This will need `root` access.  Log in as `root` for these next steps.


```sh
cat << EOF > /etc/systemd/system/satschat.service
[Unit]
Description=SatsChat Service
After=network.target

[Service]
User=satoshi
WorkingDirectory=/home/satoshi/satschat
ExecStart=/bin/bash -c "/home/satoshi/satschat/production"
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

nano /etc/systemd/system/satschat.service
```

Also, replace `satoshi` with the non-root Linux username that you created earlier.

## start the service and monitor for errors

```sh
systemctl start satschat
systemctl status satschat

# works..?  If so:
systemctl enable satschat

# watch it run via:
journalctl -u satschat -f # hitting 'q' will exit
```

## Visit the application

Open a browser and go to the IP address of the server at port 8501. To determine the ip address, run the `ip addr` command.

For example, if your ip address is `192.169.10.200`, then put `192.169.10.200:8501` in your browser and it should work.

If you're running this locally instead of on a dedicated server then visit [localhost:8501](http://localhost:8501)
