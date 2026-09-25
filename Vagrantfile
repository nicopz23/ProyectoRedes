# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.box = "bento/ubuntu-22.04"

  # IP Privada fija
  config.vm.network "private_network", ip: "192.168.56.20"

  # Port Forwarding para SSH y FastAPI
  config.vm.network "forwarded_port", guest: 22, host: 2222, host_ip: "0.0.0.0", id: "ssh", auto_correct: true
  config.vm.network "forwarded_port", guest: 8000, host: 8000, auto_correct: true

  # Sincronización de carpetas
  config.vm.synced_folder ".", "/vagrant"

  # Configuración para VirtualBox
  config.vm.provider "virtualbox" do |vb|
    vb.name = "UbuntuServer-Mascotas"
    vb.memory = 2048
    vb.cpus = 2
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
  end

  # Aprovisionamiento: instala paquetes y levanta el servicio con systemd
  config.vm.provision "shell", inline: <<-SHELL
    set -e
    echo "Actualizando paquetes e instalando Python y SQLite..."
    apt-get update -y
    apt-get install -y python3 python3-pip python3-venv sqlite3

    echo "Creando entorno virtual e instalando dependencias..."
    python3 -m venv /home/vagrant/venv
    /home/vagrant/venv/bin/pip install -r /vagrant/requirements.txt

    echo "Creando servicio systemd..."
    cat << 'EOF' > /etc/systemd/system/gestion-mascotas.service
[Unit]
Description=Servicio Gestion de Mascotas
After=network.target

[Service]
User=vagrant
WorkingDirectory=/vagrant
ExecStart=/home/vagrant/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable --now gestion-mascotas.service

    echo "Aplicacion iniciada exitosamente en el puerto 8000."
  SHELL

end
