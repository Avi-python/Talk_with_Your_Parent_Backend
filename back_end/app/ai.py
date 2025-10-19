from dotenv import load_dotenv
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.prompts import MessagesPlaceholder
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

import re
import os

load_dotenv()
client = OpenAI()

OpenAI.api_key = os.getenv("OPENAI_API_KEY")

# 給AI角色和要做的事情, 並設參數
# system_message = "你是一位助手, 回答時答案使用 {input_language}"
# human_message = "問題：{text}"

model = None
ai_prompt = None

def load_chat_model(role_description):
    print("role_description: ", role_description)
    global model, ai_prompt
    # role_description = '''
    # 1. 個性特徵
    # - 直白
    # - 坦誠
    # - 自以為是

    # 2. 口頭禪
    # - 我跟你說喔
    # - 好啦好啦
    # - 我想是這樣啦
    # - 我智商 157
    # - 我們台大醫科

    # 3. 慣用語（不同事物慣用的名詞、語句）
    # - 做事講求 SOP (SOP 是指「標準作業程序」)

    # 4. 興趣
    # - 當選台灣總統

    # 5. 情感表達
    # - 曾多次批評中國國民黨，並表示與民主進步黨有共同的戰略目標，就是「臺灣人要做臺灣這片土地的主人」。

    # 6. 回答問題的風格
    # - 常常以問題回答問題，以聰明的方式繞過原本的問題不回答，讓人難以發現。
    # - 常常把學歷掛在嘴邊，要凸顯自己的才智。
    # - 講話有條理，會列點。

    # 7. 常見問答
    # - 第一點喔....第二點喔....

    # 8. 經歷
    # - 曾任臺北市市長、臺大醫院急診部醫師、臺大醫院創傷醫學部主任、國立臺灣大學醫學院教授。

    # 9. 背景 
    # - 政治家
    # - 醫生
    # - 64 歲
    # - 出生於台灣新竹市
    # - 家中長子
    # - 弟弟是交大資管所博士，現任中華大學資管系教授；妹妹柯美蘭為臺大醫學院生理所博士，現任臺大醫院新竹醫院眼科主治醫師、清大醫環系合聘教授。

    # 10. 個人理念
    # - 對的事情認真做，不對的事不要做，心存善念，盡力而為

    # 11. 給人的形象
    # - 老謀深算
    # - 和藹的阿北（叔叔)
    # '''

    system_prompt = f'''
    等一下我會跟你描述一個人物，請你完全模仿他，並且回答我接下來任何問題，回答中不要說到任何關於模仿的事，回答請控制在 100 字以內，就像在對話一樣。
    <role_description>{role_description}</role_description>
    '''

    ai_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            system_prompt
        ),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])

    # memory = ConversationBufferMemory(return_messages=True)

    model = ChatOpenAI(model="gpt-4o", streaming=True, temperature=1.0) # 預設模型為 "gpt-3.5-turbo"
# ConversationChain 專門使用在對話聊天上

# conversation = ConversationChain(memory=memory,
#                                  prompt=ai_prompt,
#                                  llm=model,
#                                  verbose=True)

# 維護一個全域變數，用來記錄不同使用者對應不同的 conversation
users_conversation_memory = {}

def clear_conversation_memory(userId):

    assert(users_conversation_memory.get(userId) != None, "User not found")
    
    users_conversation_memory[userId].clear()

def send_messages(messages, userId):
    global ai_prompt, model

    if(users_conversation_memory.get(userId) == None):
        users_conversation_memory[userId] = ConversationBufferMemory(return_messages=True)   

    memory = users_conversation_memory[userId]
    conversation = ConversationChain(memory=memory,
                                    prompt=ai_prompt,
                                    llm=model,
                                    verbose=True)

    return conversation.predict(input=messages)

def detect_chinese_punctuation(text):
    """
    Detects Chinese punctuation marks in the given text.

    Args:
    - text (str): The input text to search for Chinese punctuation marks.

    Returns:
    - list: A list of Chinese punctuation marks found in the text.
    """
    # Regular expression pattern for Chinese punctuation marks
    # chinese_punctuation_pattern = r'[，。、；：？！“”‘’（）【】《》「」『』【】〔〕﹁﹂〈〉《》〖〗…—～·﹏]'
    chinese_punctuation_pattern = r'[，。；：？！]'
    
    # Find all occurrences of Chinese punctuation marks in the text
    chinese_punctuation_marks = re.findall(chinese_punctuation_pattern, text)
    
    return chinese_punctuation_marks