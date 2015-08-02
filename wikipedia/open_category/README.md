###处理维基百科的开放分类
维基百科的[开放分类树](https://zh.wikipedia.org/wiki/Category:%E9%A0%81%E9%9D%A2%E5%88%86%E9%A1%9E)是一个“准森林”。如果除去根节点“页面分类”，则分类体系呈现一个树状结构，然而每个节点都可能有多个父节点，同时不同深度的节点之间可能有交叉关系。因此从一个节点出发，可能有多条路径到达多个根节点，还会出现“环”，即因为浅层的节点有深层的节点作为父节点，永远无法通过遍历到达一个根节点。

为了解决这个问题，结合我们的目标（将节点投影到几个一级节点上），这里采用了将这个“准森林”中的每一个节点转化成N维球面上的一个点的方法，通过“准森林”之间的父子关系，每一个节点都应该处于其几个父节点的重心上。再通过对几个浅层根节点人工定位的方法，就可以确定大量的节点在N维球面上的位置，从而给定一个开放分类，我们可以得知其属于一级节点的概率（N维空间的坐标表达了这个相对概率）。

举例来说，假定我们有“人物”，“地理”两个根分类，标号为1和2，它们处于圆上(0,1)、(1,0)；同时“中国艺术家”的父节点是“人物”和“地理”，因此“中国艺术家”（标号3）处于(0.707, 0.707)，即它属于两个根分类的概率相等；另外，“运动员”（标号4）只有一个父节点“人物”，于是它处于(0,1)，即不可能属于“地理”。

ProbabilitySpace.cpp计算“准森林”中的每一个节点的空间向量。首先需要输入所有的节点位置和节点之间的父子关系，然后输入选定的根节点的初始向量（选定的根节点不应该有父节点）：

```
Distribute a quasi-tree in a N-dimensional space
Please enter nodes now, end them using a blank line (CR)
1
2
3
4

Please enter node links in form: treeId inlinkId, end them using a blank line (CR).
3 1
3 2
4 1

Please enter initial vectors in form: nodeId value0 value1 ...
end them using a blank line (CR)
1 0 1
2 1 0 

```

输出结果：

```
roots: 1 2 
Iter 1, accumulate 2.41421
Iter 2, accumulate 0
1 0 1 
2 1 0 
3 0.707107 0.707107 
4 0 1
```

程序未提供文件输入输出，需要保存数据时，可以将输入输出重定向到文件：

```
./ProbabilitySpace < nodes.txt < initvalues.txt >> output.txt
```