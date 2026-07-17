import asyncio
import cv2
import numpy as np
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan
from mavsdk.offboard import OffboardError, PositionNedYaw

# Yapay Zeka Engel Algılama Sınıfı (Örnek Renk Filtreleme Tabanlı)
class ObstacleDetector:
    def __init__(self):
        # Örnek olarak kırmızı nesneleri engel kabul ediyoruz
        self.lower_red = np.array([0, 120, 70])
        self.upper_red = np.array([10, 255, 255])

    def detect_obstacle(self, frame):
        if frame is None:
            return False
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2. some_mask = cv2.inRange(hsv, self.lower_red, self.upper_red)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            if cv2.contourArea(contour) > 5000: # Büyük bir nesne varsa engeldir
                return True
        return False

# Küresel Engel Durumu Değişkeni
obstacle_detected = False

async def run():
    global obstacle_detected
    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("İHA'ya bağlanılıyor...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("İHA başarıyla bağlandı!")
            break

    # 1. Görev Noktalarının Belirlenmesi
    mission_items = [
        MissionItem(37.363, -122.042, 10, 5, True, float('nan'), float('nan'), MissionItem.CameraAction.NONE, float('nan'), float('nan'), float('nan'), float('nan'), float('nan')),
        MissionItem(37.364, -122.042, 10, 5, True, float('nan'), float('nan'), MissionItem.CameraAction.NONE, float('nan'), float('nan'), float('nan'), float('nan'), float('nan')),
        MissionItem(37.364, -122.043, 10, 5, True, float('nan'), float('nan'), MissionItem.CameraAction.NONE, float('nan'), float('nan'), float('nan'), float('nan'), float('nan'))
    ]
    
    mission_plan = MissionPlan(mission_items)
    await drone.mission.set_return_to_launch_after_mission(True)
    await drone.mission.upload_mission(mission_plan)
    print("Otonom rota otopilota yüklendi.")

    # 2. Asenkron Arka Plan Görevleri
    asyncio.ensure_future(track_battery(drone))
    asyncio.ensure_future(camera_pipeline())
    asyncio.ensure_future(avoidance_controller(drone))

    # 3. Kalkış ve Görevi Başlatma
    print("Arm ediliyor...")
    await drone.action.arm()
    
    print("Kalkış yapılıyor...")
    await drone.action.takeoff()
    await asyncio.sleep(5)

    print("Otonom görev başlatılıyor...")
    await drone.mission.start_mission()

    # Görev ilerlemesini takip etme
    async for mission_progress in drone.mission.mission_progress():
        print(f"Görev Durumu: {mission_progress.current}/{mission_progress.total}")
        if mission_progress.current == mission_progress.total:
            print("Otonom rota başarıyla tamamlandı.")
            break

# Kamera Görüntü İşleme Hattı
async def camera_pipeline():
    global obstacle_detected
    detector = ObstacleDetector()
    cap = cv2.VideoCapture(0) # 0 numaralı kamera (Simülasyonda kamera akışı)

    while True:
        ret, frame = cap.read()
        if ret:
            obstacle_detected = detector.detect_obstacle(frame)
        await asyncio.sleep(0.03) # ~30 FPS hızında çalış

# Engel Kaçınma ve Mod Yönetim Motoru
async def avoidance_controller(drone):
    global obstacle_detected
    while True:
        if obstacle_detected:
            print("🚨 ENGEL TESPİT EDİLDİ! Otonom görev durduruluyor, kaçış manevrasına geçiliyor...")
            try:
                await drone.mission.pause_mission()
                # Offboard (Dışarıdan Kontrol) modunu başlat
                await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0.0))
                await drone.offboard.start()

                # Sağa doğru 5 metre kaçış manevrası
                print("➡️ Manevra yapılıyor: Sağa 5 metre kayma.")
                await drone.offboard.set_position_ned(PositionNedYaw(0.0, 5.0, -10.0, 90.0))
                await asyncio.sleep(5)

                # Engel ortadan kalktıysa göreve geri dön
                await drone.offboard.stop()
                print("🔄 Engel aşıldı. Otonom göreve kalındığı yerden devam ediliyor...")
                await drone.mission.start_mission()
            except OffboardError as error:
                print(f"Kaçış moduna geçilemedi: {error._result.result}")
                
        await asyncio.sleep(0.1)

# Fail-Safe: Pil Seviyesi Takip Sistemi
async def track_battery(drone):
    async for battery in drone.telemetry.battery():
        if battery.remaining_percent < 0.20: # %20'nin altına düşerse
            print("⚠️ KRİTİK PİL SEVİYESİ! Otomatik Eve Dönüş (RTL) tetiklendi.")
            await drone.action.return_to_launch()
            break

if __name__ == "__main__":
    asyncio.run(run())
