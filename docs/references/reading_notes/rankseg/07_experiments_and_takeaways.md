# 第 5、6 节：实验、结论和可借鉴写法

这一份笔记对应论文的 Numerical experiments、Conclusions and future work。实验部分的核心不是证明某个网络最强，而是证明：

```text
在同一个概率模型输出上，
把固定阈值/argmax 后处理换成 RankDice，
通常能提高 Dice/IoU。
```

## 1. 实验要验证什么

论文实验主要验证三个观点：

1. 固定阈值不是 Dice 最优，尤其当不同输入需要不同阈值时。
2. RankDice 的 adaptive volume selection 能带来更好的 Dice。
3. 在真实分割数据集上，RankDice 可以作为概率输出后的后处理框架，配合不同网络和 loss 使用。

注意：RankDice 不是重新发明一个神经网络架构。它更多是在已有网络输出概率之后，改变最后的决策方式。

## 2. 模拟实验 Example 1

Example 1 构造了一些二维概率矩阵，模拟图像分割里的空间结构。

作者设计了三类概率衰减模式：

```text
step decay
exponential decay
linear decay
```

可以理解成：真实前景区域或高概率区域从某些位置开始逐渐变弱。

实验设置里，作者假设真实概率 `p_j(x)` 已经完美知道。这样做的目的是排除训练模型误差，只比较后处理决策：

```text
固定阈值 0.5
RankDice
```

这个设计很干净，因为它把问题聚焦在：

```text
即使概率已经知道，固定阈值是不是最优？
```

实验结论是：RankDice 在很多设置下明显优于固定阈值。特别是概率衰减更明显、目标和背景更分离时，RankDice 优势更大。

## 3. 模拟实验 Example 2

Example 2 专门说明一个重要问题：

```text
不同图片的最优阈值不同。
```

作者让每张图的目标区域大小或概率模式不同，然后比较：

```text
固定阈值 0.1, 0.2, ..., 0.9
RankDice
```

结果是：即使你调固定阈值，RankDice 仍然更好。

原因是固定阈值只能给所有图片用同一条线，而 RankDice 每张图都会估计自己的最优 `tau`，等价于每张图有自己的阈值。

这正好呼应 Remark 2：

```text
Dice 最优阈值是输入相关的，不应该固定。
```

## 4. 真实数据集

论文使用了三个真实数据集：

```text
Fine-annotated CityScapes
PASCAL VOC 2012
Kvasir-SEG
```

其中：

CityScapes 和 PASCAL VOC 是多类别语义分割数据集。

Kvasir-SEG 是医学息肉分割数据集，主要是单类别分割。

论文测试了多个网络架构：

```text
DeepLab-V3+
PSPNet
FCN8
```

也测试了多个 loss：

```text
CE
Focal
BCE
Soft-Dice
B-Soft-Dice
LovaszSoftmax
```

## 5. 实验比较对象

真实数据实验主要比较三种后处理方式：

```text
Threshold：固定阈值
Argmax：逐像素取最大类别
mRankDice / RankDice：排序 + 体积估计
```

重要的是：在许多比较里，它们基于同一个训练好的网络概率输出。

也就是说，RankDice 的提升不是因为换了更强网络，而是因为：

```text
概率到 mask 的决策规则更适合 Dice。
```

## 6. 表 2、表 3、表 4 怎么读

表 2：CityScapes。

表 3：PASCAL VOC 2012。

表 4：Kvasir-SEG。

这些表格的共同读法是：

1. 横向比较同一模型、同一 loss 下不同后处理的 Dice/IoU。
2. 看 mRankDice 是否高于 threshold/argmax。
3. 注意灰色或不适合的情况：论文指出 RankDice 理论上更适合 strictly proper loss，比如 CE、BCE。

整体结果：

```text
mRankDice 经常优于 threshold 和 argmax。
```

尤其在 CE、BCE 等概率解释较明确的 loss 下更符合理论预期。

## 7. 单类别结果为什么重要

论文还单独看 CityScapes 和 PASCAL VOC 里的每个类别。

这个分析很有价值，因为总体 mDice 可能掩盖某些类别的变化。

论文观察到：

```text
RankDice 在困难类别上提升更明显。
```

例如一些类别本身形状复杂、遮挡严重、和背景相似，固定阈值更容易失误，而 RankDice 的自适应体积估计更有帮助。

这也符合直觉：

```text
越是容易分割的类别，传统阈值已经不错；
越是困难类别，阈值选择更关键。
```

## 8. Figure 4 和 Figure 7 的意义

Figure 4 和 Figure 7 都在强调一个思想：

```text
最优阈值不是固定的。
```

Figure 7 是模拟数据上的最优阈值变化。

Figure 4 是 PASCAL VOC 上不同类别、不同样本的 RankDice 截断概率热力图。

这些图的作用是视觉化 Remark 2：

```text
不同输入 x 的最优 cutpoint 可能差异很大。
```

因此，统一用 0.5 或者统一调一个 threshold 都不够理想。

## 9. Temperature scaling 实验

论文还做了 temperature scaling，也就是概率校准。

Theorem 11 说：

```text
RankDice 的表现依赖概率估计 q_hat 是否接近真实 p。
```

所以如果模型概率校准更好，RankDice 可能更好。

Temperature scaling 的作用就是校准概率，让输出概率更接近真实置信度。

实验表明，概率校准有时能进一步改善 RankDice 表现，但需要额外验证集调温度参数。

## 10. 论文自己的 limitations

结论部分提到几个限制和未来方向。

最重要的是：

```text
non-overlapping 多类别最优分割还没有完全解决。
```

论文第 3 节已经说明，这种情况涉及 assignment problem 和整数优化，计算复杂。

另外，虽然 RankDice 理论上适合严格 proper loss 估计概率，但对于 focal loss、soft-Dice、Lovasz 等 loss 的行为还需要更细分析。

## 11. 如果你要写 related work 或 motivation

这篇论文可以被概括为：

```text
现有分割方法常把分割看成逐像素分类，再用固定阈值或 argmax 得到 mask。
但 Dice/IoU 是全局重合指标，逐像素分类最优和 Dice/IoU 最优并不等价。
RankSEG 从 Bayes 最优规则出发，提出排序加体积估计的后处理框架，并证明其 Dice/IoU calibration。
```

如果之后写自己的 project，可以借鉴这种叙事：

1. 指出常见做法和目标指标之间的 mismatch。
2. 给出理论最优规则。
3. 从理论规则导出可实现算法。
4. 证明 calibration 或 excess risk。
5. 用实验说明后处理或框架替换能带来稳定收益。

## 12. 这篇论文对我们最有用的地方

对当前 project 来说，这篇论文最值得吸收的不是具体实验数字，而是三种写作和理论套路：

1. 先定义任务的 population metric，再讨论 Bayes rule。
2. 用一个非常小的反例说明传统方法不一致。
3. 把方法设计成 Bayes rule 的 plug-in estimator，然后证明概率估计误差可以控制最终指标误差。

这是一种很 JMLR 的论文结构：问题定义清楚，理论对象清楚，方法从理论自然推出，实验只是验证理论动机。

