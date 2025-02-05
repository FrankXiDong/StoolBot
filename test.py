class Test:
    """
    该类用于处理文本内容，根据特定的规则对文本进行分割和缓存管理。
    本模块代码来自@幽灵。
    """
    def __init__(self):
        """
        初始化Test类的实例。
        
        初始化一个空的字符串buffer用于缓存文本内容，
        并设置最大长度max_length为150字符。
        """
        self.buffer = ''
        self.max_length = 150

    def process(self, new_content):
        """
        处理新的文本内容。
        
        参数:
        - new_content: 新的文本内容，将被添加到缓存中。
        
        该方法根据文本中的换行符和最大长度限制，对文本内容进行分割和缓存更新。
        """
        self.buffer += new_content
        # 优先处理双换行
        dbl_newline = self.buffer.rfind('\n\n')
        if dbl_newline != -1:
            yield self.buffer[:dbl_newline]
            self.buffer = self.buffer[dbl_newline+2:]
            return
        # 处理单换行（仅在超过长度时）
        single_newline = self.buffer.rfind('\n')
        if single_newline > self.max_length:
            yield self.buffer[:single_newline]
            self.buffer = self.buffer[single_newline+1:]
            return

    def flush(self):
        """
        清空缓存并返回剩余的文本内容。
        
        返回:
        - 如果缓存中有内容，则返回缓存内容；否则返回None。
        """
        content = self.buffer.strip()
        self.buffer = ''
        return content if content else None