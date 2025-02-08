from openai import OpenAI
client = OpenAI(api_key="sk-a18fcb9ce10f425bb75c7f811c73a20d", base_url="https://api.deepseek.com/v1")

# Round 1
messages = [{"role": "user", "content": "9.11 和 9.8, 哪个更大？"}]
response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=messages,
    stream=True
)

reasoning_content = ""
content = ""

for chunk in response:
    if chunk.choices[0].delta.reasoning_content:
        reasoning_content += chunk.choices[0].delta.reasoning_content
        print(chunk.choices[0].delta.reasoning_content,end="")
    else:
        content += chunk.choices[0].delta.content
        print(chunk.choices[0].delta.content,end="")