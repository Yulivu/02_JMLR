# 第 2.3 节：如何计算最优 tau

RankDice 的核心决策是：

```text
选概率最高的前 tau_hat(x) 个像素
```

因此真正的计算难点是：怎么找到 `tau_hat(x)`。

## 1. 为什么 tau 难算

理论上，`tau` 可以从：

```text
0, 1, 2, ..., d
```

里面选。

如果一张图片有 `512 x 512` 个像素，那么：

```text
d = 262144
```

光是枚举 `tau` 就很多。更麻烦的是，每个 `tau` 的得分还需要计算 Poisson-binomial 随机变量的概率：

```text
P(Gamma = l)
P(Gamma_minus_j = l)
```

这些概率描述的是“真实前景像素数量可能是多少”。对于高维图像，这个分布不容易直接算。

论文第 2.3 节的全部目的就是让这件事可计算。

## 2. pi_tau 是什么

论文把每个候选体积的目标值写成：

```text
pi_tau(x) = omega_tau(x) + nu_tau(x)
```

可以这样理解：

```text
pi_tau(x) = 如果我选择前 tau 个像素，估计得到的期望 Dice 分数
```

所以 RankDice 做的是：

```text
tau_hat(x) = argmax_tau pi_tau(x)
```

`omega_tau` 主要来自 Dice 分子的 `2TP` 部分，也就是选中像素和真实前景重合的贡献。

`nu_tau` 来自 smoothing 参数 `gamma` 的那部分。如果 `gamma = 0`，这部分会消失。

读这节时不用把 `omega` 和 `nu` 的每个细节都背下来。你只要知道：

```text
作者把复杂目标拆成两个可计算的部分，
然后围绕这两个部分做精确计算或近似计算。
```

## 3. 低维情况：FFT 精确算法

如果维度不高，例如：

```text
d <= 500
```

论文说可以精确计算 Poisson-binomial 分布的概率质量函数，也就是：

```text
P(Gamma = 0), P(Gamma = 1), ..., P(Gamma = d)
```

作者使用 FFT，也就是 fast Fourier transform。

你可以把 FFT 理解成一种快速计算多项式卷积的工具。Poisson-binomial 分布本质上可以通过很多 Bernoulli 变量的生成函数相乘得到，而“很多东西相乘/卷积”正是 FFT 擅长加速的地方。

对阅读论文而言，不需要深入 FFT 细节。记住：

```text
低维时，作者可以较准确地算出真实所需概率。
```

## 4. 递推更新 omega_tau

论文公式 (9) 说：

```text
omega_tau = omega_{tau-1} + 新加入第 tau 个像素的贡献
```

直觉很简单：

如果从 `tau - 1` 增加到 `tau`，其实只是多选了一个像素，也就是排序后的第 `tau` 个像素。

所以不需要每次从头算：

```text
tau = 1 从头算
tau = 2 从头算
tau = 3 从头算
...
```

而是可以：

```text
上一步结果 + 新增像素贡献
```

这降低了存储和计算压力。

## 5. 高维情况：为什么需要近似

图像分割里 `d` 很大。比如：

```text
32 x 32    -> d = 1024
512 x 512  -> d = 262144
```

这时精确计算每个 `tau` 的 Poisson-binomial 概率会太慢。

论文采用三类加速思想：

1. shrinkage：缩小 `tau` 的搜索范围。
2. T-RNA：用 refined normal approximation 近似 Poisson-binomial。
3. BA：blind approximation，进一步简化以适合 GPU 并行。

## 6. Lemma 3：shrinkage 是什么

Lemma 3 给出一个提前停止条件。

直觉是：

```text
如果前 tau 个像素的累计概率已经足够大，
而第 tau+1 个像素的概率相对太小，
那么继续增加 tau 不会让 pi_tau 更好。
```

论文条件大概是：

```text
sum_{s=1}^tau q_hat_{j_s}(x) >= (tau + gamma + d) q_hat_{j_{tau+1}}(x)
```

如果这个条件成立，那么：

```text
pi_tau(x) >= pi_tau'(x), 对所有 tau' > tau
```

也就是说，后面不用看了。

因此搜索范围可以从：

```text
0 到 d
```

缩到：

```text
0 到 d0(x)
```

这里 `d0(x)` 是第一个满足提前停止条件的位置。

## 7. well-separated segmentation 是什么

论文提到 well-separated segmentation。

意思是：少数像素概率很高，其他像素概率明显低。

例如：

```text
[0.99, 0.98, 0.97, 0.05, 0.04, 0.03, ...]
```

这种情况下，前几个像素和后面像素差距很大，`d0(x)` 往往很小。搜索体积就会非常快。

在实际分割里，如果目标区域和背景区分明显，这种现象比较常见。

## 8. T-RNA：截断精细正态近似

T-RNA 是：

```text
Truncated refined normal approximation
```

可以拆成三层：

### 第一层：normal approximation

Poisson-binomial 是很多独立 0/1 随机变量相加。很多随机变量相加时，中心极限定理告诉我们，它的分布可以近似成正态分布。

