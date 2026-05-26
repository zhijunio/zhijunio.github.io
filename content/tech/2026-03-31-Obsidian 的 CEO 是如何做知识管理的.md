---
title: "Obsidian CEO 的知识管理方法：文件优先、内链与分形日记"
date: 2026-03-31 13:40:00+08:00
slug: how-obsidian-ceo-does-knowledge-management
draft: false
tags: [ "tools" ]
description: "根据 Steph Ango（kepano）《How I use Obsidian》等文整理的用法笔记：库结构、Bases、内链与分形日记、模板属性、评分与发稿，附参考链接。"
---

Obsidian 的 CEO **Steph Ango** 就是 *kepano*，个人站见 [stephango.com](https://stephango.com)。

下面是**读书笔记**，不是全文翻译。是使用大模型抓取文章的 md 文件，然后基于 md 文件进行总结归纳的。

<!--more-->

## 一、文件优先，少进笼子

[File over app](https://stephango.com/file-over-app) 的核心很直白：如果你想让数字作品更耐久，最好把它们做成**你能控制的文件**，而且格式要容易读取、容易迁移。

Steph Ango 反复在讲一件事：软件会过时，文件才更有机会留下来。就算他自己在用 Obsidian，也不把「某个 App 会一直在」当成前提。原文里还有一句很能代表他的态度：哪怕这些笔记最后只有“未来的自己”会读，也值得保存。

这篇里还有一层意思很重要：`file over app` 不只是用户该怎么选工具，也是他拿来要求工具作者的。软件作者最好承认一件事：软件终究短命，数据所有权应该尽量还给用户。

[Self-guaranteeing promises](https://stephango.com/self-guarantee) 又把这件事往前推了一步：真正可靠的承诺，最好是**可验证、不可逆**的，不需要你相信公司怎么说。

放到笔记工具上，他给的判断标准是：

- 文件是不是在你手里
- 格式是不是开放、通用
- 能不能直接拿**同一批文件**去别的软件继续用，而不是依赖一次性的导出；原文强调得很死：**不是 export 出来的副本，而是 exact same files**

他还提醒了一句：条款、政策、治理结构，甚至“开源”本身，都不自动等于长期安全；如果数据还是卡在难迁移的数据库或私有格式里，承诺一样很脆。

原文还有个很好用的判断法：如果你希望 2060 年、甚至更久以后还能读到这些内容，那它最好在更古老、更朴素的计算环境里也能被读出来。说白了，就是把长期价值压在文件和格式上，不要压在某家产品还活着。

## 二、他的库是怎么搭的

[How I use Obsidian](https://stephango.com/vault) 才是这篇的主轴。Steph Ango 在里面把自己的用法讲得很清楚：他用 Obsidian 来思考、记笔记、写文章、发布网站；整体方法是**自下而上**的，允许混乱、允许偷懒，让结构慢慢长出来。

这里最关键的一句是：**vault 本质上只是一个文件夹**。这不只是术语解释，而是他整套方法的地基。

如果硬要总结一下适合谁，大概是这几类：愿意长期维护纯文本文件的人；更依赖搜索、链接和回顾，而不是层层目录的人；接受“先记下来，结构以后再长”的写作者。反过来说，如果你特别依赖前置分类、严格流程，或者希望系统自动替你收拾大部分东西，那这套方法未必会让你轻松。

### 先把库打开

他公开了一个示例库：[kepano-obsidian](https://github.com/kepano/kepano-obsidian)。文章里给的步骤很简单：下载或 clone，解压，然后在 Obsidian 里把这个文件夹直接打开。

### 主题和配套工具

他写过自己用的组合（具体安装以原文为准）：

- [Minimal](https://stephango.com/minimal) 主题 + [Flexoki](https://stephango.com/flexoki) 配色
- [Obsidian Web Clipper](https://stephango.com/obsidian-web-clipper) 剪网页；针对不同站点有 [clipper templates](https://github.com/kepano/clipper-templates)
- [Obsidian Sync](https://obsidian.md/sync) 做桌面、手机、平板同步
- [Obsidian Bases](https://help.obsidian.md/bases) 按类别浏览、总览笔记
- [Obsidian Maps](https://help.obsidian.md/bases/views/map) 配合部分模板里的地图需求

### 他给自己立的规矩

在个人库里他坚持几件事（和模板里能看到的风格一致）：

- **不**把内容拆成很多个 vault（下面写网站时会破一次例）
- **尽量不用文件夹**当主要组织方式
- **不用**非标准 Markdown
- 分类、标签**一律复数**，省得以后纠结命名
- **内链尽量多**：第一次提到就链上
- 日期统一 **`YYYY-MM-DD`**
- 需要打分时用 **1～7 分**那套刻度（下面单列一节）
- 待办按 [每周一张清单](https://stephango.com/todos) 做，而且他通常会**每周从头写一遍**，不先看上周列表；想不起来的任务，大概率就没那么重要

这些规则背后的逻辑，和 [Style is consistent constraint](https://stephango.com/style) 是一套东西：先定一组自己愿意长期复用的约束，把后面成百上千个小决定折叠掉。比如标签永远用复数，以后就不用每次重新想命名。

### 文件夹为什么很少

他**不用嵌套子文件夹**，也**不太依赖文件树导航**；平时主要靠 quick switcher、反向链接和正文里的链接。理由也简单：很多笔记同时属于多个主题，硬塞进单一路径只会增加归档成本。原文这里还有一句很关键：他的系统就是朝着 **speed and laziness** 设计的，不想老为“这条该放哪”再多费一遍脑子。

真正承担“分类浏览”工作的，更多是笔记里的 **`categories` 属性**，再配合 **Bases** 看总览。

**大多数笔记直接放在 vault 根目录**：日记、文章、[常青笔记](https://stephango.com/evergreen-notes) 等。按他的说法，根目录里的通常就是“我写的”或“和我直接相关的”内容。

两个「外向」资料夹：

- **References**：书、电影、地点、人、播客等“存在于我之外”的对象；文件名直接用标题
- **Clippings**：别人写的文章、随笔、资料剪藏

三个偏「后台」、不想让内容挡住主视图的夹：

- **Attachments**：图、音频、视频、PDF 等
- **Daily**：每日一页，文件名 `YYYY-MM-DD.md`；他通常不在里面写正文，主要是给别的笔记提供日期落点
- **Templates**：模板稿

公开下载的示例库里还有 **Categories**、**Notes** 两个文件夹，只是为了让结构更容易看懂；在他自己的库里，这些内容其实也更接近放在根目录。

### 内链多到什么程度

他的习惯是：**第一次提到某个东西就链上**。哪怕这个链接当下还是未解析的、目标笔记还不存在，也先留着，因为这就是以后建立连接的面包屑。

原文举了一个日记例子：看了哪部电影、和谁去、在哪家影院、吃了什么；电影、地点、人物分别链接到 **References**，一句值得留下的话会单独长成一条常青笔记，别人写的文章则进 **Clippings**。这种重链接风格的好处是，时间一长，你可以沿着链接回看“这些想法是怎么冒出来、又分叉出去的”。

### 分形日记和“随机回访”

白天他用 **unique note** 快捷键，念头一来就记一条，文件名前缀自动是 `YYYY-MM-DD HHmm`，后面可以再补标题。

接着每隔几天，把这些碎片整理成阶段性回顾；再按月回顾这些回顾；按年再回顾月度总结，年末常配合 [每年 40 问](https://stephango.com/40-questions) 模板。这样慢慢就形成了他所谓的“分形”结构：同一段人生，可以从不同粒度重新看。

每隔几个月，他会专门做一次 **random revisit**：用 **random note** 快捷键随机翻旧笔记，再配合浅层 local graph，看遗漏的链接、旧想法和潜在灵感。

有人问这件事能不能交给语言模型自动化处理，他在原文里明确说：**不想**。因为维护、重读、修链的过程，本身就在帮助他理解自己的模式。这一点和 [Don't delegate understanding](https://stephango.com/understand) 是直接连着的。

### 属性和模板

他几乎每篇都从 [Templates 目录](https://github.com/kepano/kepano-obsidian/tree/main/Templates) 起稿。模板头顶是 [Properties](https://help.obsidian.md/properties)，常见块包括：日期（created / start / end / published）、人物（author、director、cast…）、主题（genre、topic、相关笔记）、地点、评分等。

几条明确写出来的偏好：

- 属性名尽量**跨类别复用**，例如 `genre` 同时用于书影音，就能在一个视图里捞出「所有科幻」
- 模板可**组合**（例如 Person 和 Author 叠用）
- 属性名**打短**，`start` 优于拖长的 `start-date`
- 如果将来可能出现多个值，默认先用 **list**，不要急着把字段做成单值 text

类型表在仓库的 `.obsidian/types.json` 里对齐。

### 1～7 分评分

凡是 `rating`，用整数 1～7。原文定义得很细：7 是完美、值得专门去追；6 是优秀、值得重复；5 是不错；4 是勉强可用；3 是差；2 是糟糕；1 是“坏到另一种改变人生”。他选 7 分制，是因为**高分区需要更细一点的区分**，但 10 分又太碎。

### 个人站为什么单独开一个 vault

[this site](https://stephango.com) 是在 Obsidian 里写、改、发布的，但这里他**打破**「单一 vault」规则：**网站单独一个库**。用 **Jekyll** 把 Markdown 收成静态站（搭建偏工程；若要省事也可以看 [Obsidian Publish](https://obsidian.md/publish)，但它是付费服务；他的 Minimal 文档站就是用 Publish）。

工作流里常见组合：**Obsidian Git** 推到 GitHub，**Netlify** 一类托管跑构建；**Permalink Opener** 用来对照浏览器里的成品和本地稿。配色仍是 Flexoki。Jekyll 主题他没公开，但文中点名可参考 [digital-garden-jekyll-template](https://github.com/maximevaillancourt/digital-garden-jekyll-template)，以及 [Quartz](https://quartz.jzhao.xyz/)、[Astro](https://astro.build/)、[Eleventy](https://www.11ty.dev/)、[Hugo](https://gohugo.io/) 等替代栈。

## 三、别把“理解”外包掉

如果把前面那些规则压缩成一句话，大概就是：**流程上要稳定，内容上才容易生长**。统一 Markdown、统一日期、统一标签、尽量多写链接，这些看着像“死规矩”，本质是在减少摩擦。

而在 [Don't delegate understanding](https://stephango.com/understand) 里，他把这件事讲得更尖锐：不要把理解本身外包掉。原文用了“寄生虫”的比喻，还把外包理解拆成三个阶段：先是 **acceptance**，你接受“这件难事交给别人更省心”；接着是 **extraction**，你开始持续为这种依赖付费；最后是 **intervention**，问题积累到一定程度，只能再花更高代价补救。

放回知识管理里，这篇文章并不是在反对工具，而是在提醒：检索、格式整理、搬运，都可以让工具代劳；但如果连“这条笔记为什么重要”“旧想法之间怎么连起来”“哪些规则该留下”也一起外包，最后被抽空的就是你自己的判断过程。

我自己在 AI 和手写之间也还在试，但会记住：**自动化换不回你对自己笔记的体感**。

## 四、常青笔记：小块、规矩、写短

[Evergreen notes](https://stephango.com/evergreen-notes) 这一篇给了常青笔记一个很直接的定义：把复杂想法拆成可以复用、可以组合的小对象。标题最好本身就是一句清楚、好记、能放进句子里的话。

原文给过一些很典型的标题，比如 `A company is a superorganism`、`Everything is a remix`、`Writing is telepathy`、`Calmness is a superpower`。这些标题本身就是可引用、可拼接的“想法对象”。

他还特别说：**不需要完全同意一个观点，它也可以先成为常青笔记**。你可以先把它当作一个可操作对象存下来，之后再和别的想法组合、叠加、修正。文中还举了一个例子：如果接受 `Everything is a remix`，就可以进一步长出 `Creativity is combinatory uniqueness` 这样的上层判断。

[Style is consistent constraint](https://stephango.com/style) 像是在给这些积木定规则；[Concise explanations accelerate progress](https://stephango.com/concise) 则是在提醒你把积木写短、写清楚，因为只有足够简洁，想法才更容易被反驳、重组、沿用。

回到原文标题那句“turn ideas into objects that you can manipulate”，重点其实就是：一旦想法被写成足够短、足够独立的对象，你就可以**组合、堆叠、改写**它们，不用把所有推理同时塞在脑子里。Steph Ango 觉得这正是常青笔记的价值。

## 五、顺带记两篇

给远程小团队看的 [If you're remote, ramble](https://stephango.com/ramblings)：每人一个碎碎念频道，只有本人能发顶层消息，别人在线程里接。原文建议团队规模大致在 2 到 10 人之间，频道默认静音、放在列表底部，不要求别人一定阅读。它不是知识管理主文，但和前面的笔记习惯有一点相通：先允许轻量记录，再让有价值的东西自己浮上来。

他还提到，这类 ramblings 在 Obsidian 团队里有点像“异步版茶水间聊天”。因为没有固定会议，它反而成了维持松散连接、减少打断、顺手冒出新点子的方式。

年终复盘他维护两套问卷，分别是 [每年 40 问](https://stephango.com/40-questions) / [十年 40 问](https://stephango.com/40-questions-decade)，题目在 [GitHub](https://github.com/kepano/40-questions) 开源。原文里提到，年度版通常要花他大约一周慢慢答完；比单个答案更有意思的，是连续多年回答同一组问题之后出现的趋势。十年版则更偏个人哲学和长期不太变化的特质，灵感部分来自 Proust Questionnaire。下面中文版题目便于自用自答，与英文原版措辞不一定逐句对齐。

每年 40 问（中文备忘）：

```text
1. 你今年做了哪些之前从未做过的事？
2. 你有没有遵守年初时和自己许下的约定？
3. 你身边有人生孩子了吗？
4. 你身边有人去世了吗？
5. 你去了哪些城市/州/国家？
6. 明年你想要获得哪些你今年没有的东西？
7. 今年的哪个或哪些日子会铭刻在你的记忆中，为什么？
8. 你今年最大的成就是什么？
9. 你今年最大的失败是什么？
10. 你今年还遇到过哪些困难？
11. 你今年是否生过病或受过伤？
12. 你今年买过的最好的东西是什么？
13. 谁的行为值得去表扬？
14. 谁的行为令你感到震惊？
15. 你大部分的钱都花到哪里去了？
16. 有什么事让你感到超级、超级、超级兴奋？
17. 哪首歌会永远让你想起这一年？
18. 与去年的这个时候相比，你是：感到更快乐还是更悲伤了？变得更健康还是更糟了？变得更富还是更穷了？
19. 你希望自己能做得更多的是什么？
20. 你希望自己能做得更少的是什么？
21. 你是如何度过节假日的？
22. 你今年坠入爱河了吗？
23. 你是否有讨厌某个你去年此时不觉得讨厌的人呢？
24. 你最喜欢的电视节目是什么？
25. 你读过最好的一本书是什么？
26. 你今年发现的最好听的一首歌是什么？
27. 你今年看过最喜欢的一部电影是什么？
28. 你今年吃过最好吃的一顿饭是什么？
29. 有什么是你想要且得到了的？
30. 有什么是你想要却没有得到的？
31. 你生日那天做了什么？
32. 有什么还未发生的事，如果发生了，会让你的这一年变得无比满足?
33. 你会如何描述你今年的个人时尚风格？
34. 是什么让你保持理智？
35. 你最欣赏哪个名人/公众人物？
36. 哪个政治问题最令你有感而发？
37. 你想念哪些人？
38. 在你新认识的人之中，谁是最好的？
39. 今年你学到了什么宝贵的人生经验？
40. 能够总结你这一年的一句话是什么？
```

十年 40 问（中文备忘）：

```text
1. 若生命只剩最后六个月，你会去做什么？
2. 若拥有亿万财富，你会做什么？
3. 现在的你会给十年前的你一些什么建议？
4. 你希望十年之后，什么依旧保持一致？
5. 你希望十年之后，什么是发生了变化？
6. 在你心中什么是最完美的幸福？
7. 何时何地，你最幸福过？
8. 为什么每天要起床？
9. 什么是最痛苦的？
10. 你的性格是什么？
11. 你最害怕的是什么？
12. 你最想培养的特质是什么？
13. 你最希望别人的拥有的特质是什么？
14. 什么时候会骗自己？
15. 浪费过什么？
16. 什么样的美德被过誉了？
17. 你最不喜欢自己外表的什么方面？
18. 如果你能改变一件事情，那是什么？
19. 你期望什么样的天赋？
20. 别人通常会误解你什么？
21. 你欣赏男人身上的气质是什么？
22. 你欣赏女人身上的气质是什么？
23. 你最看重朋友的什么？
24. 过去一年，最大的成就？
25. 如果你可以给每一个人同样一个礼物，那是什么？
26. 时间浪费在什么上了？
27. 最痛苦却又最值得做的是什么？
28. 你最想去什么地方生活？
29. 你最喜欢的一件东西？
30. 谁是你最好的朋友？
31. 谁或什么是你最珍贵的？
32. 当今世上，你最欣赏的人是？
33. 你最欣赏的一个小说英雄？
34. 你觉得和哪个历史人物最像？
35. 最后悔什么？
36. 你希望以何种方式结束自己的生命？
37. 座右铭是？
38. 你受到最好赞美是？
39. 最幸运的一件事是？
40. 什么让你充满了希望？
```

有意思的不是某一年答得多漂亮，而是**连续多年用同一套题**之后，能看到自己的变化轨迹。

## 六、如何实践

下面按「新手能直接动手」的顺序，把 [kepano-obsidian](https://github.com/kepano/kepano-obsidian) 和原文 [How I use Obsidian](https://stephango.com/vault) 里的思路收成一份**入门用法说明**。

### 1. Obsidian 是什么

- **Vault（库）= 电脑上的一个普通文件夹**，里面是一堆 Markdown（`.md`）等文件。
- Obsidian 是这个文件夹的**编辑器 + 浏览 + 图谱 + 插件**外壳；数据在你本机（或你自己选的同步方式），不是「锁在云端格式」那一类。
- kepano 的仓库是他的**个人库模板**，可下载后当起点，**不必全盘照抄**。

### 2. 把模板跑起来

1. 打开 [kepano/kepano-obsidian](https://github.com/kepano/kepano-obsidian)，用 **Code → Download ZIP**，或 `git clone` 到本地。

 ```bash
 cd ~/Documents
 git clone git@github.com:kepano/kepano-obsidian.git
 mv kepano-obsidian notes
 ```

1. 解压到**任意目录**（路径里尽量**不要**奇怪符号，避免以后同步/Git 出问题）。

2. 安装 [Obsidian](https://obsidian.md/)，启动后选 **「打开本地库」**，指向**刚才那个文件夹**。

3. 先到处点开看看：`Notes`、`Categories` 里多半是**示例**；`Templates`、`References`、`Clippings` 等是结构示范。详细设计说明以 [How I use Obsidian](https://stephango.com/vault) 为准。

### 3. 新手建议

| 概念 | 你可以这样理解 |
| ------------------ | ------------------------------------------------------------ |
| **笔记就是文件** | 关掉 Obsidian，用记事本也能打开同一个 `.md`，这就是「文件优先」。 |
| **`[[双向链接]]`** | 在正文里写 `[[某篇标题]]` 链到另一篇；还没建篇目的叫「未解析链接」，可当**待写清单**。 |
| **Daily**| 每天一页（常命名为 `YYYY-MM-DD.md`）。kepano 的用法里，Daily **甚至可以几乎不写正文**，主要给别的笔记**链过来**当日期锚点。 |
| **文件夹少而固定** | 模板里有 `References`（书影音人等）、`Clippings`（剪藏）、`Attachments`、`Templates` 等；**大量内容在「库根目录」**，用链接和属性组织，而不是深目录。 |
| **模板** | 新建某类笔记时从模板起稿，顶部 **Properties（YAML）** 帮你统一字段，方便以后搜索、用 Bases 等视图。 |

先把 **新建笔记、写 `[[链接]]`、用模板建一条、在库里搜一句话** 练熟，再考虑插件。

### 4. 个人规矩

来自 [vault 文](https://stephango.com/vault)，新手可**先选 2～3 条**坚持住：

- 尽量用**标准 Markdown**，少用只有某软件才认的语法。
- 需要分类时，**标签/类目用复数**等一致命名（减少以后纠结）。
- 日期统一 **`YYYY-MM-DD`**。
- **内链多用**：第一次提到就 `[[链上]]`。
- 评分若要用，他采用 **1～7 分**（文中有每档含义）。

### 5. 常用配套（可选）

原文提到的工具链（按需安装）：

- **主题**：如 Minimal + Flexoki。
- **Obsidian Sync**（官方多端同步，付费）或你自己用 Git/iCloud 等。
- **Web Clipper**：剪网页进 `Clippings`。
- **Bases**：按属性/类别看一批笔记。

新手**不必第一天全装**；先默认编辑体验 + 链接习惯，再补插件。

### 6. 发布网站（可选）

kepano 个人站是**单独一个库** + 静态站生成器（如 Jekyll）+ Git + 托管；这和「日常写作库」分开。新手可**先忽略**，等笔记稳定再想 Publish / Astro / Quartz 等，原文 [Publishing to the web](https://stephango.com/vault) 有概述。

### 7. 建议的「第一周」小任务

1. 每天用 **1 条 Daily** 或一篇**根目录随笔**，写 3～5 个 `[[概念]]`，空的也别删。
2. 从模板新建 **1 条 References**（例如一本书或一部电影），填几项属性。
3. 用 **Web Clipper**（若已装）剪 **1 篇文章** 到 `Clippings`，并在别处 `[[链到]]` 它。
4. 读一遍 [How I use Obsidian](https://stephango.com/vault)，只圈出**你愿意试的两段**（例如分形日记、random note），下周再试。

Obsidian 的核心是 **「文件夹里的 Markdown + 链接」**；[kepano-obsidian](https://github.com/kepano/kepano-obsidian) 给的是**一套可 fork 的习惯与目录示范**，完整哲学与细节在 [stephango.com/vault](https://stephango.com/vault)。若你希望我把这份整理成你博客里的独立文章（frontmatter、标题、和现有 Obsidian 那篇的关系），可以说一下想放在 `content/posts` 哪一类下。

## 参考链接

**作者**

- Steph Ango（kepano）个人站
<https://stephango.com>

**文章（stephango.com）**

- 《File over app》
<https://stephango.com/file-over-app>
- 《Self-guaranteeing promises》
<https://stephango.com/self-guarantee>
- 《How I use Obsidian》（Vault 用法）
<https://stephango.com/vault>
- 《Don't delegate understanding》
<https://stephango.com/understand>
- 《Evergreen notes》
<https://stephango.com/evergreen-notes>
- 《Style is consistent constraint》
<https://stephango.com/style>
- 《Concise explanations》
<https://stephango.com/concise>
- 《If you're remote, ramble》
<https://stephango.com/ramblings>
- 《40 问》（年终复盘）
<https://stephango.com/40-questions>
- 《十年 40 问》
<https://stephango.com/40-questions-decade>

**模板**

- Obsidian 库模板 kepano-obsidian
<https://github.com/kepano/kepano-obsidian>

**主题、剪藏与待办（文中提到）**

- Minimal 主题说明
<https://stephango.com/minimal>
- Flexoki 配色
<https://stephango.com/flexoki>
- Obsidian Web Clipper
<https://stephango.com/obsidian-web-clipper>
- Clipper 模板仓库
<https://github.com/kepano/clipper-templates>
- 每周待办怎么做（How I do my to-dos）
<https://stephango.com/todos>
- Permalink Opener
<https://stephango.com/permalink-opener>

**Obsidian 官方文档**

- Bases
<https://help.obsidian.md/bases>
- Bases：地图视图
<https://help.obsidian.md/bases/views/map>
- Properties（属性）
<https://help.obsidian.md/properties>
- Obsidian Sync
<https://obsidian.md/sync>
- Obsidian Publish
<https://obsidian.md/publish>

**静态站工具（发稿流程里点名）**

- Jekyll
<https://jekyllrb.com/>
- Digital garden 模板（Maxime Vaillancourt）
<https://github.com/maximevaillancourt/digital-garden-jekyll-template>
- Quartz / Astro / Eleventy / Hugo
<https://quartz.jzhao.xyz/> / <https://astro.build/> / <https://www.11ty.dev/> / <https://gohugo.io/>
