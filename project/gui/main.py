import flet as ft
from flet import View, Text, TextField, ElevatedButton, Row, Container, Card, Divider, SnackBar
from flet import RouteChangeEvent, ViewPopEvent, MainAxisAlignment, FontWeight, KeyboardType
from gui.controller import AppController
from adapters.player_repo_memory import PlayerRepositoryMemory
from adapters.bettor_repo_memory import BettorRepositoryMemory
from adapters.match_repo_memory import MatchRepositoryMemory
from adapters.bet_repo_memory import BetRepositoryMemory
from app.results import MatchEnded, PlayersListed, MatchesListed, BettorsListed, BetPlaced, QuotasListed, Ok, Error
from domain.enums import BetType, HandicapType
# ---- HIER EINHÄNGEN: deinen echten Service erzeugen / importieren ----
from app.service import AppService
# --------------------------------------------------------------------


def main(page: ft.Page):
    page.title = "Bierpong Wetten"
    page.window_width = 1920
    page.window_height = 1080
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    service = AppService(player_repo=PlayerRepositoryMemory(), match_repo = MatchRepositoryMemory(), bettor_repo = BettorRepositoryMemory(), bet_repo = BetRepositoryMemory())
    controller = AppController(service)
    #Create Player
    text_name = TextField(label="Name", width=200)
    text_rating = TextField(label="Rating", width=200)
    text_amount_of_games = TextField(label="Anzahl der Spiele", width=200)
    create_player_button: ElevatedButton = ElevatedButton("Erstellen", disabled = True)

    # show/list players controls (opens popup)
    def show_players(e=None):
        print("DEBUG: show_players called")
        try:
            res = controller.list_players()
            print("DEBUG: controller.list_players returned:", repr(res))
            if isinstance(res, PlayersListed):
                players = res.players
            elif isinstance(res, Ok):
                players = res.data or []
            elif isinstance(res, Error):
                dlg = ft.AlertDialog(title=Text("Fehler"), content=Text(res.message))
                def _close_err(ev):
                    dlg.open = False
                    page.update()
                dlg.actions = [ft.TextButton("Schließen", on_click=_close_err)]
                page.show_dialog(dlg)
                return
            else:
                players = res

            if not players:
                lines = ["(keine Spieler)"]
            else:
                lines = [f"- {getattr(p,'name',p)}   ID: {getattr(p,'id','')}  Rating: {getattr(p,'rating','')}   Matches: {getattr(p,'matchamount','')}   RD: {getattr(p,'rd',0):.2f}" for p in players]

            content = ft.Column([Text(l) for l in lines], tight=True)
            dlg = ft.AlertDialog(title=Text("Spieler"), content=content)

            def close_dialog(ev):
                dlg.open = False
                page.update()

            dlg.actions = [ft.TextButton("Schließen", on_click=close_dialog)]
            page.show_dialog(dlg)
            print("DEBUG: dialog opened")
        except Exception as ex:
            print("DEBUG: exception in show_players:", ex)
            dlg = ft.AlertDialog(title=Text("Fehler"), content=Text(str(ex)))
            dlg.actions = [ft.TextButton("Schließen", on_click=lambda ev: (setattr(dlg, 'open', False), page.update()))]
            page.show_dialog(dlg)

        page.update()

    list_players_button = ElevatedButton("Alle Spieler anzeigen", on_click=show_players)

    page.add (
        Text("Neuen Spieler erstellen", weight=FontWeight.BOLD, size=20),
        Row([text_name, text_rating, text_amount_of_games, create_player_button, Container(expand=True), list_players_button])
    )

    def validate_create_player():
        if all([text_name.value, text_rating.value, text_amount_of_games.value]):
            create_player_button.disabled = False
        else:
            create_player_button.disabled = True
        page.update()
    text_name.on_change = lambda _: validate_create_player()
    text_rating.on_change = lambda _: validate_create_player()
    text_amount_of_games.on_change = lambda _: validate_create_player()

    def create_player_clicked(e):
        try:
            res = controller.create_player(text_name.value, text_rating.value, text_amount_of_games.value)
            msg = getattr(res, 'message', str(res))
            dlg = ft.AlertDialog(title=Text("Ergebnis"), content=Text(str(msg)))
            def _close_ok(ev):
                dlg.open = False
                page.update()
            dlg.actions = [ft.TextButton("OK", on_click=_close_ok)]
            page.show_dialog(dlg)
            refresh_player_dropdowns()
            refresh_match_dropdowns()
        except Exception as ex:
            dlg = ft.AlertDialog(title=Text("Fehler"), content=Text(str(ex)))
            def _close_err(ev):
                dlg.open = False
                page.update()
            dlg.actions = [ft.TextButton("Schließen", on_click=_close_err)]
            page.show_dialog(dlg)

    create_player_button.on_click = create_player_clicked

    # Create Bettor
    text_bettor_name = TextField(label="Gambler Name", width=200)
    create_bettor_button: ElevatedButton = ElevatedButton("Erstellen", disabled = True)
    # show/list bettors controls (opens popup)
    def show_bettors(e=None):
        try:
            res = controller.list_bettors()
            if isinstance(res, BettorsListed):
                bettors = res.bettors
            elif isinstance(res, Ok):
                bettors = res.data or []
            elif isinstance(res, Error):
                dlg = ft.AlertDialog(title=Text("Fehler"), content=Text(res.message))
                def _close_err(ev):
                    dlg.open = False
                    page.update()
                dlg.actions = [ft.TextButton("Schließen", on_click=_close_err)]
                page.show_dialog(dlg)
                return
            else:
                bettors = res

            if not bettors:
                lines = ["(keine Gambler)"]
            else:
                lines = [f"- {getattr(b,'name',b)}   ID: {getattr(b,'id','')}  Kontostand: {getattr(b,'kontostand',0):.2f}" for b in bettors]

            content = ft.Column([Text(l) for l in lines], tight=True)
            dlg = ft.AlertDialog(title=Text("Gambler"), content=content)
            def close_dialog(ev):
                dlg.open = False
                page.update()
            dlg.actions = [ft.TextButton("Schließen", on_click=close_dialog)]
            page.show_dialog(dlg)
        except Exception as ex:
            dlg = ft.AlertDialog(title=Text("Fehler"), content=Text(str(ex)))
            dlg.actions = [ft.TextButton("Schließen", on_click=lambda ev: (setattr(dlg, 'open', False), page.update()))]
            page.show_dialog(dlg)

    list_bettors_button = ElevatedButton("Alle Gambler anzeigen", on_click=show_bettors)

    def refresh_bettor_dropdowns():
        try:
            opts = get_bettor_options()
            dd_bettor.options = opts
            try:
                dd_bettor.update()
            except Exception:
                pass
        except Exception:
            pass

    def create_bettor_clicked(e):
        try:
            res = controller.create_bettor(text_bettor_name.value)
            msg = getattr(res, 'message', str(res))
            dlg = ft.AlertDialog(title=Text("Ergebnis"), content=Text(str(msg)))
            def _close_ok(ev):
                dlg.open = False
                page.update()
            dlg.actions = [ft.TextButton("OK", on_click=_close_ok)]
            page.show_dialog(dlg)
            refresh_bettor_dropdowns()
            refresh_match_dropdowns()
        except Exception as ex:
            dlg = ft.AlertDialog(title=Text("Fehler"), content=Text(str(ex)))
            def _close_err(ev):
                dlg.open = False
                page.update()
            dlg.actions = [ft.TextButton("Schließen", on_click=_close_err)]
            page.show_dialog(dlg)

    create_bettor_button.on_click = create_bettor_clicked

    page.add (
        Divider(),
        Text("Neuen Gambler erstellen", weight=FontWeight.BOLD, size=20),
        Row([text_bettor_name, Container(expand=True), list_bettors_button]),
        create_bettor_button   
    )
    # Save / Load snapshot
    tf_save_name = TextField(label="Snapshot Name", width=300)
    btn_save = ElevatedButton("Save", on_click=lambda e: None)
    tf_load_name = TextField(label="Snapshot Name (load)", width=300)
    btn_load = ElevatedButton("Load", on_click=lambda e: None)

    def save_clicked(e):
        try:
            name = tf_save_name.value
            res = controller.save_snapshot(name)
            msg = getattr(res, 'message', str(res))
            dlg = ft.AlertDialog(title=Text("Save"), content=Text(str(msg)))
            def _close(ev):
                dlg.open = False
                page.update()
            dlg.actions = [ft.TextButton("OK", on_click=_close)]
            page.show_dialog(dlg)
        except Exception as ex:
            dlg = ft.AlertDialog(title=Text("Fehler"), content=Text(str(ex)))
            def _close_err(ev):
                dlg.open = False
                page.update()
            dlg.actions = [ft.TextButton("Schließen", on_click=_close_err)]
            page.show_dialog(dlg)

    def load_clicked(e):
        try:
            name = tf_load_name.value
            res = controller.load_snapshot(name)
            msg = getattr(res, 'message', str(res))
            dlg = ft.AlertDialog(title=Text("Load"), content=Text(str(msg)))
            def _close(ev):
                dlg.open = False
                page.update()
            dlg.actions = [ft.TextButton("OK", on_click=_close)]
            page.show_dialog(dlg)
            # refresh options after load
            refresh_player_dropdowns()
            refresh_match_dropdowns()
            refresh_bettor_dropdowns()
        except Exception as ex:
            dlg = ft.AlertDialog(title=Text("Fehler"), content=Text(str(ex)))
            def _close_err(ev):
                dlg.open = False
                page.update()
            dlg.actions = [ft.TextButton("Schließen", on_click=_close_err)]
            page.show_dialog(dlg)

    btn_save.on_click = save_clicked
    btn_load.on_click = load_clicked

    page.add(
        Divider(),
        Text("Snapshot speichern / laden", weight=FontWeight.BOLD, size=20),
        Row([tf_save_name, btn_save, Container(width=20), tf_load_name, btn_load], alignment=ft.MainAxisAlignment.START, spacing=8),
    )
    def validate_create_bettor():
        if text_bettor_name.value:
            create_bettor_button.disabled = False
        else:
            create_bettor_button.disabled = True
        page.update()
    text_bettor_name.on_change = lambda _: validate_create_bettor()
    
    # Create Match - select players from dropdowns
    # Dropdown options will be populated from controller.list_players()
    def get_player_options():
        opts = []
        try:
            res = controller.list_players()
            if isinstance(res, PlayersListed):
                players = res.players
            elif isinstance(res, Ok):
                players = res.data or []
            else:
                players = res
            for p in players:
                # display name, use id as key
                try:
                    key = getattr(p, 'id')
                except Exception:
                    key = str(p)
                opts.append(ft.dropdown.Option(text=f"{getattr(p,'name',p)} (ID:{key})", key=str(key)))
        except Exception:
            pass
        return opts

    dd_t1_p1 = ft.Dropdown(width=220, options=get_player_options())
    dd_t1_p2 = ft.Dropdown(width=220, options=get_player_options())
    dd_t2_p1 = ft.Dropdown(width=220, options=get_player_options())
    dd_t2_p2 = ft.Dropdown(width=220, options=get_player_options())

    match_result = Text("", selectable=True)

    def refresh_player_dropdowns():
        opts = get_player_options()
        for dd in (dd_t1_p1, dd_t1_p2, dd_t2_p1, dd_t2_p2):
            dd.options = opts
            try:
                dd.update()
            except Exception:
                pass

    def refresh_match_dropdowns():
        try:
            opts = get_match_options()
            print("DEBUG: refresh_match_dropdowns ->", len(opts), "options")
            # ensure an explicit empty option at start
            opts_with_empty = [ft.dropdown.Option(text="(keine Auswahl)", key="")] + opts
            # update both match dropdowns if present
            try:
                dd_match_quotas.options = opts_with_empty
            except Exception:
                pass
            try:
                dd_match_bet.options = opts_with_empty
            except Exception:
                pass
            try:
                dd_match_end.options = opts_with_empty
            except Exception:
                pass
            try:
                dd_match_quotas.update()
            except Exception:
                pass
            try:
                dd_match_bet.update()
            except Exception:
                pass
            try:
                dd_match_end.update()
            except Exception:
                pass
        except Exception:
            pass


    def create_match_clicked(e):
        try:
            p1 = dd_t1_p1.value
            p2 = dd_t1_p2.value
            p3 = dd_t2_p1.value
            p4 = dd_t2_p2.value
            if not all([p1, p2, p3, p4]):
                dlg = ft.AlertDialog(title=Text("Fehler"), content=Text("Bitte alle vier Spieler auswählen."))
                def _close_missing(ev):
                    dlg.open = False
                    page.update()
                dlg.actions = [ft.TextButton("Schließen", on_click=_close_missing)]
                page.show_dialog(dlg)
                return
            # convert keys to int when possible
            try:
                p1_id = int(p1)
                p2_id = int(p2)
                p3_id = int(p3)
                p4_id = int(p4)
            except Exception:
                dlg = ft.AlertDialog(title=Text("Fehler"), content=Text("Ungültige Spieler-ID(s)."))
                def _close_invalid(ev):
                    dlg.open = False
                    page.update()
                dlg.actions = [ft.TextButton("Schließen", on_click=_close_invalid)]
                page.show_dialog(dlg)
                return

            res = controller.create_match(p1_id, p2_id, p3_id, p4_id)
            # Show result
            if hasattr(res, 'message'):
                dlg = ft.AlertDialog(title=Text("Match erstellt"), content=Text(str(res.message)))
            else:
                dlg = ft.AlertDialog(title=Text("Match erstellt"), content=Text(str(res)))
            def _close_match_ok(ev):
                dlg.open = False
                page.update()
            dlg.actions = [ft.TextButton("OK", on_click=_close_match_ok)]
            page.show_dialog(dlg)
            # refresh matches so new match appears in dropdown
            refresh_match_dropdowns()
        except Exception as ex:
            dlg = ft.AlertDialog(title=Text("Fehler"), content=Text(str(ex)))
            def _close_ex(ev):
                dlg.open = False
                page.update()
            dlg.actions = [ft.TextButton("Schließen", on_click=_close_ex)]
            page.show_dialog(dlg)

    create_match_button = ElevatedButton("Match erstellen", on_click=create_match_clicked)

    # layout
    page.add(
        Divider(),
        Text("Match erstellen", weight=FontWeight.BOLD, size=20),
        Row([
            ft.Column([Text("Team 1 - Spieler A"), dd_t1_p1]),
            ft.Column([Text("Team 1 - Spieler B"), dd_t1_p2]),
            ft.Column([Text("Team 2 - Spieler A"), dd_t2_p1]),
            ft.Column([Text("Team 2 - Spieler B"), dd_t2_p2]),
            create_match_button,
        ], alignment=ft.MainAxisAlignment.START, spacing=8),
        match_result,
    )

    # --- Place Bet section ---
    def get_bettor_options():
        opts = []
        try:
            res = controller.list_bettors()
            if isinstance(res, BettorsListed):
                bettors = res.bettors
            elif isinstance(res, Ok):
                bettors = res.data or []
            else:
                bettors = res
            for b in bettors:
                opts.append(ft.dropdown.Option(text=f"{getattr(b,'name',b)} (ID:{getattr(b,'id','')})", key=str(getattr(b,'id',''))))
        except Exception:
            pass
        return opts

    def get_match_options():
        opts = []
        try:
            res = controller.list_matches()
            if isinstance(res, MatchesListed):
                matches = res.matches
            elif isinstance(res, Ok):
                matches = res.data or []
            else:
                matches = res
            # build player lookup
            players_map = {}
            try:
                pres = controller.list_players()
                if isinstance(pres, PlayersListed):
                    for p in pres.players:
                        players_map[getattr(p,'id','')] = getattr(p,'name','')
            except Exception:
                pass
            for m in matches:
                if getattr(m, 'ended', False):
                    continue
                # try to list player names
                team1_ids = getattr(m, 'team1', [])
                team2_ids = getattr(m, 'team2', [])
                t1_names = ", ".join(players_map.get(i, str(i)) for i in team1_ids)
                t2_names = ", ".join(players_map.get(i, str(i)) for i in team2_ids)
                opts.append(ft.dropdown.Option(text=f"Match {getattr(m,'id','')} : [{t1_names}] vs [{t2_names}]", key=str(getattr(m,'id',''))))
        except Exception:
            pass
        return opts

    dd_bettor = ft.Dropdown(label="Bettor", width=200, options=get_bettor_options())
    # two separate match dropdowns: one for quotas display, one for placing bets
    dd_match_quotas = ft.Dropdown(label="Match (Quoten)", width=380, options=get_match_options())
    dd_match_bet = ft.Dropdown(label="Match (Wette)", width=240, options=get_match_options())
    tf_amount = TextField(label="Betrag", width=90)
    dd_bet_type = ft.Dropdown(label="Wetttyp", width=180, options=[ft.dropdown.Option(text=t.name, key=t.name) for t in BetType])
    # separate dropdowns for team and player as target
    dd_target_team = ft.Dropdown(label="Team (optional)", width=140, options=[ft.dropdown.Option(text="(keine)", key="")], disabled=True)
    dd_target_player = ft.Dropdown(label="Player (optional)", width=200, options=[ft.dropdown.Option(text="(keine)", key="")], disabled=True)
    dd_handicap = ft.Dropdown(label="Handicap (optional)", width=110, options=[ft.dropdown.Option(text="(keine)", key="")] + [ft.dropdown.Option(text=str(h.value), key=str(h.value)) for h in HandicapType])

    def update_target_options(e=None):
        team_opts = []
        player_opts = []
        m_id = dd_match_bet.value
        if not m_id:
            dd_target_team.options = team_opts
            dd_target_player.options = player_opts
            dd_target_team.disabled = True
            dd_target_player.disabled = True
            try:
                dd_target_team.update()
                dd_target_player.update()
            except Exception:
                pass
            return
        try:
            print("DEBUG: update_target_options m_id=", m_id)
            # find match object
            res = controller.list_matches()
            matches = res.matches if isinstance(res, MatchesListed) else (res if isinstance(res, list) else [])
            match_obj = None
            for m in matches:
                if str(getattr(m,'id','')) == str(m_id):
                    match_obj = m
                    break
            if not match_obj:
                dd_target_team.options = team_opts
                dd_target_player.options = player_opts
                dd_target_team.update()
                dd_target_player.update()
                return
            # team options: show player names for each team
            # build player name map
            pres = controller.list_players()
            players_list_all = pres.players if isinstance(pres, PlayersListed) else (pres if isinstance(pres, list) else [])
            pname_map = {getattr(p,'id',None): getattr(p,'name','') for p in players_list_all}
            t1_names = ", ".join(pname_map.get(i, str(i)) for i in getattr(match_obj, 'team1', []))
            t2_names = ", ".join(pname_map.get(i, str(i)) for i in getattr(match_obj, 'team2', []))
            team_opts.append(ft.dropdown.Option(text="(keine)", key=""))
            team_opts.append(ft.dropdown.Option(text=f"Team 1: {t1_names}", key="TEAM1"))
            team_opts.append(ft.dropdown.Option(text=f"Team 2: {t2_names}", key="TEAM2"))
            # player options
            pres = controller.list_players()
            players = pres.players if isinstance(pres, PlayersListed) else (pres if isinstance(pres, list) else [])
            player_map = {getattr(p,'id',None): p for p in players}
            for pid in getattr(match_obj, 'team1', []) + getattr(match_obj, 'team2', []):
                p = player_map.get(pid)
                name = getattr(p,'name', str(pid)) if p else str(pid)
                player_opts.append(ft.dropdown.Option(text=f"{name} (ID:{pid})", key=str(pid)))
        except Exception:
            pass
        # ensure an explicit empty option is available
        if not any(o.key == "" for o in team_opts):
            team_opts.insert(0, ft.dropdown.Option(text="(keine)", key=""))
        if not any(o.key == "" for o in player_opts):
            player_opts.insert(0, ft.dropdown.Option(text="(keine)", key=""))
        dd_target_team.options = team_opts
        dd_target_player.options = player_opts
        dd_target_team.disabled = False if team_opts else True
        dd_target_player.disabled = False if player_opts else True
        try:
            dd_target_team.update()
            dd_target_player.update()
        except Exception:
            pass

    dd_match_bet.on_change = update_target_options
    btn_refresh_match = ElevatedButton("Aktualisieren", on_click=lambda e: (refresh_match_dropdowns(), update_target_options()))

    def show_quotas_clicked(e):
        try:
            # ensure match dropdown is up-to-date and value is committed
            try:
                refresh_match_dropdowns()
            except Exception:
                pass
            page.update()
            m_id = dd_match_quotas.value
            if not m_id:
                dlg = ft.AlertDialog(title=Text("Quoten"), content=Text("Bitte zuerst ein Match auswählen."))
                def _close(ev):
                    dlg.open = False
                    page.update()
                dlg.actions = [ft.TextButton("OK", on_click=_close)]
                page.show_dialog(dlg)
                return
            # call controller
            try:
                res = controller.quotas(m_id)
            except Exception as ex:
                dlg = ft.AlertDialog(title=Text("Fehler"), content=Text(str(ex)))
                def _close_err(ev):
                    dlg.open = False
                    page.update()
                dlg.actions = [ft.TextButton("Schließen", on_click=_close_err)]
                page.show_dialog(dlg)
                return

            if isinstance(res, QuotasListed):
                lines = []
                for label, q in res.quotas:
                    qtxt = f"{q:.4f}" if isinstance(q, (int, float)) else (str(q) if q is not None else "N/A")
                    lines.append(f"{label}: {qtxt}")
                text = "\n".join(lines)
                # try copy to clipboard via tkinter
                copied = False
                try:
                    import tkinter as tk
                    r = tk.Tk()
                    r.withdraw()
                    r.clipboard_clear()
                    r.clipboard_append(text)
                    r.update()
                    r.destroy()
                    copied = True
                except Exception:
                    copied = False

                if copied:
                    dlg = ft.AlertDialog(title=Text("Quoten"), content=Text("Quoten in die Zwischenablage kopiert."))
                    def _close_ok(ev):
                        dlg.open = False
                        page.update()
                    dlg.actions = [ft.TextButton("OK", on_click=_close_ok)]
                    page.show_dialog(dlg)
                else:
                    content = ft.Column([Text(l) for l in lines], tight=True)
                    dlg = ft.AlertDialog(title=Text("Quoten"), content=content)
                    def _close2(ev):
                        dlg.open = False
                        page.update()
                    dlg.actions = [ft.TextButton("Schließen", on_click=_close2)]
                    page.show_dialog(dlg)
            elif isinstance(res, Error):
                dlg = ft.AlertDialog(title=Text("Fehler"), content=Text(res.message))
                def _close_err2(ev):
                    dlg.open = False
                    page.update()
                dlg.actions = [ft.TextButton("Schließen", on_click=_close_err2)]
                page.show_dialog(dlg)
            else:
                dlg = ft.AlertDialog(title=Text("Quoten"), content=Text(str(res)))
                def _close3(ev):
                    dlg.open = False
                    page.update()
                dlg.actions = [ft.TextButton("Schließen", on_click=_close3)]
                page.show_dialog(dlg)
        except Exception as ex:
            dlg = ft.AlertDialog(title=Text("Fehler"), content=Text(str(ex)))
            def _close_err3(ev):
                dlg.open = False
                page.update()
            dlg.actions = [ft.TextButton("Schließen", on_click=_close_err3)]
            page.show_dialog(dlg)

    btn_show_quotas = ElevatedButton("Quoten", on_click=show_quotas_clicked)

    # --- End Match section ---
    dd_match_end = ft.Dropdown(label="Match (Beenden)", width=300, options=get_match_options())
    btn_refresh_end = ElevatedButton("Aktualisieren")
    dd_winner = ft.Dropdown(label="Gewinner", width=130, options=[ft.dropdown.Option(text="Team 1", key="TEAM1"), ft.dropdown.Option(text="Team 2", key="TEAM2")])
    tf_remaining = TextField(label="Remaining", width=100)
    dd_nacktemeile = ft.Dropdown(label="Nackte Meile", width=150, options=[ft.dropdown.Option(text="(keine)", key="")], disabled=True)
    dd_deathcup = ft.Dropdown(label="Deathcup", width=150, options=[ft.dropdown.Option(text="(keine)", key="")], disabled=True)
    dd_bitchcup = ft.Dropdown(label="Bitchcup", width=150, options=[ft.dropdown.Option(text="(keine)", key="")], disabled=True)
    dd_overtime = ft.Dropdown(label="Overtime", width=100, options=[ft.dropdown.Option(text="Nein", key="False"), ft.dropdown.Option(text="Ja", key="True")])

    def update_end_match_players(e=None):
        # populate the 4 player-related dropdowns based on selected match
        opts = []
        m_id = dd_match_end.value
        if not m_id:
            for dd in (dd_nacktemeile, dd_deathcup, dd_bitchcup):
                dd.options = [ft.dropdown.Option(text="(keine)", key="")]
                dd.disabled = True
                try:
                    dd.update()
                except Exception:
                    pass
            return
        try:
            res = controller.list_matches()
            matches = res.matches if isinstance(res, MatchesListed) else (res if isinstance(res, list) else [])
            match_obj = None
            for m in matches:
                if str(getattr(m,'id','')) == str(m_id):
                    match_obj = m
                    break
            if not match_obj:
                return
            # build player map and options
            pres = controller.list_players()
            players = pres.players if isinstance(pres, PlayersListed) else (pres if isinstance(pres, list) else [])
            player_map = {getattr(p,'id',None): p for p in players}
            opts = [ft.dropdown.Option(text="(keine)", key="")] + [ft.dropdown.Option(text=f"{getattr(player_map.get(pid),'name',pid)} (ID:{pid})", key=str(pid)) for pid in getattr(match_obj,'team1',[]) + getattr(match_obj,'team2',[])]
            for dd in (dd_nacktemeile, dd_deathcup, dd_bitchcup):
                dd.options = opts
                dd.disabled = False
                try:
                    dd.update()
                except Exception:
                    pass
        except Exception:
            pass

    dd_match_end.on_change = update_end_match_players
    try:
        btn_refresh_end.on_click = update_end_match_players
    except Exception:
        pass

    def end_match_clicked(e):
        try:
            m_id = dd_match_end.value
            if not m_id:
                dlg = ft.AlertDialog(title=Text("Fehler"), content=Text("Bitte zuerst ein Match auswählen."))
                def _close(ev):
                    dlg.open = False
                    page.update()
                dlg.actions = [ft.TextButton("OK", on_click=_close)]
                page.show_dialog(dlg)
                return
            winner = dd_winner.value
            remaining = tf_remaining.value or "0"
            nack = dd_nacktemeile.value
            death = dd_deathcup.value
            bitch = dd_bitchcup.value
            ot = dd_overtime.value
            try:
                res = controller.end_match(m_id, winner, remaining, nack, death, bitch, ot)
            except Exception as ex:
                dlg = ft.AlertDialog(title=Text("Fehler"), content=Text(str(ex)))
                def _close_err(ev):
                    dlg.open = False
                    page.update()
                dlg.actions = [ft.TextButton("Schließen", on_click=_close_err)]
                page.show_dialog(dlg)
                return

            if isinstance(res, MatchEnded):
                payouts = getattr(res, 'payouts', {})
                if not payouts:
                    lines = ["Keine Auszahlungen."]
                else:
                    lines = [f"Tipper ID {tid}: {amt:.2f}" for tid, amt in payouts.items()]
                content = ft.Column([Text(l) for l in lines], tight=True)
                dlg = ft.AlertDialog(title=Text("Match beendet - Auszahlungen"), content=content)
                def _close_ok(ev):
                    dlg.open = False
                    page.update()
                dlg.actions = [ft.TextButton("OK", on_click=_close_ok)]
                page.show_dialog(dlg)
                # refresh dropdowns
                refresh_match_dropdowns()
                refresh_player_dropdowns()
                refresh_bettor_dropdowns()
            elif isinstance(res, Error):
                dlg = ft.AlertDialog(title=Text("Fehler"), content=Text(res.message))
                def _close_err2(ev):
                    dlg.open = False
                    page.update()
                dlg.actions = [ft.TextButton("Schließen", on_click=_close_err2)]
                page.show_dialog(dlg)
            else:
                dlg = ft.AlertDialog(title=Text("Result"), content=Text(str(res)))
                def _close3(ev):
                    dlg.open = False
                    page.update()
                dlg.actions = [ft.TextButton("Schließen", on_click=_close3)]
                page.show_dialog(dlg)
        except Exception as ex:
            dlg = ft.AlertDialog(title=Text("Fehler"), content=Text(str(ex)))
            def _close_err3(ev):
                dlg.open = False
                page.update()
            dlg.actions = [ft.TextButton("Schließen", on_click=_close_err3)]
            page.show_dialog(dlg)

    end_match_button = ElevatedButton("Match beenden", on_click=end_match_clicked)

    def place_bet_clicked(e):
        try:
            bettor = dd_bettor.value
            match_id = dd_match_bet.value
            amount = tf_amount.value
            bettype = dd_bet_type.value
            team_val = dd_target_team.value
            player_val = dd_target_player.value
            # choose target: prefer player if set
            if player_val:
                target = f"player:{player_val}"
            elif team_val:
                target = f"team:{team_val}"
            else:
                target = ""
            handicap_val = dd_handicap.value
            res = controller.place_bet(bettor, match_id, amount, bettype, target, handicap_val)
            if isinstance(res, BetPlaced):
                # build formatted bet details
                bet_obj = getattr(res, 'bet', None)
                bettor_res = controller.list_bettors()
                bettors = bettor_res.bettors if isinstance(bettor_res, BettorsListed) else (bettor_res if isinstance(bettor_res, list) else [])
                bettor_name = "Unbekannt"
                for b in bettors:
                    if str(getattr(b,'id','')) == str(bettor):
                        bettor_name = getattr(b,'name', str(bettor))
                        break
                # format bet details
                lines = [
                    f"Bettor: {bettor_name}",
                    f"Match-ID: {match_id}",
                    f"Betrag: {amount}",
                    f"Wetttyp: {bettype}",
                ]
                if team_val:
                    lines.append(f"Ziel: {team_val}")
                if player_val:
                    lines.append(f"Spieler: {player_val}")
                if handicap_val:
                    lines.append(f"Handicap: {handicap_val}")
                if bet_obj and hasattr(bet_obj, 'quota'):
                    lines.append(f"Quote: {getattr(bet_obj, 'quota', 'N/A'):.4f}")
                content = ft.Column([Text(l) for l in lines], tight=True)
                dlg = ft.AlertDialog(title=Text("Wette platziert"), content=content)
            else:
                msg = getattr(res,'message', str(res))
                dlg = ft.AlertDialog(title=Text("Wette"), content=Text(str(msg)))
            def _close(ev):
                dlg.open = False
                page.update()
            dlg.actions = [ft.TextButton("OK", on_click=_close)]
            page.show_dialog(dlg)
        except Exception as ex:
            dlg = ft.AlertDialog(title=Text("Fehler"), content=Text(str(ex)))
            def _close_err(ev):
                dlg.open = False
                page.update()
            dlg.actions = [ft.TextButton("Schließen", on_click=_close_err)]
            page.show_dialog(dlg)

    place_bet_button = ElevatedButton("Wette platzieren", on_click=place_bet_clicked)

    # Quotas row (separate line)
    page.add(
        Divider(),
        Text("Quoten anzeigen", weight=FontWeight.BOLD, size=20),
                Row([dd_match_quotas, btn_show_quotas], alignment=ft.MainAxisAlignment.START, spacing=8),
    )

    page.add(
        Divider(),
        Text("Wette platzieren", weight=FontWeight.BOLD, size=20),
        Row([dd_match_bet, btn_refresh_match, dd_bettor, tf_amount, dd_bet_type, dd_handicap, dd_target_team, dd_target_player, place_bet_button], alignment=ft.MainAxisAlignment.START, spacing=8),
    )

    # End match UI row
    page.add(
        Divider(),
        Text("Match beenden", weight=FontWeight.BOLD, size=20),
        Row([dd_match_end, btn_refresh_end, dd_winner, tf_remaining, dd_nacktemeile, dd_deathcup, dd_bitchcup, dd_overtime, end_match_button], alignment=ft.MainAxisAlignment.START, spacing=8),
    )

    # initial population of dropdowns
    try:
        refresh_player_dropdowns()
    except Exception:
        pass
    try:
        refresh_match_dropdowns()
    except Exception:
        pass
    try:
        refresh_bettor_dropdowns()
    except Exception:
        pass


if __name__ == "__main__":
    ft.app(main)
