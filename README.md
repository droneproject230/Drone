# Akıllı İHA Görev ve Yapay Zeka Tabanlı Engel Kaçınma Sistemi

Bu proje, **MAVSDK** ve **OpenCV** kullanarak geliştirilmiş, otonom bir İHA seyrüsefer ve karar mekanizması yazılımıdır. Simülatörler ve PX4 tabanlı otopilotlar üzerinde çalışacak şekilde tasarlanmıştır.

## 🚀 Özellikler

*   **Eşzamanlı Mimari (`asyncio`):** Telemetri takibi ve uçuş kontrolü birbirini engellemeden aynı anda çalışır.
*   **Dinamik Görev Takibi:** Görevin bitişini otopilottan gelen verilere göre otomatik algılar.
*   **Yapay Zeka Destekli Engel Kaçınma:** Kamera akışından anlık engel tespiti yapar ve otonom kaçış manevrası gerçekleştirir.
*   **Güvenlik Protokolü (Fail-Safe):** Pil seviyesini sürekli izler, kritik durumda otomatik eve dönüş (RTL) başlatır.

## 🛠️ Kurulum

```bash
pip install mavsdk opencv-python numpy
