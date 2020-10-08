# -*- mode: ruby -*-
# vi: set ft=ruby :

IMAGE_NAME = "centos/8"
N = 2

Vagrant.configure("2") do |config|
    config.ssh.insert_key = false

    config.vm.provider "libvirt" do |v|
        v.memory = 2048
        v.cpus = 2
    end
      
    config.vm.define "master" do |master|
        master.vm.box = IMAGE_NAME
        master.vm.hostname = "master"
    end

    (1..N).each do |i|
        config.vm.define "worker-#{i}" do |node|
            node.vm.box = IMAGE_NAME
            node.vm.hostname = "worker-#{i}"
        end
    end
end
