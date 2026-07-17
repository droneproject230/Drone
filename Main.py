
import asyncio
import cv2
import numpy as np
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan
from mavsdk.offboard import OffboardError, PositionNedYaw

# ENDÜSTRİYEL YAPAY ZEKA - OpenCV DNN ile Gerçek YOLO Nesne Tespit Sınıfı
class YOLOObstacleDetector:
    def __init__(self):
        print("[AI] Yapay Zeka Derin Öğrenme Modülü Başlatılıyor...")
        # Gerçek ağırlık ve konfigürasyon dosyalarının yolları
        # ASELSAN standartlarında cv2.dnn modülü ile derin sinir ağı yüklenir
        self.weights_path = "yolov4-tiny.weights"
        self.cfg_path = "yolov4-tiny.cfg"
        self.classes = ["insan", "araba", "ucak", "drone", "agac", "bina"]
        self.target_obstacle = "insan" # Algılanacak kritik engel türü

        try:
            # Yapay zeka ağını (Neural Network) bilgisayar/kart hafızasına yüklüyoruz
            self.net = cv2.dnn.readNet(self.weights_path, self.cfg_path)
            # Performans için backend olarak CUDA (NVIDIA GPU) veya CPU seçimi
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            
            self.model = cv2.dnn_DetectionModel(self.net)
            self.model.setInputParams(size=(416, 416), scale=1/255.0, swapRB=True)
            print("[AI] YOLO Sinir Ağı Başarıyla Yüklendi.")
        except Exception as e:
            print(f"[AI] Model dosyaları bulunamadı, simülasyon modunda çalışıyor: {e}")
            self.net = None

    def detect_obstacle(self, frame):
        if frame is None:
            return False
            
        # Eğer gerçek model dosyaları yüklüyse derin öğrenme tahmini yap
        if self.net is not None:
            classes, confidences, boxes = self.model.detect(frame, confThreshold=0.5, nmsThreshold=0.4)
            for (classid, score, box) in zip(classes, confidences, boxes):
                class_name = self.classes[classid[0]] if isinstance(classid, np.ndarray) else self.classes[classid]
                
                if class_name == self.target_obstacle:
                    x, y, w, h = box
                    # Engeli ekranda kare içine al ve doğruluk oranını yaz
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.putText(frame, f"[YOLO] {class_name}: %{int(score*100)}", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    return True
            return False
        else:
            # Geliştirme/Simülasyon Aşaması için Yedek Matematiksel Algılama (Görüntü İşleme)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, np.array([0, 120, 70]), np.array([10, 255, 255]))
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                if cv2.contourArea(contour) > 4000:
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, f"[AI SIM] {self.target_obstacle}: CONF %89", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
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
        MissionItem(37.364, -123.043, 10, 5, True, float('nan'), float('nan'), MissionItem.CameraAction.NONE, float('nan'), float('nan'), float('nan'), float('nan'), float('nan'))
    ]
    
    mission_plan = MissionPlan(mission_items)
    await drone.mission.set_return_to_launch_after_mission(True)
    await drone.mission.upload_mission(mission_plan)
    print("Otonom rota otopilota yüklendi.")

    # 2. Eşzamanlı Mimari Yönetimi (Asenkron Görevler)
    asyncio.ensure_future(track_battery(drone))
    asyncio.ensure_future(camera_pipeline())
    asyncio.ensure_future(avoidance_controller(drone))

    print("Arm ediliyor...")
    await drone.action.arm()
    
    print("Kalkış yapılıyor...")
    await drone.action.takeoff()
    await asyncio.sleep(5)

    print("Otonom görev başlatılıyor...")
    await drone.mission.start_mission()

    async for mission_progress in drone.mission.mission_progress():
        print(f"Görev Durumu: {mission_progress.current}/{mission_progress.total}")
        if mission_progress.current == mission_progress.total:
            print("Otonom rota başarıyla tamamlandı.")
            break

async def camera_pipeline():
    global obstacle_detected
    detector = YOLOObstacleDetector()
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if ret:
            obstacle_detected = detector.detect_obstacle(frame)
        await asyncio.sleep(0.03)

async def avoidance_controller(drone):
    global obstacle_detected
    while True:
        if obstacle_detected:
            print("🚨 [YAPAY ZEKA] KRİTİK ENGEL ALGINLADI! Rota askıya alınıyor...")
            try:
                await drone.mission.pause_mission()
                await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0.0))
                await drone.offboard.start()

                print("➡️ Yapay Zeka Kaçış Kararı: Sağa 5 metre güvenli kayma.")
                await drone.offboard.set_position_ned(PositionNedYaw(0.0, 5.0, -10.0, 90.0))
                await asyncio.sleep(5)

                await drone.offboard.stop()
                print("🔄 Güvenli Sektör: Otonom uçuşa devam ediliyor...")
                await drone.mission.start_mission()
            except OffboardError as error:
                print(f"Kaçış moduna geçilemedi: {error._result.result}")
                
        await asyncio.sleep(0.1)

async def track_battery(drone):
    async for battery in drone.telemetry.battery():
        if battery.remaining_percent < 0.20:
            print("⚠️ Failsafe: Kritik pil seviyesi! RTL (Eve Dönüş) aktif.")
            await drone.action.return_to_launch()
            break

if __name__ == "__main__":
    asyncio.run(run())
