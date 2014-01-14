# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
  config.vm.box = "raring64"
  config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/raring/current/raring-server-cloudimg-amd64-vagrant-disk1.box"
  config.vm.provision :shell, :path => "provision.sh"
  config.ssh.forward_agent = true
  config.vm.forward_port 8000, 8000

  config.vm.define :scivm do |pm_config|
    pm_config.vm.host_name = "scivm.local"
    pm_config.vm.network :hostonly, "10.10.10.25"
    pm_config.vm.share_folder "scivm", "/opt/app", "./"
  end
end

Vagrant.configure("2") do |config|
    config.vm.provider :virtualbox do |v|
        v.customize ["modifyvm", :id, "--memory", 2048]
    end
    config.vm.provider :vmware_fusion do |v|
      config.vm.define :scivm do |s|
        v.vmx["memsize"] = "2048"
      end
      config.vm.define :scivm do |s|
        v.vmx["displayName"] = "scivm"
      end
    end
end