所以：

```text
Gamma ≈ Normal(mu, sigma^2)
```

其中：

```text
mu = sum_j q_hat_j(x)
sigma^2 = sum_j q_hat_j(x)(1 - q_hat_j(x))
```

### 第二层：refined normal

普通正态近似有时不够准，因为 Poisson-binomial 可能有偏斜。

论文加了 skewness 修正，也就是考虑分布是不是左右不对称。这个修正后的 CDF 用 `Psi` 表示。

不需要记住 `Psi` 的详细公式。理解成：

```text
比普通正态更精细一点的近似分布。
```

### 第三层：truncated

Poisson-binomial 的取值是：

```text
0, 1, ..., d
```

但绝大多数概率质量集中在均值 `mu` 附近。太远的 `l`，概率几乎为 0。

因此只需要计算一个区间：

```text
L(epsilon)
```

例如从一个低分位数到一个高分位数。`epsilon` 越小，保留区间越宽，误差越小，计算越慢。

所以 T-RNA 的意思是：

```text
用带偏度修正的正态分布近似 Poisson-binomial，
并且只计算概率质量主要集中的那段 l。
```

## 9. Lemma 4：T-RNA 的误差怎么看

Lemma 4 给出 T-RNA 近似误差上界。

公式很长，但可以只读它的结构：

```text
误差 <= 和 epsilon 有关的项 + 和 1/sigma^2 有关的项 + log(d) 项
```

含义是：

1. `epsilon` 是你主动设置的截断容忍度，越小越准。
2. `sigma^2` 越大，正态近似越可靠。
3. 高维时虽然有 `log(d)`，但如果 `sigma^2` 也增长，误差可以接受。

论文强调，在图像分割里 `d` 很大，`sigma^2` 往往也不小，所以这种近似在实践中可用。

## 10. BA：Blind Approximation

T-RNA 虽然省了很多计算，但它的递推结构不太适合 GPU 并行。

BA 的想法是进一步近似：

```text
Gamma_minus_j 的分布 ≈ Gamma 的分布
```

为什么可以这么做？因为在高维图像里，`Gamma` 是很多像素的和。去掉一个像素以后，总体分布变化通常很小。

例如 `d = 262144`，少掉 1 个像素，对总前景数量分布的影响一般不大。

所以 BA 把：

```text
P(Gamma_minus_j = l)
```

近似为：

```text
P(Gamma = l)
```

这样很多计算可以统一起来，并通过 convolution 或 FFT 并行加速。

## 11. Lemma 5：BA 的误差怎么看

Lemma 5 给出 BA 的误差上界。

和 T-RNA 相比，BA 多了一个额外误差项，大概和：

```text
1 / sigma
```

有关。

直觉是：BA 多做了一层“去掉一个像素也差不多”的近似，所以误差会比 T-RNA 略大。但换来的好处是适合 GPU 并行，速度更快。

## 12. Algorithm 1 逐步解释

Algorithm 1 是 RankDice 的计算流程。

### 第 1 行：估计概率

训练模型，得到：

```text
q_hat(x)
```

### 第 2 行：排序

把概率从大到小排：

```text
j_1, j_2, ..., j_d
```

### 第 4 行：累计和

计算排序后概率的累计和：

```text
s_1 = q_hat_{j_1}
s_2 = q_hat_{j_1} + q_hat_{j_2}
...
```

这个用于 shrinkage 和 BA 计算。

### 第 5 行：求 d0

用 Lemma 3 找到提前停止上界：

```text
d0(x)
```

后面只搜索：

```text
tau = 0, ..., d0(x)
```

### 第 6 到 10 行：选择精确或近似范围

如果不用近似，就：

```text
L = {0, ..., d}
```

如果用 T-RNA 或 BA，就只保留：

```text
L(epsilon) = {l_L, ..., l_U}
```

### 第 11 行：计算 Poisson-binomial 概率

计算：

```text
P(Gamma = l)
```

或其近似值。

### 第 12 到 20 行：计算每个 tau 的得分

如果用 BA，就批量算。

否则就递推算：

```text
tau = 1, 2, ..., d0
```

### 第 21 行：选择 tau_hat

```text
tau_hat = argmax pi_tau
```

### 第 22 行：输出预测

```text
选概率最高的前 tau_hat 个像素。
```

## 13. 这节最应该记住什么

第 2.3 节看起来公式很多，但主线其实很清楚：

```text
RankDice 需要为每张图选择最优预测体积 tau。
精确计算需要 Poisson-binomial 概率。
低维可以 FFT 精确算。
高维先用 shrinkage 缩小 tau 范围，
再用 T-RNA 或 BA 近似概率和加速计算。
```

如果只是为了读懂论文思想，优先掌握：

```text
shrinkage = 提前停止搜索 tau
T-RNA = 用修正正态近似 Poisson-binomial
BA = 用 Gamma 近似 Gamma_minus_j，方便 GPU
```

