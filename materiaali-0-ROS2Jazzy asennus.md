## ROS2 Jazzy ympäristön asennus

### ROS2 versiot ja Ubuntu

Tässä materiaalissa käytetään ROS2 Jazzy ympäristöä. ROS2:n versiot kulkevat aakkosjärjestyksessä annettavilla nimillä (esimerkiksi Humble, Iron, Jazzy, ...). Kirjoitushetkellä Jazzy on uusin pitkän tuen version. ROS2:n periaatteisiin kuuluu se, että kukin versio rakennetaan jonkin tietyn Ubuntun version päälle, eikä tukea muille Ubuntun versioille mietitä. Jazzyn kohdalla tämä tarkoittaa sitoutumista Ubuntu 24.04 LTS:ään. Jos haluat kokeilla ROS2-ohjelmointia, Ubuntun asentaminen virtuaalikoneelle on järkevä ratkaisu. Tämän materiaalin kannalta on suositeltavaa rakentaa kokonaisuus, jossa (Ubuntu 24.04 ja) ROS2 Jazzy on asennettuna Raspberry Pi 5:lle ja erikseen toiselle tietokoneelle, jonka kautta ohjelmointi ja etäohjaus tehdään. On kuitenkin mahdollista asentaa ROS-ympäristö pelkästään Raspberrylle ja käyttää sitä suoraan SSH-yhteydellä esimerkiksi Windows-koneelta (jolle on asennettuna jokin kehitysympäristö kuten VSCode).

### ROS2 Jazzyn asentaminen

On suositeltavaa noudattaa suoraan ROS2:n virallista dokumentaatiota ROS2-ympäristön asentamisessa. Vaihtoehdot Jazzyn asentamiseen löytyy osoitteesta [https://docs.ros.org/en/jazzy/Installation.html](https://docs.ros.org/en/jazzy/Installation.html). Suositeltavin tapa on hyödyntää valmiiksi käännettyjä pakettijakeluita, Jazzyn tapauksessa [https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html).

Tähän tekstiin on poimittu kopiot tarvittavista käskyistä, mutta niiden selitykset jäävät virallisen dokumentaation varaan.

**Set locale**

```bash
locale  # tarkista että on UTF-8

sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

locale  # Varmistetaan asetukset
```

**Enable required repositories**

```bash
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

**Install development tools**

```bash
sudo apt update && sudo apt install ros-dev-tools
```

**ROS2 installation**

```bash
sudo apt update
sudo apt upgrade
sudo apt install ros-jazzy-desktop
source /opt/ros/jazzy/setup.bash # otetaan ROS2 ympäristö käyttöön tässä päätteessä
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc # lisätään sama käsky myös ~/.bashr-tiedostoon, jotta ympäristö on aina käytettävissä kun uusi pääte avataan.
```

### Try an example

Kokeile kahdessa päätteessä (tarvittaessa `source`-komento kirjoittaen) ROS-topicin käyttöä demo-ohjelmalla:

> Pääte 1
>
> ```bash
> ros2 run demo_nodes_cpp talker
> ```
>
> Pääte 2
>
> ```bash
> ros2 run demo_nodes_cpp listener
> ```

### Uninstalling ROS2

Tarvittaessa voit poistaa ROS2 asennuksen seuraavasti

```bash
sudo apt remove ~nros-jazzy-* && sudo apt autoremove
# Tarvittaessa voit poistaa myös repositoriot
sudo rm /etc/apt/sources.list.d/ros2.list
sudo apt update
sudo apt autoremove
sudo apt upgrade
```
