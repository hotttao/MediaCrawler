from dotenv import load_dotenv
load_dotenv()

from langchain_community.llms import Tongyi
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

# 可以在这里直接设置 API Key，或通过环境变量
# os.environ["DASHSCOPE_API_KEY"] = "your-dashscope-api-key"

# 初始化通义千问模型
llm = Tongyi(
    model_name="qwen-max",  # 可选: qwen-max, qwen-plus, qwen-turbo 等
    temperature=0.7,
    # dashscope_api_key="your-api-key"  # 也可以在这里传入
)

# 创建一个简单的 Prompt 模板
template = """
你是一个抖音达人的运营，会收到商家发送过来的邀约信息，需要你从信息中提取以下产品信息，输出格式为 yaml，**输出结果不要包含 ```yaml**

```yaml
# 商品数据示例（YAML 格式）
- brand: "小米"                     # 品牌名称：商品所属的品牌
  product_name: "小米手环8 Pro"      # 商品名称：完整的产品名称，用于展示或检索price: 299.00                    # 售价：单位为元（人民币），使用浮点数表示product_url: "https://example.com/xiaomi-band-8-pro"  # 商品链接：commissions:                     # 佣金比例信息列表
  - is_promoted: true            # 是否投流：布尔值，true 表示投流
    rate: 0.10                   # 投流佣金比例
  - is_promoted: false           # 是否投流：布尔值，false 表示未参与流量推广
    rate: 0.05                   # 不投流佣金比例
```

注意:
1. 如果对话没有明确说明，投流和不投流的佣金比例，或者一个产品只有一个佣金率，默认只支持投流。
2. 商品信息只可能来自商家，不可能来自我

下面是你和商家的对话信息: 
{wx_msg}
"""

def extract_product_info(wx_msg):
    prompt = PromptTemplate.from_template(template)
    prompt = prompt.format(wx_msg=wx_msg)
    response = llm.invoke(prompt)
    return response
