import streamlit as st
import openai
import os
import time

# Thiết lập API key của OpenAI
OPENAI_API_KEY = 'sk-proj-D0bqBJNuu5C6Lu7tQ7tRT3BlbkFJCdJk6bIpuXag34onwDNf'

if not OPENAI_API_KEY:
    st.error("API key for OpenAI is not set. Please set the OPENAI_API_KEY environment variable.")
else:
    openai.api_key = OPENAI_API_KEY

    def generate_image_prompts(story_description):
        response = openai.ChatCompletion.create(
            model="gpt-4o-2024-05-13",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Generate detailed and realistic image prompts based on this story description: {story_description}"}
            ],
            max_tokens=1000
        )
        prompts = response['choices'][0]['message']['content'].strip().split('\n')
        # Lọc bỏ các dòng trống
        prompts = [prompt for prompt in prompts if prompt.strip()]
        return prompts

    def generate_image(prompt, retry_count=3, delay=5):
        for attempt in range(retry_count):
            try:
                
                detailed_prompt = f"{prompt},highly detailed, high quality, diverse shooting angles, no text, no words, safe content, sketch styles"
                response = openai.Image.create(
                    model="dall-e-3",  
                    prompt=detailed_prompt,
                    n=1,
                    size="1024x1024"
                )
                image_url = response['data'][0]['url']
                return image_url
            except openai.error.APIError as e:
                if attempt < retry_count - 1:
                    time.sleep(delay)
                else:
                    st.error(f"Failed to generate image after {retry_count} attempts: {e}")
                    return None

    st.title("Kịch Bản Thành Hình Ảnh")

    story_description = st.text_area("Nhập kịch bản của bạn ở đây:", height=400)

    if st.button("Tạo Hình Ảnh"):
        if story_description:
            st.write("Đang tạo các prompt...")
            prompts = generate_image_prompts(story_description)
            st.write("Các prompt đã được tạo:")
            for i, prompt in enumerate(prompts, 1):
                st.write(f"Prompt {i}: {prompt}")

            st.write("Đang tạo các hình ảnh...")

            images = []
            context = ""  # Duy trì ngữ cảnh xuyên suốt

            for i, prompt in enumerate(prompts, 1):
                full_prompt = f"{context}\n{prompt}"
                image_url = generate_image(full_prompt)
                if image_url:
                    images.append(image_url)
                    context = f"Image {i}: {prompt}"  # Cập nhật ngữ cảnh với nội dung của hình ảnh vừa tạo

            for i, image_url in enumerate(images, 1):
                st.image(image_url, caption=f"Hình ảnh {i}")
        else:
            st.warning("Vui lòng nhập kịch bản trước khi tạo hình ảnh.")
