import streamlit as st
from pdf2image import convert_from_path
from PIL import Image
import os

# 페이지 설정
st.set_page_config(page_title="PDF to JPG Converter and Phraise App", layout="wide")

def main():
    st.title("앱 네비게이터")

    # 사이드바 네비게이션
    app_selection = st.sidebar.selectbox("어플 선택", ["PDF to JPG Converter", "Phraise App"], key="app_selection")

    if app_selection == "PDF to JPG Converter":
        pdf_to_jpg_converter()
    elif app_selection == "Phraise App":
        import phraise
        phraise.run_phraise_app()

# PDF to JPG 변환기
def pdf_to_jpg_converter():
    st.title("PDF to JPG Converter")

    uploaded_pdf = st.file_uploader("Choose a PDF file", type="pdf", key="uploaded_pdf")
    dpi = st.radio("Select DPI", (300, 600), index=0, key="dpi_selector")

    if 'image_paths' not in st.session_state:
        st.session_state.image_paths = []

    if 'split_image_paths' not in st.session_state:
        st.session_state.split_image_paths = []

    convert_button = st.button("Convert PDF to JPG", key="convert_button")
    split_button = st.button("Convert PDF to JPG Splitter", key="split_button")

    if convert_button and uploaded_pdf is not None:
        with open(uploaded_pdf.name, "wb") as f:
            f.write(uploaded_pdf.getbuffer())
        st.success(f"PDF uploaded: {uploaded_pdf.name}")
        try:
            st.session_state.image_paths = convert_pdf_to_jpg(uploaded_pdf.name, dpi)
            st.session_state.split_image_paths = []
            st.success("PDF has been converted to JPG")
        except Exception as e:
            st.error(f"Error during conversion: {e}")

    if split_button and uploaded_pdf is not None:
        with open(uploaded_pdf.name, "wb") as f:
            f.write(uploaded_pdf.getbuffer())
        st.success(f"PDF uploaded: {uploaded_pdf.name}")
        try:
            st.session_state.image_paths = []
            st.session_state.split_image_paths = []

            temp_image_paths = convert_pdf_to_jpg(uploaded_pdf.name, dpi)
            for image_path in temp_image_paths:
                left_path, right_path = split_jpg(image_path)
                st.session_state.split_image_paths.extend([left_path, right_path])
                os.remove(image_path)
            st.success("PDF has been converted to JPG and split")
        except Exception as e:
            st.error(f"Error during split conversion: {e}")

    # 다운로드 버튼 생성
    if st.session_state.image_paths or st.session_state.split_image_paths:
        st.subheader("Download Images")

    if st.session_state.image_paths:
        for image_path in st.session_state.image_paths:
            with open(image_path, "rb") as img_file:
                st.download_button(
                    label=f"Download {os.path.basename(image_path)}",
                    data=img_file,
                    file_name=os.path.basename(image_path),
                    mime="image/jpeg",
                    key=f"download_{image_path}"
                )

    if st.session_state.split_image_paths:
        for split_image_path in st.session_state.split_image_paths:
            with open(split_image_path, "rb") as img_file:
                st.download_button(
                    label=f"Download {os.path.basename(split_image_path)}",
                    data=img_file,
                    file_name=os.path.basename(split_image_path),
                    mime="image/jpeg",
                    key=f"download_{split_image_path}"
                )

    # 이미지 표시
    if st.session_state.image_paths:
        for image_path in st.session_state.image_paths:
            st.image(image_path, key=f"image_{image_path}")

    if st.session_state.split_image_paths:
        for split_image_path in st.session_state.split_image_paths:
            st.image(split_image_path, key=f"image_{split_image_path}")

def convert_pdf_to_jpg(pdf_file, dpi):
    try:
        images = convert_from_path(pdf_file, dpi=dpi)
    except Exception as e:
        st.error(f"Error converting PDF to images: {e}")
        return []

    image_paths = []
    base_name = os.path.splitext(os.path.basename(pdf_file))[0]
    for i, image in enumerate(images):
        image_path = f"{base_name}_{i+1}.jpg"
        image.save(image_path, 'JPEG')
        image_paths.append(image_path)
    return image_paths

def split_jpg(image_path):
    image = Image.open(image_path)
    width, height = image.size
    base_name = os.path.splitext(image_path)[0]
    left_path = f"{base_name}_left.jpg"
    right_path = f"{base_name}_right.jpg"
    left = image.crop((0, 0, width // 2, height))
    right = image.crop((width // 2, 0, width, height))
    left.save(left_path, 'JPEG')
    right.save(right_path, 'JPEG')
    return left_path, right_path

if __name__ == "__main__":
    main()
