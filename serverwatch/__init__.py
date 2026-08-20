from . import collectors
from .cli import *

# Compatibility exports for existing integrations and tests that patch the
# collector dependencies through the top-level `serverwatch` module.
os = collectors.os
platform = collectors.platform
psutil = collectors.psutil
socket = collectors.socket
time = collectors.time
