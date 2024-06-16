import os
import json
import jsonpatch
from utils import gnmi_set, gnmi_get, gnmi_dump

import pytest

patch_file = "/tmp/gcu.patch"
config_file = "/tmp/config_db.json.tmp"
checkpoint_file = "/etc/sonic/config.cp.json"

def create_dir(path):
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)

def create_checkpoint(file_name, text):
    create_dir(os.path.dirname(file_name))
    file_object = open(file_name, "w")
    file_object.write(text)
    file_object.close()
    return

test_data_aaa_patch = [
    {
        "test_name": "aaa_tc1_add_config",
        "operations": [
            {
                "op": "update",
                "path": "/sonic-db:CONFIG_DB/localhost/AAA",
                "value": {
                    "accounting": {
                        "login": "tacacs+,local"
                    },
                    "authentication": {
                        "debug": "True",
                        "failthrough": "True",
                        "fallback": "True",
                        "login": "tacacs+",
                        "trace": "True"
                    },
                    "authorization": {
                        "login": "tacacs+,local"
                    }
                }
            }
        ],
        "origin_json": {},
        "target_json": {
            "AAA": {
                "accounting": {"login": "tacacs+,local"},
                "authentication": {"debug": "True", "failthrough": "True", "fallback": "True", "login": "tacacs+", "trace": "True"},
                "authorization": {"login": "tacacs+,local"}
            }
        }
    },
    {
        "test_name": "aaa_tc1_replace",
        "operations": [
            {
                "op": "replace",
                "path": "/sonic-db:CONFIG_DB/localhost/AAA/authorization/login",
                "value": "tacacs+"
            },
            {
                "op": "replace",
                "path": "/sonic-db:CONFIG_DB/localhost/AAA/authentication/login",
                "value": "tacacs+"
            },
            {
                "op": "replace",
                "path": "/sonic-db:CONFIG_DB/localhost/AAA/accounting/login",
                "value": "tacacs+"
            },
        ],
        "origin_json": {
            "AAA": {
                "accounting": {"login": "tacacs+,local"},
                "authentication": {"debug": "True", "failthrough": "True", "fallback": "True", "login": "tacacs+", "trace": "True"},
                "authorization": {"login": "tacacs+,local"}
            }
        },
        "target_json": {
            "AAA": {
                "accounting": {"login": "tacacs+"},
                "authentication": {"debug": "True", "failthrough": "True", "fallback": "True", "login": "tacacs+", "trace": "True"},
                "authorization": {"login": "tacacs+"}
            }
        }
    },
    {
        "test_name": "aaa_tc1_add_duplicate",
        "operations": [
            {
                "op": "update",
                "path": "/sonic-db:CONFIG_DB/localhost/AAA/authorization/login",
                "value": "tacacs+"
            },
            {
                "op": "update",
                "path": "/sonic-db:CONFIG_DB/localhost/AAA/authorization/login",
                "value": "tacacs+"
            },
            {
                "op": "update",
                "path": "/sonic-db:CONFIG_DB/localhost/AAA/authorization/login",
                "value": "tacacs+"
            }
        ],
        "origin_json": {
            "AAA": {
                "authorization": {"login": ""}
            }
        },
        "target_json": {
            "AAA": {
                "authorization": {"login": "tacacs+"}
            }
        }
    },
    {
        "test_name": "aaa_tc1_remove",
        "operations": [
            {
                "op": "del",
                "path": "/sonic-db:CONFIG_DB/localhost/AAA",
            }
        ],
        "origin_json": {
            "AAA": {
                "authorization": {"login": ""}
            }
        },
        "target_json": {}
    },
    {
        "test_name": "tacacs_global_tc2_add_config",
        "operations": [
            {
                "op": "update",
                "path": "/sonic-db:CONFIG_DB/localhost/TACPLUS",
                "value": {
                    "global": {
                        "auth_type": "login",
                        "passkey": "testing123",
                        "timeout": "10"
                    }
                }
            }
        ],
        "origin_json": {},
        "target_json": {
            "TACPLUS": {
                "global": {
                    "auth_type": "login",
                    "passkey": "testing123",
                    "timeout": "10"
                }
            }
        }
    },
    {
        "test_name": "tacacs_global_tc2_duplicate_input",
        "operations": [
            {
                "op": "update",
                "path": "/sonic-db:CONFIG_DB/localhost/TACPLUS",
                "value": {
                    "global": {
                        "auth_type": "login",
                        "passkey": "testing123",
                        "timeout": "10"
                    }
                }
            }
        ],
        "origin_json": {
            "TACPLUS": {
                "global": {
                    "auth_type": "login",
                    "passkey": "testing123",
                    "timeout": "10"
                }
            }
        },
        "target_json": {
            "TACPLUS": {
                "global": {
                    "auth_type": "login",
                    "passkey": "testing123",
                    "timeout": "10"
                }
            }
        }
    },
    {
        "test_name": "tacacs_global_tc2_remove",
        "operations": [
            {
                "op": "del",
                "path": "/sonic-db:CONFIG_DB/localhost/TACPLUS"
            }
        ],
        "origin_json": {
            "TACPLUS": {
                "global": {
                    "auth_type": "login",
                    "passkey": "testing123",
                    "timeout": "10"
                }
            }
        },
        "target_json": {}
    },
    {
        "test_name": "tacacs_server_tc3_add_init",
        "operations": [
            {
                "op": "update",
                "path": "/sonic-db:CONFIG_DB/localhost/TACPLUS_SERVER",
                "value": {
                    "100.127.20.21": {
                        "auth_type": "login",
                        "passkey": "testing123",
                        "priority": "10",
                        "tcp_port": "50",
                        "timeout": "10"
                    },
                    "fc10::21": {
                        "auth_type": "login",
                        "passkey": "testing123",
                        "priority": "10",
                        "tcp_port": "50",
                        "timeout": "10"
                    }
                }
            }
        ],
        "origin_json": {},
        "target_json": {
            "TACPLUS_SERVER": {
                "100.127.20.21": {
                    "auth_type": "login",
                    "passkey": "testing123",
                    "priority": "10",
                    "tcp_port": "50",
                    "timeout": "10"
                },
                "fc10::21": {
                    "auth_type": "login",
                    "passkey": "testing123",
                    "priority": "10",
                    "tcp_port": "50",
                    "timeout": "10"
                }
            }
        }
    },
    {
        "test_name": "tacacs_server_tc3_add_duplicate",
        "operations": [
            {
                "op": "update",
                "path": "/sonic-db:CONFIG_DB/localhost/TACPLUS_SERVER/100.127.20.21",
                "value": {
                    "auth_type": "login",
                    "passkey": "testing123",
                    "priority": "10",
                    "tcp_port": "50",
                    "timeout": "10"
                }
            }
        ],
        "origin_json": {
            "TACPLUS_SERVER": {
                "100.127.20.21": {
                    "auth_type": "login",
                    "passkey": "testing123",
                    "priority": "10",
                    "tcp_port": "50",
                    "timeout": "10"
                },
                "fc10::21": {
                    "auth_type": "login",
                    "passkey": "testing123",
                    "priority": "10",
                    "tcp_port": "50",
                    "timeout": "10"
                }
            }
        },
        "target_json": {
            "TACPLUS_SERVER": {
                "100.127.20.21": {
                    "auth_type": "login",
                    "passkey": "testing123",
                    "priority": "10",
                    "tcp_port": "50",
                    "timeout": "10"
                },
                "fc10::21": {
                    "auth_type": "login",
                    "passkey": "testing123",
                    "priority": "10",
                    "tcp_port": "50",
                    "timeout": "10"
                }
            }
        }
    },
    {
        "test_name": "tacacs_server_tc3_remove",
        "operations": [
            {
                "op": "del",
                "path": "/sonic-db:CONFIG_DB/localhost/TACPLUS_SERVER"
            }
        ],
        "origin_json": {
            "TACPLUS_SERVER": {
                "100.127.20.21": {
                    "auth_type": "login",
                    "passkey": "testing123",
                    "priority": "10",
                    "tcp_port": "50",
                    "timeout": "10"
                },
                "fc10::21": {
                    "auth_type": "login",
                    "passkey": "testing123",
                    "priority": "10",
                    "tcp_port": "50",
                    "timeout": "10"
                }
            }
        },
        "target_json": {}
    }
]

