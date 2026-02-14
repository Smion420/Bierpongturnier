import flet as ft
from flet import View, RouteChangeEvent



def main(page: ft.Page):
    page.title = "Bierpong Wetten"
    page.window_width = 900
    page.window_height = 650

    def route_change(e: RouteChangeEvent):
        page.views.clear()

        page.views.append(
            View(
                route="/",
                controls=[
                    ft.Text("Willkommen zum Bierpong Wettportal!", size=22, weight=ft.FontWeight.BOLD)
                ]
            )
        )
        page.update()
    
    page.on_route_change = route_change
    page.go(page.route)

if __name__ == "__main__":
    ft.app(main)