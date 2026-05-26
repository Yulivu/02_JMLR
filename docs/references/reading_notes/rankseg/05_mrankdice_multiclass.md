# 第 3 节：mRankDice 多类别/多标签扩展

第 2 节讨论的是二分类分割：每个像素只需要判断是不是目标区域。第 3 节讨论更常见的场景：一张图里有多个类别，比如道路、车、人、天空。

## 1. 从 Dice 到 mDice

二分类分割里，真实标签是：

```text
Y in {0, 1}^d
```

多类别或多标签分割里，真实标签变成：

```text
Y_{·1}, Y_{·2}, ..., Y_{·K}
```

其中 `K` 是类别数量。

可以把它想成一个矩阵：

```text
d 个像素 x K 个类别
```

第 `j` 个像素、第 `k` 个类别的标签是：

```text
Y_{jk}
```

如果：

```text
Y_{jk} = 1
```

表示第 `j` 个像素属于第 `k` 类。

对每个类别都可以算一个 Dice：

```text
Dice_k
```

然后把所有类别的 Dice 加权平均，就得到 mDice：

```text
mDice = sum_k alpha_k Dice_k
```

这里 `alpha_k` 是类别权重。最简单情况是每个类别同等重要：

```text
alpha_k = 1 / K
```

## 2. multilabel 和 multiclass 的区别

论文区分两个概率建模方式：multilabel 和 multiclass。

### multilabel

multilabel 表示一个像素可以同时属于多个类别。

例如医学图像或文本 feature 中，一个位置可能同时有多个属性。

数学上：

```text
||Y_j||_1 可以是 0, 1, 2, ..., K
```

也就是说，第 `j` 个像素的多个类别标签可以同时为 1。

这种情况下，模型通常用 sigmoid 输出：

```text
q_{jk}(x) in [0, 1]
```

每个类别独立给一个概率。训练损失常用 binary cross-entropy。

### multiclass

multiclass 表示一个像素只能属于一个类别。

例如语义分割里，一个像素要么是 road，要么是 car，要么是 person，通常不会同时是多个类别。

数学上：

```text
||Y_j||_1 = 1
```

每个像素所有类别概率加起来等于 1：

```text
sum_k q_{jk}(x) = 1
```

模型通常用 softmax 输出，训练损失常用 multiclass cross-entropy。

## 3. overlapping 和 non-overlapping 的区别

论文还区分预测结果是否允许重叠。

### overlapping

overlapping 表示不同类别的预测区域可以重叠。

例如第 `j` 个像素可以同时被预测为类别 1 和类别 2：

```text
Delta_{j1}(x) = 1
Delta_{j2}(x) = 1
```

在这种情况下，各个类别之间没有互斥约束。

### non-overlapping

non-overlapping 表示每个像素只能被分给一个类别。

论文写成：

```text
sum_k Delta_k(x) = 1_d
```

意思是对每个像素，所有类别预测加起来必须等于 1。

这就像普通语义分割的 argmax 规则：每个像素最终只能拿一个类别标签。

## 4. Lemma 6：overlapping 情况很简单

Lemma 6 的结论是：

```text
如果允许类别预测重叠，
那么 mDice 最优问题可以拆成 K 个单独的 Dice 最优问题。
```

为什么？

因为：

```text
mDice = alpha_1 Dice_1 + alpha_2 Dice_2 + ... + alpha_K Dice_K
```

如果类别之间没有互斥约束，那么优化 `Dice_1` 不会影响 `Dice_2`，优化 `Dice_2` 也不会影响 `Dice_3`。

所以每个类别可以单独跑一次 RankDice。

这就是 mRankDice 最自然的扩展：

```text
对每个类别 k：
    取第 k 类概率 q_{·k}(x)
    排序
    估计 tau_k
    选前 tau_k 个像素作为第 k 类预测
```

## 5. Lemma 7：non-overlapping 情况很难

如果要求每个像素只能属于一个类别，问题就复杂了。

原因是不同类别之间会相互抢像素。

例如一个像素对类别 car 的概率是 0.51，对类别 bus 的概率是 0.50。单独看两个类别，它可能都值得选；但 non-overlapping 要求它只能选一个。

Lemma 7 说：即使每个类别的最优体积 `tau_k` 都已经知道，求 non-overlapping 的 Bayes rule 仍然等价于 assignment problem。

assignment problem 可以理解成“把像素分配给类别，使总收益最大，同时满足每个类别要拿多少像素、每个像素只能分给一个类别”。

如果最优体积都不知道，那就更难。论文说一般会变成非线性整数优化，可能是 NP-hard。

所以这篇论文主要处理 overlapping 版本，把 non-overlapping 的更优算法留作 future work。

## 6. mRankDice 的三种情况

论文总结了三种情况。

### multilabel + overlapping

训练方式：

```text
sigmoid 输出
binary cross-entropy
```

预测方式：

```text
每个类别单独 RankDice
```

这是最直接的情况。

### multiclass + overlapping

训练方式：

```text
softmax 输出
multiclass cross-entropy
```

虽然训练时每个像素类别概率和为 1，但预测时如果允许 overlapping，后处理仍然可以：

```text
每个类别单独 RankDice
```

也就是说，概率估计方式变了，但排序和体积估计不变。

### multilabel/multiclass + non-overlapping

这是难的情况。

论文没有给出完整最优 mRankDice 方案，而是指出它与 assignment problem 和整数优化有关，留作未来研究。

## 7. Algorithm 2 怎么读

Algorithm 2 很短，核心就是：

1. 如果是 multilabel，就用式 (17) 估计概率。
2. 如果是 multiclass，就用式 (18) 估计概率。
3. 对每个类别 `k = 1, ..., K`：

```text
用第 k 类概率运行 Algorithm 1 的 RankDice。
```

最后输出：

```text
Delta_hat(x) = (Delta_hat_1(x), ..., Delta_hat_K(x))
```

## 8. 和传统 argmax 的区别

传统 multiclass 语义分割常用：

```text
每个像素取概率最大的类别
```

也就是 argmax。

mRankDice 不是逐像素 argmax。它是每个类别分别问：

```text
对这个类别来说，我应该选多少个像素才能让 Dice 最好？
```

所以它更关注每个类别的区域整体质量，而不是单个像素局部最大概率。

## 9. 这节最应该记住什么

第 3 节的核心可以压缩成三句话：

```text
mDice 是多个类别 Dice 的加权平均。
如果允许类别预测重叠，mDice 最优可以拆成每个类别单独 RankDice。
如果不允许重叠，类别之间会抢像素，问题会变成 assignment/integer optimization，论文没有完全解决。
```

