# RankSEG 阅读路线

这组笔记对应论文 `2023_RankSEG_Consistent_Ranking_Framework_for_Segmentation_JMLR.pdf`。论文题目是 **RankSEG: A Consistent Ranking-based Framework for Segmentation**，发表于 JMLR 2023。

先说结论：这篇论文不是 Tensor CRF 方法本身，更像是一篇“分割任务的理论框架 + 损失一致性 + Bayes 最优规则”的参考论文。它放在 `2_Tensor_CRF_JMLR` 里是合理的，因为它和 JMLR 理论写法、结构化预测、分割指标一致性有关；但它的核心不是 CRF，也不是 tensor network。

## 这篇论文到底在讲什么

分割任务里，模型通常先给每个像素一个概率，例如“这个像素属于前景的概率是 0.73”。传统做法是：

1. 训练一个概率模型，比如用 cross-entropy。
2. 对每个像素做固定阈值判断，比如概率大于 0.5 就预测为前景。

论文说：如果最终评估指标是 Dice 或 IoU，那么这个固定阈值框架理论上并不总是最优。原因是 Dice/IoU 看的是“整张图预测出来的区域和真实区域有多重合”，不是每个像素单独分类对不对。

RankSEG 的想法是：

1. 先估计每个像素属于目标区域的条件概率。
2. 按概率从大到小排序。
3. 不用固定阈值，而是估计这张图应该选多少个像素，也就是最优体积 `tau`。
4. 最后选择概率最高的前 `tau` 个像素。

所以它不是简单地问“这个像素概率是否超过 0.5”，而是问“这张图里最应该选出多少个最可信的像素，才能让 Dice 最高”。

## 建议阅读顺序

如果数学基础不强，不建议从论文原文第 2 节公式直接硬啃。建议按下面顺序读这组笔记：

1. `03_math_foundations.md`
   先补符号、Dice、条件概率、Bernoulli、Poisson-binomial、Bayes rule 等基础。

2. `01_background_and_intro.md`
   读论文第 1 节：分割任务、Dice/IoU、固定阈值框架、为什么传统方法不够。

3. `02_rankdice_core.md`
   读论文第 2 节：Theorem 1 和 RankDice 三步法。这是全文核心。

4. `04_volume_estimation_algorithms.md`
   读第 2.3 节：作者怎么实际求最优 `tau`。这里算法多，但主线其实是“精确算太慢，所以做近似”。

5. `05_mrankdice_multiclass.md`
   读第 3 节：多类别/多标签扩展。

6. `06_theory_proofs.md`
   读第 4 节和附录证明：Dice-calibrated、Lemma 9、Lemma 10、Theorem 11、Corollary 12。这里是论文最像 JMLR 理论文章的部分。

7. `07_experiments_and_takeaways.md`
   读第 5、6 节：实验怎么证明它有用，哪些结果值得记。

8. `08_symbol_glossary.md`
   看公式时随手查符号。

## 论文结构总览

第 1 节 Introduction：
介绍分割任务、Dice/IoU 指标、传统固定阈值框架，以及为什么分类损失加固定阈值可能不适合 Dice/IoU。

第 2 节 RankDice：
给出 Dice 指标下的 Bayes 最优分割规则。核心结论是：先按条件概率排序，再选择最优预测体积。RankDice 就是这个 Bayes 规则的 plug-in 版本。

第 2.3 节 Scalable computing schemes：
解决实际计算问题。低维可以精确算 Poisson-binomial 概率；高维图像分割要用 shrinkage、T-RNA、BA 等近似算法。

第 3 节 mDice-segmentation and mRankDice：
把二分类分割推广到多类别、多标签分割。重点是 overlapping 情况可以拆成每个类别一个 RankDice；non-overlapping 情况会变得像 assignment problem，比较难。

第 4 节 Theory：
证明 RankDice 是 Dice-calibrated，而固定阈值加 classification-calibrated loss 不是 Dice-calibrated。还给出 Dice excess risk bound：如果概率估计得好，RankDice 的 Dice 表现就接近最优。

第 5 节 Experiments：
模拟实验和真实数据集实验。主要结论是，在同一个训练模型输出的概率上，RankDice 的后处理经常比固定阈值和 argmax 更好，尤其在难分割类别上更明显。

第 6 节 Conclusions：
总结 RankSEG/RankDice/RankIoU，承认 non-overlapping 多类别最优问题还没有完全解决。

## 一句话理解

传统分割像是在每个像素上单独做考试：“概率超过 0.5 就通过。”RankDice 像是在整张图上做预算：“我应该选出多少个最可能正确的像素，才能让整张图的 Dice 分数最高。”

