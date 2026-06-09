import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import (
    SquareModuleDrawer, RoundedModuleDrawer, CircleModuleDrawer, GappedSquareModuleDrawer
)
from PIL import Image, ImageTk
import io
import os

# ---------- Renkler ----------
BG        = "#f8f7f4"
SURFACE   = "#ffffff"
BORDER    = "#e0ddd6"
TEXT      = "#1a1a18"
MUTED     = "#6b6b67"
ACCENT    = "#5b4fcf"
ACCENT_FG = "#ffffff"
DANGER    = "#c0392b"

class QROlusturucu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("QR Oluşturucu")
        self.configure(bg=BG)
        self.resizable(False, False)

        self.qr_img_pil  = None   # kaydetmek için orijinal PIL
        self.qr_img_tk   = None   # canvas için
        self.on_renk     = "#000000"
        self.arka_renk   = "#ffffff"

        self._widgets()
        self._center()

    # ── Pencereyi ortala ──────────────────────────────────────────
    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{(sw-w)//2}+{(sh-h)//2}")

    # ── Yardımcı widget oluşturucular ─────────────────────────────
    def _kart(self, parent, **kwargs):
        f = tk.Frame(parent, bg=SURFACE, bd=0, highlightthickness=1,
                     highlightbackground=BORDER, **kwargs)
        return f

    def _etiket(self, parent, text, bold=False, muted=False):
        return tk.Label(parent, text=text,
                        bg=parent.cget("bg"),
                        fg=MUTED if muted else TEXT,
                        font=("Segoe UI", 9, "bold" if bold else "normal"))

    def _dugme(self, parent, text, cmd, primary=False, danger=False, width=14):
        bg = ACCENT if primary else (DANGER if danger else SURFACE)
        fg = ACCENT_FG if (primary or danger) else TEXT
        b = tk.Button(parent, text=text, command=cmd,
                      bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
                      relief="flat", bd=0, cursor="hand2",
                      font=("Segoe UI", 9, "bold" if primary else "normal"),
                      width=width, pady=6)
        b.bind("<Enter>", lambda e: b.config(bg=self._hover(bg)))
        b.bind("<Leave>", lambda e: b.config(bg=bg))
        return b

    def _hover(self, hex_color):
        r, g, b = int(hex_color[1:3],16), int(hex_color[3:5],16), int(hex_color[5:7],16)
        d = -20 if (r+g+b)/3 > 128 else 20
        return "#{:02x}{:02x}{:02x}".format(
            max(0,min(255,r+d)), max(0,min(255,g+d)), max(0,min(255,b+d)))

    # ── Arayüz ────────────────────────────────────────────────────
    def _widgets(self):
        # ── Başlık ──
        baslik = tk.Frame(self, bg=BG)
        baslik.pack(fill="x", padx=20, pady=(18, 0))
        tk.Label(baslik, text="✦  QR Oluşturucu", bg=BG,
                 fg=TEXT, font=("Segoe UI", 15, "bold")).pack(side="left")

        ana = tk.Frame(self, bg=BG)
        ana.pack(padx=20, pady=14, fill="both")

        sol = tk.Frame(ana, bg=BG)
        sol.pack(side="left", fill="y", padx=(0,14))

        sag = tk.Frame(ana, bg=BG)
        sag.pack(side="left", fill="y")

        # ── İçerik girişi ──
        giris_kart = self._kart(sol)
        giris_kart.pack(fill="x", pady=(0,10))

        ic = tk.Frame(giris_kart, bg=SURFACE)
        ic.pack(padx=12, pady=12)

        self._etiket(ic, "İÇERİK", bold=True).grid(row=0, column=0, sticky="w", pady=(0,4))

        # Tür seçimi
        tur_frame = tk.Frame(ic, bg=SURFACE)
        tur_frame.grid(row=1, column=0, sticky="w", pady=(0,8))
        self._etiket(tur_frame, "Tür:", muted=True).pack(side="left", padx=(0,6))
        self.tur_var = tk.StringVar(value="Metin / URL")
        turler = ["Metin / URL", "E-posta", "Telefon", "SMS", "WiFi", "vCard (Kartvizit)"]
        tur_menu = ttk.Combobox(tur_frame, textvariable=self.tur_var,
                                values=turler, state="readonly", width=18,
                                font=("Segoe UI", 9))
        tur_menu.pack(side="left")
        tur_menu.bind("<<ComboboxSelected>>", self._tur_degisti)

        # Dinamik form alanı
        self.form_frame = tk.Frame(ic, bg=SURFACE)
        self.form_frame.grid(row=2, column=0, sticky="w")
        self._metin_formu()

        # ── Ayarlar ──
        ayar_kart = self._kart(sol)
        ayar_kart.pack(fill="x", pady=(0,10))
        ay = tk.Frame(ayar_kart, bg=SURFACE)
        ay.pack(padx=12, pady=12)

        self._etiket(ay, "AYARLAR", bold=True).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0,8))

        # Boyut
        self._etiket(ay, "Boyut:", muted=True).grid(row=1, column=0, sticky="w", padx=(0,6))
        self.boyut_var = tk.IntVar(value=300)
        boyut_scale = tk.Scale(ay, from_=150, to=600, orient="horizontal",
                               variable=self.boyut_var, length=150,
                               bg=SURFACE, fg=TEXT, highlightthickness=0,
                               troughcolor=BORDER, activebackground=ACCENT,
                               sliderrelief="flat", bd=0)
        boyut_scale.grid(row=1, column=1, padx=(0,6))
        self.boyut_lbl = tk.Label(ay, textvariable=tk.StringVar(), bg=SURFACE, fg=MUTED,
                                  font=("Segoe UI",9))
        self.boyut_lbl.grid(row=1, column=2, sticky="w")
        def guncelle_boyut(*a):
            self.boyut_lbl.config(text=f"{self.boyut_var.get()}px")
        self.boyut_var.trace_add("write", guncelle_boyut)
        guncelle_boyut()

        # Hata düzeltme
        self._etiket(ay, "Hata Düz.:", muted=True).grid(row=2, column=0, sticky="w", pady=(8,0), padx=(0,6))
        self.hata_var = tk.StringVar(value="M — Orta")
        hata_menu = ttk.Combobox(ay, textvariable=self.hata_var,
                                 values=["L — Düşük (%7)", "M — Orta (%15)", "Q — Yüksek (%25)", "H — Maksimum (%30)"],
                                 state="readonly", width=17, font=("Segoe UI",9))
        hata_menu.grid(row=2, column=1, columnspan=2, sticky="w", pady=(8,0))

        # Stil
        self._etiket(ay, "Modül Stili:", muted=True).grid(row=3, column=0, sticky="w", pady=(8,0), padx=(0,6))
        self.stil_var = tk.StringVar(value="Kare")
        stil_menu = ttk.Combobox(ay, textvariable=self.stil_var,
                                 values=["Kare", "Yuvarlak Köşe", "Daire", "Boşluklu Kare"],
                                 state="readonly", width=17, font=("Segoe UI",9))
        stil_menu.grid(row=3, column=1, columnspan=2, sticky="w", pady=(8,0))

        # Renkler
        renk_frame = tk.Frame(ay, bg=SURFACE)
        renk_frame.grid(row=4, column=0, columnspan=3, sticky="w", pady=(10,0))

        self._etiket(renk_frame, "QR Rengi:", muted=True).pack(side="left", padx=(0,6))
        self.on_renk_btn = tk.Button(renk_frame, width=3, relief="flat", bd=1,
                                     bg=self.on_renk, cursor="hand2",
                                     command=lambda: self._renk_sec("on"))
        self.on_renk_btn.pack(side="left", padx=(0,12))

        self._etiket(renk_frame, "Arkaplan:", muted=True).pack(side="left", padx=(0,6))
        self.arka_renk_btn = tk.Button(renk_frame, width=3, relief="flat", bd=1,
                                       bg=self.arka_renk, cursor="hand2",
                                       command=lambda: self._renk_sec("arka"))
        self.arka_renk_btn.pack(side="left")

        # ── Butonlar ──
        btn_frame = tk.Frame(sol, bg=BG)
        btn_frame.pack(fill="x")
        self._dugme(btn_frame, "✦  Oluştur", self._olustur, primary=True, width=16).pack(side="left", padx=(0,8))
        self._dugme(btn_frame, "💾  Kaydet", self._kaydet, width=12).pack(side="left", padx=(0,8))
        self._dugme(btn_frame, "✕  Temizle", self._temizle, danger=True, width=10).pack(side="left")

        # ── Önizleme ──
        oniz_kart = self._kart(sag)
        oniz_kart.pack(fill="both", expand=True)
        oi = tk.Frame(oniz_kart, bg=SURFACE)
        oi.pack(padx=12, pady=12)
        self._etiket(oi, "ÖNİZLEME", bold=True).pack(anchor="w", pady=(0,8))
        self.canvas = tk.Canvas(oi, width=300, height=300, bg=BORDER,
                                bd=0, highlightthickness=0)
        self.canvas.pack()
        self.canvas_placeholder()

    # ── Form türleri ──────────────────────────────────────────────
    def _form_temizle(self):
        for w in self.form_frame.winfo_children():
            w.destroy()

    def _entry(self, parent, placeholder="", width=32, show=""):
        e = tk.Entry(parent, width=width, relief="flat", bd=0,
                     bg="#f1efe9", fg=TEXT, insertbackground=TEXT,
                     font=("Segoe UI", 9), show=show)
        e.insert(0, placeholder)
        e.bind("<FocusIn>",  lambda ev, en=e, ph=placeholder: en.delete(0,"end") if en.get()==ph else None)
        e.bind("<FocusOut>", lambda ev, en=e, ph=placeholder: en.insert(0,ph) if en.get()==""  else None)
        return e

    def _satir(self, parent, etiket, widget, row):
        tk.Label(parent, text=etiket, bg=SURFACE, fg=MUTED,
                 font=("Segoe UI",9), width=10, anchor="w").grid(row=row, column=0, sticky="w", pady=3)
        widget.grid(row=row, column=1, sticky="w", pady=3)

    def _metin_formu(self):
        self._form_temizle()
        f = self.form_frame
        self.metin_entry = tk.Text(f, width=32, height=5, relief="flat",
                                   bg="#f1efe9", fg=TEXT, insertbackground=TEXT,
                                   font=("Segoe UI",9), wrap="word", bd=4)
        self.metin_entry.grid(row=0, column=0, columnspan=2)
        self.metin_entry.insert("1.0", "https://")

    def _eposta_formu(self):
        self._form_temizle()
        f = self.form_frame
        self.ep_adres = self._entry(f, "ornek@email.com")
        self.ep_konu  = self._entry(f, "Konu")
        self.ep_mesaj = self._entry(f, "Mesaj")
        self._satir(f, "E-posta:", self.ep_adres, 0)
        self._satir(f, "Konu:",    self.ep_konu,  1)
        self._satir(f, "Mesaj:",   self.ep_mesaj, 2)

    def _telefon_formu(self):
        self._form_temizle()
        f = self.form_frame
        self.tel_entry = self._entry(f, "+90 5xx xxx xx xx", width=26)
        self._satir(f, "Telefon:", self.tel_entry, 0)

    def _sms_formu(self):
        self._form_temizle()
        f = self.form_frame
        self.sms_tel = self._entry(f, "+90 5xx xxx xx xx", width=26)
        self.sms_msg = self._entry(f, "Mesaj metni", width=26)
        self._satir(f, "Telefon:", self.sms_tel, 0)
        self._satir(f, "Mesaj:",   self.sms_msg, 1)

    def _wifi_formu(self):
        self._form_temizle()
        f = self.form_frame
        self.wifi_ssid = self._entry(f, "Ağ adı (SSID)", width=26)
        self.wifi_sifre = self._entry(f, "Şifre", width=26)
        self.wifi_tip = tk.StringVar(value="WPA")
        tip_frame = tk.Frame(f, bg=SURFACE)
        for t in ["WPA","WEP","Açık"]:
            tk.Radiobutton(tip_frame, text=t, variable=self.wifi_tip, value=t,
                           bg=SURFACE, fg=TEXT, activebackground=SURFACE,
                           font=("Segoe UI",9)).pack(side="left", padx=(0,8))
        self._satir(f, "SSID:",  self.wifi_ssid,  0)
        self._satir(f, "Şifre:", self.wifi_sifre, 1)
        self._satir(f, "Güvenlik:", tip_frame, 2)

    def _vcard_formu(self):
        self._form_temizle()
        f = self.form_frame
        self.vc_ad     = self._entry(f, "Ad Soyad", width=26)
        self.vc_tel    = self._entry(f, "Telefon",  width=26)
        self.vc_email  = self._entry(f, "E-posta",  width=26)
        self.vc_sirket = self._entry(f, "Şirket",   width=26)
        self.vc_web    = self._entry(f, "Web sitesi", width=26)
        for i,(lbl,w) in enumerate([
            ("Ad Soyad:", self.vc_ad),
            ("Telefon:",  self.vc_tel),
            ("E-posta:",  self.vc_email),
            ("Şirket:",   self.vc_sirket),
            ("Web:",      self.vc_web),
        ]):
            self._satir(f, lbl, w, i)

    def _tur_degisti(self, event=None):
        tur = self.tur_var.get()
        {"Metin / URL":    self._metin_formu,
         "E-posta":        self._eposta_formu,
         "Telefon":        self._telefon_formu,
         "SMS":            self._sms_formu,
         "WiFi":           self._wifi_formu,
         "vCard (Kartvizit)": self._vcard_formu,
        }[tur]()

    # ── İçerik üret ───────────────────────────────────────────────
    def _icerik_al(self):
        tur = self.tur_var.get()
        def g(e):  # entry değeri
            v = e.get().strip()
            return v if v not in ("", None) else ""
        def placeholder_mi(e, ph):
            return e.get().strip() == ph

        if tur == "Metin / URL":
            v = self.metin_entry.get("1.0","end").strip()
            return v or None

        elif tur == "E-posta":
            adres = g(self.ep_adres)
            konu  = g(self.ep_konu)
            mesaj = g(self.ep_mesaj)
            if not adres or placeholder_mi(self.ep_adres,"ornek@email.com"):
                return None
            return f"mailto:{adres}?subject={konu}&body={mesaj}"

        elif tur == "Telefon":
            tel = g(self.tel_entry)
            return f"tel:{tel}" if tel and not placeholder_mi(self.tel_entry,"+90 5xx xxx xx xx") else None

        elif tur == "SMS":
            tel = g(self.sms_tel)
            msg = g(self.sms_msg)
            return f"sms:{tel}?body={msg}" if tel and not placeholder_mi(self.sms_tel,"+90 5xx xxx xx xx") else None

        elif tur == "WiFi":
            ssid  = g(self.wifi_ssid)
            sifre = g(self.wifi_sifre)
            tip   = self.wifi_tip.get()
            if not ssid or placeholder_mi(self.wifi_ssid,"Ağ adı (SSID)"):
                return None
            return f"WIFI:T:{tip};S:{ssid};P:{sifre};;"

        elif tur == "vCard (Kartvizit)":
            ad = g(self.vc_ad)
            if not ad or placeholder_mi(self.vc_ad,"Ad Soyad"):
                return None
            tel    = "" if placeholder_mi(self.vc_tel,"Telefon")    else g(self.vc_tel)
            email  = "" if placeholder_mi(self.vc_email,"E-posta")  else g(self.vc_email)
            sirket = "" if placeholder_mi(self.vc_sirket,"Şirket")  else g(self.vc_sirket)
            web    = "" if placeholder_mi(self.vc_web,"Web sitesi") else g(self.vc_web)
            lines = ["BEGIN:VCARD","VERSION:3.0",f"FN:{ad}"]
            if tel:    lines.append(f"TEL:{tel}")
            if email:  lines.append(f"EMAIL:{email}")
            if sirket: lines.append(f"ORG:{sirket}")
            if web:    lines.append(f"URL:{web}")
            lines.append("END:VCARD")
            return "\n".join(lines)

    # ── QR oluştur ────────────────────────────────────────────────
    def _olustur(self):
        icerik = self._icerik_al()
        if not icerik:
            messagebox.showwarning("Eksik Bilgi", "Lütfen gerekli alanları doldurun.")
            return

        hata_map = {
            "L — Düşük (%7)":    qrcode.constants.ERROR_CORRECT_L,
            "M — Orta (%15)":    qrcode.constants.ERROR_CORRECT_M,
            "Q — Yüksek (%25)":  qrcode.constants.ERROR_CORRECT_Q,
            "H — Maksimum (%30)":qrcode.constants.ERROR_CORRECT_H,
        }
        stil_map = {
            "Kare":           SquareModuleDrawer(),
            "Yuvarlak Köşe":  RoundedModuleDrawer(),
            "Daire":          CircleModuleDrawer(),
            "Boşluklu Kare":  GappedSquareModuleDrawer(),
        }

        hata  = hata_map.get(self.hata_var.get(), qrcode.constants.ERROR_CORRECT_M)
        stil  = stil_map.get(self.stil_var.get(), SquareModuleDrawer())
        boyut = self.boyut_var.get()

        qr = qrcode.QRCode(error_correction=hata, box_size=10, border=4)
        qr.add_data(icerik)
        qr.make(fit=True)

        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=stil,
            color_mask=None,
        ).convert("RGB")

        # Renk uygula
        if self.on_renk != "#000000" or self.arka_renk != "#ffffff":
            from PIL import Image as PILImage
            w, h = img.size
            pixels = img.load()
            on_r  = tuple(int(self.on_renk[i:i+2],16) for i in (1,3,5))
            arka_r = tuple(int(self.arka_renk[i:i+2],16) for i in (1,3,5))
            for y in range(h):
                for x in range(w):
                    r,g,b = pixels[x,y]
                    pixels[x,y] = arka_r if (r+g+b)/3 > 128 else on_r

        img = img.resize((boyut, boyut), Image.LANCZOS)
        self.qr_img_pil = img

        # Canvas güncelle
        self.canvas.config(width=min(boyut,360), height=min(boyut,360))
        goster = img.resize((min(boyut,360), min(boyut,360)), Image.LANCZOS)
        self.qr_img_tk = ImageTk.PhotoImage(goster)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.qr_img_tk)

    # ── Kaydet ────────────────────────────────────────────────────
    def _kaydet(self):
        if not self.qr_img_pil:
            messagebox.showinfo("Bilgi", "Önce bir QR kodu oluşturun.")
            return
        yol = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")],
            title="QR Kodunu Kaydet"
        )
        if yol:
            self.qr_img_pil.save(yol)
            messagebox.showinfo("Kaydedildi", f"QR kod kaydedildi:\n{yol}")

    # ── Renk seç ──────────────────────────────────────────────────
    def _renk_sec(self, tip):
        mevcut = self.on_renk if tip == "on" else self.arka_renk
        renk = colorchooser.askcolor(color=mevcut, title="Renk Seç")[1]
        if renk:
            if tip == "on":
                self.on_renk = renk
                self.on_renk_btn.config(bg=renk)
            else:
                self.arka_renk = renk
                self.arka_renk_btn.config(bg=renk)

    # ── Temizle ───────────────────────────────────────────────────
    def _temizle(self):
        self._tur_degisti()
        self.boyut_var.set(300)
        self.hata_var.set("M — Orta (%15)")
        self.stil_var.set("Kare")
        self.on_renk = "#000000"
        self.arka_renk = "#ffffff"
        self.on_renk_btn.config(bg="#000000")
        self.arka_renk_btn.config(bg="#ffffff")
        self.qr_img_pil = None
        self.qr_img_tk = None
        self.canvas.config(width=300, height=300)
        self.canvas_placeholder()

    def canvas_placeholder(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0,0,300,300, fill=BORDER, outline="")
        self.canvas.create_text(150,150, text="QR önizleme\nburada görünür",
                                fill=MUTED, font=("Segoe UI",11), justify="center")


if __name__ == "__main__":
    app = QROlusturucu()
    app.mainloop()