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
        # Instruction to force a pure JSON response
        query = f'''Please stick to the following instructions while generating the response:
- Generate only {no_ques} questions.
- With {no_correct} correct answer for each question.
- Please return the question and answers in the same format as specified in the template that is passed as reference for response generation.
- Please mandatorily add a question mark at the end of every question.
- Please generate only the specified number of options as answers.
- Return only valid JSON with a top-level key "questions" that contains a list of question objects, each having "question", "options", and "correct_options".
'''
        # Merge and clean the input paragraph
        input_lines = input_text.split('\n')
        merged_paras = " ".join([line.strip() for line in input_lines if line.strip()])
        input2 = 'Paragraph: ' + merged_paras

        # Choose the template based on the number of correct answers
        if no_correct == 1:
            prompt = template_1 + query + input2
        else:
            prompt = template_2 + query + input2

        # Generate content using Google Gemini
        model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")
        response = model.generate_content(prompt)
        res = response.text

        # Extract JSON using regex to handle any extra text
        json_match = re.search(r'({.*})', res, re.DOTALL)
        if json_match:
            res_clean = json_match.group(1)
            try:
                qa_json = json.loads(res_clean)
            except json.JSONDecodeError:
                st.error("Failed to parse JSON after extraction. Please try again.")
                return
        else:
            st.error("Failed to locate JSON in the response. Please try again.")
            return

        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Agdasima');
            .custom-text-02 { font-family: 'Perpetua', sans-serif; font-size: 30px; color: #f9e79f; }
            </style>
            <p class="custom-text-02">Displaying the generated Q&A</p>
            """, unsafe_allow_html=True)

        # Define fixed option letters
        fixed_letters = ['A', 'B', 'C', 'D']

        if "questions" in qa_json and isinstance(qa_json["questions"], list):
            for q_data in qa_json["questions"]:
                if isinstance(q_data, dict):
                    question_text = q_data.get("question", "Question text missing")
                    options_data = q_data.get("options", {})
                    correct_options = q_data.get("correct_options", [])

                    st.subheader(question_text)

                    # Convert options to a list of texts
                    options_list = []
                    if isinstance(options_data, dict):
                        # Sort keys to ensure order; you can adjust ordering as needed.
                        for key in sorted(options_data.keys()):
                            options_list.append(options_data[key])
                    elif isinstance(options_data, list):
                        options_list = options_data
                    else:
                        st.warning("Options data is not in the expected format.")
                        continue

                    # Only proceed if we have exactly 4 options; otherwise warn.
                    if len(options_list) != 4:
                        st.warning("Expected 4 options but received a different number. Displaying available options.")
                    
                    # Determine which options are correct.
                    # If correct_options are already letters, convert them to uppercase.
                    if all(isinstance(x, str) and len(x.strip()) == 1 and x.strip().isalpha() for x in correct_options):
                        correct_letters = [x.strip().upper() for x in correct_options]
                    else:
                        # Otherwise, try matching based on option text.
                        correct_letters = []
                        for i, option in enumerate(options_list):
                            # If any correct option string (normalized) is found within the option text, mark it.
                            normalized_option = option.strip().lower()
                            if any(normalized_option == corr.strip().lower() for corr in correct_options):
                                correct_letters.append(fixed_letters[i])

                    # Display options with fixed letters.
                    for i, option in enumerate(options_list):
                        letter = fixed_letters[i] if i < len(fixed_letters) else chr(65+i)
                        option_text = option.strip()
                        option_display = f"{letter}. {option_text}"
                        if letter in correct_letters:
                            st.markdown(f"**:green[{option_display}]**")
                        else:
                            st.markdown(option_display)

                    if correct_letters:
                        st.markdown(f"**Correct Options:** :green[{', '.join(correct_letters)}]")
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
    # Header images
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
            <h1 class="custom-text-01">Q&A Generation using LLM</h1>
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
        '<div style="text-align: justify">Creating multiple-choice questions based on a given paragraph offers a multifaceted approach to learning. It not only deepens comprehension by distilling key concepts and main ideas but also engages learners actively with the material.</div>',
        unsafe_allow_html=True)
    st.write('')
    st.markdown(
        '<div style="text-align: justify">As learners compare their questions to model answers, they engage in self-assessment, identifying strengths and areas for improvement. This exercise mirrors assessment formats, aiding effective test preparation and knowledge retention.</div>',
        unsafe_allow_html=True)
    st.write('')
    st.markdown(
        '<div style="text-align: justify">This practice nurtures vocabulary enrichment and encourages the logical organization of information, empowering students to take charge of their learning journey.</div>',
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
