if __name__ == "__main__":
    from pathlib import Path
    import gradio as gr
    from backend import MK

    me = MK()
    # Path to your photo (use one that exists: assets/mk_avatar.png or me/mk_avatar.png)
    assets_dir = Path(__file__).resolve().parent / "assets"
    mk_avatar = assets_dir / "mk_avatar.jpg"
    if not mk_avatar.exists():
        mk_avatar = Path(__file__).resolve().parent / "me" / "mk_avatar.jpg"  # fallback

    chatbot = gr.Chatbot(
        avatar_images=(None, str(mk_avatar) if mk_avatar.exists() else None),
        layout="bubble",
        placeholder="Chat with MK — Ask about his background, experience, or leave your email to get in touch.",
        height=600,
    )

    demo = gr.Blocks(
        title="MK's Alter Ego",
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="slate",
        ),
        css="""
        .gradio-container { max-width: 700px !important; margin: auto; }
        .message.user { margin-left: 2rem; }
        .message.bot { margin-right: 2rem; }
        """,
    )
    with demo:
        gr.Markdown("# MK's Alter Ego\n*Chat with Mathanbabu Kaliappan*")
        gr.ChatInterface(fn=me.chat, chatbot=chatbot, submit_btn="Send")
    demo.launch()