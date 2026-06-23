# zelda-like-action-rpg

# Архитектурные решения и ключевые алгоритмы игры

## Реализованные алгоритмы

### 1. Перемещение камеры и плавный переход между комнатами (Room Transitions)

Для воссоздания аутентичной атмосферы оригинальной Зельды был реализован алгоритм плавного сдвига экрана при переходе игрока в другую комнату. Менеджер комнат отслеживает пересечение границ текущего экрана. При переходе запускается фаза транзиции, где положение отрисовки старой и новой комнат линейно интерполируется в зависимости от времени.

```python
def start_transition(self, dx, dy, target_x, target_y):
    self.state = "STATE_TRANSITION"
    self.trans_prog = 0.0
    self.trans_dir = (dx, dy)
    self.next_room = (self.world.current_room[0] + dx, self.world.current_room[1] + dy)
    self.trans_start_pos = (self.player.rect.x, self.player.rect.y)
    self.trans_target_pos = (target_x, target_y)

def _update_transition(self):
    self.trans_prog += self.trans_speed
    if self.trans_prog >= 1.0:
        self.trans_prog = 1.0
        self.world.current_room = self.next_room
        self.state = "STATE_PLAYING"
        self.world.room_projectiles[self.next_room].empty() 
    self.player.rect.x = self.trans_start_pos[0] + (self.trans_target_pos[0] - self.trans_start_pos[0]) * self.trans_prog
    self.player.rect.y = self.trans_start_pos[1] + (self.trans_target_pos[1] - self.trans_start_pos[1]) * self.trans_prog

```

### 2. Сложное поведение врагов (Конечный автомат Driller)

Враг типа `Driller` обладает нелинейным поведением, реализованным через паттерн «Конечный автомат» (State Machine). Он циклически переключается между состояниями: перемещение по поверхности (`SURFACE`), закапывание (`DIGGING`), нахождение под землей вне видимости игрока (`HIDDEN`) и выкапывание (`EMERGING`). Находясь в состоянии `HIDDEN`, алгоритм рассчитывает расстояние до игрока и заставляет врага появиться именно на векторе его движения с небольшим смещением, создавая эффект засады.

```python
elif self.state == "HIDDEN":
    self.action_timer -= 1
    if self.action_timer <= 0:
        dist = 150
        is_horizontal = random.choice([True, False])
        if is_horizontal:
            self.rect.centerx = player.rect.centerx
            self.rect.centery = player.rect.centery + random.choice([-dist, dist])
        else:
            self.rect.centerx = player.rect.centerx + random.choice([-dist, dist])
            self.rect.centery = player.rect.centery
            
        safe_bounds = pygame.Rect(WALL_SIZE, WALL_SIZE, WIDTH - WALL_SIZE*2, HEIGHT - WALL_SIZE*2)
        self.rect.clamp_ip(safe_bounds)
        self.state = "EMERGING"
        self.action_timer = 30 

```

### 3. Умная система передвижения игрока

Для соответствия ретро-механикам было наложено ограничение на диагональное перемещение. Движение обрабатывается через список зажатых клавиш `active_keys`. Приоритет всегда отдается последней нажатой кнопке (`active_keys[-1]`). Дополнительно реализован алгоритм взаимного поглощения: если игрок одновременно зажимает противоположные направления (например, влево и вправо), движение полностью аннулируется.

```python
if self.active_keys:
    last_key = self.active_keys[-1]
    dx, dy = self.movement_map[last_key]
    self.player.facing = (dx, dy)
    
    cancel_movement = False
    for key in self.active_keys:
        kx, ky = self.movement_map[key]
        if dx == -kx and dy == -ky:
            cancel_movement = True
            break
            
    if not cancel_movement:
        self.player.is_moving = True

```

### 4. Безопасная Fallback-загрузка ассетов

Для предотвращения критического падения приложения (например, при запуске на проверяющем компьютере без папки ресурсов) вся работа с диском обернута в блоки обработки исключений. Если графический файл отсутствует или поврежден, алгоритм перехватывает ошибку и динамически генерирует стандартные одноцветные поверхности (`pygame.Surface`) программным путем.

