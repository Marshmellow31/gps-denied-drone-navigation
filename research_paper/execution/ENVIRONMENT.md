# T01 environment inventory

Captured: 22 September 2026 (Asia/Kolkata). This is a factual inventory, not proof that any dataset or LIO backend can run.

## Repository state

- Working directory: `/home/harshil/Desktop/GPS Denied Drone navigation`
- Git revision: `a4d2e7d2b390744b33f34d026322721727aa323e`
- Branch: `main`
- Initial short status: `?? research_paper/AGENT_EXECUTION_PLAN.md`
- The untracked execution plan was supplied by the user and was read without modification.
- Existing `research_paper/` content at task start: the plan, active goal/scope/review documents, and `paper/`; no prior `execution/` artifacts existed.
- No files under `old_data/` were inspected or modified.

Commands:

```bash
git rev-parse --show-toplevel
git rev-parse HEAD
git branch --show-current
git status --short
find research_paper -maxdepth 2 -type d -print | sort
```

## Host capacity

| Property | Observed value |
| --- | --- |
| OS | Ubuntu 26.04.1 LTS (`resolute`) |
| Kernel | Linux 7.0.0-31-generic, x86_64 |
| CPU | Intel Core i7-14700HX; 20 cores, 28 online logical CPUs |
| RAM | 15 GiB total; 4.9 GiB available at capture |
| Swap | 4.0 GiB total; unused at capture |
| Workspace filesystem | 51 GiB total, 43 GiB used, 5.5 GiB available (89% used) |

Commands:

```bash
uname -a
cat /etc/os-release
lscpu
free -h
df -h .
```

The low remaining disk capacity is material: dataset selection and backend builds must verify published/download sizes before acquisition.

## Available command-line tools

| Tool | Observation |
| --- | --- |
| Git | `/usr/bin/git` |
| Python | `/usr/bin/python3`, Python 3.14.4 |
| pip | `/usr/bin/pip3` |
| CMake | `/usr/bin/cmake`, version 4.2.3 |
| GNU Make | `/usr/bin/make`, version 4.4.1 |
| GCC / G++ | `/usr/bin/gcc` and `/usr/bin/g++`, version 15.2.0 |
| Ninja | Not found |
| Docker | Not found |
| Podman | Not found |
| ROS 2 CLI | Not found |
| colcon | Not found |
| CUDA compiler (`nvcc`) | Not found |

Commands:

```bash
command -v git python3 pip3 cmake ninja make gcc g++ docker podman ros2 colcon nvcc || true
python3 --version
cmake --version
ninja --version
make --version
gcc --version
g++ --version
docker --version
podman --version
ros2 --help
colcon --help
nvcc --version
```

Absence was confirmed by the shell returning `command not found`; presence does not establish backend or recording compatibility. No packages or dependencies were installed in T01, and the system Python was not changed.

## Generated-output handling

The existing root `.gitignore` already excludes `data/generated/` and `results/generated/`, but the new study has not yet created `research_paper/experiments/generated/`. In accordance with T01, no speculative ignore rule or empty generated directory was added. A later task must add a narrowly scoped rule when that directory is actually used.
