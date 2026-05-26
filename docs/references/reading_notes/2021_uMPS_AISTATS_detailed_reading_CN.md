# 2021 AISTATS: u-MPS Tensor Networks for Probabilistic Sequence Modeling 细读笔记

本文档带你细读 Jacob Miller, Guillaume Rabusseau, John Terilla 的论文 **Tensor Networks for Probabilistic Sequence Modeling**。目标不是把每个公式背下来，而是理解它们在做什么、为什么能用于序列建模、以及它对我们后续做 Tensor CRF / 结构化序列模型有什么启发。

> 适合读者：数学基础一般，但愿意通过例子理解公式。
>
> 读法建议：先读 0-2 节建立直觉，再读 3-8 节跟论文走，最后用 9-11 节复盘。

## 0. 论文信息与一句话总结

- 论文：Tensor Networks for Probabilistic Sequence Modeling
- 作者：Jacob Miller, Guillaume Rabusseau, John Terilla
- 会议：AISTATS 2021, PMLR 130:3079-3087
- 本地 PDF：`01_tensor_crf_project/2021_uMPS_Tensor_Networks_for_Probabilistic_Sequence_Modeling_AISTATS.pdf`
- 官方页面：[PMLR](https://proceedings.mlr.press/v130/miller21a.html)
- arXiv：[2003.01039](https://arxiv.org/abs/2003.01039)
- 官方代码：[jemisjoky/umps_code](https://github.com/jemisjoky/umps_code)

一句话总结：

这篇论文把一种循环式张量网络 **uniform Matrix Product State, u-MPS** 用作生成式序列模型，并证明它有三个有趣能力：可以并行评估序列概率、可以按正则表达式条件采样、还可以把正则表达式概率作为训练正则项。

更口语一点：

作者说，传统 RNN 像一个人从左到右读字符串，u-MPS 也有“顺序模型”的外形，但因为里面只有矩阵乘法，没有非线性激活，所以很多计算可以重新括号化并行做；更厉害的是，它能直接回答“生成一个满足这个正则表达式的字符串”的概率和采样问题。

## 1. 先别被名字吓到：本文到底在建什么模型

论文要处理的是 **probabilistic sequence modeling**，也就是给一个字符串或序列分配概率。

例如字母表是：

$$
\Sigma = \{a, b\}
$$

长度为 3 的所有字符串有：

```text
aaa, aab, aba, abb, baa, bab, bba, bbb
```

一个概率序列模型要做的事就是给它们分配概率，例如：

```text
P(aaa)=0.30
P(aab)=0.12
...
P(bbb)=0.05
```

如果长度固定为 3，这其实就是一个有 $2^3=8$ 个格子的表。长度变成 20 时，就有 $2^{20}$ 个格子，已经非常大。字母表更大、序列更长时，完整存储所有概率完全不可行。

u-MPS 的核心想法：

不用直接存一张巨大概率表，而是给每个字符一个小矩阵。一个字符串的分数由这些矩阵连乘得到。

形象例子：

```text
字符串 "abba"
分数 = 左边界向量 × A(a) × A(b) × A(b) × A(a) × 右边界向量
```

所以，论文其实是在问：

1. 这种“字符变矩阵、字符串变矩阵乘积”的模型能不能当概率模型？
2. 能不能高效计算归一化常数？
3. 能不能按正则表达式约束来采样？
4. 它在小数据、语法型任务上表现如何？

## 2. 符号速查表

| 符号 | 含义 | 小白解释 |
|---|---|---|
| $\Sigma$ | 字母表 | 可以出现的字符集合，例如 `{0,1}` 或所有 email 字符 |
| $\Sigma^n$ | 所有长度为 $n$ 的字符串 | 例如二进制长度 3 有 8 个 |
| $\Sigma^*$ | 所有有限长度字符串 | 长度 0、1、2、... 全部包含 |
| $s=s_1s_2\cdots s_n$ | 一个字符串 | 第 $i$ 个字符是 $s_i$ |
| $d=|\Sigma|$ | 字母表大小 | 二进制时 $d=2$ |
| $D$ | bond dimension / 隐状态维度 | 小矩阵的大小，越大表达力越强但越贵 |
| $\mathcal{A}$ | u-MPS 核张量 | 形状是 $(D,d,D)$ |
| $\mathcal{A}(c)$ | 字符 $c$ 对应的矩阵 | 从 $\mathcal{A}$ 中取出一个 $D \times D$ 切片 |
| $\alpha,\omega$ | 左右边界向量 | 让矩阵链最后变成一个标量 |
| $f_{\mathcal{A}}(s)$ | 字符串 $s$ 的振幅/分数 | 还不是概率，可能为负 |
| $\tilde P(s)$ | 未归一化概率 | $\tilde P(s)=|f_{\mathcal{A}}(s)|^2$ |
| $Z_n$ | 固定长度 $n$ 的归一化常数 | 把所有长度为 $n$ 的 $\tilde P$ 加起来 |
| $R$ | 正则表达式 | 例如 `a.*b`，表示某类字符串 |
| $Z_R$ | 匹配正则 $R$ 的总未归一化概率 | 把所有 $s \in R$ 的 $\tilde P(s)$ 加起来 |
| $\mathcal{E}^r,\mathcal{E}^{\ell}$ | 右/左 transfer operator | 用来“把所有可能字符求和”的线性算子 |

## 3. 预备知识 1：张量到底是什么

论文从 tensor network 讲起。你可以先这样理解：

| 名字 | 直觉 | 数学形状 |
|---|---|---|
| 标量 | 一个数 | $3.14$ |
| 向量 | 一排数 | $[1,2,3]$ |
| 矩阵 | 一张二维表 | $3 \times 4$ |
| 三阶张量 | 很多张矩阵叠成一摞 | $3 \times 4 \times 5$ |
| $n$ 阶张量 | 多维表 | $d_1 \times \cdots \times d_n$ |

对序列建模来说，一个很自然的张量是“长度为 $n$ 的所有字符串概率表”。

例子：

如果 $\Sigma=\{0,1\}$，长度 $n=3$，那么概率表可以写成一个三阶张量：

$$
T_{i_1,i_2,i_3}
$$

其中每个 $i_k$ 可以是 0 或 1。于是：

```text
T[0,0,0] = P("000")
T[0,0,1] = P("001")
T[0,1,0] = P("010")
...
```

问题来了：如果 $n=100$，这个表有 $2^{100}$ 个格子。无法直接存。

张量网络的目的就是：

把一个巨大的多维表，拆成很多小块，通过“连线求和”的方式表示。

## 4. 预备知识 2：tensor contraction 是什么

论文里最重要的操作是 **contraction**。最简单的 contraction 就是矩阵乘法。

假设：

$$
A =
\begin{bmatrix}
1 & 2\\
3 & 4
\end{bmatrix},
\quad
B =
\begin{bmatrix}
5 & 6\\
7 & 8
\end{bmatrix}
$$

矩阵乘法：

$$
(AB)_{1,1}=1\cdot5+2\cdot7=19
$$

这里的“对中间维度求和”就是 contraction。

再看向量内积：

$$
[1,2,3]\cdot[4,5,6]=1\cdot4+2\cdot5+3\cdot6=32
$$

这也是 contraction。

所以不要怕图里的线条。张量网络图中，一条连线通常表示“这个维度要被求和消掉”。最后如果所有线都被消掉，就得到一个数。

## 5. 预备知识 3：MPS 是把大表压成一串小张量

MPS 全称 Matrix Product State，也叫 Tensor Train。它把一个高阶张量写成一串小核心张量的乘积。

固定长度 MPS 的形式大概是：

$$
\mathcal{T}_{i_1,\ldots,i_n}
=
A^{(1)}_{i_1}
A^{(2)}_{i_2}
\cdots
A^{(n)}_{i_n}
$$

每个 $A^{(k)}_{i_k}$ 可以理解成一个小矩阵。

如果每个位置都有自己的核心 $A^{(k)}$，它适合固定长度；而本文使用的是 **uniform MPS**：

$$
A^{(1)} = A^{(2)} = \cdots = A
$$

也就是说，不管字符串有多长，每个位置都用同一个核心张量 $\mathcal{A}$。这就像 RNN 每一步复用同一组参数，所以它可以处理任意长度。

这也是 uniform 的意思：位置共享参数。

## 6. 第 3 节核心：u-MPS 如何给字符串打分

论文定义：

$$
f_{\mathcal{A}}(s)
=
\alpha^T
\mathcal{A}(s_1)
\mathcal{A}(s_2)
\cdots
\mathcal{A}(s_n)
\omega
$$

其中：

- $\mathcal{A}(s_i)$ 是字符 $s_i$ 对应的 $D\times D$ 矩阵。
- $\alpha^T$ 是左边界。
- $\omega$ 是右边界。
- 最后结果是一个数。

### 6.1 小例子：用 u-MPS 给 `"ab"` 打分

设字母表：

$$
\Sigma=\{a,b\}
$$

设 $D=2$，也就是每个字符对应 $2\times2$ 矩阵：

$$
A(a)=
\begin{bmatrix}
0.8 & 0.1\\
0.0 & 0.5
\end{bmatrix},
\quad
A(b)=
\begin{bmatrix}
0.2 & 0.0\\
0.4 & 0.7
\end{bmatrix}
$$

边界向量：

$$
\alpha=
\begin{bmatrix}
1\\
0
\end{bmatrix},
\quad
\omega=
\begin{bmatrix}
1\\
1
\end{bmatrix}
$$

字符串 `"ab"` 的分数是：

$$
f(ab)=\alpha^T A(a)A(b)\omega
$$

一步步算：

$$
\alpha^T A(a)=[1,0]
\begin{bmatrix}
0.8 & 0.1\\
0.0 & 0.5
\end{bmatrix}
= [0.8,0.1]
$$

再乘 $A(b)$：

$$
[0.8,0.1]A(b)
=
[0.8,0.1]
\begin{bmatrix}
0.2 & 0.0\\
0.4 & 0.7
\end{bmatrix}
=
[0.20,0.07]
$$

再乘 $\omega$：

$$
[0.20,0.07]
\begin{bmatrix}
1\\
1
\end{bmatrix}
=0.27
$$

所以：

$$
f(ab)=0.27
$$

这只是一个分数，还不是概率。

### 6.2 为什么说它是 compositional

论文指出：

$$
\mathcal{A}(st)=\mathcal{A}(s)\mathcal{A}(t)
$$

意思是，把字符串拼起来，对应的矩阵表示也拼起来。

例子：

```text
s = "ab"
t = "ba"
st = "abba"
```

那么：

$$
A(abba)=A(ab)A(ba)
$$

这很重要。因为正则表达式也有“拼接、或、重复”的结构，后面作者就是利用这个结构，把 regex 和 transfer operator 对齐起来。

## 7. u-MPS 为什么可以并行评估

普通 RNN 的计算大概是：

```text
h1 = RNN(h0, x1)
h2 = RNN(h1, x2)
h3 = RNN(h2, x3)
...
```

因为每一步有非线性，$h_2$ 必须等 $h_1$ 算完，$h_3$ 必须等 $h_2$ 算完。

u-MPS 的字符串分数是矩阵乘积：

$$
A(s_1)A(s_2)\cdots A(s_n)
$$

矩阵乘法满足结合律：

$$
(((A_1A_2)A_3)A_4)
=
((A_1A_2)(A_3A_4))
$$

所以长度为 4 时，可以这样并行：

```text
第 1 层：同时算 A1A2 和 A3A4
第 2 层：再算 (A1A2)(A3A4)
```

深度从 4 步变成约 $\log_2 4=2$ 步。

论文结论：

- 顺序评估成本：$\mathcal{O}(nD^2)$，但并行深度是 $\mathcal{O}(n)$。
- 并行评估成本：$\mathcal{O}(nD^3)$，但并行深度是 $\mathcal{O}(\log n)$。

直觉：

并行方法每次做的是矩阵乘矩阵，所以单次更贵；但在 GPU 上可以大量并行，长序列时可能更快。

论文实验中，长度 500、batch 100、$D=50$：

| 设备 | 顺序评估 | 并行评估 |
|---|---:|---:|
| CPU | 73.0 ms | 232.7 ms |
| GPU | 49.9 ms | 45.2 ms |

这说明：CPU 上顺序更划算，GPU 上并行稍快。

## 8. Born machine：如何把分数变成概率

问题：$f_{\mathcal{A}}(s)$ 可能是负数，但概率必须非负。

作者采用 Born machine 思路：

$$
\tilde P(s)=|f_{\mathcal{A}}(s)|^2
$$

然后固定长度 $n$ 时，用所有长度为 $n$ 的字符串做归一化：

$$
P_n(s)=\frac{\tilde P(s)}{Z_n}
$$

其中：

$$
Z_n=\sum_{s\in\Sigma^n}\tilde P(s)
$$

### 8.1 小例子：归一化长度为 2 的字符串

沿用前面的玩具矩阵，可以算出：

| 字符串 | $f(s)$ | $\tilde P(s)=f(s)^2$ |
|---|---:|---:|
| `aa` | 0.77 | 0.5929 |
| `ab` | 0.27 | 0.0729 |
| `ba` | 0.18 | 0.0324 |
| `bb` | 0.04 | 0.0016 |

所以：

$$
Z_2=0.5929+0.0729+0.0324+0.0016=0.6998
$$

于是：

$$
P_2(aa)=0.5929/0.6998\approx0.847
$$

$$
P_2(ab)=0.0729/0.6998\approx0.104
$$

这就是概率模型。

小白直觉：

`aa` 的矩阵链乘出来的分数最大，所以它分到的概率也最大。

## 9. Transfer operator：把“枚举所有字符串”变成矩阵递推

如果直接计算：

$$
Z_n=\sum_{s\in\Sigma^n}\tilde P(s)
$$

需要枚举所有长度为 $n$ 的字符串。二进制长度 30 就有十亿级别，不能这么做。

作者引入 transfer operator：

$$
\mathcal{E}^r(Q)
=
\sum_{c\in\Sigma} A(c)Q A(c)^T
$$

你可以把它理解成：

“给定右边已经聚合好的信息 $Q$，把当前字符的所有可能性都加进去。”

### 9.1 小例子：二进制字母表

如果 $\Sigma=\{0,1\}$，那么：

$$
\mathcal{E}^r(Q)
=A(0)QA(0)^T + A(1)QA(1)^T
$$

这行公式就是“对当前位置可能是 0 或 1 求和”。

如果有 3 个位置：

```text
所有字符串 = 000, 001, 010, 011, 100, 101, 110, 111
```

直接枚举是 8 项。transfer operator 做的是：

```text
第 3 个位置：把 0/1 聚合进 Q
第 2 个位置：再把 0/1 聚合进去
第 1 个位置：再把 0/1 聚合进去
```

最后用边界矩阵读出 $Z_3$。

论文写成：

$$
Z_n
=
\mathrm{Tr}\left(
Q_{\ell}^{\alpha}
(\mathcal{E}^r)^{\circ n}
(Q_r^{\omega})
\right)
$$

其中：

$$
Q_{\ell}^{\alpha}=\alpha\alpha^T,\quad
Q_r^{\omega}=\omega\omega^T
$$

这里的 $(\mathcal{E}^r)^{\circ n}$ 表示把 $\mathcal{E}^r$ 连续用 $n$ 次。

### 9.2 把 transfer operator 和 HMM 类比

如果你知道 HMM，可以这样类比：

- HMM 里，转移矩阵把隐藏状态概率往前推。
- u-MPS 里，transfer operator 把一个隐藏矩阵 $Q$ 往前推。

区别是 HMM 的状态是向量，u-MPS/Born machine 这里为了平方概率，状态变成了矩阵。

## 10. 正则表达式和 u-MPS：本文最漂亮的部分

论文第 4 节的关键想法：

正则表达式由几种操作递归定义，而 transfer operator 也可以按同样结构递归组合。

正则表达式的基本构造：

| regex 操作 | 例子 | 含义 |
|---|---|---|
| 字符串 literal | `ab` | 精确匹配 `"ab"` |
| 拼接 | `R1R2` | 先匹配 R1，再匹配 R2 |
| 并集 | `R1|R2` | 匹配 R1 或 R2 |
| Kleene star | `S*` | 重复 S 零次或多次 |

论文把每个 regex $R$ 对应到一个广义 transfer operator：

$$
\mathcal{E}^r_R(Q)
=
\sum_{s\in R} A(s)QA(s)^T
$$

这句话非常重要：

不是对所有字符串求和，而是只对匹配正则 $R$ 的字符串求和。

于是：

$$
Z_R
=
\sum_{s\in R}\tilde P(s)
$$

就表示模型分配给“所有匹配 $R$ 的字符串”的总分数。

### 10.1 字典表：regex 操作对应 transfer operator 操作

论文表 1 的核心可以这样记：

| regex | 右 transfer operator |
|---|---|
| $s$ | $\mathcal{E}^r_s(Q)=A(s)QA(s)^T$ |
| $R_1R_2$ | $\mathcal{E}^r_{R_1R_2}(Q)=\mathcal{E}^r_{R_1}(\mathcal{E}^r_{R_2}(Q))$ |
| $R_1|R_2$ | $\mathcal{E}^r_{R_1|R_2}(Q)=\mathcal{E}^r_{R_1}(Q)+\mathcal{E}^r_{R_2}(Q)$ |
| $S^*$ | $\mathcal{E}^r_{S^*}(Q)=\sum_{n=0}^{\infty}(\mathcal{E}^r_S)^{\circ n}(Q)$ |

### 10.2 小例子 1：`a|b`

正则：

```text
R = a|b
```

它匹配 `"a"` 或 `"b"`。

所以：

$$
\mathcal{E}^r_R(Q)
=
A(a)QA(a)^T + A(b)QA(b)^T
$$

这和普通的 $\mathcal{E}^r$ 一样，因为字母表就是 `{a,b}`。

### 10.3 小例子 2：`ab|ba`

正则：

```text
R = ab|ba
```

它匹配 `"ab"` 或 `"ba"`。

因此：

$$
\mathcal{E}^r_R(Q)
=
A(ab)QA(ab)^T + A(ba)QA(ba)^T
$$

其中：

$$
A(ab)=A(a)A(b)
$$

$$
A(ba)=A(b)A(a)
$$

这就把“两个候选字符串的总概率”变成了矩阵计算。

### 10.4 小例子 3：`a.*b`

如果字母表是 `{a,b}`，`.*` 可以理解为 $\Sigma^*$。

正则：

```text
R = a Σ* b
```

匹配所有以 `a` 开头、以 `b` 结尾的字符串，例如：

```text
ab
aab
abb
aaab
abab
...
```

u-MPS 可以计算：

$$
Z_R=\sum_{s\in R}\tilde P(s)
$$

这相当于问模型：

“你总共给所有以 `a` 开头、以 `b` 结尾的字符串分配了多少概率？”

神奇之处在于，不需要枚举无穷多个字符串，而是通过 $S^*$ 对应的几何级数或线性方程来计算。

## 11. 正则条件采样：REGSAMP 算法在做什么

第 5 节的 Theorem 1 说：

如果给定一个无歧义正则表达式 $R$，并且相关 transfer operator 收敛，那么 `REGSAMP(R, αα^T, ωω^T)` 可以从条件分布中采样：

$$
P(s \mid s\in R)
=
\frac{P(s)}{P(R)}
$$

直觉：

不是先随便生成再过滤，而是直接在“满足正则 $R$ 的空间里”抽样。

这点很重要。先生成再过滤在稀有约束下会非常浪费，例如你要生成“包含某个特定短语”的长文本，随机生成可能很久都遇不到。

### 11.1 小例子：从 `a|b` 中采样

正则：

```text
R = a|b
```

算法先计算：

$$
Z_a,\quad Z_b,\quad Z_{a|b}=Z_a+Z_b
$$

然后：

$$
P(\text{选择 }a)=Z_a/Z_{a|b}
$$

$$
P(\text{选择 }b)=Z_b/Z_{a|b}
$$

如果模型认为 `a` 更可能，就更常采到 `a`。

### 11.2 小例子：fill-in-the-blank

给定前缀 `ab` 和后缀 `ba`，中间缺一个字符：

```text
ab _ ba
```

用 regex 写：

$$
R = ab \Sigma ba
$$

如果 $\Sigma=\{a,b\}$，候选只有：

```text
ababa
abbba
```

REGSAMP 会根据 u-MPS 对这两个完整字符串的条件概率来抽样。

如果中间缺任意长度：

$$
R = ab \Sigma^* ba
$$

就可以生成任意长度的中间片段。

普通单向 RNN 很难自然利用右边后缀 `ba`；u-MPS 的 regex sampling 可以直接把前缀和后缀都写进约束。

### 11.3 小例子：包含目标短语

正则：

$$
R=\Sigma^* t \Sigma^*
$$

意思是“生成的字符串必须包含目标短语 $t$”。

例如希望 email 文本包含 `@gmail.com`：

```text
R = Σ* "@gmail.com" Σ*
```

u-MPS 可以在这个条件下采样，而不是生成后再检查。

## 12. 正则正则化：把“想要的格式”放进 loss

Theorem 2 说：

匹配正则 $R$ 的总概率可以精确计算：

$$
P(R)=\frac{Z_R}{Z_*}
$$

这意味着 $P(R)$ 是模型参数的可微函数，可以放进训练 loss。

论文给了三类例子。

### 12.1 惩罚坏模式

如果 $R$ 表示某些不想生成的内容，例如不礼貌短语集合：

$$
R=\Sigma^* S \Sigma^*
$$

其中 $S$ 是坏短语的并集。

可以把 $P(R)$ 加到 loss 中：

$$
\mathcal{L}_{total}=\mathcal{L}_{NLL}+\lambda P(R)
$$

这样训练会让模型降低生成这些内容的概率。

### 12.2 平衡两个模式

如果想让两个短语概率接近，例如：

```text
R1 = Σ* "his career" Σ*
R2 = Σ* "her career" Σ*
```

可以加入：

$$
\mathcal{L}_{bias}=|P(R_1)-P(R_2)|
$$

直觉：如果模型偏向其中一个，这个 loss 会变大。

### 12.3 鼓励合法格式

如果希望模型尽量生成合法变量名、合法 email、合法代码片段，可以用：

$$
\mathcal{L}_{regex}=-\log P(R)
$$

这会鼓励模型把更多概率放到满足 $R$ 的字符串上。

论文 email 实验中，用近似 email 格式的 regex：

```text
[\w-.]+@([\w-]+.)+[\w-][\w-]+
```

加正则后，unconditional sampling 的语法正确率从 35.4% 提到 37.2%，测试 per-character perplexity 从 7.8 降到 7.3。

提升不算巨大，但证明了这个想法可以工作。

## 13. 实验部分怎么读

论文实验不是大规模语言模型竞赛，而是验证 u-MPS 的结构能力。

主要任务：

1. Tomita grammars：二进制字符串上的规则语言。
2. Motzkin grammar：括号平衡语言，属于 context-free grammar。
3. Email 地址：真实结构化文本。
4. 顺序/并行评估速度对比。

### 13.1 Tomita grammar

Tomita grammar 是一组经典的形式语言任务。模型训练时只看长度 1 到 15 的字符串，然后要采样长度 16 和 30 的字符串，检查是否仍满足语法。

重点结果：

- Tomita 3：u-MPS 在长度 16 和 30 上都是 100.0%。
- Tomita 5：要求 0 和 1 的数量都是偶数，是非局部约束；u-MPS 长度 16 为 100.0%，长度 30 为 99.9%。
- Tomita 6：所有模型都学不好，u-MPS 也只有 35.9% / 33.1%。

小白理解：

Tomita 5 很能说明问题，因为“偶数个 0 和偶数个 1”不是只看最后几个字符就能判断的。模型要记住一种全局 parity 信息。u-MPS 表现很好，说明它能学到某些长距离结构。

### 13.2 Motzkin grammar

Motzkin grammar 类似括号匹配：

```text
()
(0)
()0()
((0))
```

其中 `0` 可以自由出现，但括号要平衡。

训练只用长度 15 的字符串，测试要采样更长长度，比如 50。

重点结果：

- 训练 10K 时，u-MPS 在长度 50 的 sampling 上达到 91.6%。
- 同时 HMM 是 12.4%，LSTM 是 5.4%，Transformer 是 0.2%。
- completion 任务中，小数据短长度时 bidirectional LSTM 更强，但长度 50 且 10K 训练时 u-MPS 也达到 92.4%。

小白理解：

括号匹配需要跨很远位置配对。u-MPS 在只见过长度 15 的情况下，还能生成长度 50 且大多合法，说明它不是简单记忆训练长度。

### 13.3 Email 实验

这里不是验证 email 是否真的存在，而是验证语法格式是否像 email：

```text
name@site.tld
```

论文发现：

- 条件 regex sampling 可以保证生成的字符串匹配 regex。
- 模型刚初始化时，生成格式正确但内容很随机。
- 训练后，生成结果逐渐像真实 email。

这体现了两层能力：

1. regex 负责硬约束格式。
2. u-MPS 学到格式内的真实分布。

## 14. 这篇论文和 CRF / Tensor CRF 的关系

注意：这篇论文本身不是 CRF 论文。

它做的是 **生成式序列建模**：

$$
P(s)
$$

而 CRF 做的是 **条件序列标注**：

$$
P(y\mid x)
$$

但它对 Tensor CRF 项目有很强启发：

1. **张量网络可以表示序列上的高阶相关。**
   CRF 里标签序列 $y_1,\ldots,y_n$ 的势函数也可以看成一张大表，张量网络能压缩这张大表。

2. **transfer operator 是高效求和工具。**
   CRF 的 partition function 也是对所有标签序列求和：

   $$
   Z(x)=\sum_y \exp(\mathrm{score}(x,y))
   $$

   u-MPS 论文展示了如何通过张量结构把指数级枚举变成递推/收缩。

3. **正则约束可以变成概率约束。**
   在序列标注中，我们可能希望标签序列满足规则，例如 BIO 标注中 `I-PER` 前面不能随便接 `O`。如果能把规则语言与张量网络结合，就可能设计结构化约束或正则项。

4. **要警惕差异。**
   本文的 Born probability 是 $|f(s)|^2$；CRF 通常是 $\exp(\mathrm{score}(x,y))$。两者归一化方式和训练目标不同，不能直接照搬。

一句话：

这篇论文更像是“张量网络怎样优雅处理序列概率和规则约束”的工具箱，而不是直接给出 Tensor CRF。

## 15. 常见卡点解释

### 15.1 为什么要平方 $|f(s)|^2$

因为 $f(s)$ 可能为负，概率不能为负。平方后一定非负。

类比：

如果一个模型输出分数：

```text
score(a)=2
score(b)=-3
```

直接当概率不行；平方后：

```text
4 和 9
```

都非负，再归一化即可。

### 15.2 为什么不强行让所有矩阵元素非负

可以，但论文说这类模型很接近 HMM，会限制表达能力。Born machine 允许矩阵里有负数或复数，再通过平方得到概率，保留了更丰富的干涉/抵消结构。

### 15.3 为什么 regex 要求 unambiguous

如果一个字符串能以多种方式匹配同一个 regex，采样算法可能会按“匹配次数”重复计权。

例子：

```text
R = a* a*
```

字符串 `"a"` 可以看成：

```text
第一个 a* 匹配 "a"，第二个匹配 ""
第一个 a* 匹配 ""，第二个匹配 "a"
```

这就有歧义。论文说可以把任意 ambiguous regex 转换为等价的 unambiguous regex，所以理论上不是根本问题。

### 15.4 Kleene star 为什么会有收敛问题

`S*` 表示重复零次或多次，可能有无限多个字符串。计算：

$$
Z_{S^*}=\sum_{s\in S^*}\tilde P(s)
$$

就可能是无穷和。如果模型给长字符串太多概率，总和会发散。

直觉例子：

如果长度每增加 1，总权重乘 0.5，那么：

$$
1+0.5+0.25+\cdots=2
$$

收敛。

如果长度每增加 1，总权重乘 1.2，那么：

$$
1+1.2+1.44+\cdots
$$

发散。

实现时要检查缩放后的 transfer operator 谱半径是否小于 1。论文通过缩放 core tensor 来保证 $\Sigma^*$ 相关求和可用。

### 15.5 为什么 Transformer 在实验里差

论文自己的解释是数据集很小。Transformer 通常需要更多数据和更合适的训练设置；这里任务偏形式语法、小数据、强结构，正好是 u-MPS / HMM 这类模型有优势的地方。

## 16. 读论文时可以抓住的主线

按论文结构，建议这样读：

1. **Introduction**
   只抓三点：并行、regex sampling、regex regularization。

2. **Background**
   把 tensor contraction 理解为“广义矩阵乘法”。不要纠结图形细节。

3. **Uniform MPS**
   重点读公式：

   $$
   f_{\mathcal{A}}(s)=\alpha^TA(s_1)\cdots A(s_n)\omega
   $$

   它是全篇根基。

4. **Born Machines**
   重点读：

   $$
   \tilde P(s)=|f_{\mathcal{A}}(s)|^2
   $$

   以及 $Z_n$ 如何用 transfer operator 算。

5. **Regular Expressions and u-MPS**
   重点读表 1。它是全篇最核心的桥。

6. **Regex Sampling and Regularization**
   重点理解 Theorem 1 和 Theorem 2 的意思，不必先深究证明。

7. **Experiments**
   重点看它证明的不是“大模型 SOTA”，而是“结构泛化和受约束采样能力”。

## 17. 手算练习

### 练习 1：字符串打分

给定：

$$
A(a)=
\begin{bmatrix}
1 & 0\\
0 & 0.5
\end{bmatrix},
\quad
A(b)=
\begin{bmatrix}
0.5 & 0\\
0 & 1
\end{bmatrix}
$$

$$
\alpha=\omega=
\begin{bmatrix}
1\\
1
\end{bmatrix}
$$

计算：

```text
f("ab")
f("ba")
```

提示：因为两个矩阵都是对角矩阵，乘法会比较简单。

### 练习 2：固定长度归一化

继续练习 1，算所有长度为 1 的字符串：

```text
"a", "b"
```

然后算：

$$
P_1(a),\quad P_1(b)
$$

### 练习 3：regex 总概率

如果 $\Sigma=\{a,b\}$，正则：

```text
R = a|bb
```

请写出：

$$
Z_R
$$

应该包含哪几个字符串的 $\tilde P(s)$？

答案形式：

$$
Z_R=\tilde P(a)+\tilde P(bb)
$$

### 练习 4：把序列标注规则写成 regex

BIO 标注中，假设标签集合是：

```text
O, B-PER, I-PER
```

思考：为什么一个序列以 `O I-PER` 开头通常是不合法的？

如果想约束合法 BIO 标签序列，能否把它近似写成 regular language？

这就是本文和 Tensor CRF 的一个潜在连接点。

## 18. 最后复盘：你应该带走什么

这篇论文最值得带走的不是“u-MPS 一定比 Transformer 强”。它真正的价值是：

1. **矩阵乘法结构带来并行化。**
   没有非线性激活，括号可以重排，序列可以树形并行计算。

2. **Born rule 把任意实数分数变成非负概率。**
   $|f(s)|^2$ 是从张量网络到概率模型的桥。

3. **Transfer operator 把指数级枚举变成线性代数。**
   它相当于“对一类字符串求和”的机器。

4. **正则表达式和 transfer operator 的递归结构相互匹配。**
   这是全篇最漂亮的结构洞见。

5. **模型可以直接做条件采样。**
   例如前缀、后缀、包含短语、满足 email 格式。

6. **规则可以进入训练目标。**
   $P(R)$ 可微，所以 regex 约束不只是后处理，也能参与学习。

对我们项目的启发：

如果要做 Tensor CRF，可以把标签序列的结构约束、高阶势函数、partition function 计算都往“张量收缩 + transfer operator + 规则语言约束”这个方向想。但要清楚本文是生成式 $P(s)$，CRF 是条件式 $P(y\mid x)$，需要重新设计 score、归一化和训练目标。