test_data_bgp_prefix_patch = [
    {
        "test_name": "bgp_prefix_tc1_add_config",
        "operations": [
            {
                "op": "update",
                "path": "/sonic-db:CONFIG_DB/localhost/BGP_ALLOWED_PREFIXES",
                "value": {
                    "DEPLOYMENT_ID|0|1010:1010": {
                        "prefixes_v4": [
                            "10.20.0.0/16"
                        ],
                        "prefixes_v6": [
                            "fc01:20::/64"
                        ]
                    }
                }
            }
        ],
        "origin_json": {},
        "target_json": {
            "BGP_ALLOWED_PREFIXES": {
                "DEPLOYMENT_ID|0|1010:1010": {
                    "prefixes_v4": [
                        "10.20.0.0/16"
                    ],
                    "prefixes_v6": [
                        "fc01:20::/64"
                    ]
                }
            }
        }
    },
    {
        "test_name": "bgp_prefix_tc1_replace",
        "operations": [
            {
                "op": "replace",
                "path": "/sonic-db:CONFIG_DB/localhost/BGP_ALLOWED_PREFIXES/DEPLOYMENT_ID\\|0\\|1010:1010/prefixes_v6/0",
                "value": "fc01:30::/64"
            },
            {
                "op": "replace",
                "path": "/sonic-db:CONFIG_DB/localhost/BGP_ALLOWED_PREFIXES/DEPLOYMENT_ID\\|0\\|1010:1010/prefixes_v4/0",
                "value": "10.30.0.0/16"
            }
        ],
        "origin_json": {
            "BGP_ALLOWED_PREFIXES": {
                "DEPLOYMENT_ID|0|1010:1010": {
                    "prefixes_v4": [
                        "10.20.0.0/16"
                    ],
                    "prefixes_v6": [
                        "fc01:20::/64"
                    ]
                }
            }
        },
        "target_json": {
            "BGP_ALLOWED_PREFIXES": {
                "DEPLOYMENT_ID|0|1010:1010": {
                    "prefixes_v4": [
                        "10.30.0.0/16"
                    ],
                    "prefixes_v6": [
                        "fc01:30::/64"
                    ]
                }
            }
        }
    },
    {
        "test_name": "bgp_prefix_tc1_add",
        "operations": [
            {
                "op": "update",
                "path": "/sonic-db:CONFIG_DB/localhost/BGP_ALLOWED_PREFIXES/DEPLOYMENT_ID\\|0\\|1010:1010/prefixes_v6/0",
                "value": "fc01:30::/64"
            },
            {
                "op": "update",
                "path": "/sonic-db:CONFIG_DB/localhost/BGP_ALLOWED_PREFIXES/DEPLOYMENT_ID\\|0\\|1010:1010/prefixes_v4/0",
                "value": "10.30.0.0/16"
            }
        ],
        "origin_json": {
            "BGP_ALLOWED_PREFIXES": {
                "DEPLOYMENT_ID|0|1010:1010": {
                    "prefixes_v4": [
                        "10.20.0.0/16"
                    ],
                    "prefixes_v6": [
                        "fc01:20::/64"
                    ]
                }
            }
        },
        "target_json": {
            "BGP_ALLOWED_PREFIXES": {
                "DEPLOYMENT_ID|0|1010:1010": {
                    "prefixes_v4": [
                        "10.30.0.0/16", "10.20.0.0/16"
                    ],
                    "prefixes_v6": [
                        "fc01:30::/64", "fc01:20::/64"
                    ]
                }
            }
        }
    },
    {
        "test_name": "bgp_prefix_tc1_remove",
        "operations": [
            {
                "op": "del",
                "path": "/sonic-db:CONFIG_DB/localhost/BGP_ALLOWED_PREFIXES"
            }
        ],
        "origin_json": {
            "BGP_ALLOWED_PREFIXES": {
                "DEPLOYMENT_ID|0|1010:1010": {
                    "prefixes_v4": [
                        "10.30.0.0/16", "10.20.0.0/16"
                    ],
                    "prefixes_v6": [
                        "fc01:30::/64", "fc01:20::/64"
                    ]
                }
            }
        },
        "target_json": {}
    }
]

