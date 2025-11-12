## ROS2 Jazzy Environment Installation

### ROS2 Versions and Ubuntu

This material uses the ROS2 Jazzy environment. ROS2 versions are named alphabetically (e.g., Humble, Iron, Jazzy, ...). At the time of writing, Jazzy is the newest long-term support version. One of ROS2's principles is that each version is built on a specific Ubuntu version, and support for other Ubuntu versions is not considered. For Jazzy, this means committing to Ubuntu 24.04 LTS. If you want to try ROS2 programming, installing Ubuntu on a virtual machine is a sensible solution. For the purposes of this material, it is recommended to build a system where (Ubuntu 24.04 and) ROS2 Jazzy is installed on a Raspberry Pi 5 and separately on another computer, from which programming and remote control are done. However, it is possible to install the ROS environment only on the Raspberry Pi and use it directly via an SSH connection from, for example, a Windows machine (which has a development environment such as VSCode installed).

### Installing ROS2 Jazzy

It is recommended to follow the official ROS2 documentation directly for installing the ROS2 environment. Options for installing Jazzy can be found at [https://docs.ros.org/en/jazzy/Installation.html](https://docs.ros.org/en/jazzy/Installation.html). The most recommended way is to utilize pre-compiled package distributions, in Jazzy's case [https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html).

This text contains copied commands, but their explanations are left to the official documentation.

**Locale settings**

```bash
locale  # check that it is UTF-8

sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

locale  # Confirm settings
```

**Enabling necessary repositories**

```bash
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

**Installing development tools**

```bash
sudo apt update && sudo apt install ros-dev-tools
```

**ROS2 installation**

```bash
sudo apt update
sudo apt upgrade
sudo apt install ros-jazzy-desktop
source /opt/ros/jazzy/setup.bash # enable ROS2 environment in this terminal
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc # add the same command to ~/.bashrc, so the environment is always available when a new terminal is opened.
```

### Try an example

Try using a ROS topic with a demo program in two terminals (writing the `source` command if necessary):

> Terminal 1
>
> ```bash
> ros2 run demo_nodes_cpp talker
> ```
>
> Terminal 2
>
> ```bash
> ros2 run demo_nodes_cpp listener
> ```

### Uninstalling ROS2

If necessary, you can uninstall the ROS2 installation as follows:

```bash
sudo apt remove ~nros-jazzy-* && sudo apt autoremove
# If necessary, you can also remove the repositories
sudo rm /etc/apt/sources.list.d/ros2.list
sudo apt update
sudo apt autoremove
sudo apt upgrade
```
