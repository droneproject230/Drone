import asyncio
import cv2
import numpy as np
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan
from mavsdk.offboard import OffboardError, PositionNedYaw

# GELİŞMİŞ ASKERİ STANDART - Akıllı Kaçış ve Hedef Takip Sistemli Yapay Zeka
class AdvancedAIConfig:
    def __init__(self):
        print("[AI] Askeri Standart Yapay Zeka Görev Bilgisayarı Başlatılıyor...")
        self.classes = ["insan", "araba", "ucak", "target_drone", "agac", "bina"]
        self.target_class = "target_drone" # Kilitlenilecek ve kaçınılacak hedef
        self.frame_width = 640  # Kamera çözünürlük genişliği
        self.frame_height = 480 # Kamera çözünürlük yüksekliği

    def process_vision(self, frame):
        """
        Görüntü İşleme ve Yapay Zeka Algılama Hattı.
        Hem Hedef Takip (Tracking) için merkez sapmasını hesaplar 
        hem de Dinamik Kaçış (Avoidance) için yön ve büyüklük kararı verir.
        """
        if frame is None:
            return "NORMAL", 0, 0
            
        # Simülasyon ve Geliştirme için Gelişmiş Renk & Geometri Filtresi (YOLO Çıktısı Simülasyonu)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array([0, 120, 70]), np.array([10, 255, 255]))
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 3000: # Nesne algılandı
                x, y, w, h = cv2.boundingRect(contour)
                obj_center_x = x + (w // 2)
                screen_center_x = self.frame_width // 2
                
                # Ekranın merkezinden ne kadar saptığımızı buluyoruz (Hedef Takip İçin)
                error_x = obj_center_x - screen_center_x
                
                # ÖNEMLİ: Eğer nesne çok büyükse (Örn: Alan > 25000), bu yakında bir ENGELLİDİR -> KAÇIŞ tetiklenir
                if area > 25000:
                    # Engelin ekranın hangi tarafında olduğunu buluyoruz
                    yön = "SOLDA" if obj_center_x < screen_center_x else "SAĞDA"
                    
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 3)
                    cv2.putText(frame, f"[AI CRITICAL] CRASH RISK! Enemy: {yön}", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    return "CRITICAL_AVOID", error_x, yön
                
                # Eğer nesne uzaktaysa (Alan küçükse) -> TAKİP / KİLİTLENME tetiklenir
                else:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
                    cv2.line(frame, (screen_center_x, self.frame_height//2), (obj_center_x, y + h//2), (0, 255, 0), 2)
                    cv2.putText(frame, f"[AI LOCK-ON] Tracking: {self.target_class}", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                    return "TRACKING", error_x, None
                    
        return "NORMAL", 0, None

# Küresel Sistem Durum Değişkenleri
ai_state = "NORMAL"  # NORMAL, TRACKING, CRITICAL_AVOID
tracking_error_x = 0
obstacle_direction = None

async def run():
    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("İHA Sistemine bağlanılıyor...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("İHA Otopilotu başarıyla entegre oldu!")
            break

    # Otonom Rota Planlama
    mission_items = [
        MissionItem(37.363, -122.042, 10, 5, True, float('nan'), float('nan'), MissionItem.CameraAction.NONE, float('nan'), float('nan'), float('nan'), float('nan'), float('nan')),
        MissionItem(37.364, -122.042, 10, 5, True, float('nan'), float('nan'), MissionItem.CameraAction.NONE, float('nan'), float('nan'), float('nan'), float('nan'), float('nan'))
    ]
    mission_plan = MissionPlan(mission_items)
    await drone.mission.upload_mission(mission_plan)

    # İşlem Hatlarını Başlatma
    asyncio.ensure_future(camera_processing_pipeline())
    asyncio.ensure_future(ai_decision_core(drone))

    print("Arming...")
    await drone.action.arm()
    print("Takeoff...")
    await drone.action.takeoff()
    await asyncio.sleep(5)

    print("Ana Görev Başlatılıyor...")
    await drone.mission.start_mission()

    async for progress in drone.mission.mission_progress():
        if progress.current == progress.total:
            print("Görev tamamlandı.")
            break

async def camera_processing_pipeline():
    """ Kameradan canlı görüntü alıp yapay zeka işlemcisine gönderen asenkron fonksiyon """
    global ai_state, tracking_error_x, obstacle_direction
    ai_system = AdvancedAIConfig()
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, ai_system.frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, ai_system.frame_height)

    while True:
        ret, frame = cap.read()
        if ret:
            ai_state, tracking_error_x, obstacle_direction = ai_system.process_vision(frame)
        await asyncio.sleep(0.03)

async def ai_decision_core(drone):
    """ Yapay Zekanın Kararlarına Göre İHA'yı Havada Yöneten Ana Karar Mekanizması """
    global ai_state, tracking_error_x, obstacle_direction
    
    in_offboard = False

    while True:
        # DURUM 1: KRİTİK ENGEL - DİNAMİK KAÇIŞ
        if ai_state == "CRITICAL_AVOID":
            print(f"🚨 [YAPAY ZEKA KARARI] Çarpışma Riski! Engel {obstacle_direction} tarafında tespit edildi!")
            if not in_offboard:
                await drone.mission.pause_mission()
                await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0.0))
                await drone.offboard.start()
                in_offboard = True

            # Dinamik Karar: Engel soldaysa SAĞA (5m), sağdaysa SOLA (-5m) kaç!
            escape_y = 5.0 if obstacle_direction == "SOLDA" else -5.0
            print(f"➡️ Manevra Başlatıldı: Yön ekseninde {escape_y} metre kayma yapılıyor.")
            await drone.offboard.set_position_ned(PositionNedYaw(0.0, escape_y, -10.0, 0.0))
            await asyncio.sleep(4) # Kaçış süresi
            
        # DURUM 2: UZAKTAKİ HEDEF - KİLİTLENME VE HEDEF TAKİBİ (LOCK-ON)
        elif ai_state == "TRACKING":
            print(f"🎯 [YAPAY ZEKA KİLİTLENME] Hedef takip ediliyor. Merkez Sapması: {tracking_error_x}")
            if not in_offboard:
                await drone.mission.pause_mission()
                await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0.0))
                await drone.offboard.start()
                in_offboard = True

            # Sapma değerine göre İHA'nın kendi ekseninde (Yaw) dönerek hedefi ortalamasını sağlıyoruz
            yaw_rate = 5.0 if tracking_error_x > 0 else -5.0
            # Hedefe doğru yavaşça yaklaşma (X ekseninde 1 m/s hız)
            await drone.offboard.set_position_ned(PositionNedYaw(1.0, 0.0, -10.0, yaw_rate))

        # DURUM 3: HER ŞEY NORMAL - OTONOM ROTA
        elif ai_state == "NORMAL" and in_offboard:
            print("🔄 Güvenli Durum: Yapay zeka tehdit veya hedef algılamadı. Rotaya dönülüyor.")
            await drone.offboard.stop()
            in_offboard = False
            await drone.mission.start_mission()

        await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(run())