test_data_bgp_sentinel_patch = [
    {
        "test_name": "bgp_sentinel_tc1_add_config",
        "operations": [
            {
                "op": "update",
                "path": "/sonic-db:CONFIG_DB/localhost/BGP_SENTINELS",
                "value": {
                    "BGPSentinel": {
                        "ip_range": [
                            "10.10.20.0/24"
                        ],
                        "name": "BGPSentinel",
                        "src_address": "10.5.5.5"
                    },
                    "BGPSentinelV6": {
                        "ip_range": [
                            "2603:10a1:30a:8000::/59"
                        ],
                        "name": "BGPSentinelV6",
                        "src_address": "fc00:fc00:0:10::5"
                    }
                }
            }
        ],
        "origin_json": {},
        "target_json": {
            "BGP_SENTINELS": {
                "BGPSentinel": {
                    "ip_range": [
                        "10.10.20.0/24"
                    ],
                    "name": "BGPSentinel",
                    "src_address": "10.5.5.5"
                },
                "BGPSentinelV6": {
                    "ip_range": [
                        "2603:10a1:30a:8000::/59"
                    ],
                    "name": "BGPSentinelV6",
                    "src_address": "fc00:fc00:0:10::5"
                }
            }
        }
    },
    {
        "test_name": "bgp_sentinel_tc1_add_dummy_ip_range",
        "operations": [
            {
                "op": "update",
                "path": "/sonic-db:CONFIG_DB/localhost/BGP_SENTINELS/BGPSentinel/ip_range/1",
                "value": "10.255.0.0/25"
            },
            {
                "op": "update",
                "path": "/sonic-db:CONFIG_DB/localhost/BGP_SENTINELS/BGPSentinelV6/ip_range/1",
                "value": "cc98:2008:2012:2022::/64"
            }
        ],
        "origin_json": {
            "BGP_SENTINELS": {
                "BGPSentinel": {
                    "ip_range": [
                        "10.10.20.0/24"
                    ],
                    "name": "BGPSentinel",
                    "src_address": "10.5.5.5"
                },
                "BGPSentinelV6": {
                    "ip_range": [
                        "2603:10a1:30a:8000::/59"
                    ],
                    "name": "BGPSentinelV6",
                    "src_address": "fc00:fc00:0:10::5"
                }
            }
        },
        "target_json": {
            "BGP_SENTINELS": {
                "BGPSentinel": {
                    "ip_range": [
                        "10.10.20.0/24", "10.255.0.0/25"
                    ],
                    "name": "BGPSentinel",
                    "src_address": "10.5.5.5"
                },
                "BGPSentinelV6": {
                    "ip_range": [
                        "2603:10a1:30a:8000::/59", "cc98:2008:2012:2022::/64"
                    ],
                    "name": "BGPSentinelV6",
                    "src_address": "fc00:fc00:0:10::5"
                }
            }
        }
    },
    {
        "test_name": "bgp_sentinel_tc1_rm_dummy_ip_range",
        "operations": [
            {
                "op": "del",
                "path": "/sonic-db:CONFIG_DB/localhost/BGP_SENTINELS/BGPSentinel/ip_range/1",
                "value": "10.255.0.0/25"
            },
            {
                "op": "del",
                "path": "/sonic-db:CONFIG_DB/localhost/BGP_SENTINELS/BGPSentinelV6/ip_range/1",
                "value": "cc98:2008:2012:2022::/64"
            }
        ],
        "origin_json": {
            "BGP_SENTINELS": {
                "BGPSentinel": {
                    "ip_range": [
                        "10.10.20.0/24", "10.255.0.0/25"
                    ],
                    "name": "BGPSentinel",
                    "src_address": "10.5.5.5"
                },
                "BGPSentinelV6": {
                    "ip_range": [
                        "2603:10a1:30a:8000::/59", "cc98:2008:2012:2022::/64"
                    ],
                    "name": "BGPSentinelV6",
                    "src_address": "fc00:fc00:0:10::5"
                }
            }
        },
        "target_json": {
            "BGP_SENTINELS": {
                "BGPSentinel": {
                    "ip_range": [
                        "10.10.20.0/24"
                    ],
                    "name": "BGPSentinel",
                    "src_address": "10.5.5.5"
                },
                "BGPSentinelV6": {
                    "ip_range": [
                        "2603:10a1:30a:8000::/59"
                    ],
                    "name": "BGPSentinelV6",
                    "src_address": "fc00:fc00:0:10::5"
                }
            }
        }
    },
    {
        "test_name": "bgp_sentinel_tc1_replace_src_address",
        "operations": [
            {
                "op": "replace",
                "path": "/sonic-db:CONFIG_DB/localhost/BGP_SENTINELS/BGPSentinel/src_address",
                "value": "10.1.0.33"
            },
            {
                "op": "replace",
                "path": "/sonic-db:CONFIG_DB/localhost/BGP_SENTINELS/BGPSentinelV6/src_address",
                "value": "fc00:1::33"
            }
        ],
        "origin_json": {
            "BGP_SENTINELS": {
                "BGPSentinel": {
                    "ip_range": [
                        "10.10.20.0/24"
                    ],
                    "name": "BGPSentinel",
                    "src_address": "10.5.5.5"
                },
                "BGPSentinelV6": {
                    "ip_range": [
                        "2603:10a1:30a:8000::/59"
                    ],
                    "name": "BGPSentinelV6",
                    "src_address": "fc00:fc00:0:10::5"
                }
            }
        },
        "target_json": {
            "BGP_SENTINELS": {
                "BGPSentinel": {
                    "ip_range": [
                        "10.10.20.0/24"
                    ],
                    "name": "BGPSentinel",
                    "src_address": "10.1.0.33"
                },
                "BGPSentinelV6": {
                    "ip_range": [
                        "2603:10a1:30a:8000::/59"
                    ],
                    "name": "BGPSentinelV6",
                    "src_address": "fc00:1::33"
                }
            }
        }
    }
]

