agent_data_original = {
    "name": node_name,
    "nodeDescription": node_ip,
    "numExecutors": "1",
    "remoteFS": "/tmp/",
    "labelString": "do-not-use",
    "mode": "NORMAL",
    "": ["hudson.slaves.CommandLauncher", "hudson.slaves.RetentionStrategy$Always"],
    "launcher": {
        "stapler-class": "hudson.slaves.CommandLauncher",
        "$class": "hudson.slaves.CommandLauncher",
        "command": "/binary/build_results/tools/agent_connect.sh 156.147.61.181"
    },
    "retentionStrategy": {
        "stapler-class": "hudson.slaves.RetentionStrategy$Always",
        "$class": "hudson.slaves.RetentionStrategy$Always"
    },
    "nodeProperties": {
        "stapler-class-bag": "true",
        "hudson-slaves-EnvironmentVariablesNodeProperty": {
            "env": {
                "key": "you_name", "value": "you_value"
            }
        }
    },
    "type": "hudson.slaves.DumbSlave"
}