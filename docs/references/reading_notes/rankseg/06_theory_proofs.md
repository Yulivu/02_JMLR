# 第 4 节和附录：理论证明慢读

这份笔记解释论文最难的理论部分：Dice-calibrated、Lemma 9、Lemma 10、Theorem 11、Corollary 12，以及 IoU 的平行结果。

先给一个心理预期：这一节不是为了让你手推每一行不等式，而是理解作者在证明什么、为什么这样证明、每个结论在论文中起什么作用。

## 1. 第 4 节整体逻辑

作者想证明三件事：

1. 传统固定阈值框架在 Dice 指标下不一致。
2. RankDice 在 Dice 指标下是一致的。
3. 如果概率估计误差小，那么 RankDice 的 Dice 分数离最优 Dice 不远。

对应论文结论：

```text
Lemma 9：传统 fixed threshold + classification-calibrated loss 不是 Dice-calibrated
Lemma 10：RankDice + strictly proper loss 是 Dice-calibrated
Theorem 11：RankDice 的 excess Dice risk 被概率估计误差控制
Corollary 12：如果 cross-entropy 学得好，Dice excess risk 也会收敛
```

## 2. Definition 8：Dice-calibrated

论文定义：

```text
M_gamma: P -> D
```

这里 `M_gamma` 是一个 population segmentation method。

不用怕这个写法。它的意思是：

```text
如果我知道完整的数据分布 P_{X,Y}，
这个方法会输出一个分割规则。
```

Dice-calibrated 的定义是：

```text
Dice_gamma(M_gamma(P_{X,Y})) = Dice_gamma(delta*)
```

其中 `delta*` 是 Theorem 1 里的 Bayes 最优 Dice 分割规则。

翻译：

```text
在理论层面，如果数据分布完全已知，
这个方法能达到 Dice 最优分割的表现，
那么它就是 Dice-calibrated。
```

这是一个“最低限度的一致性要求”。如果一个方法连 population 层面都不能达到 Bayes 最优，那么样本再多、模型再大，也可能在 Dice 目标下有系统性偏差。

## 3. Lemma 9：固定阈值为什么不是 Dice-calibrated

Lemma 9 说：

```text
classification-calibrated loss + 固定 0.5 阈值
不是 Dice-calibrated。
```

cross-entropy 和 focal loss 都属于这里讨论的范围。

关键点是：问题不在于 cross-entropy 不能学概率。相反，cross-entropy 在理想情况下能学到真实条件概率：

```text
q(x) = p(x)
```

问题出在后处理：

```text
delta(x) = 1(q(x) >= 0.5)
```

这个固定 0.5 阈值是分类 Bayes rule，不是 Dice Bayes rule。

### Lemma 9 的最小反例

附录 D.7 用 `d = 2` 的例子说明。

假设：

```text
gamma = 0
d = 2
p_1(x) > p_2(x)
```

作者计算出：

```text
如果 0.5 * p_1(x) > p_2(x)，Bayes Dice 选择 (1, 0)
否则 Bayes Dice 选择 (1, 1)
```

然后取：

```text
p_1(x) = 0.45
p_2(x) = 0.44
```

固定 0.5 阈值得到：

```text
(0, 0)
```

但 Bayes Dice 规则判断：

```text
0.5 * p_1 = 0.225
p_2 = 0.44
```

因为：

```text
0.225 < 0.44
```

所以 Bayes Dice 选择：

```text
(1, 1)
```

因此：

```text
固定阈值输出 != Dice Bayes 最优输出
```

这就证明了它不是 Dice-calibrated。

### 为什么这个反例很有力

这个例子非常小，只有两个像素。它说明即使在最简单的场景中，固定 0.5 阈值也可能和 Dice 最优规则不同。

它不是在说 cross-entropy 不能训练模型，而是在说：

```text
学到正确概率以后，如果还用分类阈值做分割决策，
仍然可能不是 Dice 最优。
```

## 4. Lemma 10：RankDice 为什么是 Dice-calibrated

Lemma 10 说：

```text
RankDice + strictly proper loss 是 Dice-calibrated。
```

这里有一个关键词：

```text
strictly proper loss
```

直觉上，strictly proper loss 是一种能让最优预测等于真实概率的损失。

常见例子：

```text
cross-entropy
squared error
```

在 population 层面，如果用 strictly proper loss 估计概率，那么最优解满足：

```text
q_hat(x) = p(x)
```

RankDice 接下来做的事是：

1. 用 `q_hat` 排序。
2. 用 `q_hat` 估计最优体积。
3. 选前 `tau_hat` 个。

如果：

```text
q_hat = p
```

那么 RankDice 里的排序和体积估计就完全等同于 Theorem 1 的 Bayes Dice 规则。

所以：

```text
RankDice 输出 = delta*
```

这就证明 RankDice 是 Dice-calibrated。

## 5. Theorem 11：excess risk bound

Theorem 11 是论文最重要的统计保证。

它说：

```text
Dice_gamma(delta*) - Dice_gamma(delta_hat)
<= C_1 E_X ||q_hat(X) - p(X)||_1
```

拆开看：

```text
delta* = 理论最优 Dice 分割
delta_hat = RankDice 基于估计概率 q_hat 得到的分割
```

左边：

```text
Dice(delta*) - Dice(delta_hat)
```

表示 RankDice 距离理论最优还差多少。

右边：

```text
E_X ||q_hat(X) - p(X)||_1
```

表示估计概率和真实概率之间的平均 L1 误差。

所以 Theorem 11 的直觉是：

```text
如果概率估计得准，RankDice 的分割表现就接近 Dice 最优。
```