```python
try:
    tiles_sheet = SpriteSheet('assets/tiles.bmp')
    self.assets['wall'] = tiles_sheet.get_image(1, 1, 16, 16, WALL_SIZE, None)
except Exception:
    surf = pygame.Surface((WALL_SIZE, WALL_SIZE))
    surf.fill((100, 100, 100))
    self.assets['wall'] = surf

```

### 5. Алгоритм поосного разделения столкновений (AABB Collisions)

Чтобы избежать классической проблемы «залипания» объектов в углах статических препятствий, проверка коллизий разделена по осям координат. Сначала к позиции объекта прибавляется смещение по оси X, после чего сразу же проверяются пересечения со стенами и осуществляется выталкивание. Только после этого аналогичные действия производятся для оси Y.

```python
self.player.rect.x += dx * self.player.speed
for wall in walls:
    if self.player.rect.colliderect(wall.rect):
        if dx > 0:
            self.player.rect.right = wall.rect.left
        elif dx < 0:
            self.player.rect.left = wall.rect.right
        
self.player.rect.y += dy * self.player.speed
for wall in walls:
    if self.player.rect.colliderect(wall.rect):
        if dy > 0:
            self.player.rect.bottom = wall.rect.top
        elif dy < 0:
            self.player.rect.top = wall.rect.bottom

```

### 6. Триггерная система секретных проходов

Алгоритм динамического изменения карты. В цикле игры проверяется условие полной очистки комнат от противников. Как только метод `is_cleared()` возвращает истину, срабатывает триггер: изменяется флаг состояния игрового мира, и карта стен для ключевой комнаты генерируется заново с добавлением открытого прохода на месте глухой стены.

---

## Применение архитектурных принципов

### DRY (Don't Repeat Yourself)

* **Генерация геометрии комнат:** Конфигурация стен для всех четырех комнат не прописана вручную. Вместо этого создан единый метод `_generate_walls` в `WorldManager`, который принимает координаты комнаты и параметры дверей, автоматически рассчитывая положение блоков.
* **Нарезка спрайт-листов:** Весь функционал по извлечению отдельных кадров, масштабированию и применению цветового ключа прозрачности инкапсулирован в повторно используемом методе `SpriteSheet.get_image`.

### KISS (Keep It Simple, Stupid)

* **Менеджмент состояний:** Вместо построения сложной и громоздкой иерархии классов под паттерн State для управления экранами и поведением объектов используются строковые литералы (`"IDLE"`, `"ATTACKING"`, `"STATE_MENU"`). Это существенно упрощает отладку, делает код легко читаемым и избавляет от избыточных абстракций.
* **Централизованная конфигурация:** Все глобальные константы, размеры объектов, скорости и цветовые палитры вынесены в один плоский файл `settings.py`.

### SOLID

#### S — Single Responsibility Principle (Принцип единой ответственности)

Каждый модуль выполняет строго одну задачу:

* `main.py` является точкой входа и отвечает только за запуск.
* `settings.py` хранит конфигурационные данные.
* `utils.py` предоставляет вспомогательный инструмент для работы с графикой.
* `entities.py` содержит описание физических свойств и логику поведения игровых объектов.
* `world.py` изолирует управление комнатами, хранение матриц противников и геометрию уровней.
* `game.py` координирует игровой цикл, обрабатывает глобальный ввод и рендеринг.

#### O — Open/Closed Principle (Принцип открытости/закрытости)

Архитектура классов противников спроектирована так, что код открыт для расширения, но закрыт для модификации. Базовый класс `Enemy` содержит общее поведение и алгоритмы перемещения. При добавлении новых типов врагов (`Shooter`, `Driller`) базовый класс не подвергается изменениям — новые механики атак и движения реализуются через переопределение методов в подклассах.

#### L — Liskov Substitution Principle (Принцип подстановки Лисков)

Классы `Shooter` и `Driller` являются полноценными подтипами `Enemy`. Они принимают те же параметры в конструктор и не нарушают контракты базовых методов. Благодаря этому менеджер комнат хранит их в единой стандартной группе `pygame.sprite.Group()` и вызывает метод `update` полиморфно, не зная конкретного типа объекта.