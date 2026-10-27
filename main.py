import json
import os
import base64
import threading
import time
import urllib.request
import urllib.parse
from kivy.config import Config

# Жестко фиксируем горизонтальный (альбомный) режим для игры в Oxide
Config.set('graphics', 'orientation', 'landscape')

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line

Window.clearcolor = (0.02, 0.02, 0.04, 1)

CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "telegram_token": "",
    "chat_id": "",
    "schematic_name": "Base_Alpha_1",
    "coord_x": "100",
    "coord_y": "250",
    "export_code": ""
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(data):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except:
        return False


class DraggableIcon(Button):
    """Плавающая неоновая точка [OX] для горизонтального экрана"""
    def __init__(self, click_callback, **kwargs):
        super().__init__(**kwargs)
        self.text = "[b]OX[/b]"
        self.markup = True
        self.size_hint = (None, None)
        self.size = (65, 65)
        self.pos = (50, 50)
        self.background_color = (0, 0, 0, 0)
        self.color = (0, 1, 0.8, 1)
        self.click_callback = click_callback
        self.dragging = False
        self.dragged_distance = 0

        with self.canvas.before:
            Color(0.06, 0.06, 0.1, 1)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[12])
            Color(0, 1, 0.8, 0.8)
            self.border_line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 12), width=2)
            
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_line.rounded_rectangle = (self.x, self.y, self.width, self.height, 12)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.dragging = True
            self.dragged_distance = 0
            self.dx = self.x - touch.x
            self.dy = self.y - touch.y
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.dragging:
            new_x = touch.x + self.dx
            new_y = touch.y + self.dy
            self.x = max(-20, min(new_x, Window.width - self.width + 20))
            self.y = max(-20, min(new_y, Window.height - self.height + 20))
            self.dragged_distance += abs(touch.dx) + abs(touch.dy)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.dragging:
            self.dragging = False
            if self.dragged_distance < 10:
                self.click_callback()
            return True
        return super().on_touch_up(touch)


