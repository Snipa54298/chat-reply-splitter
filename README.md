# Chat Reply Splitter

轻量中文聊天消息切分器。适用于模型生成完成后的展示层：最多两条、短片段不强拆、零第三方运行依赖，不调用模型。

这是 Python 库，不是 QQ / AstrBot / DSH 的即装插件。不包含账号登录、消息收发、记忆、等待间隔或模型文件。

## 使用

Python 3.10+。下载或克隆本仓库后，在仓库根目录执行：

```python
from chat_reply_splitter import split_reply

print(split_reply("今天真的很开心。谢谢你一直陪我聊天。", casual=True))
# ['今天真的很开心', '谢谢你一直陪我聊天']
```

也可在仓库目录执行 `python -m pip install .` 安装本地包。尚未发布到 PyPI；不要假定同名线上包就是本项目。
运行 `python -m unittest discover -s tests -v` 测试。

## 行为

- `split_reply(text, casual=False) -> list[str]`：默认原文返回，调用方自行决定是否闲聊。
- 闲聊模式仅在原文不超过 50 个 Python 字符时尝试切分；每侧至少 6 字符，最多两条，候选中取较均衡位置。
- 识别引号外的 `。！？!?`；英文句点仅支持紧接汉字且后接汉字或结尾的情况。
- 不按逗号、裸换行或波浪号切分；不使用语法关键词表。
- 保留引用内容；引号不配对时原样返回。括号、书名号、链接标记、代码围栏及 CQ 标记触发整条保护。
- 未被整体保护的闲聊会删除末尾中文句号、将段内中文句号变为逗号，并将换行合并为空格。支持的中文英文句点同样整理。问号和感叹号保留。

这是带标点整理的展示工具，不是无损分句器。空字符串返回 `['']`，发送方应自行过滤空消息。

## 局限

依赖原文标点，不能理解复杂语义，也不会纠正错误句号。比如 `只要你明天还有空。我们就去河边走走，不用安排太满` 仍可能被拆开条件关系。
偏向漏切：完整但只用逗号或换行分隔的两句话可能保持一条。引号/括号和链接保护较保守；混合语言、转义引号及不规范标点未经全面验证。
50 字符限制不是最大输入长度限制。对外部不可信超长输入，宿主应限制长度；本库不是安全过滤器。

## 项目范围

默认只维护精简中文核心。英语、日语、阿拉伯语包位于独立实验模块，未经充分语言质量验证，详见下方。
核心来自本项目的精简实现，开发过程中使用了 AI 辅助；没有将第三方框架源码打包进来。
未承诺优于其他项目，也没有声称通过 GitHub 官方认证。

## 贡献与许可

见 [贡献指南](CONTRIBUTING.md)、[行为准则](CODE_OF_CONDUCT.md) 和 [安全政策](SECURITY.md)。
MIT 许可证，允许使用、修改和再分发，请保留许可证及版权声明。


## 可选语言接口（实验版本）

中文原入口不变：`from chat_reply_splitter import split_reply`。核心文件保持 0.1.0 内容不变，不会导入任何实验模块。
需要语言选择时，显式使用独立接口：

```python
from chat_reply_splitter.experimental.router import split_reply

# 每次按用户偏好选择；省略 language 时仍使用精简中文核心。
parts = split_reply("You did a great job! Take a well deserved break.", True, language="en-US")
# ['You did a great job!', 'Take a well deserved break.']
parts = split_reply("今日は本当にお疲れ様！ゆっくり休んでください", True, language="ja")
```

内置 `en`、`ja`、`ar`，支持 `en-US` 等区域代码回退；`zh` 和中文区域代码固定调用原精简核心。未知语言报错，不自动检测或翻译。
实验包会保留句末标点，使用各自长度、标点和有限缩写规则；可按换行切分，行为不同于精简中文。
现有已知问题包括缩写末尾漏切（如 U.S.）、跨行语义误切、字符阈值未充分本地化。测试通过不代表母语聊天效果已验证。

自定义包可通过接口替换，无需改中文核心：

```python
from chat_reply_splitter.experimental.router import LanguageRules, register_language

register_language(LanguageRules("demo", periods="۔", questions="؟", commas="،"))
parts = split_reply("abcdef ghi۔ jklmnop qrs", True, language="demo")
```

也可传 `language=LanguageRules(...)`，避免注册状态。继承并重写 `split` 可提供完整策略，或重写 `valid_boundary` / `cleanup` 复用引擎。
同名实验包需显式 `replace=True` 才能替换；建议在启动时注册。中文代码保留，不允许注册覆盖。
`starters` 只用于实验包的可选逗号规则；中文忽略此参数，始终使用无关键词精简策略。
这些是同一安装包内的可选 Python 模块，并非分别上架的 PyPI 插件。总仓库/安装包体积会增加，但中文核心字节数和默认导入路径不变。
