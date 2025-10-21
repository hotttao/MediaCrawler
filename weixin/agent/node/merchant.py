import yaml
from langchain.prompts import PromptTemplate
from weixin.agent.prompts.template import load_prompt

PROMPT_MERCHANT = load_prompt("merchant")

def parse_yaml(llm_res):
    try:
        llm_res = llm_res.strip()
        data = yaml.safe_load(llm_res)
    except Exception as e:
        
        print(f"解析异常: \n {e}")
        return []
    return data

def extract_merchant_info(llm, wx_msg):
    prompt = PromptTemplate.from_template(PROMPT_MERCHANT, template_format="jinja2")
    prompt = prompt.format(wx_msg=wx_msg)
    response = llm.invoke(prompt)
    res = parse_yaml(response)
    return res
