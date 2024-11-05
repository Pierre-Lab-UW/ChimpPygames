sudo echo "dtoverlay=i2c-gpio,bus=4,i2c_gpio_delay_us=1,i2c_gpio_sda=10,i2c_gpio_scl=9" >> /boot/config.txt
sudo echo "dtoverlay=i2c-rtc,ds1307" >> /boot/config.txt

sudo apt-get install python-smbus i2c-tools
sudo i2cdetect -y 4


sudo modprobe rtc-ds1307
sudo bash
echo ds1307 0x68 > /sys/class/i2c-adapter/i2c-4/new_device
exit
sudo hwclock -r
sudo hwclock -w
sudo hwclock -r

sudo apt-get -y remove fake-hwclock
sudo update-rc.d -f fake-hwclock remove
sudo systemctl disable fake-hwclock

echo "rtc-ds1307" | sudo tee -a /etc/modules

#enable i2c
sudo raspi-config nonint do_i2c 0
#add line to txt file
sudo sed '18 a\
echo ds1307 0x68 > /sys/class/i2c-adapter/i2c-4/new_device\
sudo hwclock -s' /etc/rc.local > temp && mv temp /etc/rc.local
#reboot
sudo reboot