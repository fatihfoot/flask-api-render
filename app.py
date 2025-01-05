import flet as ft
import requests
from threading import Timer

BASE_URL = "https://flask-api-render-9okr.onrender.com"  # عنوان الخادم

def main(page: ft.Page):
    page.window_width = 380
    page.window_height = 700
    page.title = "فريق الخير - لوحة الأدمين"
    page.theme_mode = "dark"
    page.scroll = "auto"

    status_text = ft.Text(value="يرجى التحكم في حالة الأزرار وتوزيع الفرق.")
    players_container = ft.Column(
        spacing=5,
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.START,
    )

    def toggle_buttons(e):
        """فتح/إغلاق أزرار المستخدمين"""
        response = requests.post(f"{BASE_URL}/toggle_open")
        if response.status_code == 200:
            state = response.json()
            status_text.value = "الأزرار مفتوحة." if state['is_open'] else "الأزرار مغلقة."
            status_container.bgcolor = "green" if state['is_open'] else "red"
            page.update()

    def reset_players(e):
        """حذف جميع اللاعبين"""
        response = requests.post(f"{BASE_URL}/reset_players")
        if response.status_code == 200:
            status_text.value = "تم حذف جميع اللاعبين بنجاح."
            players_container.controls.clear()
            page.update()

    def distribute_teams(e):
        """توزيع الفرق"""
        try:
            response = requests.post(f"{BASE_URL}/distribute")
            if response.status_code == 200:
                teams = response.json()
                team1 = teams.get('team1', [])
                team2 = teams.get('team2', [])

                if not team1 and not team2:
                    status_text.value = "لا يوجد عدد كافٍ من اللاعبين لتوزيع الفرق."
                    page.update()
                    return

                # تنظيف الصفحة
                page.clean()

                # AppBar مع زر الرجوع
                page.appbar = ft.AppBar(
                    leading=ft.IconButton(
                        icon=ft.icons.ARROW_BACK,
                        icon_color="white",
                        on_click=lambda e: build_admin_screen()
                    ),
                    title=ft.Text("تقسيم الفرق", color="white"),
                    bgcolor="red",
                    center_title=True
                )

                # تصميم فريق A
                team1_container = ft.Container(
                    content=ft.Column(
                        [
                            ft.ElevatedButton(
                                "A فريق",
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                                width=160,
                                bgcolor="blue",
                                color="white",
                                height=50
                            ),
                            *[ft.ElevatedButton(
                                player,
                                bgcolor="white",
                                color="blue",
                                width=140,
                                height="auto"
                            ) for player in team1]
                        ],
                        spacing=10
                    ),
                    bgcolor="blue",
                    padding=10,
                    width=160,
                    height=410,
                    border_radius=20
                )

                # تصميم فريق B
                team2_container = ft.Container(
                    content=ft.Column(
                        [
                            ft.ElevatedButton(
                                "B فريق",
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                                width=160,
                                bgcolor="white",
                                color="black",
                                height=50
                            ),
                            *[ft.ElevatedButton(
                                player,
                                bgcolor="black",
                                color="white",
                                width=140,
                                height="auto"
                            ) for player in team2]
                        ],
                        spacing=10
                    ),
                    bgcolor="white",
                    padding=10,
                    width=160,
                    height=410,
                    border_radius=20
                )

                # عرض الفرق في صف (Row)
                teams_table = ft.Row(
                    [
                        team1_container,
                        team2_container
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=10
                )

                # إضافة النصوص التوضيحية والفرق إلى الصفحة
                page.add(
                    teams_table,
                    ft.Row(
                        [ft.Text("متنساش تجيب معاك \n           10 dh", size=30, color="red")],
                        alignment="center"
                    )
                )
                page.update()
            else:
                status_text.value = f"خطأ: {response.status_code} - {response.reason}"
                page.update()
        except requests.exceptions.RequestException as e:
            status_text.value = f"خطأ في الاتصال بالخادم: {e}"
            page.update()

    def fetch_admin_state():
        """جلب حالة اللعبة وعرض الأسماء في لوحة الأدمين."""
        try:
            response = requests.get(f"{BASE_URL}/state", timeout=5)
            if response.status_code == 200:
                state = response.json()
                is_open = state['is_open']
                players = state['players']
    
                # تحديث حالة الأزرار
                status_container.bgcolor = "green" if is_open else "red"
                status_text.value = "الأزرار مفتوحة." if is_open else "الأزرار مغلقة."
    
                # تحديث قائمة اللاعبين
                players_container.controls.clear()
                for i, player in enumerate(players):
                    player_button = ft.ElevatedButton(
                        text=f"{i + 1}. {player}",  # استخدام player مباشرة لأنه نص
                        bgcolor="gray",
                        color="white",
                        width=300,
                        height=40,
                        style=ft.ButtonStyle(text_style=ft.TextStyle(size=30))
                    )
                    players_container.controls.append(player_button)
    
                page.update()
        else:
            status_text.value = f"خطأ في الاتصال بالخادم: {response.status_code}"
            status_container.bgcolor = "red"
            page.update()
    except requests.exceptions.RequestException as e:
        status_text.value = f"خطأ في الاتصال بالخادم. السبب: {e}"
        status_container.bgcolor = "red"
        page.update()

            else:
                status_text.value = f"خطأ في الاتصال بالخادم: {response.status_code}"
                status_container.bgcolor = "red"
                page.update()
        except requests.exceptions.RequestException as e:
            status_text.value = f"خطأ في الاتصال بالخادم. السبب: {e}"
            status_container.bgcolor = "red"
            page.update()

    def start_auto_refresh():
        """بدء التحديث التلقائي"""
        fetch_admin_state()
        Timer(5, start_auto_refresh).start()

    status_container = ft.Container(
        content=status_text,
        bgcolor="red",
        width=300,
        height=50,
        alignment=ft.alignment.center,
        border_radius=15,
        padding=10,
    )

    def build_admin_screen():
        """بناء واجهة لوحة الأدمين."""
        page.clean()
        page.add(
            ft.Text("لوحة التحكم", size=24, color="white", weight="bold"),
            ft.Container(
                content=status_container,
                alignment=ft.alignment.center,
                margin=ft.margin.only(top=20, bottom=20),
            ),
            ft.Row(
                [
                    ft.ElevatedButton(
                        "فتح/إغلاق",
                        bgcolor="blue",
                        color="white",
                        on_click=toggle_buttons,
                        width=110,
                    ),
                    ft.ElevatedButton(
                        "توزيع", bgcolor="green", color="white", on_click=distribute_teams, width=110
                    ),
                    ft.ElevatedButton(
                        "مسح", bgcolor="red", color="white", on_click=reset_players, width=110
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Text(
                "قائمة اللاعبين", size=18, color="white", weight="bold"
            ),
            ft.Container(
                content=players_container,
                bgcolor="blue",
                padding=10,
                border_radius=15,
                height=700,
                width=350,
            ),
        )

    # عرض واجهة الأدمين
    build_admin_screen()

    # بدء التحديث التلقائي
    start_auto_refresh()

ft.app(target=main)
