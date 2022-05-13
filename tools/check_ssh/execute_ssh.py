import paramiko
import logging

def handle_ssh():
    logging.error("get ssh library")
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    host = "221.139.0.145"
    user = "sunjoo.park"
    password = "ParkKeonYul1@"
    logging.error("Make connection")
    cli.connect(hostname=host, port=2222, username=user, password=password)
    logging.error("Prepare environment")
    _, out, _ = cli.exec_command("pkill -f 'java -jar.*agent.*'")
    _, out1, _ = cli.exec_command("rm -rfv /tmp/agent.jar")
    _, out2, err = cli.exec_command("curl https://scheduler.netspresso.ai/jnlpJars/agent.jar -o /tmp/agent.jar")
    logging.error("".join(err.readlines()))
    #import time
    #time.sleep(5)
    logging.error("Run command")
    _, out, _ = cli.exec_command("hostname")
    logging.error("".join(out.readlines()))
    #_, out3, err = cli.exec_command("java -jar /tmp/agent.jar -jnlpUrl https://scheduler.netspresso.ai/computer/testagent/jenkins-agent.jnlp -secret 4a0381d048bdae45b7d106ec353a0daabd36a16e15b0e5003a2b6a28bcc1f93d -workDir \"/tmp\" &")
    _ , out3, err2 = cli.exec_command('java -jar /tmp/agent.jar -jnlpUrl https://scheduler.netspresso.ai/computer/testagent/jenkins-agent.jnlp -secret 4a0381d048bdae45b7d106ec353a0daabd36a16e15b0e5003a2b6a28bcc1f93d -workDir "/tmp" &')
    #print(' '.join(err2.readlines()))
    cli.close()
if __name__ == "__main__":
    handle_ssh()
    print("hello, world")