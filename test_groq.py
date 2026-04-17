import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

prompts = [
    "transformer architectures",
    "reinforcement learning from human feedback",
    "fine-tuning large language models",
]

for topic in prompts:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a regular user posting on the subreddit r/MachineLearning."},
            {"role": "user", "content": f"Write a Reddit post about: {topic}. Between 150 and 300 words. No hashtags, no markdown headers."}
        ],
        max_tokens=400,
        temperature=0.7
    )
    print(f"\n--- Topic: {topic} ---")
    print(response.choices[0].message.content.strip())
    print(f"Wörter: {len(response.choices[0].message.content.split())}")

    filename = f"output_{topic.replace(' ', '_')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(response.choices[0].message.content.strip())
