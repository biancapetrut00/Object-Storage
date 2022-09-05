import toml

CONF = {}

def load_conf(path):
    global CONF 
    CONF = toml.load(path)