test_data_bgp_speaker_patch = [
    {
        "test_name": "bgp_speaker_tc1_add_config",
        "operations": [
            {
                "op": "update",
                "path": "/sonic-db:CONFIG_DB/localhost/BGP_PEER_RANGE",
                "value": {
                    "BGPSLBPassive": {
                        "ip_range": [
                            "10.255.0.0/25"
                        ],
                        "name": "BGPSLBPassive",
                        "src_address": "10.1.0.33"
                    },
                    "BGPSLBPassiveV6": {
                        "ip_range": [
                            "cc98:2008:2012:2022::/64"
                        ],
                        "name": "BGPSLBPassiveV6",
                        "src_address": "fc00:1::33"
                    }
                }
            }
        ],
        "origin_json": {},
        "target_json": {
            "BGP_PEER_RANGE": {
                "BGPSLBPassive": {
                    "ip_range": [
                        "10.255.0.0/25"
                    ],
                    "name": "BGPSLBPassive",
                    "src_address": "10.1.0.33"
                },
                "BGPSLBPassiveV6": {
                    "ip_range": [
                        "cc98:2008:2012:2022::/64"
                    ],
                    "name": "BGPSLBPassiveV6",
                    "src_address": "fc00:1::33"
                }
            }
        }
    },
    {
        "test_name": "bgp_speaker_tc1_add_dummy_ip_range",
        "operations": [
            {
                "op": "update",
                "path": "/sonic-db:CONFIG_DB/localhost/BGP_PEER_RANGE/BGPSLBPassive/ip_range/1",
                "value": "20.255.0.0/25"
            },
            {
                "op": "update",
                "path": "/sonic-db:CONFIG_DB/localhost/BGP_PEER_RANGE/BGPSLBPassiveV6/ip_range/1",
                "value": "cc98:2008:2012:2222::/64"
            }
        ],
        "origin_json": {
            "BGP_PEER_RANGE": {
                "BGPSLBPassive": {
                    "ip_range": [
                        "10.255.0.0/25"
                    ],
                    "name": "BGPSLBPassive",
                    "src_address": "10.1.0.33"
                },
                "BGPSLBPassiveV6": {
                    "ip_range": [
                        "cc98:2008:2012:2022::/64"
                    ],
                    "name": "BGPSLBPassiveV6",
                    "src_address": "fc00:1::33"
                }
            }
        },
        "target_json": {
            "BGP_PEER_RANGE": {
                "BGPSLBPassive": {
                    "ip_range": [
                        "10.255.0.0/25", "20.255.0.0/25"
                    ],
                    "name": "BGPSLBPassive",
                    "src_address": "10.1.0.33"
                },
                "BGPSLBPassiveV6": {
                    "ip_range": [
                        "cc98:2008:2012:2022::/64", "cc98:2008:2012:2222::/64"
                    ],
                    "name": "BGPSLBPassiveV6",
                    "src_address": "fc00:1::33"
                }
            }
        }
    },
    {
        "test_name": "bgp_speaker_tc1_rm_dummy_ip_range",
        "operations": [
            {
                "op": "del",
                "path": "/sonic-db:CONFIG_DB/localhost/BGP_PEER_RANGE/BGPSLBPassive/ip_range/1"
            },
            {
                "op": "del",
                "path": "/sonic-db:CONFIG_DB/localhost/BGP_PEER_RANGE/BGPSLBPassiveV6/ip_range/1"
            }
        ],
        "origin_json": {
            "BGP_PEER_RANGE": {
                "BGPSLBPassive": {
                    "ip_range": [
                        "10.255.0.0/25", "20.255.0.0/25"
                    ],
                    "name": "BGPSLBPassive",
                    "src_address": "10.1.0.33"
                },
                "BGPSLBPassiveV6": {
                    "ip_range": [
                        "cc98:2008:2012:2022::/64", "cc98:2008:2012:2222::/64"
                    ],
                    "name": "BGPSLBPassiveV6",
                    "src_address": "fc00:1::33"
                }
            }
        },
        "target_json": {
            "BGP_PEER_RANGE": {
                "BGPSLBPassive": {
                    "ip_range": [
                        "10.255.0.0/25"
                    ],
                    "name": "BGPSLBPassive",
                    "src_address": "10.1.0.33"
                },
                "BGPSLBPassiveV6": {
                    "ip_range": [
                        "cc98:2008:2012:2022::/64"
                    ],
                    "name": "BGPSLBPassiveV6",
                    "src_address": "fc00:1::33"
                }
            }
        }
    },
    {
        "test_name": "bgp_speaker_tc1_replace_src_address",
        "operations": [
            {
                "op": "replace",
                "path": "/sonic-db:CONFIG_DB/localhost/BGP_PEER_RANGE/BGPSLBPassive/src_address",
                "value": "10.2.0.33"
            },
            {
                "op": "replace",
                "path": "/sonic-db:CONFIG_DB/localhost/BGP_PEER_RANGE/BGPSLBPassiveV6/src_address",
                "value": "fc00:2::33"
            }
        ],
        "origin_json": {
            "BGP_PEER_RANGE": {
                "BGPSLBPassive": {
                    "ip_range": [
                        "10.255.0.0/25"
                    ],
                    "name": "BGPSLBPassive",
                    "src_address": "10.1.0.33"
                },
                "BGPSLBPassiveV6": {
                    "ip_range": [
                        "cc98:2008:2012:2022::/64"
                    ],
                    "name": "BGPSLBPassiveV6",
                    "src_address": "fc00:1::33"
                }
            }
        },
        "target_json": {
            "BGP_PEER_RANGE": {
                "BGPSLBPassive": {
                    "ip_range": [
                        "10.255.0.0/25"
                    ],
                    "name": "BGPSLBPassive",
                    "src_address": "10.2.0.33"
                },
                "BGPSLBPassiveV6": {
                    "ip_range": [
                        "cc98:2008:2012:2022::/64"
                    ],
                    "name": "BGPSLBPassiveV6",
                    "src_address": "fc00:2::33"
                }
            }
        }
    }
]

