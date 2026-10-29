"""Memory cap for the airflow-sim scripts.

Set the cap with the SIM_MEM_GB environment variable (default 3 GB; raise it when the machine has more RAM).
  SIM_MEM_GB=6 python lbm.py ...

apply()   : sets an OS limit on the process's private data memory (RLIMIT_DATA), so going over the cap raises
            MemoryError in this process instead of pushing the whole machine into swap.
require() : pre-flight check; stops with a readable message when an estimate does not fit under the cap.
chunk()   : number of items per chunk so that a temporary of `bytes_per_item` stays under a share of the cap.
peak_gb() : peak resident memory of this process so far.
"""
import os, resource, sys

def cap_gb():
    return float(os.environ.get("SIM_MEM_GB", "3"))

def cap_bytes():
    return int(cap_gb() * 2**30)

def apply():
    lim = cap_bytes()
    try:
        soft, hard = resource.getrlimit(resource.RLIMIT_DATA)
        if hard != resource.RLIM_INFINITY:
            lim = min(lim, hard)
        resource.setrlimit(resource.RLIMIT_DATA, (lim, hard))
    except (ValueError, OSError) as e:
        print("memcap: could not set the OS limit (%s); only the pre-flight checks apply" % e, file=sys.stderr)
    print("memcap: cap %.1f GB (SIM_MEM_GB)" % cap_gb(), flush=True)

def require(est_bytes, what, overhead_gb=0.4):
    """Stop early when `what` is estimated to need more than the cap (overhead_gb covers Python, numba, numpy)."""
    need = est_bytes / 2**30 + overhead_gb
    if need > cap_gb():
        sys.exit("memcap: %s needs about %.2f GB (+%.1f GB overhead) but the cap is %.1f GB. Use a coarser grid, crop the domain, "
                 "or raise SIM_MEM_GB." % (what, est_bytes / 2**30, overhead_gb, cap_gb()))
    print("memcap: %s about %.2f GB of the %.1f GB cap" % (what, need, cap_gb()), flush=True)

def chunk(bytes_per_item, share=0.1, lo=1000, hi=1_000_000):
    """Items per chunk for a temporary of bytes_per_item each, using at most `share` of the cap."""
    return int(max(lo, min(hi, cap_bytes() * share / bytes_per_item)))

def peak_gb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20  # ru_maxrss is in KB on Linux
