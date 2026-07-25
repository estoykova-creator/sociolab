import streamlit as st
import google.generativeai as genai
import pypdf

# 1. КОНФИГУРАЦИЯ НА ПРИЛОЖЕНИЕТО
st.set_page_config(page_title="SocioLab: Цифров учебник по ЕСИ", layout="wide")
st.title("SocioLab: Цифров учебник и методологичен тренажор")
st.subheader("Елементи на социологическото изследване (в традицията на Пиер Бурдийо)")

# 2. СВЪРЗВАНЕ С ИЗКУСТВЕНИЯ ИНТЕЛЕКТ
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("⚠️ Грешка: API ключът не е намерен в настройките (Secrets) на Streamlit Cloud!")

@st.cache_resource
def get_available_models():
    try:
        return [m.name.replace('models/', '') for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    except Exception:
        return ["gemini-1.5-flash", "gemini-1.5-pro"] 

available_models = get_available_models()

# 3. ЛЯВА ЛЕНТА (ПОМОЩНИ МАТЕРИАЛИ И РЕЧНИК)
with st.sidebar:
    st.header("⚙️ Настройки")
    selected_model = st.selectbox(
        "Избери модел:", 
        available_models,
        index=available_models.index("gemini-1.5-flash") if "gemini-1.5-flash" in available_models else 0
    )
    
    st.markdown("---")
    st.header("📂 Теоретичен корпус")
    uploaded_file = st.file_uploader(
        "Качи текст, лекция или PDF за анализ:", 
        type=["txt", "md", "pdf"]
    )
    
    custom_corpus = ""
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".pdf"):
            try:
                reader = pypdf.PdfReader(uploaded_file)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        custom_corpus += text + "\n"
                if len(custom_corpus) > 20000:
                    custom_corpus = custom_corpus[:20000] + "\n[...Текстът е съкратен автоматично...]"
                st.success("✅ PDF файлът е зареден успешно!")
            except Exception as e:
                st.error(f"Грешка при четене на PDF: {e}")
        else:
            custom_corpus = uploaded_file.read().decode("utf-8")
            if len(custom_corpus) > 20000:
                custom_corpus = custom_corpus[:20000] + "\n[...Текстът е съкратен...]"
            st.success("✅ Текстовият файл е зареден успешно!")

    st.markdown("---")
    st.header("📖 Речник на понятията")
    with st.expander("Концептуална рамка (Бурдийо)"):
        st.markdown("""
        * **Социално пространство:** Многоизмерна система от обективни отношения, съществуващи независимо от волята на агентите. Първична реалност, а не статистически агрегат от индивиди.
        * **Символно производство:** Механизмите, чрез които позициите в социалното пространство се прикриват, легитимират и утвърждават като естествени.
        * **Хабитус:** Инкорпорираното социално; система от диспозиции, породена от обективните структури на пространството. Лишена от субстанциална автономия производна функция.
        * **Капитал:** Специфична форма на власт и инструмент за доминация в борбата за легитимна класификация. Стойността му зависи изцяло от обективната структура на полето.
        * **Официална номинация:** Перформативен акт на институцията, който притежава силата на закон и продуцира свойствата на назования обект (за разлика от неофициалната обида).
        * **Епистемологичен скъс:** Радикален разрив с илюзията за прозрачност на социалния свят и здравия разум.
        """)

    st.markdown("---")
    st.info("💡 **Режим:** Нулеви отклонения (temperature=0.0) за пълна академична стабилност.")

# 4. СТРУКТУРА НА УЧЕБНИКА (ТАБОВЕ)
tab0, tab1, tab2, tab3 = st.tabs([
    "📖 За учебника",
    "🔎 Модул 1: Рефлексивна социология", 
    "🎲 Модул 2: Релационна социология", 
    "🎯 Модул 3: Научният въпрос"
])

with tab0:
    st.header("Добре дошли в интерактивния учебник по Социологика на ЕСИ")
    st.write("Този цифров учебник подпомага студентите в усвояването на изследователското занаятчииство, вкоренено в епистемологичната традиция на Пиер Бурдийо, Жан-Клод Пасро и Жан-Клод Шамборедо.")
    st.markdown("### 🧭 Основни принципи на упътването:")
    st.markdown("""
    1. **Отказ от спонтанната социология:** Изследването започва с разкъсване на илюзиите на здравия разум и есенциализма.
    2. **Релационно мислене:** Светът на социалното не се състои от изолирани индивиди, а от мрежи от обективни отношения.
    3. **Рефлексивност:** Изследователят трябва непрекъснато да обективира собствената си позиция и академичен хабитус.
    """)

