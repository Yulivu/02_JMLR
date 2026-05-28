# GitHub + AutoDL + FileZilla 通用工作流

这份文档记录一套可以迁移到所有研究项目的固定流程：

```text
GitHub 管代码
AutoDL/HPC 跑实验
FileZilla 传数据和拖结果
本地做审计、改代码、画图和写文档
```

核心原则：

- GitHub 只同步代码、脚本、配置、文档和小型元数据。
- 大数据、`.npy`、`.zip`、模型 checkpoint、实验输出默认不进 GitHub。
- AutoDL 每台新机器都先建立 SSH key，再从 GitHub clone repo。
- FileZilla 只负责上传缺失数据、下载结果文件夹，不双向同步整个仓库。
- 服务器只跑已提交到 GitHub 的代码，不手工改服务器代码。

## 0. 本地先准备好 GitHub

在本地项目里确认代码已经提交并推送：

```powershell
git status --short
git log -1 --oneline
git push origin master
```

如果项目主分支叫 `main`，替换成：

```powershell
git push origin main
```

记录这几个信息：

```text
GitHub SSH URL: git@github.com:<USER>/<REPO>.git
branch: master 或 main
latest commit: git log -1 --oneline
server repo dir: /root/autodl-tmp/<REPO>
```

本项目例子：

```text
GitHub SSH URL: git@github.com:Yulivu/02_JMLR.git
branch: master
server repo dir: /root/autodl-tmp/02_JMLR
```

## 1. AutoDL 新机器创建 SSH Key

每台 AutoDL 新实例都建议创建机器专用 key。不要上传本地私钥。

```bash
mkdir -p /root/.ssh /root/autodl-tmp
chmod 700 /root/.ssh

ssh-keygen -t ed25519 \
  -C "autodl_<PROJECT>_$(date +%Y%m%d_%H%M)" \
  -f /root/.ssh/id_ed25519_<PROJECT> \
  -N ""

cat > /root/.ssh/config <<'EOF'
Host github.com
  HostName github.com
  User git
  IdentityFile /root/.ssh/id_ed25519_<PROJECT>
  IdentitiesOnly yes
EOF

chmod 600 /root/.ssh/config
chmod 600 /root/.ssh/id_ed25519_<PROJECT>
chmod 644 /root/.ssh/id_ed25519_<PROJECT>.pub

cat /root/.ssh/id_ed25519_<PROJECT>.pub
```

把最后输出的整行 `ssh-ed25519 ...` 复制到 GitHub。

推荐放到：

```text
GitHub repo -> Settings -> Deploy keys -> Add deploy key
```

Title 示例：

```text
autodl_<PROJECT>_<DATE>
```

通常不要勾选 `Allow write access`。服务器只需要 clone/pull，写权限放本地。

如果你想让同一把 key 访问多个私有 repo，可以把公钥加到：

```text
GitHub account -> Settings -> SSH and GPG keys
```

但更推荐每个项目/每台机器用 repo deploy key，权限更小，出了问题更容易删。

测试：

```bash
ssh -T git@github.com
```

成功时会看到：

```text
Hi <USER>! You've successfully authenticated, but GitHub does not provide shell access.
```

如果看到：

```text
Permission denied (publickey).
```

说明 GitHub 没有接受当前公钥。检查：

```bash
cat /root/.ssh/config
ls -l /root/.ssh
cat /root/.ssh/id_ed25519_<PROJECT>.pub
ssh -vT git@github.com
```

## 2. 从 GitHub Clone Repo

```bash
cd /root/autodl-tmp
git clone git@github.com:<USER>/<REPO>.git
cd <REPO>
git rev-parse --short HEAD
git status --short
```

确认 commit 是本地刚推上去的版本。

如果是已经存在的 repo：

```bash
cd /root/autodl-tmp/<REPO>
git pull --ff-only
git rev-parse --short HEAD
```

不要在服务器上 `git reset --hard` 或手工改代码，除非明确知道会丢什么。

## 3. 安装依赖

优先使用项目自己的安装脚本：

```bash
bash scripts/autodl_setup.sh
```

如果项目没有安装脚本，通用 Python 项目可以用：

```bash
python -m pip install -U pip
python -m pip install -e . --no-deps
```

如果项目有 `requirements.txt`：

```bash
python -m pip install -r requirements.txt
python -m pip install -e . --no-deps
```

不要轻易覆盖 AutoDL 镜像自带的 PyTorch/CUDA。先确认：

```bash
python --version
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu')"
nvidia-smi
```

## 4. 快速环境确认

通用确认：

```bash
python -c "import sys; print(sys.version)"
python -c "import torch, numpy; print('imports ok')"
nvidia-smi
```

如果项目有 quick verify，先运行：

```bash
python scripts/run_hpc_quick_verify.py
```

只有 quick verify 通过后，才进入数据 staging 或正式实验。

## 5. 查缺哪些数据和文件

GitHub clone 后，通常会缺这些：

```text
data/raw/
data/processed/
external/
outputs/
artifacts/
*.npy
*.zip
*.pt
*.ckpt
```

原因是 `.gitignore` 会排除大数据和输出。

先看项目的 `.gitignore`：

```bash
cat .gitignore
```

再检查项目要求的数据路径。最好每个项目都写一个清单，例如：

```text
data/processed/<dataset>.npy
data/raw/<dataset>.zip
external/<baseline>/...
outputs/<previous_stage>/
```

本项目 S13 例子：

```bash
ls -lh data/processed/tensorcodec/uber.npy \
       data/processed/tensorcodec/airquality.npy \
       data/processed/tensorcodec/action.npy \
       data/processed/tensorcodec/pems.npy \
       data/processed/tensorcodec/activity.npy
```