test_data_bgp_mon_patch = [
    {
        "test_name": "bgpmon_tc1_add_init",
        "operations": [
            {
                "op": "update",
                "path": "/sonic-db:CONFIG_DB/localhost/BGP_MONITORS",
                "value": {
                    "10.10.10.10": {
                        "admin_status": "up",
                        "asn": "66666",
                        "holdtime": "180",
                        "keepalive": "60",
                        "local_addr": "10.10.10.20",
                        "name": "BGPMonitor",
                        "nhopself": "0",
                        "rrclient": "0"
                    }
                }
            }
        ],
        "origin_json": {},
        "target_json": {
            "BGP_MONITORS": {
                "10.10.10.10": {
                    "admin_status": "up",
                    "asn": "66666",
                    "holdtime": "180",
                    "keepalive": "60",
                    "local_addr": "10.10.10.20",
                    "name": "BGPMonitor",
                    "nhopself": "0",
                    "rrclient": "0"
                }
            }
        }
    },
    {
        "test_name": "bgpmon_tc1_add_duplicate",
        "operations": [
            {
                "op": "update",
                "path": "/sonic-db:CONFIG_DB/localhost/BGP_MONITORS/10.10.10.10",
                "value": {
                    "admin_status": "up",
                    "asn": "66666",
                    "holdtime": "180",
                    "keepalive": "60",
                    "local_addr": "10.10.10.20",
                    "name": "BGPMonitor",
                    "nhopself": "0",
                    "rrclient": "0"
                }
            }
        ],
        "origin_json": {
            "BGP_MONITORS": {
                "10.10.10.10": {
                    "admin_status": "up",
                    "asn": "66666",
                    "holdtime": "180",
                    "keepalive": "60",
                    "local_addr": "10.10.10.20",
                    "name": "BGPMonitor",
                    "nhopself": "0",
                    "rrclient": "0"
                }
            }
        },
        "target_json": {
            "BGP_MONITORS": {
                "10.10.10.10": {
                    "admin_status": "up",
                    "asn": "66666",
                    "holdtime": "180",
                    "keepalive": "60",
                    "local_addr": "10.10.10.20",
                    "name": "BGPMonitor",
                    "nhopself": "0",
                    "rrclient": "0"
                }
            }
        }
    },
    {
        "test_name": "bgpmon_tc1_admin_change",
        "operations": [
            {
                "op": "replace",
                "path": "/sonic-db:CONFIG_DB/localhost/BGP_MONITORS/10.10.10.10/admin_status",
                "value": "down"
            }
        ],
        "origin_json": {
            "BGP_MONITORS": {
                "10.10.10.10": {
                    "admin_status": "up",
                    "asn": "66666",
                    "holdtime": "180",
                    "keepalive": "60",
                    "local_addr": "10.10.10.20",
                    "name": "BGPMonitor",
                    "nhopself": "0",
                    "rrclient": "0"
                }
            }
        },
        "target_json": {
            "BGP_MONITORS": {
                "10.10.10.10": {
                    "admin_status": "down",
                    "asn": "66666",
                    "holdtime": "180",
                    "keepalive": "60",
                    "local_addr": "10.10.10.20",
                    "name": "BGPMonitor",
                    "nhopself": "0",
                    "rrclient": "0"
                }
            }
        }
    },
    {
        "test_name": "bgpmon_tc1_ip_change",
        "operations": [
            {
                "op": "del",
                "path": "/sonic-db:CONFIG_DB/localhost/BGP_MONITORS/10.10.10.10",
            },
            {
                "op": "update",
                "path": "/sonic-db:CONFIG_DB/localhost/BGP_MONITORS/10.10.10.30",
                "value": {
                    "admin_status": "up",
                    "asn": "66666",
                    "holdtime": "180",
                    "keepalive": "60",
                    "local_addr": "10.10.10.20",
                    "name": "BGPMonitor",
                    "nhopself": "0",
                    "rrclient": "0"
                }
            }
        ],
        "origin_json": {
            "BGP_MONITORS": {
                "10.10.10.10": {
                    "admin_status": "up",
                    "asn": "66666",
                    "holdtime": "180",
                    "keepalive": "60",
                    "local_addr": "10.10.10.20",
                    "name": "BGPMonitor",
                    "nhopself": "0",
                    "rrclient": "0"
                }
            }
        },
        "target_json": {
            "BGP_MONITORS": {
                "10.10.10.30": {
                    "admin_status": "up",
                    "asn": "66666",
                    "holdtime": "180",
                    "keepalive": "60",
                    "local_addr": "10.10.10.20",
                    "name": "BGPMonitor",
                    "nhopself": "0",
                    "rrclient": "0"
                }
            }
        }
    },
    {
        "test_name": "bgpmon_tc1_remove",
        "operations": [
            {
                "op": "del",
                "path": "/sonic-db:CONFIG_DB/localhost/BGP_MONITORS",
            }
        ],
        "origin_json": {
            "BGP_MONITORS": {
                "10.10.10.10": {
                    "admin_status": "up",
                    "asn": "66666",
                    "holdtime": "180",
                    "keepalive": "60",
                    "local_addr": "10.10.10.20",
                    "name": "BGPMonitor",
                    "nhopself": "0",
                    "rrclient": "0"
                }
            }
        },
        "target_json": {}
    }
]

