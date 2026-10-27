import unittest
from chat_reply_splitter import split_reply

class LiteTests(unittest.TestCase):
    def test_no_comma_or_newline_split(self):
        for text in ['我刚刚突然想到\n咱们上次说好的电影还没看呢', '我先去洗个澡，等会儿回来找你，你也别熬太晚']:
            self.assertEqual(len(split_reply(text,True)),1)
    def test_sentences_and_quotes(self):
        self.assertEqual(split_reply('他说“晚安。好梦！”。我也准备早点回家休息了。',True), ['他说“晚安。好梦！”','我也准备早点回家休息了'])
    def test_numbers_and_fragments(self):
        for text in ['今天温度是23.5度，出去散步应该会很舒服','哇！你今天真的好厉害','他说“明天见。']:
            self.assertEqual(split_reply(text,True),[text])
    def test_max_two_and_non_casual(self):
        text='饭已经吃完了。碗也顺手洗好了。现在终于能坐下来歇会儿。'
        self.assertEqual(len(split_reply(text,True)),2)
        self.assertEqual(split_reply(text),[text])

class PublicApiTests(unittest.TestCase):
    def test_default_and_empty(self):
        self.assertEqual(split_reply("原文。\n保留。"), ["原文。\n保留。"])
        self.assertEqual(split_reply("", True), [""])
    def test_known_condition_limitation(self):
        self.assertEqual(len(split_reply("只要你明天还有空。我们就去河边走走，不用安排太满", True)), 2)
    def test_long_reply_stays_one(self):
        self.assertEqual(len(split_reply("今天终于可以好好休息了。"*6, True)), 1)
    def test_protected_text(self):
        for text in ["看看 https://example.com。再说吧。", "我忙完了（真的好累！现在想睡了），晚点再聊", "```print(1)```"]:
            self.assertEqual(split_reply(text, True), [text])