如果缺文件，就不要启动实验。先补数据。

## 6. 用 FileZilla 上传缺失数据

原则：

- 上传数据到项目预期路径。
- 不上传整个本地仓库覆盖服务器仓库。
- 不上传 `.git/`，除非是明确的外部 baseline 源码。
- 上传后在服务器 `ls -lh` 确认大小。

通用目录建议：

```text
/root/autodl-tmp/<REPO>/data/processed/
/root/autodl-tmp/<REPO>/data/raw/
/root/autodl-tmp/<REPO>/external/
/root/autodl-tmp/incoming/
```

本项目例子：

```text
本地:
C:\...\5_Tensor_Compression_TPAMI\data\processed\tensorcodec\uber.npy

服务器:
/root/autodl-tmp/05_TPAMI/data/processed/tensorcodec/uber.npy
```

上传后确认：

```bash
ls -lh <uploaded-file>
```

必要时记录 hash：

```bash
sha256sum <uploaded-file>
```

## 7. 服务器运行实验

固定流程：

```bash
cd /root/autodl-tmp/<REPO>
git status --short
git rev-parse --short HEAD
```

先生成 manifest 或 dry-run：

```bash
python scripts/<experiment_manifest>.py
```

先跑一行 smoke：

```bash
python scripts/<experiment_row>.py <args>
```

单行通过后再跑全量：

```bash
bash outputs/<experiment_manifest>/run_<experiment>.sh
```

运行时关注这些输出：

```text
status=go...
error_count=0
summary_dir=outputs/...
```

如果出现 `stop...`，不要继续全量。先看对应 `outputs/.../*errors.json`。

## 8. 用 FileZilla 下载结果

跑完后，从服务器拖回结果文件夹。

通用下载目标：

```text
/root/autodl-tmp/<REPO>/outputs/<experiment_rows>/
/root/autodl-tmp/<REPO>/outputs/<experiment_manifest>/
/root/autodl-tmp/<REPO>/outputs/hpc_quick_verify/
```

下载到本地同一个 repo 的：

```text
<LOCAL_REPO>\outputs\
```

通常不需要下载：

```text
data/raw/
data/processed/
__pycache__/
.pytest_cache/
临时 clone 目录
```

如果输出很大，优先下载关键 JSON/CSV/MD 文件，或者用项目 packaging 脚本打包。

## 9. 本地审计结果

回到本地运行审计脚本：

```powershell
cd <LOCAL_REPO>
python scripts/<experiment_audit>.py
```

通过标准：

```text
status=go...
fail_count=0
error_count=0
```

审计通过后，才把结果用于图表、导师汇报或论文材料。

## 10. 新实例之间迁移

如果从一个 AutoDL 实例复制到另一个实例，先确认三件事：

```bash
cd /root/autodl-tmp/<REPO>
git rev-parse --short HEAD
python --version
nvidia-smi
```

再确认关键数据：

```bash
ls -lh <required-data-files>
```

再确认 manifest：

```bash
python scripts/<experiment_manifest>.py
```

如果 manifest 显示 prerequisites missing，说明复制时数据没带全。

## 11. 通用项目模板

把下面占位符替换成项目自己的值。

```text
<PROJECT>      项目短名，例如 05_tpami
<USER>         GitHub 用户名，例如 Yulivu
<REPO>         GitHub repo 名，例如 05_TPAMI
<BRANCH>       master 或 main
<LOCAL_REPO>   本地 repo 绝对路径
```

服务器初始化：

```bash
mkdir -p /root/.ssh /root/autodl-tmp
chmod 700 /root/.ssh

ssh-keygen -t ed25519 \
  -C "autodl_<PROJECT>_$(date +%Y%m%d_%H%M)" \
  -f /root/.ssh/id_ed25519_<PROJECT> \
  -N ""

cat > /root/.ssh/config <<'EOF'
Host github.com
  HostName github.com
  User git
  IdentityFile /root/.ssh/id_ed25519_<PROJECT>
  IdentitiesOnly yes
EOF

chmod 600 /root/.ssh/config /root/.ssh/id_ed25519_<PROJECT>
cat /root/.ssh/id_ed25519_<PROJECT>.pub
```

GitHub 添加 deploy key 后：

```bash
ssh -T git@github.com
cd /root/autodl-tmp
git clone git@github.com:<USER>/<REPO>.git
cd <REPO>
git checkout <BRANCH>
bash scripts/autodl_setup.sh
```

检查数据、运行、回传：

```bash
python scripts/run_hpc_quick_verify.py
python scripts/<experiment_manifest>.py
python scripts/<experiment_row>.py <args>
bash outputs/<experiment_manifest>/run_<experiment>.sh
```

FileZilla 下载：

```text
/root/autodl-tmp/<REPO>/outputs/<experiment_rows>/
```

本地审计：

```powershell
cd <LOCAL_REPO>
python scripts/<experiment_audit>.py
```

## 12. 固定边界

不要做：

- 不要把 AutoDL 私钥发到聊天或上传到 GitHub。
- 不要把本地私钥复制到 AutoDL。
- 不要把大 `.npy`、`.zip`、checkpoint 直接提交到普通 Git。
- 不要用 FileZilla 双向覆盖整个 repo。
- 不要在服务器手工改代码后直接跑正式实验。
- 不要在 audit 之前把结果写进论文结论。

应该做：

- 代码改动在本地完成、测试、commit、push。
- 服务器只 `git pull --ff-only`。
- 数据缺什么传什么。
- 每轮实验先 manifest，再单行 smoke，再全量。
- 全量跑完下载 `outputs/<stage>/`。
- 本地 audit 通过后再画图和总结。
