# 人物 IP 与封面构图

身份母版：本技能 `assets/character-reference.png`，由用户提供的原图直接复制。文件校验和见 `assets/character-reference.sha256`。使用时先查看，再把图片实际传给参考图生成/编辑工具；不用之前生成的封面代替原图来延续克隆。

## 保持辨识度

- 深棕色侧分短发，发量丰厚，粗而自然的深色眉毛。
- 棕色大眼睛、圆润面颊、小鼻子、温暖的表情；保持参考图的五官间距与脸部轮廓。
- 大头小身体的高质感 3D 卡通比例，材质柔和；不变成真人或另一位卡通人物。
- 默认米色麻花针织毛衣、深灰裤子、灰色帆布鞋。若版式仅用半身，也要保留脸和毛衣特征。
- 裤子字母是原素材细节，不作为个人品牌强制复现；角落的星形装饰不作为角色身份的一部分。
- 可改变：手势、身体朝向、表情、道具、背景。用户未指定时不擅自换装、添眼镜、改发型或性别。

## 动作要解释文章

| 文章内容 | 推荐动作 | 可见道具 | 构图重点 |
| --- | --- | --- | --- |
| 学 AI / 入门 | 指向第一步、向读者展示卡片 | 步骤卡、电脑 | 亲和清晰，不遮挡步骤 |
| 工作流提效 | 操作节点、连接两个模块 | 节点图、任务卡 | 把输入到产出的关系画清楚 |
| AI 副业实践 | 展示真实交付物、整理订单流程 | 作品、服务清单 | 无收入证据不用钞票雨和收益战报 |
| 认知观点 | 比较两条路线、思考、打开一扇门 | 路径、镜子、门 | 一个主要隐喻，不塞满全画面 |
| 避坑 | 抬手提醒、指出一个错误节点 | 警示牌、分叉路 | 提醒而非夸张恐吓 |

这些是起点，动作必须来自本篇文章，不是按类别机械复用。

## 图像工具提示词骨架

```text
Use the provided image as the character identity reference, not as the background or layout template.
Preserve the same face, brown side-parted hair, brown eyes, head-to-body proportions,
beige cable-knit sweater and default outfit. Render the same recognizable 3D cartoon character.
Article idea: <one grounded claim>. Character action: <a visible action related to the article>.
Scene and props: <concrete objects>. Cover layout/style: <selected catalog template adapted for the character>.
Keep the title and face unobstructed. No reference-image corner sparkle, no watermark, no invented logos.
```

正文提到第三方品牌时不自动生成 Logo；人物可以操作无品牌电脑、流程模块。风格提示词的默认主体应替换或调整，不能保留一位无关陌生主角再塞入 IP。

## 交付与检查

- 默认 1500×600 PNG，四周约 5% 留安全边距；人物约占画面宽度 20%–35%，依标题/图解内容调整。
- 为确保“融入”，让人物目光、手势或道具与画面主信息发生关系，避免角落机械贴头像。
- 大字说明一个卖点，副标题可省。不要把文章标题缩写成更夸张的承诺。
- 人物脸部/发型/毛衣/比例分别与原图比较；手指自然；主要动作在裁切后仍可理解。
- 缩到约 500×200 预览，核对标题是否能读、人物是否清晰；视觉检查应实际查看图片，不用文件存在或 ASR 代替。
- 若只能输出 16:9 预览或提示词，明确说明尚未交付 5:2 成品。不要在未实际生成、检查前声称身份一致性已通过。
