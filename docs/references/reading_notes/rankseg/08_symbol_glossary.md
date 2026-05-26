# 公式符号表

这份符号表用来读论文和前面笔记时快速查意思。

## 基本对象

| 符号 | 含义 |
|---|---|
| `X` | 输入，可以是图像、文本或 feature vector |
| `x` | 某一个具体输入样本 |
| `d` | 像素或 feature 的数量 |
| `j` | 像素或 feature 下标，通常 `j = 1, ..., d` |
| `Y` | 真实分割标签，`Y in {0,1}^d` |
| `Y_j` | 第 `j` 个像素的真实标签 |
| `delta` | 分割规则或分割函数 |
| `delta_j(X)` | 对第 `j` 个像素的预测，取 0 或 1 |
| `I(Y)` | 真实为 1 的位置集合 |
| `I(delta(X))` | 预测为 1 的位置集合 |

## 概率相关

| 符号 | 含义 |
|---|---|
| `p_j(x)` | 真实条件概率 `P(Y_j = 1 | X = x)` |
| `p(x)` | 所有像素真实条件概率组成的向量 |
| `q_j(x)` | 候选概率函数对第 `j` 个像素的输出 |
| `q_hat_j(x)` | 训练后估计出的第 `j` 个像素概率 |
| `B_j(x)` | 成功概率为 `p_j(x)` 的 Bernoulli 随机变量 |
| `B_hat_j(x)` | 成功概率为 `q_hat_j(x)` 的 Bernoulli 随机变量 |
| `Gamma(x)` | `sum_j B_j(x)`，真实前景数量的随机版本 |
| `Gamma_hat(x)` | `sum_j B_hat_j(x)`，基于估计概率的前景数量随机版本 |
| `Gamma_minus_j(x)` | 去掉第 `j` 个像素后，其他像素真实为 1 的数量 |
| `PB(p)` | Poisson-binomial 分布，参数是概率向量 `p` |

## Dice 和 IoU

| 符号 | 含义 |
|---|---|
| `TP` | true positive，预测为 1 且真实为 1 的像素数 |
| `FP` | false positive，预测为 1 但真实为 0 的像素数 |
| `FN` | false negative，预测为 0 但真实为 1 的像素数 |
| `Dice_gamma(delta)` | 带 smoothing 参数 `gamma` 的期望 Dice |
| `IoU_gamma(delta)` | 带 smoothing 参数 `gamma` 的期望 IoU |
| `gamma` | smoothing parameter，防止极端分母问题 |
| `mDice` | 多类别或多标签 Dice 的加权平均 |
| `mIoU` | 多类别或多标签 IoU 的加权平均 |

## 排序和体积

| 符号 | 含义 |
|---|---|
| `tau` | 预测体积，也就是预测为 1 的像素数量 |
| `tau*(x)` | Bayes 最优预测体积 |
| `tau_hat(x)` | RankDice 估计出的预测体积 |
| `J_tau(x)` | 条件概率最高的前 `tau` 个像素下标集合 |
| `j_1, ..., j_d` | 按估计概率从大到小排序后的像素下标 |
| `d0(x)` | shrinkage 后的最大搜索范围 |
| `pi_tau(x)` | 选择体积 `tau` 时的估计目标分数 |
| `omega_tau(x)` | `pi_tau` 中来自 Dice 分子重合项的部分 |
| `nu_tau(x)` | `pi_tau` 中来自 smoothing 项的部分 |

## 多类别相关

| 符号 | 含义 |
|---|---|
| `K` | 类别数量 |
| `k` | 类别下标 |
| `Y_{·k}` | 第 `k` 类的真实二值 mask |
| `Y_{jk}` | 第 `j` 个像素是否属于第 `k` 类 |
| `Delta_k` | 第 `k` 类的预测分割函数 |
| `Delta_{jk}(x)` | 第 `j` 个像素对第 `k` 类的预测 |
| `alpha_k` | 第 `k` 类在 mDice 中的权重 |
| `Q(x)` | 多类别概率矩阵 |
| `q_{jk}(x)` | 第 `j` 个像素属于第 `k` 类的概率 |

## 理论部分

| 符号 | 含义 |
|---|---|
| `delta*` | Dice 或 IoU 指标下的 Bayes 最优分割规则 |
| `D` | 所有可测分割规则的集合 |
| `P` | 满足条件独立假设的数据分布集合 |
| `M_gamma` | population segmentation method |
| `Dice-calibrated` | population 层面能达到 Dice Bayes 最优 |
| `strictly proper loss` | 理想情况下能恢复真实概率的损失 |
| `ECE(q_hat)` | cross-entropy excess risk |
| `KL` | Kullback-Leibler divergence |
| `TV` | total variation distance |
| `||q_hat - p||_1` | 概率估计的 L1 误差 |

## 近似算法相关

| 符号 | 含义 |
|---|---|
| `FFT` | fast Fourier transform，用于快速计算 Poisson-binomial 概率 |
| `T-RNA` | truncated refined normal approximation |
| `BA` | blind approximation |
| `L(epsilon)` | T-RNA/BA 中保留的主要概率质量区间 |
| `epsilon` | 截断容忍度 |
| `mu` | Poisson-binomial 的均值 |
| `sigma^2` | Poisson-binomial 的方差 |
| `eta` | Poisson-binomial 的偏度相关量 |
| `Phi` | 标准正态分布的 CDF |
| `Psi` | 带偏度修正的 refined normal CDF |

## 最容易混淆的三组符号

### `p` 和 `q_hat`

```text
p = 真实条件概率，理论上存在但现实不知道
q_hat = 模型估计出来的概率
```

RankDice 的理论公式用 `p`，实际算法用 `q_hat`。

### `tau` 和 threshold

```text
tau = 选多少个像素
threshold = 概率截断值
```

RankDice 直接估计 `tau`，它隐含了一个输入相关 threshold：

```text
threshold(x) = 第 tau_hat(x) 大的概率
```

### `Gamma` 和 `tau`

```text
Gamma = 真实前景数量的随机变量
tau = 模型预测前景数量，由算法选择
```

一个来自真实标签分布，一个来自预测规则。

