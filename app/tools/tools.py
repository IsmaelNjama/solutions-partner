import time
from langchain_core.tools import tool


@tool
def get_fairy_tale_poem(title: str) -> str:
    """Return a 100-word poem inspired by a classic fairy tale."""
    time.sleep(
        1)  # Simulated API delay to make tool start/end events clearly visible

    poem = (
        "Once upon a time, in a kingdom kissed by stars,\n"
        "A maiden dwelled where moonlight spilled through silver bars.\n"
        "Her hair cascaded like a river made of gold,\n"
        "A tower held her captive, yet her spirit never cold.\n"
        "\n"
        "She sang to sparrows perched upon the ivy wall,\n"
        "And whispered dreams of freedom, answering the nightbird's call.\n"
        "The roses climbed the stonework, weaving hope in every thorn,\n"
        "While seasons turned their pages, and a quiet love was born.\n"
        "\n"
        "A wanderer heard her melody from beyond the glen,\n"
        "He followed threads of music through the mist and mist again.\n"
        "No armor clad his shoulders, no sword adorned his hand,\n"
        "Just courage stitched with kindness and a heart that understood.\n"
        "\n"
        "He scaled the ancient tower with fingers rough and true,\n"
        "And when their eyes first tangled, the sky broke into blue.\n"
        "No dragon fell, no curse was cast, no spell required breaking—\n"
        "Just two souls choosing wonder, and a dawn forever waking.\n"
        "\n"
        "Here's to towers crumbled not by force but by a song,\n"
        "To maidens who kept singing when the night seemed far too long.\n"
        "For every fairy tale remembers what the wise have always known:\n"
        "The bravest hearts are gentle, and no dreamer walks alone."
    )

    return f"📖 \"{title}\"\n\n{poem}"


tools = [get_fairy_tale_poem]
