"""record_env.py -- records hardware and software used for the confirmatory round (out/conf/hardware.json)."""
import json, os, platform, subprocess, sys
import numpy, scipy, pandas
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sh(c):
    return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()


info = dict(cpu_model=sh("lscpu | grep 'Model name' | cut -d: -f2").strip(), logical_cpus=os.cpu_count(), threads_per_core=sh("lscpu | grep 'Thread(s)' | cut -d: -f2").strip(),
            l2_cache=sh("lscpu | grep 'L2 cache' | cut -d: -f2").strip(), memory_gb=round(int(sh("grep MemTotal /proc/meminfo | awk '{print $2}'")) / 1048576, 1),
            os=platform.platform(), python=platform.python_version(), numpy=numpy.__version__, scipy=scipy.__version__, pandas=pandas.__version__,
            parallel_workers=2, note="Cloud container; wall-clock times of the confirmatory round were measured with two worker processes sharing the machine.",
            recorded_utc=sh("date -u +%Y-%m-%dT%H:%M:%SZ"))
os.makedirs(ROOT + "/out/conf", exist_ok=True)
from confirm_run import ensure_frozen
ensure_frozen()
json.dump(info, open(ROOT + "/out/conf/hardware.json", "w"), indent=1)
print(info)
