import yaml


def parse_yaml(llm_res):
    try:
        llm_res = llm_res.strip()
        data = yaml.safe_load(llm_res)
    except Exception as e:
        
        print(f"解析异常: \n {e}")
        return []
    return data
