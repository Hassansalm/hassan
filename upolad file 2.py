from flet import *
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']
TOKEN_FILE = "token.pickle"
CREDENTIALS_FILE = "credentials.json"

# ================== GOOGLE AUTH ==================
def get_drive_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as t:
            creds = pickle.load(t)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "wb") as t:
            pickle.dump(creds, t)

    return build("drive", "v3", credentials=creds)

# ================== FOLDER ==================
def get_or_create_folder(service, name, parent_id=None):
    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    res = service.files().list(q=query, fields="files(id,name)").execute()
    files = res.get("files", [])

    if files:
        return files[0]["id"]

    folder_metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder"
    }

    if parent_id:
        folder_metadata["parents"] = [parent_id]

    created = service.files().create(body=folder_metadata, fields="id").execute()
    return created["id"]

# ================== MAIN ==================
def main(page: Page):
    page.theme_mode = ThemeMode.DARK
    page.window.width = 400
    page.window.height = 800
    page.rtl = True

    service = get_drive_service()

    current_folder_id = {"id": None}
    navigation_stack = []

    # ===== INPUTS =====
    zone_name = TextField(label='zone num',color=colors.BLACK,
                          bgcolor="#FFFFFF",
                          helper_text='ex: zone 60..',
                          )
    fat_name = TextField(label='fat num',color=colors.BLACK,
                          bgcolor="#FFFFFF",
                          helper_text='ex: fat 29..',
                          )

    # ===== IMAGES =====
    image1 = Image(width=150, height=150, fit=ImageFit.COVER)
    image2 = Image(width=150, height=150, fit=ImageFit.COVER)
    image3 = Image(width=150, height=150, fit=ImageFit.COVER)
    image4 = Image(width=150, height=150, fit=ImageFit.COVER)

    # ===== FILE PICKER =====
    picker_target = {"img": None}

    def on_file(e: FilePickerResultEvent):
        if e.files:
            picker_target["img"].src = e.files[0].path
            page.update()

    picker = FilePicker(on_result=on_file)
    page.overlay.append(picker)

    def pick(img):
        picker_target["img"] = img
        picker.pick_files()

    # ===== UPLOAD =====
    def upload(e):
        if not zone_name.value or not fat_name.value:
            page.snack_bar = SnackBar(Text("أدخل البيانات"))
            page.snack_bar.open = True
            page.update()
            return

        z = get_or_create_folder(service, zone_name.value)
        f = get_or_create_folder(service, fat_name.value, z)

        for img, name in [(image1, "من داخل قبل"), (image2, "من خارج قبل"),(image3,"من داخل بعد"),(image4,"من خارج بعد")]:
            if img.src:
                media = MediaFileUpload(img.src)
                service.files().create(
                    body={"name": name, "parents": [f]},
                    media_body=media
                ).execute()
        page.snack_bar = SnackBar(Text("جاري رفع الصور..."))
        page.snack_bar = SnackBar(Text("تم الرفع"))
        page.snack_bar.open = True
        page.update()

    # ===== GRID =====
    grid = GridView(expand=True, runs_count=2, spacing=10)

    # ===== IMAGE VIEW =====
    def open_image(url, title):
        dlg = AlertDialog(
            content=Column([
                Text(title),
                Image(src=url, expand=True)
            ]),
            actions=[
                TextButton("إغلاق", on_click=lambda e: close_dialog(dlg))
            ]
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def close_dialog(dlg):
        dlg.open = False
        page.update()

    # ===== LOAD FILES =====
    def load(folder_id=None):
        grid.controls.clear()

        query = f"'{folder_id or 'root'}' in parents and trashed=false"
        res = service.files().list(
            q=query,
            fields="files(id,name,mimeType)"
        ).execute()

        for f in res.get("files", []):
            if f["mimeType"] == "application/vnd.google-apps.folder":
                grid.controls.append(
                    GestureDetector(
                        on_tap=lambda e, fid=f["id"]: open_folder(fid),
                        content=Container(
                            expand=True,
                            ink=True,
                            alignment=alignment.center,
                            bgcolor=colors.with_opacity(0.1, colors.WHITE),
                            border_radius=10,
                            padding=10,
                            content=Column(
                                [
                                    Icon(icons.FOLDER, size=40),
                                    Text(f["name"], size=12)
                                ],
                                alignment=MainAxisAlignment.CENTER,
                                horizontal_alignment=CrossAxisAlignment.CENTER
                            )
                        )
                    )
                )
            else:
                url = f"https://lh3.googleusercontent.com/d/{f['id']}"
                grid.controls.append(
                    GestureDetector(
                        on_tap=lambda e, u=url, n=f["name"]: open_image(u, n),
                        content=Container(
                            content=Column([
                                Image(src=url, height=120, fit=ImageFit.COVER),
                                Text(f["name"], size=10)
                            ]),
                            padding=5,
                            bgcolor=colors.BLACK12,
                            border_radius=10
                        )
                    )
                )

        page.update()

    # ===== NAVIGATION =====
    def open_folder(fid):
        navigation_stack.append(current_folder_id["id"])
        current_folder_id["id"] = fid
        load(fid)

    def back(e):
        if navigation_stack:
            prev = navigation_stack.pop()
            current_folder_id["id"] = prev
            load(prev)

    # ===== UI =====
    def show(i):
        page.controls.clear()

        if i == 0:
            page.add(
                zone_name, fat_name,
                Row([
                    ElevatedButton("قبل للفات من الخارج", on_click=lambda e: pick(image1)),
                    ElevatedButton("قبل للفات من الداخل", on_click=lambda e: pick(image2))
                ]),
                Row([image1, image2]),
                Row([
                    ElevatedButton("بعد للفات من الخارج" , bgcolor=colors.GREY ,
                                     
                                     
                                     on_click=lambda e: pick(image1)),
                    ElevatedButton("بعد للفات من الداخل" , bgcolor=colors.GREY ,
                                     
                                     
                                     on_click=lambda e: pick(image1))
                ]),
                Row([image3,image4]),
                Row([
                    ElevatedButton("رفع", on_click=upload)
                ],alignment=MainAxisAlignment.CENTER)
            )

        if i == 1:
            page.add(
                Row([
                    IconButton(icons.ARROW_BACK, on_click=back),
                    IconButton(icons.REFRESH, on_click=lambda e: load(current_folder_id["id"]))
                ]),
                grid
            )
            load(current_folder_id["id"])

        page.update()

    page.navigation_bar = NavigationBar(
        destinations=[
            NavigationBarDestination(icon=icons.UPLOAD),
            NavigationBarDestination(icon=icons.FOLDER)
        ],
        on_change=lambda e: show(e.control.selected_index)
    )

    show(0)

app(target=main)
