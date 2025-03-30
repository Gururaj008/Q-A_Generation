import streamlit as st
import re
import json
import warnings
warnings.filterwarnings('ignore')
import google.generativeai as genai

# Set the Gemini API key from st.secrets
GEMINI_API_KEY = st.secrets['auth_key']
genai.configure(api_key=GEMINI_API_KEY)

def question_and_answers(input_text, no_correct, no_ques):
    if isinstance(input_text, str):
        # Two templates based on the number of correct answers
        template_1 = '''
        paragraph: India, officially known as the Republic of India, is a diverse and vibrant country located in South Asia.
        It is the seventh-largest country in the world by land area and the second-most populous, home to over 1.3 billion people
        representing various cultures, languages, and religions.

        India's rich history dates back thousands of years, and it has been a cradle of ancient civilizations and the birthplace of
        several major religions, including Hinduism, Buddhism, Jainism, and Sikhism. India boasts a mesmerizing tapestry of landscapes,
        from the snow-capped Himalayas in the north to the lush tropical forests in the south. The country is renowned for its cultural heritage,
        with magnificent architectural marvels such as the Taj Mahal, an epitome of love, and the historic forts and palaces that narrate stories of its illustrious past.

        Question 01 : What kind of country is India?
        a. Diverse
        b. Non-Vibrant
        c. Monotonous
        d. Dull
        Correct Option : a

        Question 02 : Population of India is greater than?
        a. 1.0 billion
        b. 1.2 Billion
        c. 1.3 Billion
        d. 1.4 Billion
        Correct Option : c

        Question 03 : What is India called as?
        a. Cradle of modren world
        b. Cradle of Ancient civilization
        c. Cradle of Innovation
        d. Cradle of Invention
        Correct Options: b

        Question 04 : Where in India is Himalayas located?
        a. South
        b. West
        c. North-East
        d. North
        Correct Options: d
        '''
        template_2 = '''
        paragraph: India, officially known as the Republic of India, is a diverse and vibrant country located in South Asia.
        It is the seventh-largest country in the world by land area and the second-most populous, home to over 1.3 billion people
        representing various cultures, languages, and religions.

        India's rich history dates back thousands of years, and it has been a cradle of ancient civilizations and the birthplace of
        several major religions, including Hinduism, Buddhism, Jainism, and Sikhism. India boasts a mesmerizing tapestry of landscapes,
        from the snow-capped Himalayas in the north to the lush tropical forests in the south. The country is renowned for its cultural heritage,
        with magnificent architectural marvels such as the Taj Mahal, an epitome of love, and the historic forts and palaces that narrate stories of its illustrious past.

        Question 01 : What kind of country is India?
        a. Diverse
        b. Vibrant
        c. Monotonous
        d. Dull
        Correct Options :(a) & (b)

        Question 02 : Population of India is greater than?
        a. 1.0 billion
        b. 1.2 Billion
        c. 1.3 Billion
        d. 1.4 Billion
        Correct Options : (b) & (c)

        Question 03 : What is India called as?
        a. Cradle of modren world
        b. Cradle of Ancient civilization
        c. Cradle of Innovation
        d. Cradle of Invention
        Correct Options: (b) & (c)

        Question 04 : Where in India is Himalayas located?
        a. South
        b. West
        c. North-East
        d. North
        Correct Options: (c) & (d)
        '''
        # Detailed instruction to force a pure JSON response
        query = f'''Please stick to the following instructions while generating the response:
- Generate only {no_ques} questions.
- With {no_correct} correct answer for each question.
- Please return the question and answers in the same format as specified in the template that is passed as reference for response generation.
- Please mandatorily add a question mark at the end of every question.
- Please generate only the specified number of options as answers (do not always generate 4 options).
- Return only valid JSON with a top-level key "questions" that contains a list of question objects, each having "question", "options", and "correct_options".
'''
        # Clean and merge the user input paragraph
        input1 = input_text.split('\n')
        input1 = [para for para in input1 if para.strip()]
        merged_paras = " ".join(input1)
        input2 = 'Paragraph: ' + merged_paras

        # Select template based on the number of correct answers
        if no_correct == 1:
            input3 = template_1 + query + input2
        else:
            input3 = template_2 + query + input2

        # Use Google Gemini for text generation
        model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")
        response = model.generate_content(input3)
        res = response.text

        st.write("Raw LLM Response (before JSON parsing):")
        st.code(res)

        # Extract JSON part using regex to handle extra text
        json_match = re.search(r'({.*})', res, re.DOTALL)
        if json_match:
            res_clean = json_match.group(1)
            try:
                qa_json = json.loads(res_clean)
            except json.JSONDecodeError:
                st.error("Failed to parse JSON after extraction. Displaying raw output.")
                st.code(res)
                return
        else:
            st.error("Failed to locate JSON in the response. Displaying raw output.")
            st.code(res)
            return

        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Agdasima');
            .custom-text-02 { font-family: 'Perpetua', sans-serif; font-size: 30px; color: #f9e79f; }
            </style>
            <p class="custom-text-02">Displaying the generated Q&A</p>
            """, unsafe_allow_html=True)

        if "questions" in qa_json and isinstance(qa_json["questions"], list):
            for q_data in qa_json["questions"]:
                if isinstance(q_data, dict):
                    question_text = q_data.get("question", "Question text missing")
                    options_data = q_data.get("options", {})
                    correct_options = q_data.get("correct_options", [])

                    st.subheader(question_text)

                    if isinstance(options_data, dict):
                        for option_letter, option_text in options_data.items():
                            is_correct = option_letter in correct_options
                            option_display = f"{option_letter}. {option_text}"
                            if is_correct:
                                st.markdown(f"**:green[{option_display}]**")
                            else:
                                st.markdown(option_display)
                    else:
                        st.warning("Options data is not in the expected dictionary format.")

                    if correct_options:
                        correct_options_str = ", ".join(correct_options)
                        st.markdown(f"**Correct Options:** :green[{correct_options_str}]")
                    else:
                        st.warning("Correct options are missing for this question.")
                    st.write("")
                else:
                    st.warning("Question data is not in the expected dictionary format.")
        else:
            st.warning("No questions found in the JSON response or questions format is incorrect.")
    else:
        raise TypeError("Value must be a string data type.")

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    # Display header images
    col001, col002, col003 = st.columns([10, 10, 10])
    with col001:
        st.image('1.gif')
    with col002:
        st.image('1.gif')
    with col003:
        st.image('1.gif')
    
    # Title section
    col004, col005, col006 = st.columns([100, 300, 100])
    with col005:
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Agdasima');
            .custom-text-01 { font-family: 'Agdasima', sans-serif; font-size: 70px; color: cyan; }
            </style>
            <p class="custom-text-01">Q&A Generation using LLM</p>
            """, unsafe_allow_html=True)
    
    # About the project section
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Agdasima');
        .custom-text-02 { font-family: 'Perpetua', sans-serif; font-size: 30px; color: #f9e79f; }
        </style>
        <p class="custom-text-02"> About the project </p>
        """, unsafe_allow_html=True)
    st.write('')
    st.markdown(
        '<div style="text-align: justify"> Creating multiple-choice questions based on a given paragraph offers students a multifaceted approach to learning. It not only deepens comprehension by requiring them to distil key concepts and main ideas, but also engages them actively in the material, fostering a stronger grasp of the subject matter. This process encourages critical thinking as students formulate plausible distracters that challenge their own understanding and uncover potential misconceptions. Moreover, the skill of crafting questions cultivates the practical application of acquired knowledge, bridging the gap between theory and real-world scenarios.  </div>',
        unsafe_allow_html=True)
    st.write('')
    st.markdown(
        '<div style="text-align: justify"> As students compare their questions to model answers, they engage in meaningful self-assessment, identifying areas of strength and those in need of review. This exercise mirrors the format of assessments, thus aiding in effective test preparation. Beyond assessment, the act of generating questions prompts students to organize information logically, strengthening their ability to structure thoughts coherently. Collaborative sharing of questions with peers and educators initiates a valuable feedback loop, refining their understanding and enhancing communication skills.  </div>',
        unsafe_allow_html=True)
    st.write('')
    st.markdown(
        '<div style="text-align: justify"> This practice also nurtures vocabulary enrichment as students carefully select appropriate terminology. Ultimately, the process empowers students to take charge of their learning journey, cultivating autonomy and honing higher-order thinking skills. The lasting impact of question generation on long-term retention solidifies its role as a holistic tool for comprehensive understanding, effective study strategies, and academic growth.  </div>',
        unsafe_allow_html=True)
    st.write('')
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Agdasima');
        .custom-text-02 { font-family: 'Baskerville', sans-serif; font-size: 30px; color: #f7dc6f; }
        </style>
        <p class="custom-text-02">Let's try generating some Q&A from the paragraph of your choice..... </p>
        """, unsafe_allow_html=True)

    # Input section
    input_text = st.text_area('', 'Please enter your text here', height=200)
    if len(input_text.split()) < 30:
        st.error('Please input a paragraph with at least 30 words for generating Q&A...', icon="🚨")
    else:
        st.write('')
        col007, col008 = st.columns([10, 10])
        with col007:
            no_ques = int(st.radio(label='Please choose the number of questions to generate', options=[1, 2, 3, 4]))
        with col008:
            no_correct = int(st.radio('Please choose the number of correct/nearly_correct answers to generate', options=[1, 2]))
        st.write('')
        if st.button('Generate the Q&A for the above paragraph', use_container_width=True):
            question_and_answers(input_text, no_correct, no_ques)

    # Developer contact details
    st.divider()
    st.subheader(':orange[Developer contact details]')
    st.write('')
    st.write('')
    col301, col302 = st.columns([10, 20])
    with col301:
        st.markdown(":orange[email id:]")
    with col302:
        st.markdown(":yellow[gururaj008@gmail.com]")

    col301, col302 = st.columns([10, 20])
    with col301:
        st.markdown(":orange[Personal webpage hosting other Datascience projects:]")
    with col302:
        st.markdown(":yellow[http://gururaj008.pythonanywhere.com/]")

    col301, col302 = st.columns([10, 20])
    with col301:
        st.markdown(":orange[LinkedIn profile:]")
    with col302:
        st.markdown(":yellow[https://www.linkedin.com/in/gururaj-hc-data-science-enthusiast/]")

    col301, col302 = st.columns([10, 20])
    with col301:
        st.markdown(":orange[Github link:]")
    with col302:
        st.markdown(":yellow[https://github.com/Gururaj008]")

    st.divider()
    col1001, col1002, col1003, col1004, col1005 = st.columns([10, 10, 10, 10, 15])
    with col1005:
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Agdasima');
            .custom-text-10 { font-family: 'Agdasima', sans-serif; font-size: 28px; color: cyan; }
            </style>
            <p class="custom-text-10">An Effort by : MAVERICK_GR</p>
            """, unsafe_allow_html=True)
