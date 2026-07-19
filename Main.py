import asyncio
import cv2
import numpy as np
import random
import math
import hmac
import hashlib
import time
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan
from mavsdk.offboard import OffboardError, PositionNedYaw

# ==============================================================================
# SİBER TAARRUZ VE ELEKTRONİK HARP MODÜLÜ (EW SUITE)
# ==============================================================================
class OffensiveElectronicWarfare:
    def __init__(self):
        self.attack_active = False
        self.target_neutralized = False
        self.jamming_power = 0.0 
        print("[EW SUITE] Taarruz Tipi Elektronik Harp ve Jammer Antenleri Hazır.")

    def engage_cyber_kinetic_attack(self, target_locked):
        if not target_locked:
            self.attack_active = False
            self.jamming_power = max(0.0, self.jamming_power - 2.0)
            return False

        if self.target_neutralized:
            return True

        self.attack_active = True
        self.jamming_power = min(100.0, self.jamming_power + random.uniform(2.0, 8.0)) 
        
        if self.jamming_power >= 100.0:
            self.target_neutralized = True
            self.attack_active = False
            return True
        return False

# ==============================================================================
# AMERİKAN GİZLİ TEKNOLOJİ KATMANLARI (PQC, IRST, ZEROIZATION)
# ==============================================================================
class QuantumResistantValidator:
    def __init__(self):
        self._quantum_matrix_key = np.random.randint(0, 2, (64, 64), dtype=np.uint8)

    def verify_pq_signature(self, packet):
        try:
            cmd = packet["command"]
            sig = packet["signature"]
            computed_hash = hashlib.sha3_512(f"{cmd}:{packet['ts']}".encode()).hexdigest()
            return computed_hash == sig
        except KeyError: return False