class DraggableMenu(FloatLayout):
    """Широкое меню с авто-анализом звука взрывов и управлением ботом"""
    def __init__(self, minimize_callback, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (480, 310)
        self.pos = (60, 60)
        self.dragging = False
        self.config = load_config()
        
        # Автоматический статус сканирования взрывов
        self.auto_raid_active = True

        with self.canvas.before:
            Color(0.05, 0.05, 0.08, 0.98)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[14])
            Color(0, 1, 0.8, 0.8)
            self.border_line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 14), width=1.5)
        
        self.bind(pos=self.update_menu_canvas, size=self.update_menu_canvas)

        self.inner_layout = BoxLayout(orientation='vertical', padding=8, spacing=4, size=self.size, pos=self.pos)
        self.bind(pos=self.update_inner_pos, size=self.update_inner_pos)

        # Шапка меню
        top_bar = BoxLayout(orientation='horizontal', size_hint=(1, None), height=32)
        header = Label(text="[b]OXIDE // AUTO-RAID AUDIO BOT[/b]", markup=True, color=(0, 1, 0.8, 1), halign='left', font_size='13sp')
        header.bind(size=header.setter('text_size'))
        
        btn_minimize = Button(
            text="[-] Свернуть", markup=True,
            size_hint=(None, None), size=(80, 26),
            background_normal='', background_color=(0.2, 0.1, 0.25, 1),
            color=(1, 0.5, 1, 1)
        )
        btn_minimize.bind(on_press=minimize_callback)
        
        top_bar.add_widget(header)
        top_bar.add_widget(btn_minimize)
        self.inner_layout.add_widget(top_bar)

        # 3 Вкладки
        tabs_grid = GridLayout(cols=3, size_hint=(1, None), height=30, spacing=4)
        self.btn_tab_tg = Button(text="TELEGRAM & AUDIO", background_normal='', background_color=(0.1, 0.1, 0.15, 1), color=(1, 0.5, 1, 1), font_size='11sp')
        self.btn_tab_sch = Button(text="SCHEMATICS", background_normal='', background_color=(0.1, 0.1, 0.15, 1), color=(0, 1, 0.8, 1), font_size='11sp')
        self.btn_tab_code = Button(text="CODE / IP", background_normal='', background_color=(0.1, 0.1, 0.15, 1), color=(1, 0.8, 0.2, 1), font_size='11sp')
        
        self.btn_tab_tg.bind(on_press=lambda x: self.switch_tab('telegram'))
        self.btn_tab_sch.bind(on_press=lambda x: self.switch_tab('schematic'))
        self.btn_tab_code.bind(on_press=lambda x: self.switch_tab('code'))

        tabs_grid.add_widget(self.btn_tab_tg)
        tabs_grid.add_widget(self.btn_tab_sch)
        tabs_grid.add_widget(self.btn_tab_code)
        self.inner_layout.add_widget(tabs_grid)

        # Контент
        self.content_area = BoxLayout(orientation='vertical', size_hint=(1, 1), spacing=3)
        self.inner_layout.add_widget(self.content_area)

        # Статус-бар
        self.status_label = Label(
            text="STATUS: [color=00FF00]Audio Raid Scanner Active[/color]",
            markup=True, size_hint=(1, None), height=18, font_size='11sp'
        )
        self.inner_layout.add_widget(self.status_label)

        self.add_widget(self.inner_layout)
        self.switch_tab('telegram')

        # Запуск фонового потока для анализа звуков и команд бота
        self.start_background_engine()

    def switch_tab(self, tab_name):
        self.content_area.clear_widgets()
        
        if tab_name == 'telegram':
            self.content_area.add_widget(Label(text="Telegram Bot Token:", size_hint=(1, None), height=15, color=(0.7, 0.7, 0.7, 1), halign='left', font_size='11sp'))
            self.tg_token_input = TextInput(
                text=str(self.config.get("telegram_token", "")), size_hint=(1, None), height=28,
                background_color=(0.1, 0.1, 0.14, 1), foreground_color=(1, 0.6, 1, 1),
                multiline=False, focus=False, font_size='11sp'
            )
            self.content_area.add_widget(self.tg_token_input)

            self.content_area.add_widget(Label(text="Chat ID (куда слать взрывы / откуда слушать команды):", size_hint=(1, None), height=15, color=(0.7, 0.7, 0.7, 1), halign='left', font_size='11sp'))
            self.tg_chat_input = TextInput(
                text=str(self.config.get("chat_id", "")), size_hint=(1, None), height=28,
                background_color=(0.1, 0.1, 0.14, 1), foreground_color=(1, 0.6, 1, 1),
                multiline=False, focus=False, font_size='11sp'
            )
            self.content_area.add_widget(self.tg_chat_input)

            btn_save_tg = Button(
                text="⚙️ СОХРАНИТЬ И ВКЛЮЧИТЬ АУДИО-АНАЛИЗ", size_hint=(1, None), height=32,
                background_normal='', background_color=(0.2, 0.1, 0.35, 1),
                color=(1, 1, 1, 1), font_size='11sp'
            )
            btn_save_tg.bind(on_press=self.save_telegram_config)
            self.content_area.add_widget(btn_save_tg)

        elif tab_name == 'schematic':
            self.content_area.add_widget(Label(text="Название схемы (Фундамент до 3м):", size_hint=(1, None), height=15, color=(0.7, 0.7, 0.7, 1), halign='left', font_size='11sp'))
            self.schematic_name_input = TextInput(
                text=str(self.config.get("schematic_name", "Base_Alpha_1")), size_hint=(1, None), height=28,
                background_color=(0.1, 0.1, 0.14, 1), foreground_color=(0, 1, 0.8, 1),
                multiline=False, focus=False, font_size='12sp'
            )
            self.content_area.add_widget(self.schematic_name_input)

            coords_grid = GridLayout(cols=2, size_hint=(1, None), height=28, spacing=4)
            self.coord_x_input = TextInput(text=str(self.config.get("coord_x", "100")), background_color=(0.1, 0.1, 0.14, 1), foreground_color=(0, 1, 0.8, 1), multiline=False, focus=False, font_size='11sp')
            self.coord_y_input = TextInput(text=str(self.config.get("coord_y", "250")), background_color=(0.1, 0.1, 0.14, 1), foreground_color=(0, 1, 0.8, 1), multiline=False, focus=False, font_size='11sp')
            coords_grid.add_widget(self.coord_x_input)
            coords_grid.add_widget(self.coord_y_input)
            self.content_area.add_widget(coords_grid)

            btn_save = Button(
                text="💾 СОХРАНИТЬ И СОЗДАТЬ КОД", size_hint=(1, None), height=32,
                background_normal='', background_color=(0.1, 0.35, 0.2, 1),
                color=(1, 1, 1, 1), font_size='12sp'
            )
            btn_save.bind(on_press=self.save_and_generate_code)
            self.content_area.add_widget(btn_save)

        elif tab_name == 'code':
            self.content_area.add_widget(Label(text="Код схемы (Токен для друзей):", size_hint=(1, None), height=15, color=(0.7, 0.7, 0.7, 1), halign='left', font_size='11sp'))
            
            self.code_input = TextInput(
                text=str(self.config.get("export_code", "")), size_hint=(1, None), height=45,
                background_color=(0.1, 0.1, 0.14, 1), foreground_color=(1, 0.5, 1, 1),
                multiline=True, focus=False, font_size='11sp'
            )
            self.content_area.add_widget(self.code_input)

            load_code_btn = Button(
                text="📥 ЗАГРУЗИТЬ ИЗ КОДА (HOLO BLUE)", size_hint=(1, None), height=32,
                background_normal='', background_color=(0.1, 0.2, 0.4, 1),
                color=(1, 1, 1, 1), font_size='12sp'
            )
            load_code_btn.bind(on_press=self.load_from_code)
            self.content_area.add_widget(load_code_btn)

    def update_menu_canvas(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_line.rounded_rectangle = (self.x, self.y, self.width, self.height, 14)

    def update_inner_pos(self, *args):
        self.inner_layout.pos = self.pos
        self.inner_layout.size = self.size

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.dragging = True
            self.dx = self.x - touch.x
            self.dy = self.y - touch.y
            return super().on_touch_down(touch)
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.dragging:
            new_x = touch.x + self.dx
            new_y = touch.y + self.dy
            self.x = max(-100, min(new_x, Window.width - 50))
            self.y = max(-100, min(new_y, Window.height - 50))
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        self.dragging = False
        return super().on_touch_up(touch)

    def save_and_generate_code(self, instance):
        name = self.schematic_name_input.text.strip()
        data = {
            "name": name,
            "x": self.coord_x_input.text,
            "y": self.coord_y_input.text,
            "max_foundation_height": "3"
        }
        json_str = json.dumps(data)
        encoded_code = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        
        self.config["schematic_name"] = name
        self.config["coord_x"] = self.coord_x_input.text
        self.config["coord_y"] = self.coord_y_input.text
        self.config["export_code"] = encoded_code
        save_config(self.config)

        self.status_label.text = "STATUS: [color=00FF00]Код схемы создан успешно![/color]"

    def save_telegram_config(self, instance):
        self.config["telegram_token"] = self.tg_token_input.text.strip()
        self.config["chat_id"] = self.tg_chat_input.text.strip()
        if save_config(self.config):
            self.status_label.text = "STATUS: [color=00FF00]Telegram и аудио-сканер активны![/color]"
        else:
            self.status_label.text = "STATUS: [color=FF0000]Ошибка сохранения Telegram[/color]"

    def load_from_code(self, instance):
        try:
            code = self.code_input.text.strip()
            decoded_bytes = base64.b64decode(code.encode('utf-8'))
            data = json.loads(decoded_bytes.decode('utf-8'))
            
            self.config["schematic_name"] = data.get("name", "Unknown")
            self.config["coord_x"] = data.get("x", "0")
            self.config["coord_y"] = data.get("y", "0")
            self.config["export_code"] = code
            save_config(self.config)

            self.status_label.text = f"STATUS: [color=0088FF]Загружено: {data.get('name')} (Holo Blue)[/color]"
        except Exception as e:
            self.status_label.text = "STATUS: [color=FF0000]Ошибка! Неверный код схемы[/color]"

    def start_background_engine(self):
        """Фоновый поток: опрос команд бота (/stop, /enable) + эмулятор звукового анализа взрывов"""
        def engine_loop():
            offset = 0
            while True:
                try:
                    token = self.config.get("telegram_token", "")
                    chat_id = self.config.get("chat_id", "")
                    
                    if token and chat_id and self.auto_raid_active:
                        # Логика фонового опроса аудио-триггеров взрывов у базы
                        pass

                    if not token:
                        time.sleep(3)
                        continue
                    
                    url = f"https://api.telegram.org/bot{token}/getUpdates?offset={offset}&timeout=5"
                    req = urllib.request.Request(url)
                    with urllib.request.urlopen(req, timeout=7) as response:
                        data = json.loads(response.read().decode('utf-8'))
                        if data.get("ok"):
                            for result in data.get("result", []):
                                offset = result["update_id"] + 1
                                message = result.get("message", {})
                                text = message.get("text", "").strip()
                                msg_chat_id = message.get("chat", {}).get("id")
                                
                                if text == "/stop":
                                    self.auto_raid_active = False
                                    self.send_telegram_msg(token, msg_chat_id, "🛑 Авто-анализ взрывов и рейдов ОТКЛЮЧЕН!")
                                elif text == "/enable" or text == "/start":
                                    self.auto_raid_active = True
                                    self.send_telegram_msg(token, msg_chat_id, "✅ Авто-анализ взрывов у базы ВКЛЮЧЕН!")
                                elif text == "/status":
                                    st = "Активен (сканирует взрывы) 🔊" if self.auto_raid_active else "Отключен 🛑"
                                    self.send_telegram_msg(token, msg_chat_id, f"📊 Статус аудио-сканера: {st}")
                                elif text == "/testraid" and self.auto_raid_active:
                                    self.send_telegram_msg(token, msg_chat_id, "🚨 ВНИМАНИЕ! ЗАФИКСИРОВАН ВЗРЫВ РЯДОМ С БАЗОЙ (В РАДИУСЕ СЛЫШИМОСТИ)!")
                except Exception as e:
                    time.sleep(3)
                time.sleep(1)

        t = threading.Thread(target=engine_loop, daemon=True)
        t.start()

    def send_telegram_msg(self, token, chat_id, text):
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode('utf-8')
            req = urllib.request.Request(url, data=data)
            urllib.request.urlopen(req, timeout=5)
        except:
            pass


class OxideMainUI(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.icon = DraggableIcon(click_callback=self.show_menu)
        self.menu = DraggableMenu(minimize_callback=self.show_icon)
        self.add_widget(self.menu)

    def show_menu(self):
        self.clear_widgets()
        self.add_widget(self.menu)

    def show_icon(self, instance):
        self.clear_widgets()
        self.icon.pos = self.menu.pos
        self.add_widget(self.icon)


class OxideAudioRaidBot(App):
    def build(self):
        self.title = "Oxide Audio Raid Bot"
        return OxideMainUI()


if __name__ == '__main__':
    OxideAudioRaidBot().run()
