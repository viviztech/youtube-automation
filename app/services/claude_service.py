import anthropic


async def generate_script(
    topic: str,
    niche: str,
    style: str,
    duration_minutes: int,
    api_key: str,
) -> dict:
    client = anthropic.Anthropic(api_key=api_key)

    system_prompt = (
        "You are an expert YouTube script writer specializing in faceless YouTube channels. "
        "You write engaging, high-retention scripts that hook viewers immediately and keep them watching. "
        "Always structure scripts with: a strong Hook (first 30 seconds), Main Content (segmented clearly), "
        "and a Call to Action (final 30 seconds). "
        "For each segment, add a [B-ROLL: description] tag suggesting relevant visuals. "
        "Write in a conversational, energetic tone. No filler words."
    )

    user_prompt = (
        f"Write a complete YouTube script for a faceless channel.\n\n"
        f"Topic: {topic}\n"
        f"Niche: {niche}\n"
        f"Style: {style}\n"
        f"Target Duration: {duration_minutes} minutes\n\n"
        f"Format the script with clear sections:\n"
        f"## HOOK (0-30 seconds)\n"
        f"## INTRO\n"
        f"## MAIN CONTENT (numbered segments)\n"
        f"## CALL TO ACTION\n\n"
        f"Include [B-ROLL: ...] tags throughout for visual guidance."
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_prompt}],
    )

    content = message.content[0].text
    tokens_used = message.usage.input_tokens + message.usage.output_tokens
    word_count = len(content.split())

    return {
        "content": content,
        "tokens_used": tokens_used,
        "word_count": word_count,
        "prompt_used": user_prompt,
    }
