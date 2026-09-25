# -*- mode: ruby -*-
# vi: set ft=ruby :

# Fase 1: Configuración de la Máquina Virtual con Vagrant
Vagrant.configure("2") do |config|

  # 1. Sistema operativo base: Ubuntu Server 22.04 LTS
  config.vm.box = "bento/ubuntu-22.04"

  # 2. Configuración de Red
  # IP Privada fija para acceder desde la máquina anfitriona
  config.vm.network "private_network", ip: "192.168.56.20"

  # Port Forwarding: redirige el puerto 8000 de la VM a tu computadora
  config.vm.network "forwarded_port", guest: 8000, host: 8000

  # 3. Sincronización de carpetas: monta la carpeta actual en /vagrant dentro de la VM
  config.vm.synced_folder ".", "/vagrant"

  # 4. Configuración de recursos para VirtualBox
  config.vm.provider "virtualbox" do |vb|
    vb.name = "UbuntuServer-Mascotas"
    vb.memory = "2048"
    vb.cpus = 2
  end

  # 5. Aprovisionamiento básico con comandos de Linux
  config.vm.provision "shell", inline: <<-SHELL
    echo "Actualizando paquetes e instalando Python y SQLite..."
    apt-get update -y
    apt-get install -y python3 python3-pip python3-venv sqlite3

    echo "Listo. Para iniciar el proyecto entra con: vagrant ssh"
  SHELL

end
