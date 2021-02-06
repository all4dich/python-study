agent_config = {
    "name": "z-strike",
    "nodeDescription": "description-strike",
    "numExecutors": "1",
    "remoteFS": "/tmp",
    "labelString": "do-not-use",
    "mode": "NORMAL",
    "": ["hudson.plugins.sshslaves.SSHLauncher", "hudson.slaves.RetentionStrategy$Always"],
    "launcher": {
        "stapler-class": "hudson.plugins.sshslaves.SSHLauncher",
        "$class": "hudson.plugins.sshslaves.SSHLauncher",
        "host": "192.168.100.100",
        "includeUser": "false",
        "credentialsId": "ad_info",
        "": "0",
        "sshHostKeyVerificationStrategy": {
            "stapler-class": "hudson.plugins.sshslaves.verifiers.KnownHostsFileKeyVerificationStrategy",
            "$class": "hudson.plugins.sshslaves.verifiers.KnownHostsFileKeyVerificationStrategy"
        },
        "port": "22",
        "javaPath": "",
        "jvmOptions": "",
        "prefixStartSlaveCmd": "",
        "suffixStartSlaveCmd": "",
        "launchTimeoutSeconds": "",
        "maxNumRetries": "",
        "retryWaitTime": ""
    },
    "retentionStrategy": {
        "stapler-class": "hudson.slaves.RetentionStrategy$Always",
        "$class": "hudson.slaves.RetentionStrategy$Always"
    },
    "nodeProperties": {
        "stapler-class-bag": "true",
        "hudson-slaves-EnvironmentVariablesNodeProperty": {
            "env": {
                "key": "a", "value": "1"
            }
        }
    },
    "type": "hudson.slaves.DumbSlave"
}
