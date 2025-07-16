import streamlit as st
import requests
from openai import OpenAI

from PROMPTS.story_generation_prompt import generate_story_prompt
from PROMPTS.image_generation_prompt import generate_image_prompt
from PROMPTS.music_generation_prompt import generate_music_prompt
from imaginera_chat import get_imaginera_system_prompt, get_imaginera_response

# Load environment variables
st.warning("🔐 To use this app, please enter your own OpenAI API key. Your key will be used only during this session and never stored,logged or shared .")
api_key = st.text_input("Enter your OpenAI API key", type="password")

# Stop app if no key is entered
if not api_key:
    st.stop()

# Initialize client with user key
try:
    client = OpenAI(api_key=api_key)
    client.models.list()  
except Exception as e:
    st.error("❌ Failed to authenticate your OpenAI API key. Please check if the key entered is valid and has access to GPT-4 and DALL·E 3.")
    st.stop()

# Page config
st.set_page_config(page_title="Creative Content Studio", layout="wide")

# Inject custom CSS for dark UI
st.markdown("""
    <style>
        body {
            background-color: #0e1117;
            color: #f0f0f0;
            font-family: 'Segoe UI', sans-serif;
        }
        h1, h2, h3, h4 {
            color: #f4f4f5;
        }
        .stButton>button {
            background-color: #6c63ff;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 10px 20px;
            margin: 10px 0;
            transition: background-color 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #7d75ff;
        }
        .stDownloadButton>button {
            background-color: #21c48c;
            color: white;
            border-radius: 8px;
        }
        .stDownloadButton>button:hover {
            background-color: #2de6a1;
        }
        .stTextInput>div>div>input,
        .stSelectbox>div>div,
        .stTextArea>div>div>textarea {
            background-color: #2c2f36;
            border: 1px solid #3e3e42;
            border-radius: 8px;
            color: #f0f0f0;
        }
        .block-container {
            padding: 2rem;
        }
        .info-box {
            padding: 12px;
            border-radius: 8px;
            background-color: #20232a;
            margin-top: 10px;
            color: #ffffff;
        }
        .onboarding-box {
            padding: 1rem;
            background-color: #1c1f26;
            border-left: 4px solid #6c63ff;
            border-radius: 8px;
            margin-bottom: 1.5rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("✨ AI-Powered Creative Content Studio")
st.markdown("##### Your creative spark, ignited by AI — generate written visions, stylized images, and curated music vibes to fuel your imagination.")

st.markdown("""
<div class="onboarding-box">
👋 **Welcome to your Creative Content Studio!**<br><br>

Unleash your imagination with the power of AI. Here's what you can do:
<ul>
  <li>🌟 Enter a theme or select from rich templates and categories like personal storytelling, kids' tales, fantasy worlds, brand stories, education, and more</li>
  <li>🧠 Choose from 70+ unique creative use cases across 8 categories — from bedtime stories and cinematic scenes to marketing concepts and metaphor-driven prompts</li>
  <li>🎨 Instantly generate a complete creative pack — including narrative content, a visually styled AI image, and a curated music vibe — all tailored to your theme</li>
  <li>🖼️ Choose from 50+ unique image styles — from watercolor and anime to surrealist paintings, 3D renders, and more</li>
  <li>💬 Get help anytime from <b>Imaginera</b> — your built-in creative assistant who can suggest ideas, brainstorm concepts, or co-create content with you</li>
</ul>

🔥 Try it out, 💡explore ideas, 🌈 and let your creativity flow!
</div>
""", unsafe_allow_html=True)


if 'history' not in st.session_state:
    st.session_state.history = []

if 'templates' not in st.session_state:
    st.session_state.templates = {
        "None": "",
        "Fantasy Adventure": "A hero's journey through a mythical land full of dragons and secrets.",
        "Romantic Tale": "Two strangers fall in love during a rainy evening in Paris.",
        "Sci-Fi Thriller": "A robot awakens to consciousness in a future where machines rule.",
        "Mystery": "A detective solves a murder in a haunted mansion.",
        "Children's Fable": "A talking rabbit helps a lost child find home through a magical forest.",
        "Superhero Origin": "An ordinary teen discovers they have superpowers after a cosmic event and must learn to use them wisely.",
        "Historical Fiction": "A young warrior in ancient Egypt is forced to choose between loyalty and rebellion.",
        "Post-Apocalyptic Survival": "In a world destroyed by climate collapse, a lone survivor finds hope in an unexpected place.",
        "Comedy Skit": "A clumsy magician tries to impress a crowd but keeps messing up his tricks in hilarious ways.",
        "AI Gone Rogue": "An artificial intelligence becomes self-aware and starts writing its own story — bending the rules of reality."
    }

# Tab layout
tabs = st.tabs(["Create", "History", "Chat with Imaginera"])

with tabs[0]:
    st.markdown("#### 🎭 Choose a creative prompt:")
    templates = st.session_state.templates
    selected_template = st.selectbox("Select a template:", list(templates.keys()))
    theme = st.text_area("Or enter your custom theme:")

    if selected_template != "None" and not theme:
        theme = templates[selected_template]
        st.info(f"Using template: {selected_template}")

    # Grouped Use Cases
    use_case_groups = {
    "📜 Personal & Narrative Based": [
        "✍️ A creative writing starter",
        "🧍 A day in the life of an imaginary character",
        "📝 A letter from the future or past",
        "💌 A poetic love confession or breakup note",
        "📱 A fictional social media post from a character",
        "📆 A dream journal entry turned story",
        "🧘 A journaling prompt with metaphor",
        "💭 A story that represents a feeling",
        "🔒 A journal prompt from your shadow self",
        "😨 A short story to process fear",
        "💤 A subconscious dream turned surreal tale"
    ],
    "🧸 Kids & Family": [
        "🛌 A bedtime story for a child",
        "🐾 A fun animal tale for children",
        "📖 A moral lesson in a fairy-tale style",
        "👶 A baby’s first adventure",
        "👨‍👩‍👧 A family tradition as a story",
        "🎠 A day at a magical fair",
        "🦕 A dinosaur time-travel story",
        "🎈 A birthday surprise with a twist",
        "🐉 A dragon who doesn’t want to fight",
        "🌈 A color-themed story for toddlers",
        "📘 A child's dream turned real"
    ],
    "🎮 Fantasy, Worldbuilding & RPG": [
        "🕹️ A fictional game world",
        "👤 A character backstory for an RPG",
        "🔮 A magic system or world rule",
        "📜 A mythical backstory for a fantasy novel",
        "🧱 A mythology from a new civilization",
        "🌌 A parallel universe theory as a narrative",
        "🛸 An imaginative escape for relaxation",
        "⚔️ A prophecy in an ancient tome",
        "🗺️ A travel diary from an imaginary land",
        "🏛️ A fictional historical event",
        "🧙 A school for magic with new rules"
    ],
    "🎬 Film, Script & Visual Storytelling": [
        "🎬 A short film idea",
        "🎞️ A cinematic scene description",
        "📹 A video content script prompt",
        "🎭 A dramatic plot twist idea",
        "🗨️ A dialogue between two characters",
        "🕵️ A noir detective intro scene",
        "🎤 A musical scene concept",
        "🔫 A heist sequence in a movie",
        "👽 A sci-fi first contact scene",
        "🧛 A horror transformation scene",
        "🎟️ A movie trailer voiceover script"
    ],
    "🖼️ Visual & Inspirational Concepts": [
        "🎨 A moodboard for inspiration",
        "🌱 A guided visual meditation story",
        "🎶 A music genre as a character",
        "🪄 A scene built around a color palette",
        "🏞️ A place that only exists in dreams",
        "👁️ A story seen through another’s eyes",
        "💎 A metaphor turned into an image",
        "🧩 A surreal combination of objects",
        "🎐 An emotion described without words",
        "🕰️ A frozen moment in time, visualized",
        "📷 A snapshot story from a fictional photo"
    ],
    "📦 Brand, Marketing & Business": [
        "📦 A product story for a brand",
        "📢 A short story ad concept",
        "💡 A brand’s origin story told as a fable",
        "🧬 A metaphor-driven pitch for a startup",
        "📊 A data story (turning a dataset into narrative)",
        "🎯 A campaign idea in narrative format",
        "🎁 A brand described as a character",
        "🛍️ A shopping experience story",
        "💬 A fictional customer review as a tale",
        "🔍 A behind-the-scenes brand journey",
        "🧾 A receipt that tells a story"
    ],
    "🧪 Experimental, Meta & Thoughtful": [
        "🤖 A chatbot personality and its user story",
        "🎭 A story that breaks the fourth wall",
        "🌐 A website that gains sentience",
        "📚 A lesson from history retold as a fairy tale",
        "🔬 A scientific concept as a fantasy story",
        "⚖️ A courtroom drama on a moral dilemma",
        "👥 A cross-cultural friendship story",
        "🌀 A looped or paradoxical narrative",
        "🧠 A conversation between logic and emotion",
        "🎡 A tale that plays with time and memory",
        "📎 A mundane object with a secret past"
    ],
    "📚 Education & Edutainment": [
        "📚 A historical event reimagined as a story",
        "🔬 A science concept explained with fantasy",
        "🧠 A brain cell’s point of view",
        "🌍 A planet narrating its life cycle",
        "🦠 A virus or bacteria as a character",
        "🔢 A number or math concept as a tale",
        "✍️ A grammar rule turned into a fable",
        "🗣️ A language learning comic scene",
        "🎨 An art movement described as a journey",
        "🎵 A musical note who finds its rhythm",
        "📖 A textbook chapter as a story"
    ]
}
    
    category = st.selectbox("📂 Choose a category:", list(use_case_groups.keys()))
    use_case = st.selectbox("🎯 What are you creating today?", use_case_groups[category])

    tone = st.selectbox("🎼 Choose a tone for your content:",
         ["Default", "Emotional", "Casual", "Poetic", "Humorous",
         "Mystery", "Romantic","Ancient","Ironic","Sarcastic","Tragic","Surreal","Empowering","Horror",
        "Thriller","Philosophical", "Motivational", "Visionary", "Satirical", "Whimsical", "Epic",
        "Candid", "Suspenseful", "Uplifting", "Witty", "Adventurous", "Didactic", "Minimalist", "Narrative"])
    style = st.selectbox("🖼️ Choose an image style:", [
        "Default", "Realistic", "Anime", "Sketch", "Watercolor", "Digital Art",
        "Pixel Art", "Steampunk", "Noir", "Cyberpunk", "Fantasy Realism",
        "Impressionist Painting", "Oil Painting", "3D Render", "Line Art", "Low Poly","ASCII Art","Comic Book Style","Wireframe",
        "Vintage Cartoon Style","Webtoon Style","Graphic Novel Style","Miniature Style",
        "Claymation Style","Infographic Style","Thermal Imaging","X-Ray Style","Ink Print Style",
        "Pop Art","Pencil Drawing","Neon Art","Graffiti","Stop-Motion Illustration Style","Crayon Drawing Style", "Paper Cutout Style", "Storybook Illustration",
        "Chalkboard Style", "Cel Shading", "Runestone Glyph Style",
        "Dreamcore Style", "Bioluminescent Style", "Cinematic Lighting Style",
        "VHS Aesthetic", "Storyboard Panels", "Collage Art Style", "Papercraft 3D Style",
        "Ink Wash Style", "Surrealist Painting Style", "Whiteboard Doodle Style",
        "Blueprint Style", "Retro Textbook Illustration", "Molecular Model Style"

    ])

    if theme:
        st.markdown(f"""
        <div class='info-box'>
        <b>Theme:</b> {theme}<br>
        <b>Use Case:</b> {use_case}<br>
        <b>Tone:</b> {tone}<br>
        <b>Style:</b> {style}
        </div>
        """, unsafe_allow_html=True)
     
    if st.button("Generate Content") and theme:
      with st.spinner("Writing your content✍️..."):
        try:
            custom_prompt = generate_story_prompt(theme, use_case, tone)
            story_response = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[{"role": "user", "content": custom_prompt}],
                max_tokens=600
            )
            st.session_state.story = story_response.choices[0].message.content.strip()
        except Exception as e:
            st.error("❌ Failed to generate story. Please ensure your API key has GPT-4 access and available credits.")
            st.stop()


        with st.spinner("Generating your image..."):
            image_prompt = generate_image_prompt(theme, style)

            if not image_prompt or image_prompt.strip() == "":
                st.error("Image prompt is empty. Please enter a valid theme or select a proper template.")
                st.stop()

            st.write("🧠 Image Prompt Sent:", image_prompt)

            for attempt in range(2):
                try:
                    image_response = client.images.generate(
                        model="dall-e-3",
                        prompt=image_prompt,
                        size="1024x1024",
                        quality="standard",
                        n=1
                    )
                    break
                except Exception as e:
                    if attempt == 1:
                        st.error("❌ Image generation failed after retry.")
                        st.exception(e)
                        st.stop()
                    else:
                        st.warning("⚠️ First attempt failed. Retrying...")

            st.session_state.image_url = image_response.data[0].url
            st.session_state.image_data = requests.get(st.session_state.image_url).content

        with st.spinner("Suggesting a music vibe..."):
            music_prompt = generate_music_prompt(theme)
            music_response = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[{"role": "user", "content": music_prompt}],
                max_tokens=300,
                temperature=0.7
                
            )   
            st.session_state.music_vibe = music_response.choices[0].message.content.strip()

        st.session_state.creative_text = f"Use Case: {use_case}\n\nTheme: {theme}\n\nStory ({tone} tone):\n{st.session_state.story}\n\nMusic Vibe:\n{st.session_state.music_vibe}"

        st.session_state.history.append({
            "theme": theme,
            "tone": tone,
            "use_case": use_case,
            "story": st.session_state.story,
            "image_url": st.session_state.image_url,
            "music_vibe": st.session_state.music_vibe
        })

    if 'story' in st.session_state:
        st.subheader("📖 Content")
        st.write(st.session_state.story)

    if 'image_url' in st.session_state:
        st.subheader("🎨 Image")
        cols = st.columns([2, 1])
        cols[0].image(st.session_state.image_url, use_container_width=True)
        cols[1].download_button("Download Image", st.session_state.image_data, "ai_image.png", mime="image/png")

    if 'music_vibe' in st.session_state:
        st.subheader("🎵 Music Vibe")
        st.write(st.session_state.music_vibe)

    if 'creative_text' in st.session_state:
        st.download_button("Download Creative Pack (Text)", st.session_state.creative_text, "creative_pack.txt", mime="text/plain")
with tabs[1]:
    if st.session_state.history:
        st.subheader("📜 History (This Session)")
        for item in reversed(st.session_state.history[-5:]):
            st.markdown(f"**Use Case:** {item['use_case']} | **Theme:** {item['theme']} | **Tone:** {item['tone']}")
            st.markdown(f"*Story Preview:* {item['story'][:150]}...")
            st.markdown(f"*Music:* {item['music_vibe'][:100]}...")
            st.image(item["image_url"], width=200)
            st.markdown("---")
    else:
        st.info("No history yet. Generate content to view your creative session here.")

with tabs[2]:
    st.subheader("💬 Chat with Imaginera")
    if "imaginera_history" not in st.session_state:
        st.session_state.imaginera_history = [
            {"role": "system", "content": get_imaginera_system_prompt()}
        ]

    user_input = st.chat_input("Hi there! I’m Imaginera - I’m here to spark ideas, craft prompts, and bring your imagination to life.”")
    if user_input:
        st.session_state.imaginera_history.append({"role": "user", "content": user_input})
        with st.spinner("Imaginera is thinking..."):
            reply = get_imaginera_response(client, st.session_state.imaginera_history)
            st.session_state.imaginera_history.append({"role": "assistant", "content": reply})

    for msg in st.session_state.imaginera_history[1:]:
        st.chat_message(msg["role"]).write(msg["content"])