test_data_cacl_patch = [
    {
        "test_name": "cacl_tc1_add_new_table",
        "operations": [
            {
                "op": "update",
                "path": "/sonic-db:CONFIG_DB/localhost/ACL_TABLE/TEST_1",
                "value": {
                    "policy_desc": "Test_Table_1",
                    "services": [
                        "SNMP"
                    ],
                    "stage": "ingress",
                    "type": "CTRLPLANE"
                }
            }
        ],
        "origin_json": {
            "ACL_TABLE": {}
        },
        "target_json": {
            "ACL_TABLE": {
                "TEST_1": {
                    "policy_desc": "Test_Table_1",
                    "services": [
                        "SNMP"
                    ],
                    "stage": "ingress",
                    "type": "CTRLPLANE"
                }
            }
        }
    },
    {
        "test_name": "cacl_tc1_add_duplicate_table",
        "operations": [
            {
                "op": "update",
                "path": "/sonic-db:CONFIG_DB/localhost/ACL_TABLE/SNMP_ACL",
                "value": {
                    "policy_desc": "SNMP_ACL",
                    "services": [
                        "SNMP"
                    ],
                    "stage": "ingress",
                    "type": "CTRLPLANE"
                }
            }
        ],
        "origin_json": {
            "ACL_TABLE": {
                "SNMP_ACL": {
                    "policy_desc": "SNMP_ACL",
                    "services": [
                        "SNMP"
                    ],
                    "stage": "ingress",
                    "type": "CTRLPLANE"
                }
            }
        },
        "target_json": {
            "ACL_TABLE": {
                "SNMP_ACL": {
                    "policy_desc": "SNMP_ACL",
                    "services": [
                        "SNMP"
                    ],
                    "stage": "ingress",
                    "type": "CTRLPLANE"
                }
            }
        }
    },
    {
        "test_name": "cacl_tc1_replace_table_variable",
        "operations": [
            {
                "op": "replace",
                "path": "/sonic-db:CONFIG_DB/localhost/ACL_TABLE/SNMP_ACL/stage",
                "value": "egress"
            },
            {
                "op": "replace",
                "path": "/sonic-db:CONFIG_DB/localhost/ACL_TABLE/SNMP_ACL/services/0",
                "value": "SSH"
            },
            {
                "op": "replace",
                "path": "/sonic-db:CONFIG_DB/localhost/ACL_TABLE/SNMP_ACL/policy_desc",
                "value": "SNMP_TO_SSH"
            }
        ],
        "origin_json": {
            "ACL_TABLE": {
                "SNMP_ACL": {
                    "policy_desc": "SNMP_ACL",
                    "services": [
                        "SNMP"
                    ],
                    "stage": "ingress",
                    "type": "CTRLPLANE"
                }
            }
        },
        "target_json": {
            "ACL_TABLE": {
                "SNMP_ACL": {
                    "policy_desc": "SNMP_TO_SSH",
                    "services": [
                        "SSH"
                    ],
                    "stage": "egress",
                    "type": "CTRLPLANE"
                }
            }
        }
    },
    {
        "test_name": "cacl_tc1_remove_table",
        "operations": [
            {
                "op": "del",
                "path": "/sonic-db:CONFIG_DB/localhost/ACL_TABLE/SSH_ONLY"
            }
        ],
        "origin_json": {
            "ACL_TABLE": {
                "SNMP_ACL": {
                    "policy_desc": "SNMP_ACL"
                },
                "SSH_ONLY": {
                    "policy_desc": "SSH_ONLY"
                },
                "NTP_ACL": {
                    "policy_desc": "NTP_ACL"
                }
            }
        },
        "target_json": {
            "ACL_TABLE": {
                "SNMP_ACL": {
                    "policy_desc": "SNMP_ACL"
                },
                "NTP_ACL": {
                    "policy_desc": "NTP_ACL"
                }
            }
        }
    }
]