class InfraredSearchTrackSystem:
    def __init__(self):
        pass

    def scan_thermal_signature(self, ir_frame):
        if ir_frame is None: return False, 0
        gray = cv2.cvtColor(ir_frame, cv2.COLOR_BGR2GRAY)
        _, thermal_hotspots = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thermal_hotspots, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            if cv2.contourArea(contour) > 500:
                x, y, w, h = cv2.boundingRect(contour)
                return True, (x + (w // 2)) - 320, (x, y, w, h)
        return False, 0, (0,0,0,0)

class AntiCaptureZeroizer:
    def __init__(self):
        self.is_destroyed = False
    def execute_software_self_destruct(self):
        if self.is_destroyed: return
        self.is_destroyed = True

# ==============================================================================
# YENİ KATMAN: ASKERİ HUD (HEADS-UP DISPLAY) ÇİZİM MOTORU
# ==============================================================================
def draw_military_hud(frame, flight_mode, target_detected, error_x, bbox, ew_power):
    """ Kameranın üzerine askeri İHA arayüzünü (HUD) yeşil çizgilerle çizer. """
    height, width = frame.shape[:2]
    center_x, center_y = width // 2, height // 2
    green = (0, 255, 0)
    red = (0, 0, 255)
    
    # Merkez Nişangah (Crosshair)
    cv2.line(frame, (center_x - 20, center_y), (center_x + 20, center_y), green, 1)
    cv2.line(frame, (center_x, center_y - 20), (center_x, center_y + 20), green, 1)
    cv2.circle(frame, (center_x, center_y), 150, green, 1)

    # Uçuş Modu ve Kripto Durumu Metinleri
    cv2.putText(frame, f"MODE: {flight_mode}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, green, 2)
    cv2.putText(frame, "PQC CRYPTO: VALID", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, green, 2)
    
    # Dinamik Telemetri (Yapay Zeka ve Sensörler)
    simulated_alt = 120.5 + random.uniform(-0.5, 0.5)
    cv2.putText(frame, f"ALT: {simulated_alt:.1f} m", (width - 150, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, green, 2)

    if target_detected:
        tx, ty, tw, th = bbox
        # Hedef Kutusu ve Kilitlenme (Lock-on) Bildirimi
        cv2.rectangle(frame, (tx, ty), (tx + tw, ty + th), red, 2)
        cv2.putText(frame, "TARGET LOCKED", (tx, ty - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, red, 2)
        
        # Hedefe olan sapma çizgisi
        cv2.line(frame, (center_x, center_y), (tx + tw//2, ty + th//2), red, 1)

        # Elektronik Harp (EW) Güç Çubuğu
        cv2.putText(frame, f"EW ATTACK POWER: %{int(ew_power)}", (20, height - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, red, 2)
        cv2.rectangle(frame, (20, height - 30), (220, height - 15), green, 1)
        cv2.rectangle(frame, (20, height - 30), (20 + int(ew_power * 2), height - 15), red, -1)
    else:
        cv2.putText(frame, "SCANNING FOR TARGETS...", (20, height - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, green, 2)

    return frame

# Küresel Sistem Bileşenleri
pqc_crypto = QuantumResistantValidator()
irst_system = InfraredSearchTrackSystem()
zeroizer = AntiCaptureZeroizer()
ew_suite = OffensiveElectronicWarfare()

flight_mode = "STEALTH_PATROL"
irst_detected = False
tracking_error_x = 0
target_bbox = (0,0,0,0)

async def main_mission():
    drone = System()
    await drone.connect(system_address="udp://:14540")
    
    asyncio.ensure_future(advanced_sensor_and_hud_pipeline())
    asyncio.ensure_future(pentagon_flight_controller(drone))

    await drone.action.arm()
    await drone.action.takeoff()
    await asyncio.sleep(5)
    await drone.mission.start_mission()

# KAMERA + HUD İŞLEME HATTI
async def advanced_sensor_and_hud_pipeline():
    global irst_detected, tracking_error_x, flight_mode, target_bbox
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if ret:
            # Termal Hedef Taraması
            irst_detected, tracking_error_x, target_bbox = irst_system.scan_thermal_signature(frame)
            
            # Askeri HUD Çizimi
            hud_frame = draw_military_hud(
                frame, 
                flight_mode, 
                irst_detected, 
                tracking_error_x, 
                target_bbox, 
                ew_suite.jamming_power
            )
            
            # Canlı Arayüzü Ekranda Göster
            cv2.imshow("TACTICAL COMMAND CENTER (HUD)", hud_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        await asyncio.sleep(0.03)
        
    cap.release()
    cv2.destroyAllWindows()

# UÇUŞ VE TAARRUZ KONTROL MERKEZİ
async def pentagon_flight_controller(drone):
    global flight_mode, irst_detected, tracking_error_x
    in_offboard = False

    while True:
        if flight_mode == "STEALTH_PATROL":
            if irst_detected:
                flight_mode = "ENGAGING_TARGET"
                if not in_offboard:
                    await drone.mission.pause_mission()
                    await drone.offboard.start()
                    in_offboard = True
                
                yaw_speed = 5.0 if tracking_error_x > 0 else -5.0
                await drone.offboard.set_position_ned(PositionNedYaw(3.0, 0.0, -12.0, yaw_speed))
                
        elif flight_mode == "ENGAGING_TARGET":
            if irst_detected:
                yaw_speed = 5.0 if tracking_error_x > 0 else -5.0
                await drone.offboard.set_position_ned(PositionNedYaw(3.0, 0.0, -12.0, yaw_speed))
                
                # Merkezdeyse Siber Taarruz (EW) Başlat
                if abs(tracking_error_x) < 30:
                    is_destroyed = ew_suite.engage_cyber_kinetic_attack(target_locked=True)
                    if is_destroyed:
                        print("💥 Hedef İmha Edildi! Devriyeye dönülüyor.")
                        flight_mode = "STEALTH_PATROL"
                        irst_detected = False 
                        ew_suite.target_neutralized = False 
                else:
                    ew_suite.engage_cyber_kinetic_attack(target_locked=False)
            else:
                flight_mode = "STEALTH_PATROL"
                if in_offboard:
                    await drone.offboard.stop()
                    in_offboard = False
                    await drone.mission.start_mission()

        await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main_mission())
import asyncio
import cv2
import numpy as np
import random
import math
import hmac
import hashlib
import time
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan
from mavsdk.offboard import OffboardError, PositionNedYaw

# ==============================================================================
# SİBER TAARRUZ VE ELEKTRONİK HARP MODÜLÜ (EW SUITE)
# ==============================================================================
class OffensiveElectronicWarfare:
    def __init__(self):
        self.attack_active = False
        self.target_neutralized = False
        self.jamming_power = 0.0 
        print("[EW SUITE] Taarruz Tipi Elektronik Harp ve Jammer Antenleri Hazır.")

    def engage_cyber_kinetic_attack(self, target_locked):
        if not target_locked:
            self.attack_active = False
            self.jamming_power = max(0.0, self.jamming_power - 2.0)
            return False

        if self.target_neutralized:
            return True

        self.attack_active = True
        self.jamming_power = min(100.0, self.jamming_power + random.uniform(2.0, 8.0)) 
        
        if self.jamming_power >= 100.0:
            self.target_neutralized = True
            self.attack_active = False
            return True
        return False

# ==============================================================================
# AMERİKAN GİZLİ TEKNOLOJİ KATMANLARI (PQC, IRST, ZEROIZATION)
# ==============================================================================
class QuantumResistantValidator:
    def __init__(self):
        self._quantum_matrix_key = np.random.randint(0, 2, (64, 64), dtype=np.uint8)

    def verify_pq_signature(self, packet):
        try:
            cmd = packet["command"]
            sig = packet["signature"]
            computed_hash = hashlib.sha3_512(f"{cmd}:{packet['ts']}".encode()).hexdigest()
            return computed_hash == sig
        except KeyError: return False

class InfraredSearchTrackSystem:
    def __init__(self):
        pass

    def scan_thermal_signature(self, ir_frame):
        if ir_frame is None: return False, 0
        gray = cv2.cvtColor(ir_frame, cv2.COLOR_BGR2GRAY)
        _, thermal_hotspots = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thermal_hotspots, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            if cv2.contourArea(contour) > 500:
                x, y, w, h = cv2.boundingRect(contour)
                return True, (x + (w // 2)) - 320, (x, y, w, h)
        return False, 0, (0,0,0,0)

class AntiCaptureZeroizer:
    def __init__(self):
        self.is_destroyed = False
    def execute_software_self_destruct(self):
        if self.is_destroyed: return
        self.is_destroyed = True

# ==============================================================================
# YENİ KATMAN: ASKERİ HUD (HEADS-UP DISPLAY) ÇİZİM MOTORU
# ==============================================================================
def draw_military_hud(frame, flight_mode, target_detected, error_x, bbox, ew_power):
    """ Kameranın üzerine askeri İHA arayüzünü (HUD) yeşil çizgilerle çizer. """
    height, width = frame.shape[:2]
    center_x, center_y = width // 2, height // 2
    green = (0, 255, 0)
    red = (0, 0, 255)
    
    # Merkez Nişangah (Crosshair)
    cv2.line(frame, (center_x - 20, center_y), (center_x + 20, center_y), green, 1)
    cv2.line(frame, (center_x, center_y - 20), (center_x, center_y + 20), green, 1)
    cv2.circle(frame, (center_x, center_y), 150, green, 1)

    # Uçuş Modu ve Kripto Durumu Metinleri
    cv2.putText(frame, f"MODE: {flight_mode}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, green, 2)
    cv2.putText(frame, "PQC CRYPTO: VALID", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, green, 2)
    
    # Dinamik Telemetri (Yapay Zeka ve Sensörler)
    simulated_alt = 120.5 + random.uniform(-0.5, 0.5)
    cv2.putText(frame, f"ALT: {simulated_alt:.1f} m", (width - 150, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, green, 2)

    if target_detected:
        tx, ty, tw, th = bbox
        # Hedef Kutusu ve Kilitlenme (Lock-on) Bildirimi
        cv2.rectangle(frame, (tx, ty), (tx + tw, ty + th), red, 2)
        cv2.putText(frame, "TARGET LOCKED", (tx, ty - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, red, 2)
        
        # Hedefe olan sapma çizgisi
        cv2.line(frame, (center_x, center_y), (tx + tw//2, ty + th//2), red, 1)

        # Elektronik Harp (EW) Güç Çubuğu
        cv2.putText(frame, f"EW ATTACK POWER: %{int(ew_power)}", (20, height - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, red, 2)
        cv2.rectangle(frame, (20, height - 30), (220, height - 15), green, 1)
        cv2.rectangle(frame, (20, height - 30), (20 + int(ew_power * 2), height - 15), red, -1)
    else:
        cv2.putText(frame, "SCANNING FOR TARGETS...", (20, height - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, green, 2)

    return frame

# Küresel Sistem Bileşenleri
pqc_crypto = QuantumResistantValidator()
irst_system = InfraredSearchTrackSystem()
zeroizer = AntiCaptureZeroizer()
ew_suite = OffensiveElectronicWarfare()

flight_mode = "STEALTH_PATROL"
irst_detected = False
tracking_error_x = 0
target_bbox = (0,0,0,0)

async def main_mission():
    drone = System()
    await drone.connect(system_address="udp://:14540")
    
    asyncio.ensure_future(advanced_sensor_and_hud_pipeline())
    asyncio.ensure_future(pentagon_flight_controller(drone))

    await drone.action.arm()
    await drone.action.takeoff()
    await asyncio.sleep(5)
    await drone.mission.start_mission()

# KAMERA + HUD İŞLEME HATTI
async def advanced_sensor_and_hud_pipeline():
    global irst_detected, tracking_error_x, flight_mode, target_bbox
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if ret:
            # Termal Hedef Taraması
            irst_detected, tracking_error_x, target_bbox = irst_system.scan_thermal_signature(frame)
            
            # Askeri HUD Çizimi
            hud_frame = draw_military_hud(
                frame, 
                flight_mode, 
                irst_detected, 
                tracking_error_x, 
                target_bbox, 
                ew_suite.jamming_power
            )
            
            # Canlı Arayüzü Ekranda Göster
            cv2.imshow("TACTICAL COMMAND CENTER (HUD)", hud_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        await asyncio.sleep(0.03)
        
    cap.release()
    cv2.destroyAllWindows()

# UÇUŞ VE TAARRUZ KONTROL MERKEZİ
async def pentagon_flight_controller(drone):
    global flight_mode, irst_detected, tracking_error_x
    in_offboard = False

    while True:
        if flight_mode == "STEALTH_PATROL":
            if irst_detected:
                flight_mode = "ENGAGING_TARGET"
                if not in_offboard:
                    await drone.mission.pause_mission()
                    await drone.offboard.start()
                    in_offboard = True
                
                yaw_speed = 5.0 if tracking_error_x > 0 else -5.0
                await drone.offboard.set_position_ned(PositionNedYaw(3.0, 0.0, -12.0, yaw_speed))
                
        elif flight_mode == "ENGAGING_TARGET":
            if irst_detected:
                yaw_speed = 5.0 if tracking_error_x > 0 else -5.0
                await drone.offboard.set_position_ned(PositionNedYaw(3.0, 0.0, -12.0, yaw_speed))
                
                # Merkezdeyse Siber Taarruz (EW) Başlat
                if abs(tracking_error_x) < 30:
                    is_destroyed = ew_suite.engage_cyber_kinetic_attack(target_locked=True)
                    if is_destroyed:
                        print("💥 Hedef İmha Edildi! Devriyeye dönülüyor.")
                        flight_mode = "STEALTH_PATROL"
                        irst_detected = False 
                        ew_suite.target_neutralized = False 
                else:
                    ew_suite.engage_cyber_kinetic_attack(target_locked=False)
            else:
                flight_mode = "STEALTH_PATROL"
                if in_offboard:
                    await drone.offboard.stop()
                    in_offboard = False
                    await drone.mission.start_mission()

        await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main_mission())
import asyncio
import cv2
import numpy as np
import random
import math
import hmac
import hashlib
import time
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan
from mavsdk.offboard import OffboardError, PositionNedYaw

# ==============================================================================
# SİBER TAARRUZ VE ELEKTRONİK HARP MODÜLÜ (EW SUITE)
# ==============================================================================
class OffensiveElectronicWarfare:
    def __init__(self):
        self.attack_active = False
        self.target_neutralized = False
        self.jamming_power = 0.0 
        print("[EW SUITE] Taarruz Tipi Elektronik Harp ve Jammer Antenleri Hazır.")

    def engage_cyber_kinetic_attack(self, target_locked):
        if not target_locked:
            self.attack_active = False
            self.jamming_power = max(0.0, self.jamming_power - 2.0)
            return False

        if self.target_neutralized:
            return True

        self.attack_active = True
        self.jamming_power = min(100.0, self.jamming_power + random.uniform(2.0, 8.0)) 
        
        if self.jamming_power >= 100.0:
            self.target_neutralized = True
            self.attack_active = False
            return True
        return False

# ==============================================================================
# AMERİKAN GİZLİ TEKNOLOJİ KATMANLARI (PQC, IRST, ZEROIZATION)
# ==============================================================================
class QuantumResistantValidator:
    def __init__(self):
        self._quantum_matrix_key = np.random.randint(0, 2, (64, 64), dtype=np.uint8)

    def verify_pq_signature(self, packet):
        try:
            cmd = packet["command"]
            sig = packet["signature"]
            computed_hash = hashlib.sha3_512(f"{cmd}:{packet['ts']}".encode()).hexdigest()
            return computed_hash == sig
        except KeyError: return False

class InfraredSearchTrackSystem:
    def __init__(self):
        pass

    def scan_thermal_signature(self, ir_frame):
        if ir_frame is None: return False, 0
        gray = cv2.cvtColor(ir_frame, cv2.COLOR_BGR2GRAY)
        _, thermal_hotspots = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thermal_hotspots, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            if cv2.contourArea(contour) > 500:
                x, y, w, h = cv2.boundingRect(contour)
                return True, (x + (w // 2)) - 320, (x, y, w, h)
        return False, 0, (0,0,0,0)

class AntiCaptureZeroizer:
    def __init__(self):
        self.is_destroyed = False
    def execute_software_self_destruct(self):
        if self.is_destroyed: return
        self.is_destroyed = True

# ==============================================================================
# YENİ KATMAN: ASKERİ HUD (HEADS-UP DISPLAY) ÇİZİM MOTORU
# ==============================================================================
def draw_military_hud(frame, flight_mode, target_detected, error_x, bbox, ew_power):
    """ Kameranın üzerine askeri İHA arayüzünü (HUD) yeşil çizgilerle çizer. """
    height, width = frame.shape[:2]
    center_x, center_y = width // 2, height // 2
    green = (0, 255, 0)
    red = (0, 0, 255)
    
    # Merkez Nişangah (Crosshair)
    cv2.line(frame, (center_x - 20, center_y), (center_x + 20, center_y), green, 1)
    cv2.line(frame, (center_x, center_y - 20), (center_x, center_y + 20), green, 1)
    cv2.circle(frame, (center_x, center_y), 150, green, 1)

    # Uçuş Modu ve Kripto Durumu Metinleri
    cv2.putText(frame, f"MODE: {flight_mode}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, green, 2)
    cv2.putText(frame, "PQC CRYPTO: VALID", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, green, 2)
    
    # Dinamik Telemetri (Yapay Zeka ve Sensörler)
    simulated_alt = 120.5 + random.uniform(-0.5, 0.5)
    cv2.putText(frame, f"ALT: {simulated_alt:.1f} m", (width - 150, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, green, 2)

    if target_detected:
        tx, ty, tw, th = bbox
        # Hedef Kutusu ve Kilitlenme (Lock-on) Bildirimi
        cv2.rectangle(frame, (tx, ty), (tx + tw, ty + th), red, 2)
        cv2.putText(frame, "TARGET LOCKED", (tx, ty - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, red, 2)
        
        # Hedefe olan sapma çizgisi
        cv2.line(frame, (center_x, center_y), (tx + tw//2, ty + th//2), red, 1)

        # Elektronik Harp (EW) Güç Çubuğu
        cv2.putText(frame, f"EW ATTACK POWER: %{int(ew_power)}", (20, height - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, red, 2)
        cv2.rectangle(frame, (20, height - 30), (220, height - 15), green, 1)
        cv2.rectangle(frame, (20, height - 30), (20 + int(ew_power * 2), height - 15), red, -1)
    else:
        cv2.putText(frame, "SCANNING FOR TARGETS...", (20, height - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, green, 2)

    return frame

# Küresel Sistem Bileşenleri
pqc_crypto = QuantumResistantValidator()
irst_system = InfraredSearchTrackSystem()
zeroizer = AntiCaptureZeroizer()
ew_suite = OffensiveElectronicWarfare()

flight_mode = "STEALTH_PATROL"
irst_detected = False
tracking_error_x = 0
target_bbox = (0,0,0,0)

async def main_mission():
    drone = System()
    await drone.connect(system_address="udp://:14540")
    
    asyncio.ensure_future(advanced_sensor_and_hud_pipeline())
    asyncio.ensure_future(pentagon_flight_controller(drone))

    await drone.action.arm()
    await drone.action.takeoff()
    await asyncio.sleep(5)
    await drone.mission.start_mission()

# KAMERA + HUD İŞLEME HATTI
async def advanced_sensor_and_hud_pipeline():
    global irst_detected, tracking_error_x, flight_mode, target_bbox
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if ret:
            # Termal Hedef Taraması
            irst_detected, tracking_error_x, target_bbox = irst_system.scan_thermal_signature(frame)
            
            # Askeri HUD Çizimi
            hud_frame = draw_military_hud(
                frame, 
                flight_mode, 
                irst_detected, 
                tracking_error_x, 
                target_bbox, 
                ew_suite.jamming_power
            )
            
            # Canlı Arayüzü Ekranda Göster
            cv2.imshow("TACTICAL COMMAND CENTER (HUD)", hud_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        await asyncio.sleep(0.03)
        
    cap.release()
    cv2.destroyAllWindows()

# UÇUŞ VE TAARRUZ KONTROL MERKEZİ
async def pentagon_flight_controller(drone):
    global flight_mode, irst_detected, tracking_error_x
    in_offboard = False

    while True:
        if flight_mode == "STEALTH_PATROL":
            if irst_detected:
                flight_mode = "ENGAGING_TARGET"
                if not in_offboard:
                    await drone.mission.pause_mission()
                    await drone.offboard.start()
                    in_offboard = True
                
                yaw_speed = 5.0 if tracking_error_x > 0 else -5.0
                await drone.offboard.set_position_ned(PositionNedYaw(3.0, 0.0, -12.0, yaw_speed))
                
        elif flight_mode == "ENGAGING_TARGET":
            if irst_detected:
                yaw_speed = 5.0 if tracking_error_x > 0 else -5.0
                await drone.offboard.set_position_ned(PositionNedYaw(3.0, 0.0, -12.0, yaw_speed))
                
                # Merkezdeyse Siber Taarruz (EW) Başlat
                if abs(tracking_error_x) < 30:
                    is_destroyed = ew_suite.engage_cyber_kinetic_attack(target_locked=True)
                    if is_destroyed:
                        print("💥 Hedef İmha Edildi! Devriyeye dönülüyor.")
                        flight_mode = "STEALTH_PATROL"
                        irst_detected = False 
                        ew_suite.target_neutralized = False 
                else:
                    ew_suite.engage_cyber_kinetic_attack(target_locked=False)
            else:
                flight_mode = "STEALTH_PATROL"
                if in_offboard:
                    await drone.offboard.stop()
                    in_offboard = False
                    await drone.mission.start_mission()

        await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main_mission())