## 6. Theorem 11 证明思路

证明不需要逐行硬背，可以抓住三步。

### 第一步：定义一个 plug-in Dice

真实 Dice 使用真实概率 `p` 计算。

RankDice 用估计概率 `q_hat` 计算一个估计版 Dice，论文记作类似：

```text
hat_Dice
```

注意这不是最终验证集 Dice，而是理论证明里用来比较的中间对象。

### 第二步：证明真实 Dice 和估计 Dice 差距不大

如果：

```text
q_hat(x) 接近 p(x)
```

那么用 `q_hat` 算出来的 Dice 目标和用 `p` 算出来的真实 Dice 目标不会差太多。

论文通过三角不等式和期望差距，把这个差距控制在：

```text
常数 * ||q_hat(x) - p(x)||_1
```

### 第三步：利用 RankDice 对估计目标最优

RankDice 的 `delta_hat` 是让估计目标最大的规则。

所以对于估计目标来说：

```text
hat_Dice(delta_hat) >= hat_Dice(delta*)
```

换句话说，虽然 `delta*` 是真实目标最优，但在估计目标下，RankDice 至少不会比 `delta*` 差。

因此真实目标的损失差距只来自：

```text
估计目标和真实目标之间的误差
```

而这个误差已经在第二步被概率估计误差控制住了。

这就是 Theorem 11 的证明结构。

## 7. Corollary 12：从 cross-entropy 到 Dice 收敛

Corollary 12 进一步说：

如果 cross-entropy 的 excess risk 是：

```text
E_CE(q_hat) = O_P(epsilon_n)
```

那么：

```text
Dice(delta*) - Dice(delta_hat) = O_P(sqrt(d * epsilon_n^{1/2}))
```

论文排版里这个速率写法不太直观，可以理解为：

```text
cross-entropy 学得越好，
概率估计越接近真实概率，
RankDice 的 Dice 表现也越接近最优。
```

证明用到 Pinsker inequality。

## 8. Pinsker inequality 是什么

Pinsker inequality 是一个把 KL divergence 和 L1/TV distance 联系起来的不等式。

粗略说：

```text
KL 小 -> 概率分布的 L1 差距也小
```

cross-entropy 的 excess risk 本质上和 KL divergence 有关。

因此：

```text
cross-entropy excess risk 小
=> KL 小
=> L1 概率误差小
=> Theorem 11 右边小
=> Dice excess risk 小
```

这就是 Corollary 12 的逻辑链。

## 9. 第 4.2 节：Dice 和 IoU 的关系

论文还讨论 IoU。

Lemma 13 说：IoU 的 Bayes rule 也具有类似结构：

```text
先按 p_j(x) 排序，
再选择最优 tau*(x)。
```

所以 RankIoU 也可以做成：

1. 估计条件概率。
2. 排序。
3. 用 IoU 版本公式估计体积。
4. 选前 `tau` 个。

但是 IoU 的体积估计公式和 Dice 不完全一样，计算上可能更贵。尤其高维情况下，Dice 的 BA 近似不一定适合 IoU。

Theorem 15 给出 IoU 的平行 excess risk bound：

```text
IoU(delta*) - IoU(delta_hat)
<= C_2 E_X ||q_hat(X) - p(X)||_1
```

意思和 Theorem 11 类似：概率估计好，RankIoU 表现接近最优。

## 10. 附录 D.1：Theorem 1 证明慢读

Theorem 1 的证明可以这样理解。

作者固定一个输入 `x`，然后想找：

```text
delta*(x) = argmax_v Dice(v | x)
```

这里 `v` 是一个 0/1 预测向量。

### 第一步：固定预测体积 tau

假设：

```text
||v||_1 = tau
```

也就是已经决定这次要选 `tau` 个像素。

现在问题变成：

```text
在所有选 tau 个像素的方案里，选哪些像素最好？
```

### 第二步：把 Dice 贡献拆成每个像素的加和

作者把 Dice 的期望写成：

```text
sum_{j in I(v)} s_j(tau) + 只和 tau 有关的项
```

因为第二项只和 `tau` 有关，所以在固定 `tau` 时，选择哪些像素只取决于：

```text
s_j(tau)
```

哪个 `s_j(tau)` 大，就更应该选哪个像素。

### 第三步：证明 s_j(tau) 的排序等于 p_j(x) 的排序

作者比较两个像素 `j` 和 `j'`：

```text
D_{jj'}(tau) = s_j(tau) - s_{j'}(tau)
```

利用条件独立性，最后得到：

```text
D_{jj'}(tau) 的正负号
和 p_j(x) - p_{j'}(x) 的正负号一致
```

所以：

```text
s_j(tau) >= s_{j'}(tau)
等价于
p_j(x) >= p_{j'}(x)
```

这一步非常关键。它证明了：

```text
固定 tau 时，最优方案就是选概率最大的 tau 个像素。
```

### 第四步：再搜索 tau

既然固定 `tau` 时应该选前 `tau` 个概率最高像素，那么只剩下：

```text
tau = 0, 1, ..., d
```

哪个最优。

这就得到 Theorem 1。

## 11. 理论部分最重要的“因果链”

整篇理论可以记成一条链：

```text
Dice 的 Bayes rule
=> 概率排序 + 自适应体积选择
=> 固定 0.5 阈值不符合这个 Bayes rule
=> RankDice 按这个 Bayes rule 做 plug-in
=> 如果 loss 能估计真实概率，RankDice 就 Dice-calibrated
=> 如果概率估计误差小，RankDice 的 Dice excess risk 小
```

如果你只能背一段话，就背这段。

