
from weixin.agent.node.parse import parse_yaml
from langchain.prompts import PromptTemplate
from weixin.agent.prompts.template import load_prompt
from weixin.agent.node.type import User

PROMPT_MERCHANT = load_prompt("role")


def extract_role(llm, new_req, nickname):
    prompt = PromptTemplate.from_template(PROMPT_MERCHANT, template_format="jinja2")
    prompt = prompt.format(new_req=new_req, nickname=nickname)
    response = llm.invoke(prompt)
    res = parse_yaml(response)
    res["nickname"] = nickname
    user = User(**res)
    return user
