"""
Warehouse Inventory Counter Application
Automatically counts products on shelves using YOLOv8 and OCR
E-commerce warehouses and retail automation solution
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pandas as pd
from detector import WarehouseDetector
from ocr_reader import OCRReader
import tempfile
import os


def main():
    st.set_page_config(
        page_title="Depo Envanter Sayımı",
        page_icon="📦",
        layout="wide"
    )

    st.title("📦 Otomatik Depo Envanter Sayımı")
    st.markdown("""
    ### Elle sayım yerine otomatik envanter
    Raf fotoğraflarından ürün tespiti ve sayımı yapın.
    **YOLOv8 + OCR** teknolojileriyle desteklenmektedir.
    """)

    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Ayarlar")
        confidence_threshold = st.slider(
            "Güven Eşiği (Confidence)",
            min_value=0.1,
            max_value=1.0,
            value=0.4,
            step=0.05,
            help="Tespit için minimum güven skoru"
        )

        enable_ocr = st.checkbox(
            "OCR'ı Etkinleştir",
            value=True,
            help="Ürün etiketlerini okumak için OCR'ı kullan"
        )

        show_labels = st.checkbox(
            "Etiketleri Göster",
            value=True,
            help="Tespit edilen nesnelerin etiketlerini göster"
        )

        st.markdown("---")
        st.markdown("""
        **Nasıl Kullanılır:**
        1. Depo rafı fotoğrafı yükleyin
        2. Ayarları yapılandırın
        3. Tespit Et butonuna tıklayın
        4. Sonuçları inceleyin ve indirin
        """)

    # Initialize detector and OCR
    @st.cache_resource
    def load_models():
        detector = WarehouseDetector(confidence_threshold=confidence_threshold)
        ocr_reader = OCRReader() if enable_ocr else None
        return detector, ocr_reader

    detector, ocr_reader = load_models()
    detector.confidence_threshold = confidence_threshold

    # File uploader
    uploaded_file = st.file_uploader(
        "Depo Rafı Fotoğrafını Yükleyin",
        type=["jpg", "jpeg", "png"],
        help="JPG, JPEG veya PNG formatında fotoğraf yükleyin"
    )

    if uploaded_file is not None:
        # Display original image
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📸 Orijinal Görüntü")
            image = Image.open(uploaded_file)
            st.image(image, use_container_width=True)

        # Save temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        # Detection button
        if st.button("🔍 Tespit Et ve Say", type="primary"):
            with st.spinner("Ürünler tespit ediliyor..."):
                # Run detection
                detections, annotated_image = detector.detect(tmp_path)

                # Run OCR if enabled
                if enable_ocr and ocr_reader and len(detections) > 0:
                    with st.spinner("Etiketler okunuyor..."):
                        detections = ocr_reader.read_labels(tmp_path, detections)

                # Display results
                with col2:
                    st.subheader("✅ Tespit Sonuçları")
                    if show_labels:
                        st.image(annotated_image, use_container_width=True)
                    else:
                        # Show image without annotations
                        st.image(image, use_container_width=True)

                # Count products
                st.markdown("---")
                st.subheader("📊 Envanter Raporu")

                if len(detections) > 0:
                    # Create summary
                    col_a, col_b, col_c = st.columns(3)

                    with col_a:
                        st.metric("Toplam Ürün", len(detections))

                    # Count by class
                    class_counts = {}
                    for det in detections:
                        class_name = det.get('class', 'unknown')
                        class_counts[class_name] = class_counts.get(class_name, 0) + 1

                    with col_b:
                        st.metric("Farklı Ürün Türü", len(class_counts))

                    with col_c:
                        avg_conf = np.mean([det['confidence'] for det in detections])
                        st.metric("Ortalama Güven", f"{avg_conf:.2%}")

                    # Detailed table
                    st.markdown("### Detaylı Ürün Listesi")

                    # Prepare data for table
                    table_data = []
                    for idx, det in enumerate(detections, 1):
                        row = {
                            "No": idx,
                            "Ürün Türü": det.get('class', 'N/A'),
                            "Güven Skoru": f"{det['confidence']:.2%}",
                            "Konum (x,y,w,h)": f"({det['box'][0]:.0f}, {det['box'][1]:.0f}, {det['box'][2]:.0f}, {det['box'][3]:.0f})"
                        }

                        if enable_ocr and 'ocr_text' in det:
                            row["Etiket Metni"] = det['ocr_text']

                        table_data.append(row)

                    df = pd.DataFrame(table_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)

                    # Category breakdown
                    st.markdown("### Kategoriye Göre Dağılım")
                    category_df = pd.DataFrame([
                        {"Ürün Türü": k, "Adet": v}
                        for k, v in sorted(class_counts.items(), key=lambda x: x[1], reverse=True)
                    ])

                    col_chart1, col_chart2 = st.columns([2, 1])

                    with col_chart1:
                        st.bar_chart(category_df.set_index("Ürün Türü"))

                    with col_chart2:
                        st.dataframe(category_df, use_container_width=True, hide_index=True)

                    # Download results
                    st.markdown("---")
                    st.markdown("### 💾 Sonuçları İndir")

                    col_dl1, col_dl2 = st.columns(2)

                    with col_dl1:
                        # CSV download
                        csv = df.to_csv(index=False).encode('utf-8-sig')
                        st.download_button(
                            label="📥 CSV İndir",
                            data=csv,
                            file_name="envanter_raporu.csv",
                            mime="text/csv"
                        )

                    with col_dl2:
                        # Save annotated image
                        if show_labels:
                            annotated_pil = Image.fromarray(cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB))
                            img_bytes = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                            annotated_pil.save(img_bytes.name, format='JPEG')
                            with open(img_bytes.name, 'rb') as f:
                                st.download_button(
                                    label="📥 İşaretli Görsel İndir",
                                    data=f.read(),
                                    file_name="isaretli_gorsel.jpg",
                                    mime="image/jpeg"
                                )
                            os.unlink(img_bytes.name)

                else:
                    st.warning("⚠️ Hiç ürün tespit edilemedi. Lütfen farklı bir fotoğraf deneyin veya güven eşiğini düşürün.")

        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    else:
        # Show example instructions
        st.info("""
        👈 Sol taraftaki **Ayarlar** panelinden yapılandırmaları değiştirebilirsiniz.

        📤 Yukarıdan bir depo rafı fotoğrafı yükleyerek başlayın.

        **İpuçları:**
        - İyi aydınlatılmış, net fotoğraflar kullanın
        - Ürünlerin net görünebildiğinden emin olun
        - Farklı açılardan çekilen fotoğraflar deneyin
        - Çok karmaşık raf yapıları için birden fazla fotoğraf kullanın
        """)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🤖 YOLOv8 + OCR ile desteklenmektedir |
        E-ticaret depoları ve perakende için otomatik envanter çözümü</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
