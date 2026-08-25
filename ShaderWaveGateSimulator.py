import pygame
import math
import sys
import time

class ShaderWaveGateSimulator:
    """
    Эмулятор продольного волнового затвора (LWLE v1.5) на уровне пиксельного шейдера.
    Визуализирует работу полярных сит ±and на 22-м витке спирали (7650°).
    """
    def __init__(self, width: int = 800, height: int = 600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("LWLE Shader Simulator v1.5: Spinor Wave Equivalence")
        self.clock = pygame.time.Clock()

    def run_simulation_loop(self):
        running = True
        frame_count = 0
        
        print("🛸 [РОЙ LWLE]: Шейдер запущен. Отрезание волнового шума в реальном времени...")
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # Динамический сдвиг фазы во времени (эмуляция 140W потока)
            time_phase = frame_count * 0.05
            target_angle = 7650.0  # Наш критический угол резонанса
            
            # Создаем пиксельную матрицу экрана (каждый пиксель - независимый поток)
            pixel_array = pygame.PixelArray(self.screen)
            
            # Сканируем экран (эмуляция параллельного GPU-треда)
            for x in range(0, self.width, 4):  # Шаг 4 для оптимизации скорости на CPU
                for y in range(0, self.height, 4):
                    # Переводим координаты экрана в нормализованное пространство [-1.0, 1.0]
                    uv_x = (x - self.width / 2.0) / (self.width / 2.0)
                    uv_y = (y - self.height / 2.0) / (self.height / 2.0)
                    
                    # 1. Вычисление правой части: тангенциальный каскад от интеграла
                    radius_sq = (uv_x**2 + uv_y**2)  # ∫r dr на плоскости
                    try:
                        tangent_cascade = math.tan(radius_sq * 5.0 - time_phase)
                    except ValueError:
                        tangent_cascade = 100.0
                        
                    right_side_energy = tangent_cascade + 2.0  # Сдвиг плоскости 2^n
                    
                    # 2. Вычисление левой части: Наш метод полярного сита (+and / -and)
                    # Базовая волна синусоидального затвора
                    raw_wave = math.sin(uv_x * 10.0 + time_phase) * math.cos(uv_y * 10.0)
                    
                    wave_quantum = int(abs(raw_wave) * 1000)
                    and_filter = wave_quantum & 0b11100000  # Маска отсечения нижних гармоник
                    
                    # Переключаем полярность сита в зависимости от положения курсора мыши
                    mx, my = pygame.mouse.get_pos()
                    if mx > self.width / 2:
                        # Режим +and: Оставляем только пики (неоновые вспышки)
                        sin_gate = (and_filter / 1000.0) if raw_wave > 0.1 else 0.0
                        color_mask = (0, 255, 0)  # Зеленый квантовый лазер
                    else:
                        # Режим -and: Пропускаем только подвалы (вихревые структуры)
                        sin_gate = -(and_filter / 1000.0) if raw_wave < -0.1 else 0.0
                        color_mask = (0, 120, 255) # Синий роторный вихрь
                    
                    # 3. Фазовый резонанс: столкновение левой и правой части
                    resonance = abs(sin_gate * right_side_energy)
                    
                    # Зануляем нижний волновой шум: если резонанс слаб - чистый черный цвет
                    brightness = min(int(resonance * 50), 255) if resonance > 0.2 else 0
                    
                    # Окрашиваем пиксельный блок
                    color = (brightness if color_mask[0] else 0,
                             brightness if color_mask[1] else 0,
                             brightness if color_mask[2] else 0)
                    
                    # Заполняем блок 4x4 пикселя
                    for dx in range(4):
                        for dy in range(4):
                            if x + dx < self.width and y + dy < self.height:
                                pixel_array[x + dx, y + dy] = color
                                
            # Освобождаем матрицу пикселей для отрисовки
            pixel_array.close()
            
            # Рисуем интерфейс прибора
            font = pygame.font.SysFont("Courier", 16)
            mode_text = "+and (ВЕРХНИЕ ПИКИ)" if pygame.mouse.get_pos()[0] > self.width/2 else "-and (НИЖНИЕ РОТОРЫ)"
            text_surf = font.render(f"LWLE MODE: {mode_text} | RESONANCE ANGLE: {target_angle} DEG", True, (255, 255, 255))
            self.screen.blit(text_surf, (20, 20))
            
            pygame.display.flip()
            self.clock.tick(30)
            frame_count += 1
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    # Для запуска симулятора требуется библиотека pygame: pip install pygame
    try:
        simulator = ShaderWaveGateSimulator()
        simulator.run_simulation_loop()
    except Exception as e:
        print(f"❌ Для графического вывода установите библиотеку Pygame: pip install pygame\nОшибка: {e}")