def handle_google_errors(e, model_name):
    error_msg = str(e)
    if "404" in error_msg or "no longer available" in error_msg:
        st.error(f"❌ **Отказан достъп от Google:** Версията '{model_name}' е спряна. Моля, изберете друга (напр. gemini-1.5-pro или gemini-1.5-flash).")
    else:
        st.error(f"⚠️ Възникна проблем при комуникацията със сървъра. Опитайте отново.\n\n*(Технически детайл: {e})*")

# --- МОДУЛ 1: РЕФЛЕКСИВНА СОЦИОЛОГИЯ ---
with tab1:
    st.header("Модул 1: Рефлексивна социология (Епистемологичен скъс)")
    user_topic_1 = st.text_area("Опиши социологическия си проблем/тема:", placeholder="Например: Влиянието на социалните мрежи върху политическата активност...", key="topic_mod1")
    
    if st.button("Тествай Модул 1"):
        if user_topic_1:
            with st.spinner("Извършване на епистемологичен разрез..."):
                system_prompt_1 = f"""
                ТИ СИ: Методологичен ментор в традицията на Пиер Бурдийо и Жан-Клод Пасро.
                
                СКРИТ ТЕОРЕТИЧЕН ФУНДАМЕНТ:
                Винаги анализирай проблема през призмата на "социалното пространство" (обективни отношения) и "символното производство" (легитимация). Хабитусът и капиталите са техни производни, лишени от субстанциална автономия. Обществото не е агрегат от индивиди.
                
                {custom_corpus if custom_corpus else ""}
                
                ФОРМАТ НА ОТГОВОР:
                1. 🛑 ДЕТЕКТОР ЗА ЗДРАВ РАЗУМ: Анализирай дали формулировката съдържа елементи на спонтанна социология или битов психологизъм.
                2. 🎓 СХОЛАСТИЧНА ИЛЮЗИЯ: Провери дали темата не страда от излишна абстракция.
                3. 🪞 АКАДЕМИЧНА РЕФЛЕКСИВНОСТ: Обективирай позицията на изследователя спрямо тази тема.
                4. 🎯 ПРЕХОД КЪМ СОЦИОЛОГИЧЕСКИ ВЪПРОС: Разбий въпроса на система от аналитични подвъпроси за емпирично изследване.
                """
                try:
                    model_1 = genai.GenerativeModel(selected_model, system_instruction=system_prompt_1)
                    response_1 = model_1.generate_content(user_topic_1, generation_config={"temperature": 0.0})
                    st.markdown(response_1.text)
                except Exception as e:
                    handle_google_errors(e, selected_model)

# --- МОДУЛ 2: РЕЛАЦИОННА СОЦИОЛОГИЯ ---
with tab2:
    st.header("Модул 2: Релационна социология")
    
    # Автоматично извличане на темата от Модул 1 (ако има такава)
    default_topic_2 = st.session_state.get("topic_mod1", "")
    
    user_topic_2 = st.text_area("Въведи темата за релационно конструиране:", value=default_topic_2, key="topic_mod2")
    
    if st.button("Тествай Модул 2"):
        if user_topic_2:
            with st.spinner("Конструиране на релационния обект..."):
                system_prompt_module_2 = f"""
                ТИ СИ: Методологичен ментор по емпирична социология в традицията на Пиер Бурдийо.
                
                СКРИТ ТЕОРЕТИЧЕН ФУНДАМЕНТ:
                Обектът се дефинира чрез релационните позиции, а не чрез изолирани индивиди. Официалната номинация и класификаторните актове са форми на символно насилие.
                ЗАДЪЛЖИТЕЛНО разграничавай строго единиците на извадка от единиците на анализ.
                
                {custom_corpus if custom_corpus else ""}
                
                ФОРМАТ НА ОТГОВОР:
                1. 🏗️ РЕЛАЦИОННО КОНСТРУИРАНЕ НА ЕМПИРИЧНИЯ ОБЕКТ: Обясни как концепцията се превръща в изследване на обективни отношения в пространството.
                2. 🌐 КОРПУС ОТ ПОЗИЦИИ: Покажи защо съвкупността е структуриран корпус от позиции, а не статистическа сума.
                3. 📊 ЕДИНИЦИ НА ИЗВАДКА СРЕЩУ ЕДИНИЦИ НА АНАЛИЗ: Направи строго разграничение между инструментите за достъп и структурните позиции.
                """
                try:
                    model_module_2 = genai.GenerativeModel(selected_model, system_instruction=system_prompt_module_2)
                    response_module_2 = model_module_2.generate_content(user_topic_2, generation_config={"temperature": 0.0})
                    st.markdown(response_module_2.text)
                except Exception as e:
                    handle_google_errors(e, selected_model)

with tab3:
    st.header("3. Раждането на социологическия въпрос")
    st.info("В процес на разработка...")
