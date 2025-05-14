import streamlit as st
import streamlit.components.v1 as components
import base64
from PIL import Image
import io
import tempfile
import requests
import replicate
import os

# API 키 가져오기
replicate_api_token = st.secrets.get("REPLICATE_API_TOKEN", "")
api_key_1 = st.secrets.get("API_KEY_1", "")
api_key_2 = st.secrets.get("API_KEY_2", "")

# API 키 확인
if not replicate_api_token:
    st.error("REPLICATE_API_TOKEN이 설정되지 않았습니다. Streamlit Cloud의 Secrets 설정을 확인하세요.")
if not api_key_1:
    st.error("API_KEY_1이 설정되지 않았습니다. Streamlit Cloud의 Secrets 설정을 확인하세요.")
if not api_key_2:
    st.error("API_KEY_2가 설정되지 않았습니다. Streamlit Cloud의 Secrets 설정을 확인하세요.")

# 환경 변수 설정
os.environ["REPLICATE_API_TOKEN"] = replicate_api_token

# 페이지 설정
st.set_page_config(
    page_title="영상/배너 생성",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)
# 로고 이미지 표시
try:
    logo_image = Image.open("assets/logo.png")
    # 로고를 왼쪽 상단에 배치
    st.markdown(
        """
        <style>
        .logo-container {
            position: absolute;
            top: 0;
            left: 0;
            padding: 10px;
            z-index: 1000;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="logo-container">',
        unsafe_allow_html=True
    )
    st.image(logo_image, width=200)
    st.markdown('</div>', unsafe_allow_html=True)
except Exception as e:
    st.write(f"로고 이미지를 불러오는 중 오류가 발생했습니다: {str(e)}")

# CSS 스타일 적용
st.markdown("""
<style>
    body {
        font-family: 'Inter', sans-serif;
        background-color: #0e1117;
        color: #fff;
    }
    .main {
        background-color: #0e1117;
        color: #fff;
    }
    .stApp {
        max-width: 100%;
        padding: 0;
    }
    h1, h2, h3 {
        color: #fff;
        font-weight: 600;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 0.25rem;
        padding: 0.5rem 1rem;
        font-weight: 600;
        width: 100%;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #ff2b2b;
    }
    .header {
        margin-bottom: 2rem;
        text-align: center;
    }
    .subheader {
        color: #a0aec0;
        font-size: 1.2rem;
        margin-top: -1rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    .tab-content {
        background-color: #1e1e24;
        border-radius: 0.5rem;
        padding: 2rem;
        margin-top: 1rem;
    }
    .footer-text {
        text-align: center;
        margin-top: 2rem;
        font-size: 0.8rem;
        color: #a0aec0;
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.markdown("<h1 class='header'>영상/배너 생성 도구</h1>", unsafe_allow_html=True)
st.markdown("<p class='subheader'>텍스트와 이미지를 입력하여 영상/배너를 생성하세요</p>", unsafe_allow_html=True)

# 함수: 이미지를 base64로 인코딩
def encode_image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

# 함수: 영상 생성
def generate_video(text, image, menu, aspect_ratio):
    try:
        # 이미지를 base64로 인코딩
        image_base64 = encode_image_to_base64(image)
        
        # Replicate API 호출
        input = {
            "text": text,
            "image": image_base64,
            "menu": menu,
            "aspect_ratio": aspect_ratio,
            "api_key_1": api_key_1,
            "api_key_2": api_key_2
        }
        
        output = replicate.run(
            "smoretalk/agent-demo:da3364a3b51d323f5969b9f0d08422765f78b3292fa438b3ca6b140c42b5b23d",
            input=input
        )
        
        # FileOutput 객체에서 URL 추출
        if isinstance(output, list) and len(output) > 0:
            video_url = output[0].url if hasattr(output[0], 'url') else str(output[0])
        else:
            video_url = output.url if hasattr(output, 'url') else str(output)
            
        return video_url
    
    except Exception as e:
        st.error(f"영상 생성 중 오류 발생: {str(e)}")
        return None

# 메인 컨텐츠
st.markdown("<h3 style='margin-bottom: 1rem;'>영상/배너 생성</h3>", unsafe_allow_html=True)

# 텍스트 입력
text_input = st.text_area("텍스트 입력", "", height=100, placeholder="A woman is holding case.")

# 이미지 업로드
uploaded_image = st.file_uploader("이미지 업로드", type=["jpg", "jpeg", "png", "webp"])

# 메뉴 선택
menu_option = st.selectbox(
    "메뉴 선택",
    ["Short video", "Banner"],
    index=0
)

# 비율 선택
aspect_ratio_option = st.selectbox(
    "비율 선택",
    ["vertical", "square", "horizontal"],
    index=0
)

# 생성 버튼
if st.button("생성 시작", use_container_width=True):
    if uploaded_image is None:
        st.warning("이미지를 업로드해주세요.")
    else:
        # 생성 중 메시지 표시
        status_placeholder = st.empty()
        status_placeholder.info("생성이 시작되었습니다. 생성에는 몇 분 정도 소요될 수 있습니다. 생성이 완료될 때까지 기다려주세요.")
        
        with st.spinner("생성 중..."):
            # 이미지 로드
            image = Image.open(uploaded_image)
            
            # 생성
            result_url = generate_video(
                text=text_input,
                image=image,
                menu=menu_option,
                aspect_ratio=aspect_ratio_option
            )
            
            if result_url:
                # 생성 중 메시지 제거
                status_placeholder.empty()
                st.success("생성이 완료되었습니다!")
                
                try:
                    # 결과 데이터 다운로드
                    response = requests.get(result_url)
                    if response.status_code == 200:
                        result_data = response.content
                        
                        if menu_option == "Banner":
                            # 배너 이미지 표시
                            st.image(result_data, width=200)
                            
                            # 다운로드 버튼 (상태 유지)
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                st.download_button(
                                    label="다운로드",
                                    data=result_data,
                                    file_name="generated_banner.png",
                                    mime="image/png",
                                    use_container_width=True,
                                    key="download_banner"
                                )
                        else:
                            # 영상 표시 (HTML/CSS로 크기 조절)
                            st.markdown("""
                            <style>
                            .video-container {
                                width: 200px;
                                margin: 0 auto;
                            }
                            .video-container video {
                                width: 100%;
                                height: auto;
                            }
                            </style>
                            <div class="video-container">
                            """, unsafe_allow_html=True)
                            st.video(result_data)
                            st.markdown("</div>", unsafe_allow_html=True)
                            
                            # 다운로드 버튼 (상태 유지)
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                st.download_button(
                                    label="다운로드",
                                    data=result_data,
                                    file_name="generated_video.mp4",
                                    mime="video/mp4",
                                    use_container_width=True,
                                    key="download_video"
                                )
                    else:
                        st.error(f"다운로드 실패 (상태 코드: {response.status_code})")
                        st.error("URL을 직접 확인해보세요:")
                        st.code(result_url)
                except Exception as e:
                    st.error(f"표시 중 오류가 발생했습니다: {str(e)}")
                    st.error("URL을 직접 확인해보세요:")
                    st.code(result_url)
