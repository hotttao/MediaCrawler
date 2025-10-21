from langchain_community.llms import Tongyi
from langchain_core.prompts import PromptTemplate

# 可以在这里直接设置 API Key，或通过环境变量
# os.environ["DASHSCOPE_API_KEY"] = "your-dashscope-api-key"

# 初始化通义千问模型
llm = Tongyi(
    model_name="qwen-max",  # 可选: qwen-max, qwen-plus, qwen-turbo 等
    temperature=0.7,
    # dashscope_api_key="your-api-key"  # 也可以在这里传入
)