class TestGNMIConfigDbPatch:

    def common_test_handler(self, test_data):
        '''
        Common code for all patch test
        '''
        if os.path.exists(patch_file):
            os.system("rm " + patch_file)
        create_checkpoint(checkpoint_file, json.dumps(test_data['origin_json']))
        update_list = []
        replace_list = []
        delete_list = []
        for i, data in enumerate(test_data["operations"]):
            path = data["path"]
            if data['op'] == "update":
                value = json.dumps(data["value"])
                file_name = "update" + str(i)
                file_object = open(file_name, "w")
                file_object.write(value)
                file_object.close()
                update_list.append(path + ":@./" + file_name)
            elif data['op'] == "replace":
                value = json.dumps(data["value"])
                file_name = "replace" + str(i)
                file_object = open(file_name, "w")
                file_object.write(value)
                file_object.close()
                replace_list.append(path + ":@./" + file_name)
            elif data['op'] == "del":
                delete_list.append(path)
            else:
                pytest.fail("Invalid operation: %s" % data['op'])

        # Send GNMI request
        ret, msg = gnmi_set(delete_list, update_list, replace_list)
        assert ret == 0, msg
        assert os.path.exists(patch_file), "No patch file"
        with open(patch_file,"r") as pf:
            patch_json = json.load(pf)
        # Apply patch to get json result
        result = jsonpatch.apply_patch(test_data["origin_json"], patch_json)
        # Compare json result
        diff = jsonpatch.make_patch(result, test_data["target_json"])
        assert len(diff.patch) == 0, "%s failed, generated json: %s" % (test_data["test_name"], str(result))

    @pytest.mark.parametrize("test_data", test_data_aaa_patch)
    def test_gnmi_aaa_patch(self, test_data):
        '''
        Generate GNMI request for AAA and verify jsonpatch
        '''
        self.common_test_handler(test_data)

    @pytest.mark.parametrize("test_data", test_data_bgp_prefix_patch)
    def test_gnmi_bgp_prefix_patch(self, test_data):
        '''
        Generate GNMI request for BGP prefix and verify jsonpatch
        '''
        self.common_test_handler(test_data)
 
    @pytest.mark.parametrize("test_data", test_data_bgp_sentinel_patch)
    def test_gnmi_bgp_sentinel_patch(self, test_data):
        '''
        Generate GNMI request for BGP sentinel and verify jsonpatch
        '''
        self.common_test_handler(test_data)

    @pytest.mark.parametrize("test_data", test_data_bgp_speaker_patch)
    def test_gnmi_bgp_speaker_patch(self, test_data):
        '''
        Generate GNMI request for BGP speaker and verify jsonpatch
        '''
        self.common_test_handler(test_data)

    @pytest.mark.parametrize("test_data", test_data_bgp_mon_patch)
    def test_gnmi_bgp_mon_patch(self, test_data):
        '''
        Generate GNMI request for BGP monitor and verify jsonpatch
        '''
        self.common_test_handler(test_data)

    @pytest.mark.parametrize("test_data", test_data_cacl_patch)
    def test_gnmi_cacl_patch(self, test_data):
        '''
        Generate GNMI request for CACL and verify jsonpatch
        '''
        self.common_test_handler(test_data)