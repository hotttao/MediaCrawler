
from weixin.agent.node.parse import parse_yaml
from langchain.prompts import PromptTemplate
from weixin.agent.prompts.template import load_prompt
from weixin.agent.node.type import User

PROMPT_MERCHANT = load_prompt("wx_ad")


def extract_group_msg(llm, group_msg, path_cache=None):
    prompt = PromptTemplate.from_template(PROMPT_MERCHANT, template_format="jinja2")
    prompt = prompt.format(group_msg=group_msg)
    if path_cache:
        with open(path_cache, "w", encoding="utf_8_sig") as f:
            f.write(prompt)
    raise
    response = llm.invoke(prompt)
    res = parse_yaml(response)
    return res
