#!/usr/bin/env python

import subprocess
import time

playbooks_dir = "k8s_playbooks"

def run_command(cmd):
    proc = subprocess.run(cmd.split(" "), capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
        raise Exception("Failed to run %s" % cmd)
    return proc.stdout


def generate_hosts(raw_ssh_config):
    ssh_config = {}
    # Parse and generate the ssh config per host.
    state = 0
    host = None
    for line in raw_ssh_config.splitlines():
        if len(line) == 0:
            state = 0
        else:
            k, v = line.strip().split(" ")
            if state == 0:
                state = 1
                host = v
                ssh_config[host] = {}
            else:
                ssh_config[host][k] = v
    # Generate the hosts file.
    masters_template = """[masters]
    master ansible_host=%s ansible_user=%s ansible_ssh_private_key_file=%s become=yes\n""" % \
                       (ssh_config["master"]["HostName"],
                        ssh_config["master"]["User"],
                        ssh_config["master"]["IdentityFile"])
    workers_template = """[workers]
    """
    worker = "%s ansible_host=%s ansible_user=%s ansible_ssh_private_key_file=%s become=yes\n"
    for k, v in ssh_config.items():
        if k == "master":
            continue
        workers_template += worker % (k, v["HostName"], v["User"], v["IdentityFile"])
    with open("hosts", "w") as fd:
        fd.write(masters_template)
        fd.write(workers_template)
    return ssh_config


def main():
    print(run_command("vagrant up"))
    raw_ssh_config = run_command("vagrant ssh-config")
    print(raw_ssh_config)
    ssh_config = generate_hosts(raw_ssh_config)

    # Install the dependencies.
    print(run_command("ansible-playbook -i hosts %s/kube-dependencies.yml" % playbooks_dir))

    # Configure the master.
    print(run_command("ansible-playbook -i hosts %s/master.yml" % playbooks_dir))

    # Configure the workers.
    print(run_command("ansible-playbook -i hosts %s/workers.yml" % playbooks_dir))

    # Copy the kubeconfig locally.
    mc = ssh_config["master"]
    run_command("scp -i %s %s@%s:.kube/config /tmp/kubeconfig_local" % (mc["IdentityFile"], mc["User"], mc["HostName"]))

    print("Use /tmp/kubeconfig_local to access the k8s cluster")


if __name__ == '__main__':
    try:
        start_time = time.time()
        main()
        end_time = time.time()
        print("Time taken: %.2f seconds" % (end_time - start_time))
    except:
        raise
