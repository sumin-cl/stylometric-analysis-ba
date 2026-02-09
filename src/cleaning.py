def preprocess_markdown(text):
    # Remove markdown syntax
    import re
    text = re.sub(r'[#*>\-\+\=\[\]\(\)`]', '', text)
    return text.strip()

def rm_html_traces(line):
    # Remove HTML tags
    import re
    line = re.sub(r'<[^>]+>', '', line)
    return line.strip()

