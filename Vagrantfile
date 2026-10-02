# -*- mode: ruby -*-
# vi: set ft=ruby :

# Despliegue en 2 Servidores (Frontend y Backend) con dominio petmanager.local
# Proyecto de Curso – 1ª parte | Redes e Infraestructura 2026-09

Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-22.04"

  # ==========================================
  # SERVIDOR 1: FRONTEND (Nginx Web Server)
  # ==========================================
  config.vm.define "front" do |front|
    front.vm.hostname = "front.petmanager.local"
    front.vm.network "private_network", ip: "192.168.56.10"
    front.vm.network "forwarded_port", guest: 80, host: 8080, auto_correct: true
    front.vm.synced_folder ".", "/vagrant"

    front.vm.provider "virtualbox" do |vb|
      vb.name = "UbuntuServer-Front"
      vb.memory = 1024
      vb.cpus = 1
      vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    end

    front.vm.provision "shell", inline: <<-SHELL
      set -e
      apt-get update -y
      apt-get install -y nginx

      cat << 'EOF' > /etc/nginx/sites-available/petmanager
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name petmanager.local www.petmanager.local 192.168.56.10;

    # Archivos estáticos del frontend
    root /vagrant/frontend;
    index index.html;
    sendfile off;

    location / {
        try_files $uri $uri/ =404;
    }

    # Proxy inverso hacia el Servidor de Backend (192.168.56.20:8000)
    location ~ ^/(auth|admin|dashboard|mascotas|propietarios|docs|openapi.json) {
        proxy_pass http://192.168.56.20:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

      rm -f /etc/nginx/sites-enabled/default
      ln -sf /etc/nginx/sites-available/petmanager /etc/nginx/sites-enabled/
      systemctl restart nginx
      systemctl enable nginx
    SHELL
  end

  # ==========================================
  # SERVIDOR 2: BACKEND (FastAPI / Uvicorn API REST)
  # ==========================================
  config.vm.define "back" do |back|
    back.vm.hostname = "back.petmanager.local"
    back.vm.network "private_network", ip: "192.168.56.20"
    back.vm.network "forwarded_port", guest: 8000, host: 8000, auto_correct: true
    back.vm.synced_folder ".", "/vagrant"

    back.vm.provider "virtualbox" do |vb|
      vb.name = "UbuntuServer-Back"
      vb.memory = 1536
      vb.cpus = 1
      vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    end

    back.vm.provision "shell", inline: <<-SHELL
      set -e
      apt-get update -y
      apt-get install -y python3 python3-pip python3-venv sqlite3

      python3 -m venv /home/vagrant/venv
      /home/vagrant/venv/bin/pip install --upgrade pip
      /home/vagrant/venv/bin/pip install -r /vagrant/requirements.txt

      cat << 'EOF' > /etc/systemd/system/gestion-mascotas.service
[Unit]
Description=Servicio API REST Gestion de Mascotas y Censo
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

    SHELL
  end

end
