sudo apt update;sudo apt upgrade -y
sudo apt-get install -y apache2    libapache2-mod-wsgi-py3    python3    python3-pip    vim
export LC_ALL=C.UTF-8
sudo -H pip install --upgrade pip
sudo -H pip install -r requirements.txt
git clone https://github.com/splasky/flask_login.git
sudo ln -sT ~/flask_login /var/www/flask_login
sudo rm /etc/apache2/sites-available/000-default.conf
sudo ln -sT ~/flask_login/000-default.conf /etc/apache2/sites-available/000-default.conf
sudo service apache2 restart
