import os
import gradio as gr
import random

# ---------------------------------------------------------------
# WORD LIST
# Each tuple is (masculine word, feminine word).
# Taken from the uploaded word list.
# ---------------------------------------------------------------
PAIRS = [
    ("ऊँट", "ऊँटनी"), ("शिष्य", "शिष्या"), ("माली", "मालिन"),
    ("आदमी", "औरत"), ("युवक", "युवती"), ("सेठ", "सेठानी"),
    ("श्रीमान", "श्रीमती"), ("गायक", "गायिका"), ("छात्र", "छात्रा"),
    ("वर", "वधू"), ("चूहा", "चुहिया"), ("सुनार", "सुनारिन"),
    ("लेखक", "लेखिका"), ("शेर", "शेरनी"), ("दास", "दासी"),
    ("कवि", "कवयित्री"), ("बुद्धिमान", "बुद्धिमती"), ("बलवान", "बलवती"),
    ("भाई", "बहन"), ("नर्तक", "नर्तकी"), ("बैल", "गाय"),
    ("हंस", "हंसनी"), ("हाथी", "हथिनी"), ("घोड़ा", "घोड़ी"),
    ("सिंह", "सिंहनी"), ("अध्यापक", "अध्यापिका"), ("सहपाठी", "सहपाठिन"),
    ("हिरन", "हिरनी"), ("बंदर", "बंदरिया"),
]

# Turn the pairs into one flat list of (word, correct_gender)
ALL_WORDS = []
for masc, fem in PAIRS:
    ALL_WORDS.append((masc, "Masculine"))
    ALL_WORDS.append((fem, "Feminine"))

TOTAL = len(ALL_WORDS)

SUCCESS_MSGS = [
    "🎉 Yay! That's correct!", "⭐ Great job!", "✅ You got it!",
    "🌟 Awesome!", "👏 Correct! Well done!", "🥳 Super!",
]
FAIL_MSGS = ["❌ Not quite!", "😊 Nice try!", "🤔 Almost!"]

CSS = """
#word_box {
    text-align: center;
    font-size: 56px;
    font-weight: bold;
    padding: 30px;
    border-radius: 16px;
    background: #fff7e6;
    color: #3a2b13;   /* fixed dark text so it stays readable in dark mode too */
    margin-bottom: 10px;
}
"""


def word_html(word):
    return f"<div id='word_box'>{word}</div>"


def new_game():
    """Start a fresh, shuffled round. Returns everything the UI needs to reset."""
    words = ALL_WORDS.copy()
    random.shuffle(words)
    state = {"words": words, "index": 0, "score": 0}
    first_word = words[0][0]
    return (
        state,
        word_html(first_word),
        "",
        f"Score: 0 / {TOTAL}",
        f"Word 1 of {TOTAL}",
        gr.update(interactive=True),
        gr.update(interactive=True),
    )


def check_answer(chosen_gender, state):
    """Grade the current word, then advance to the next one (or end the game)."""
    words = state["words"]
    index = state["index"]

    # Safety net: if the quiz already ended (e.g. a fast double-click),
    # just re-show the end screen instead of crashing.
    if index >= len(words):
        final = f"🏁 **Game over! Final Score: {state['score']} / {TOTAL}** 🏁"
        return (
            state,
            word_html("🎊 Finished! 🎊"),
            final,
            f"Score: {state['score']} / {TOTAL}",
            "Quiz complete!",
            gr.update(interactive=False),
            gr.update(interactive=False),
        )

    word, correct_gender = words[index]

    if chosen_gender == correct_gender:
        state["score"] += 1
        feedback = random.choice(SUCCESS_MSGS)
    else:
        feedback = f"{random.choice(FAIL_MSGS)} The correct answer was **{correct_gender}**."

    index += 1
    state["index"] = index
    score_text = f"Score: {state['score']} / {TOTAL}"

    if index >= TOTAL:
        final = f"🏁 **Game over! Final Score: {state['score']} / {TOTAL}** 🏁"
        return (
            state,
            word_html("🎊 Finished! 🎊"),
            feedback + "\n\n" + final,
            score_text,
            "Quiz complete!",
            gr.update(interactive=False),
            gr.update(interactive=False),
        )
    else:
        next_word = words[index][0]
        return (
            state,
            word_html(next_word),
            feedback,
            score_text,
            f"Word {index + 1} of {TOTAL}",
            gr.update(interactive=True),
            gr.update(interactive=True),
        )


def check_masculine(state):
    return check_answer("Masculine", state)


def check_feminine(state):
    return check_answer("Feminine", state)


with gr.Blocks(title="Hindi Gender Quiz") as demo:
    gr.Markdown("# 🎈 Hindi Gender Quiz 🎈")
    gr.Markdown("Read the Hindi word below, then tap **Masculine** or **Feminine**!")

    progress_display = gr.Markdown(f"Word 1 of {TOTAL}")
    word_display = gr.HTML(word_html(ALL_WORDS[0][0]))
    score_display = gr.Markdown(f"Score: 0 / {TOTAL}")
    feedback_display = gr.Markdown("")

    with gr.Row():
        masc_btn = gr.Button("👦 Masculine", variant="primary")
        fem_btn = gr.Button("👧 Feminine", variant="primary")

    restart_btn = gr.Button("🔄 Start Over")

    state = gr.State({})

    outputs_list = [state, word_display, feedback_display, score_display,
                     progress_display, masc_btn, fem_btn]

    demo.load(new_game, inputs=None, outputs=outputs_list)
    masc_btn.click(check_masculine, inputs=state, outputs=outputs_list)
    fem_btn.click(check_feminine, inputs=state, outputs=outputs_list)
    restart_btn.click(new_game, inputs=None, outputs=outputs_list)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render assigns this via the PORT env var
    demo.launch(css=CSS, server_name="0.0.0.0", server_port=port)
