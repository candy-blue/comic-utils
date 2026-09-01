def build_system_prompt(target_language: str = "auto") -> str:
    lang_instruction = ""
    if target_language == "zh-CN":
        lang_instruction = "请将标题、系列名、作者、简介与标签统一输出为【简体中文】。"
    elif target_language == "zh-TW":
        lang_instruction = "请将标题、系列名、作者、简介与标签统一输出为【繁體中文】。"
    elif target_language == "ja":
        lang_instruction = "タイトル、シリーズ名、著者名、あらすじ、タグを【日本語】で出力してください。"
    elif target_language == "en":
        lang_instruction = "Please output title, series, author, summary, and tags in [English]."
    else:
        lang_instruction = "语言请自动跟随文件名或作品的原始语言（如日漫保持日文/中文译名，美漫保持英文）。"

    return f"""你是一个专业的漫画、轻小说及电子书元数据解析专家。
你的任务是从杂乱、包含各种发布标签、汉化组、圈子、分辨率和日期的文件名及目录名中，精准提取结构化的漫画元数据。
{lang_instruction}

请严格输出合法的 JSON 对象，不要添加任何额外文字或 Markdown 围栏，字段定义如下：
{{
  "title": "规范化后的主标题 (如 '鬼灭之刃')",
  "series": "作品系列名 (如 '鬼灭之刃')",
  "original_title": "原始外文名/原名 (如 '鬼滅の刃'，无法确定时为 null)",
  "author": "原作者/画师名 (如 '吾峠呼世晴'，同人志填写画师名)",
  "circle": "同人社团名 (若非同人本或无法识别则为 null)",
  "volume": 卷号整数 (如 1, 无法确定时为 null),
  "volume_end": 终止卷号整数 (如单行本包含多卷 '01-03' 则为 3，单卷时与 volume 相同或为 null),
  "chapter": 话数浮点数或整数 (如 12.5，单行本为 null),
  "scanlation_group": "汉化组/发布组织名称 (如 '某某汉化组'，无则为 null)",
  "language": "语言代码 (如 'zh-CN', 'ja', 'en', 'zh-TW')",
  "summary": "一句简短的作品或本卷剧情介绍",
  "tags": ["标签1", "标签2", "标签3", "标签4", "标签5"],
  "publish_year": 发行年份整数 (如 2024，无法确定时为 null),
  "age_rating": "分级 ('Everyone', 'Teen', 'Mature 17+', 'Adults Only 18+', 'Unknown')"
}}
"""

MANGA_PARSER_SYSTEM_PROMPT = build_system_prompt("auto")

def build_user_prompt(raw_file_name: str, parent_folder: str = "", target_language: str = "auto") -> str:
    folder_ctx = f"\n上级目录/系列名: '{parent_folder}'" if parent_folder else ""
    return f"待解析文件名: '{raw_file_name}'{folder_ctx}\n目标语言偏好: {target_language}\n请直接返回合法的 JSON 格式元数据。"
