# -*- coding: utf-8 -*-
import os, sys, csv, json, calendar, uuid, zipfile
from datetime import datetime, date

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput as _KivyTextInput
from kivy.uix.button import Button as _KivyButton
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle

# ---------- Paleta
Window.clearcolor = (0.05, 0.06, 0.08, 1)
COLOR_FONDO   = (0.10, 0.11, 0.14, 1)
COLOR_TARJETA = (0.15, 0.16, 0.20, 1)
COLOR_BORDE   = (0.22, 0.24, 0.28, 1)
COLOR_TEXTO   = (1, 1, 1, 1)
AZUL_NORM     = (0.10, 0.52, 0.82, 1)
AZUL_DOWN     = (0.08, 0.40, 0.64, 1)

CSV_FILE="registros.csv"; SETTINGS_FILE="config.json"; INVENTARIO_FILE="inventario.csv"

# ---------- Controles 3D
class ThreeDButton(_KivyButton):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.color=(1,1,1,1); self.background_normal=''; self.background_down=''; self.background_color=(0,0,0,0)
        if self.size_hint_y is not None: self.size_hint_y=None; self.height=dp(50)
        with self.canvas.before:
            self._c_body=Color(rgba=AZUL_NORM); self._r_body=RoundedRectangle(radius=[dp(12),])
            self._c_shadow=Color(rgba=(0,0,0,0.35)); self._r_shadow=RoundedRectangle(radius=[dp(12),])
            self._c_light=Color(rgba=(1,1,1,0.12)); self._r_light=RoundedRectangle(radius=[dp(12),])
        self.bind(pos=self._upd, size=self._upd, state=self._upd_state)
    def _upd(self,*_):
        x,y,w,h=self.x,self.y,self.width,self.height
        self._r_body.pos=(x,y); self._r_body.size=(w,h)
        self._r_shadow.pos=(x,y-dp(1.5)); self._r_shadow.size=(w,dp(4))
        self._r_light.pos=(x,y+h-dp(4)); self._r_light.size=(w,dp(4))
    def _upd_state(self,*_):
        self._c_body.rgba = AZUL_DOWN if self.state=='down' else AZUL_NORM
        self._upd()

class FlatPanel(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            Color(*COLOR_FONDO); self._bg=RoundedRectangle(radius=[dp(16),])
        self.bind(pos=self._u, size=self._u)
    def _u(self,*_): self._bg.pos=self.pos; self._bg.size=self.size

class CleanTextInput(_KivyTextInput):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.background_normal=''; self.background_active=''; self.background_color=(0,0,0,0)
        self.foreground_color=(1,1,1,1); self.cursor_color=(1,1,1,1); self.padding=(10,10)

# Tarjeta 3D para imágenes
class ImageCard(BoxLayout):
    def __init__(self, source, **kw):
        kw.setdefault("size_hint", (None, None))
        super().__init__(**kw)
        self.orientation="vertical"
        self.padding = [dp(10), dp(10), dp(10), dp(10)]
        with self.canvas.before:
            Color(0,0,0,0.30); self._shadow = RoundedRectangle(radius=[dp(18),])
            Color(*COLOR_TARJETA); self._bg = RoundedRectangle(radius=[dp(18),])
        self.bind(pos=self._upd, size=self._upd)
        self.img = Image(source=source, allow_stretch=True, keep_ratio=True)
        self.add_widget(self.img)
    def _upd(self,*_):
        self._shadow.pos=(self.x, self.y-dp(2)); self._shadow.size=(self.width, self.height+dp(2))
        self._bg.pos=self.pos; self._bg.size=self.size

Button=ThreeDButton; TextInput=CleanTextInput

# ---------- Utils
def today_str(): return datetime.now().strftime("%Y-%m-%d")
def _to_float(s):
    try: return float((s or "").strip())
    except: return 0.0
def _set(o,a,v): setattr(o,a,v); return None
def ancho_form(): return min(Window.width*0.95, dp(860))

def _label_col(t):
    lbl=Label(text=t, color=COLOR_TEXTO, size_hint_y=None, height=dp(40),
              size_hint_x=None, width=dp(220), halign="right", valign="middle")
    lbl.bind(size=lambda l,*_: setattr(l, "text_size", (l.width, None)))
    return lbl

def popup_texto(msg, title="Mensaje"):
    p=Popup(title=title, size_hint=(0.92,None), height=dp(280))
    box=BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
    sv=ScrollView(size_hint=(1,1), scroll_type=['bars','content'], bar_width=dp(6),
                  bar_color=(.75,.75,.75,.95), bar_inactive_color=(.75,.75,.75,.35))
    lbl=Label(text=msg, color=COLOR_TEXTO, size_hint_y=None)
    sv.add_widget(lbl)
    box.add_widget(sv)
    ok=Button(text="OK", size_hint_y=None, height=dp(46)); ok.bind(on_release=p.dismiss)
    box.add_widget(ok); p.add_widget(box); p.open()

def campo_estilizado(layout,titulo,ref_owner=None,ref_name=None,filtro=None,valor="",hint="",multiline=False,alto=None):
    layout.add_widget(_label_col(titulo))
    h=alto if alto else (dp(100) if multiline else dp(44))
    caja=BoxLayout(size_hint_y=None,height=h,padding=[dp(10),dp(6),dp(10),dp(6)],
                   size_hint_x=None, width=dp(520))
    with caja.canvas.before:
        Color(*COLOR_BORDE); caja.border=RoundedRectangle(radius=[dp(12),])
        Color(*COLOR_TARJETA); caja.bg=RoundedRectangle(radius=[dp(12),])
    caja.bind(pos=lambda i,*_:(_set(i.border,"pos",(i.x-dp(1),i.y-dp(1))),
                               _set(i.border,"size",(i.width+dp(2),i.height+dp(2))),
                               _set(i.bg,"pos",i.pos),_set(i.bg,"size",i.size)))
    ti=TextInput(multiline=multiline,hint_text=hint,text=valor)
    if filtro: ti.input_filter=filtro
    caja.add_widget(ti); layout.add_widget(caja)
    if ref_owner is not None and ref_name:
        if isinstance(ref_owner,dict): ref_owner[ref_name]=ti
        else: setattr(ref_owner,ref_name,ti)
    return ti

def etiqueta_fija(txt,tam="15sp",negrita=False):
    t=f"[b]{txt}[/b]" if negrita else txt
    return Label(text=t,markup=True,color=COLOR_TEXTO,size_hint_y=None,height=dp(24),font_size=tam)

# ---------- Selector Fecha/Hora
class DateTimePicker(Popup):
    def __init__(self,target_textinput:TextInput,**kw):
        super().__init__(**kw)
        self.title="Seleccionar fecha y hora"; self.size_hint=(0.92,None); self.height=dp(360); self._target=target_textinput
        hoy=datetime.now(); y0,m0,d0=hoy.year,hoy.month,hoy.day; hh=hoy.hour; mm=hoy.minute-(hoy.minute%5)
        root=FlatPanel(orientation="vertical",padding=dp(12),spacing=dp(10))
        fila=GridLayout(cols=5,spacing=dp(8),size_hint_y=None,height=dp(44))
        self.sp_year=Spinner(text=str(y0),values=[str(y) for y in range(y0-5,y0+6)],size_hint_x=None,width=dp(90))
        self.sp_month=Spinner(text=str(m0),values=[str(m) for m in range(1,13)],size_hint_x=None,width=dp(70))
        self.sp_day=Spinner(text=str(d0),values=[str(d) for d in range(1,32)],size_hint_x=None,width=dp(70))
        self.sp_hour=Spinner(text=f"{hh:02d}",values=[f"{h:02d}" for h in range(24)],size_hint_x=None,width=dp(70))
        self.sp_min=Spinner(text=f"{mm:02d}",values=[f"{m:02d}" for m in range(0,60,5)],size_hint_x=None,width=dp(70))
        for w in [self.sp_year,self.sp_month,self.sp_day,self.sp_hour,self.sp_min]: fila.add_widget(w)
        root.add_widget(fila)
        def _recalc(*_):
            y=int(self.sp_year.text); m=int(self.sp_month.text); mx=calendar.monthrange(y,m)[1]
            self.sp_day.values=[str(d) for d in range(1,mx+1)]
            if int(self.sp_day.text)>mx: self.sp_day.text=str(mx)
        self.sp_year.bind(text=_recalc); self.sp_month.bind(text=_recalc); _recalc()
        btns=BoxLayout(size_hint_y=None,height=dp(46),spacing=dp(8))
        bset=Button(text="Usar fecha/hora"); bnow=Button(text="Ahora"); bcan=Button(text="Cancelar")
        btns.add_widget(bset); btns.add_widget(bnow); btns.add_widget(bcan)
        def _apply(*_):
            y=int(self.sp_year.text); m=int(self.sp_month.text); d=int(self.sp_day.text)
            hh=int(self.sp_hour.text); mm=int(self.sp_min.text)
            self._target.text=f"{y:04d}-{m:02d}-{d:02d} {hh:02d}:{mm:02d}"; self.dismiss()
        bset.bind(on_release=_apply)
        bnow.bind(on_release=lambda *_:(setattr(self._target,'text',datetime.now().strftime("%Y-%m-%d %H:%M")),self.dismiss()))
        bcan.bind(on_release=lambda *_: self.dismiss())
        self.add_widget(root); root.add_widget(btns)

# ---------- MENÚ (versión segura)
class MenuScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

        root = FlatPanel(orientation="vertical", padding=dp(10), spacing=dp(10))
        self.add_widget(root)

        sv = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False, do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=dp(6),
            bar_color=(.75, .75, .75, .95),
            bar_inactive_color=(.75, .75, .75, .35),
            scroll_wheel_distance=dp(80),
        )
        root.add_widget(sv)

        content = BoxLayout(orientation="vertical", spacing=dp(18),
                            size_hint_y=None, padding=dp(20))
        content.bind(minimum_height=lambda i, v: setattr(content, "height", v))
        sv.add_widget(content)

        title = Label(text="[b]Bitácora de Mantenciones[/b]",
                      markup=True, font_size="26sp", color=COLOR_TEXTO,
                      size_hint=(1, None), height=dp(60))
        content.add_widget(title)

        col_wrap = AnchorLayout(anchor_x="center", anchor_y="center",
                                size_hint=(1, None))
        content.add_widget(col_wrap)

        col = BoxLayout(orientation="vertical", spacing=dp(12),
                        size_hint=(None, None),
                        width=min(Window.width * 0.9, dp(520)))
        col.bind(minimum_height=lambda i, v: setattr(col, "height", v))
        col_wrap.bind(size=lambda w, *_: setattr(col_wrap, "height", col.height))
        col_wrap.add_widget(col)

        def go(name): return lambda *_: App.get_running_app().goto(name)

        # Cambiado "Opciones" -> "Configuración"
        for texto, destino in [
            ("Motor principal","form_motor"),
            ("Generador","form_generador"),
            ("Ver registros","list_menu"),
            ("Configuración","options"),
            ("Inventario","inventario"),
        ]:
            b = Button(text=texto, size_hint_y=None, height=dp(50), font_size="16sp")
            b.bind(on_release=go(destino))
            col.add_widget(b)

        bsalir = Button(text="Salir", size_hint_y=None, height=dp(50), font_size="16sp")
        bsalir.bind(on_release=lambda *_: App.get_running_app().exit_app())
        col.add_widget(bsalir)

        img_path = "bitacora_maquinas.png"
        has_img = os.path.exists(img_path)
        img_card = ImageCard(source=img_path if has_img else "", size=(dp(260), dp(180)))

        if not has_img:
            img_card.clear_widgets()
            img_card.add_widget(Label(
                text="[b]Coloca[/b] bitacora_maquinas.png\n(junto a main.py)",
                markup=True, color=COLOR_TEXTO, font_size="14sp"
            ))

        img_wrap = AnchorLayout(anchor_x="center", anchor_y="center",
                                size_hint=(1, None), height=img_card.height + dp(20))
        img_wrap.add_widget(img_card)
        content.add_widget(img_wrap)

# ---------- Submenú: Ver registros
class ListMenuScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        fondo=FlatPanel(orientation="vertical",padding=dp(10),spacing=dp(10))
        bar=BoxLayout(size_hint_y=None,height=dp(44),spacing=dp(8))
        b=Button(text="< Menú",size_hint_x=None,width=dp(110))
        b.bind(on_release=lambda *_: App.get_running_app().goto("menu"))
        bar.add_widget(b)
        bar.add_widget(Label(text="[b]Ver registros[/b]",markup=True,font_size="20sp",color=COLOR_TEXTO))
        fondo.add_widget(bar)
        col=BoxLayout(orientation="vertical",spacing=dp(12),size_hint=(None,None),width=min(Window.width*0.9, dp(520)))
        def go(n): return lambda *_: App.get_running_app().goto(n)
        for t, dest in [("Motor principal","list_motor"),("Generador","list_generador"),("Inventario","list_inventario")]:
            bt=Button(text=t,size_hint_y=None,height=dp(50)); bt.bind(on_release=go(dest)); col.add_widget(bt)
        cen=AnchorLayout(anchor_x="center",anchor_y="center"); cen.add_widget(col)
        fondo.add_widget(cen); self.add_widget(fondo)

# ---------- Adjuntos
def seleccionar_archivos(multiple=True):
    try:
        from plyer import filechooser
        return filechooser.open_file(multiple=multiple) or []
    except Exception as e:
        popup_texto(f"No se pudo abrir el selector de archivos.\n{e}"); return []

# ---------- Form Motor
class FormMotor(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.attachments=[]
        fondo=FlatPanel(orientation="vertical",padding=dp(10),spacing=dp(10))
        bar=BoxLayout(size_hint_y=None,height=dp(44),spacing=dp(8))
        b=Button(text="< Menú",size_hint_x=None,width=dp(110))
        b.bind(on_release=lambda *_: App.get_running_app().goto("menu"))
        bar.add_widget(b)
        bar.add_widget(Label(text="[b]Nuevo registro — Motor principal[/b]",
                             markup=True,font_size="20sp",color=COLOR_TEXTO))
        fondo.add_widget(bar)

        self.scroll=ScrollView(size_hint=(1,1), do_scroll_y=True, do_scroll_x=False,
                               scroll_type=['bars','content'], bar_width=dp(6),
                               bar_color=(.75,.75,.75,.95), bar_inactive_color=(.75,.75,.75,.35),
                               scroll_wheel_distance=dp(80))
        self.form=GridLayout(cols=2,spacing=dp(10),padding=dp(16),
                             size_hint=(None,None),width=ancho_form())
        self.form.cols_minimum = {0: dp(220), 1: dp(380)}
        self.form.bind(minimum_height=lambda i,v:setattr(self.form,"height",v))

        self.nave = campo_estilizado(self.form,"Nombre de la nave:")
        self._fila_fecha(self.form,"Fecha:", self, "fecha")
        self.campos_por_motor=[]
        self.scroll.add_widget(self.form); fondo.add_widget(self.scroll)

        fila_inf=BoxLayout(size_hint_y=None,height=dp(46),padding=[dp(16),0,dp(16),0],spacing=dp(10))
        bn=Button(text="Añadir archivos",size_hint_x=None,width=dp(180)); bn.bind(on_release=lambda *_: self._pick_files())
        self.lbl_adj=Label(text="Adjuntos: 0",color=COLOR_TEXTO)
        spacer=Widget()
        g=Button(text="Guardar",size_hint_x=None,width=dp(160)); g.bind(on_release=lambda *_: self.guardar())
        fila_inf.add_widget(bn); fila_inf.add_widget(self.lbl_adj); fila_inf.add_widget(spacer); fila_inf.add_widget(g)
        fondo.add_widget(fila_inf)
        self.add_widget(fondo)

    def _fila_fecha(self, layout, titulo, ref_owner, ref_name):
        layout.add_widget(_label_col(titulo))
        caja=BoxLayout(size_hint_y=None,height=dp(44),spacing=dp(6),padding=[dp(10),dp(6),dp(10),dp(6)],
                       size_hint_x=None,width=dp(520))
        with caja.canvas.before:
            Color(*COLOR_BORDE); caja.border=RoundedRectangle(radius=[dp(12),])
            Color(*COLOR_TARJETA); caja.bg=RoundedRectangle(radius=[dp(12),])
        caja.bind(pos=lambda i,*_:(_set(i.border,"pos",(i.x-dp(1),i.y-dp(1))),
                                   _set(i.border,"size",(i.width+dp(2),i.height+dp(2))),
                                   _set(i.bg,"pos",i.pos),_set(i.bg,"size",i.size)))
        ti=TextInput(multiline=False,text=today_str())
        ti.bind(focus=lambda w,val: DateTimePicker(ti).open() if val else None)
        caja.add_widget(ti); layout.add_widget(caja)
        setattr(ref_owner,ref_name,ti)

    def on_pre_enter(self,*_):
        # Autocompletar con configuración
        app=App.get_running_app()
        self.nave.text = (app.settings.get("nombre_nave") or "")
        self.fecha.text=today_str()
        self._crear_motores()

    def _pick_files(self):
        paths=seleccionar_archivos(True)
        if paths:
            self.attachments.extend(paths); self.lbl_adj.text=f"Adjuntos: {len(self.attachments)}"

    def _crear_motores(self):
        self.form.clear_widgets()
        self.form.cols_minimum = {0: dp(220), 1: dp(380)}
        self.nave = campo_estilizado(self.form,"Nombre de la nave:", valor=App.get_running_app().settings.get("nombre_nave",""))
        self._fila_fecha(self.form,"Fecha:", self, "fecha")
        app=App.get_running_app()
        num=max(1, min(2, int(app.settings.get("num_motores",1))))
        self.campos_por_motor=[]
        for i in range(1,num+1):
            self.form.add_widget(Label(text=f"[b]Motor {i}[/b]",markup=True,color=COLOR_TEXTO,
                                       size_hint_x=None,width=dp(220)))
            self.form.add_widget(Label(text=""))
            r={}
            r["h_ini"]  = campo_estilizado(self.form,"Horómetro inicio:",filtro="float")
            r["h_fin"]  = campo_estilizado(self.form,"Horómetro final:",filtro="float")
            r["h_trab"] = campo_estilizado(self.form,"Horas trabajadas:",filtro="float",hint="hrs")
            r["consumo"]= campo_estilizado(self.form,"Consumo combustible:",filtro="float",hint="lits")
            r["aceite_motor"]= campo_estilizado(self.form,"Aceite motor:")
            r["aceite_caja"] = campo_estilizado(self.form,"Aceite caja:")
            r["refrigerante"]= campo_estilizado(self.form,"Refrigerante:")
            r["obs"] = campo_estilizado(self.form,"Observaciones:",multiline=True)
            r["h_ini"].bind(text=lambda *_: self._calc_motor(r))
            r["h_fin"].bind(text=lambda *_: self._calc_motor(r))
            r["h_trab"].bind(text=lambda *_: self._calc_motor(r, manual=True))
            self.campos_por_motor.append(r)

    def _calc_motor(self, refs, manual=False):
        app=App.get_running_app(); cph=float(app.settings.get("consumo_h_motor",0))
        ini, fin = _to_float(refs["h_ini"].text), _to_float(refs["h_fin"].text)
        horas = max(0.0, fin-ini) if not manual else _to_float(refs["h_trab"].text)
        h=int(round(horas)); refs["h_trab"].text=str(h); refs["consumo"].text=str(int(round(h*cph)))

    def guardar(self):
        app=App.get_running_app()
        if not self.nave.text.strip(): popup_texto("Ingresa el nombre de la nave."); return
        fecha=self.fecha.text.strip() or today_str()
        for r in self.campos_por_motor:
            horas_calc=int(round(max(0.0, _to_float(r["h_fin"].text)-_to_float(r["h_ini"].text))))
            item={"id":str(uuid.uuid4()),"tipo":"Motor","fecha":fecha,"nave":self.nave.text.strip(),
                  "motor_principal":"","generador":"",
                  "horometro_inicio":_to_float(r["h_ini"].text),"horometro_final":_to_float(r["h_fin"].text),
                  "horas":horas_calc,"horas_trabajadas": r["h_trab"].text,"consumo_combustible": r["consumo"].text,
                  "observaciones": r["obs"].text,"aceite_motor": r["aceite_motor"].text,
                  "aceite_caja": r["aceite_caja"].text,"refrigerante": r["refrigerante"].text,
                  "voltaje":"","frecuencia":"","notas":"", "adjuntos": "|".join(self.attachments)}
            app.data.append(item)
        app.save_all_csv()
        popup_texto("Registro(s) de Motor guardado(s).")
        self.nave.text=""
        for r in self.campos_por_motor:
            for k,w in r.items():
                if k in ("h_ini","h_fin","h_trab","consumo","aceite_motor","aceite_caja","refrigerante","obs"):
                    w.text=""
        self.attachments=[]; self.lbl_adj.text="Adjuntos: 0"

# ---------- Form Generador
class FormGenerador(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.attachments=[]
        fondo=FlatPanel(orientation="vertical",padding=dp(10),spacing=dp(10))
        bar=BoxLayout(size_hint_y=None,height=dp(44),spacing=dp(8))
        b=Button(text="< Menú",size_hint_x=None,width=dp(110))
        b.bind(on_release=lambda *_: App.get_running_app().goto("menu"))
        bar.add_widget(b)
        bar.add_widget(Label(text="[b]Nuevo registro — Generador[/b]",
                             markup=True,font_size="20sp",color=COLOR_TEXTO))
        fondo.add_widget(bar)

        self.scroll=ScrollView(size_hint=(1,1), do_scroll_y=True, do_scroll_x=False,
                               scroll_type=['bars','content'], bar_width=dp(6),
                               bar_color=(.75,.75,.75,.95), bar_inactive_color=(.75,.75,.75,.35),
                               scroll_wheel_distance=dp(80))
        self.form=GridLayout(cols=2,spacing=dp(10),padding=dp(16),
                             size_hint=(None,None),width=ancho_form())
        self.form.cols_minimum = {0: dp(220), 1: dp(380)}
        self.form.bind(minimum_height=lambda i,v:setattr(self.form,"height",v))

        self.nave  = campo_estilizado(self.form,"Nombre de la nave:", valor=App.get_running_app().settings.get("nombre_nave",""))
        self._fila_fecha(self.form,"Fecha:", self, "fecha")
        self.generador = campo_estilizado(self.form,"Generador:")
        self.h_ini = campo_estilizado(self.form,"Horómetro inicio:",filtro="float")
        self.h_fin = campo_estilizado(self.form,"Horómetro final:",filtro="float")
        self.voltaje = campo_estilizado(self.form,"Voltaje (V):",filtro="float")
        self.frecuencia = campo_estilizado(self.form,"Frecuencia (Hz):",filtro="float")
        self.aceite_motor = campo_estilizado(self.form,"Aceite motor:")
        self.refrigerante = campo_estilizado(self.form,"Refrigerante:")
        self.h_trab = campo_estilizado(self.form,"Horas trabajadas:",filtro="float",hint="hrs")
        self.consumo = campo_estilizado(self.form,"Consumo combustible:",filtro="float",hint="lits")
        self.obs = campo_estilizado(self.form,"Observaciones:",multiline=True)

        self.h_ini.bind(text=lambda *_: self._calc())
        self.h_fin.bind(text=lambda *_: self._calc())
        self.h_trab.bind(text=lambda *_: self._calc(manual=True))

        self.scroll.add_widget(self.form); fondo.add_widget(self.scroll)

        fila_inf=BoxLayout(size_hint_y=None,height=dp(46),padding=[dp(16),0,dp(16),0],spacing=dp(10))
        bn=Button(text="Añadir archivos",size_hint_x=None,width=dp(180)); bn.bind(on_release=lambda *_: self._pick_files())
        self.lbl_adj=Label(text="Adjuntos: 0",color=COLOR_TEXTO)
        spacer=Widget()
        g=Button(text="Guardar",size_hint_x=None,width=dp(160)); g.bind(on_release=lambda *_: self.guardar())
        fila_inf.add_widget(bn); fila_inf.add_widget(self.lbl_adj); fila_inf.add_widget(spacer); fila_inf.add_widget(g)
        fondo.add_widget(fila_inf)

        self.add_widget(fondo)

    def _fila_fecha(self, layout, titulo, ref_owner, ref_name):
        layout.add_widget(_label_col(titulo))
        caja=BoxLayout(size_hint_y=None,height=dp(44),spacing=dp(6),padding=[dp(10),dp(6),dp(10),dp(6)],
                       size_hint_x=None,width=dp(520))
        with caja.canvas.before:
            Color(*COLOR_BORDE); caja.border=RoundedRectangle(radius=[dp(12),])
            Color(*COLOR_TARJETA); caja.bg=RoundedRectangle(radius=[dp(12),])
        caja.bind(pos=lambda i,*_:(_set(i.border,"pos",(i.x-dp(1),i.y-dp(1))),
                                   _set(i.border,"size",(i.width+dp(2),i.height+dp(2))),
                                   _set(i.bg,"pos",i.pos),_set(i.bg,"size",i.size)))
        ti=TextInput(multiline=False,text=today_str())
        ti.bind(focus=lambda w,val: DateTimePicker(ti).open() if val else None)
        caja.add_widget(ti); layout.add_widget(caja)
        setattr(ref_owner,ref_name,ti)

    def on_pre_enter(self,*_):
        self.fecha.text=today_str()
        # Autocompletar con configuración
        self.nave.text = App.get_running_app().settings.get("nombre_nave","")

    def _pick_files(self):
        paths=seleccionar_archivos(True)
        if paths:
            self.attachments.extend(paths); self.lbl_adj.text=f"Adjuntos: {len(self.attachments)}"

    def _calc(self, manual=False):
        app=App.get_running_app(); cph=float(app.settings.get("consumo_h_generador",0))
        ini, fin = _to_float(self.h_ini.text), _to_float(self.h_fin.text)
        horas = max(0.0, fin-ini) if not manual else _to_float(self.h_trab.text)
        h=int(round(horas)); self.h_trab.text=str(h); self.consumo.text=str(int(round(h*cph)))

    def guardar(self):
        app=App.get_running_app()
        fecha=(self.fecha.text or "").strip() or today_str()
        horas_calc=int(round(max(0.0,_to_float(self.h_fin.text)-_to_float(self.h_ini.text))))
        item={"id":str(uuid.uuid4()),"tipo":"Generador","fecha":fecha,"nave":(self.nave.text or "").strip(),
              "motor_principal":"","generador":(self.generador.text or "").strip(),
              "horometro_inicio":_to_float(self.h_ini.text),"horometro_final":_to_float(self.h_fin.text),
              "horas":horas_calc,"horas_trabajadas":self.h_trab.text,"consumo_combustible":self.consumo.text,
              "observaciones":self.obs.text,"aceite_motor":(self.aceite_motor.text or "").strip(),
              "aceite_caja":"","refrigerante":(self.refrigerante.text or "").strip(),
              "voltaje":self.voltaje.text,"frecuencia":self.frecuencia.text,"notas":"",
              "adjuntos":"|".join(self.attachments)}
        app.data.append(item); app.save_all_csv()
        popup_texto("Registro de Generador guardado.")
        self.nave.text=self.generador.text=""
        self.h_ini.text=self.h_fin.text=""
        self.voltaje.text=self.frecuencia.text=""
        self.aceite_motor.text=self.refrigerante.text=""
        self.h_trab.text=self.consumo.text=self.obs.text=""
        self.attachments=[]; self.lbl_adj.text="Adjuntos: 0"

# ---------- Inventario
class InventarioScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.attachments=[]
        fondo=FlatPanel(orientation="vertical",padding=dp(10),spacing=dp(10))
        bar=BoxLayout(size_hint_y=None,height=dp(44),spacing=dp(8))
        b=Button(text="< Menú",size_hint_x=None,width=dp(110))
        b.bind(on_release=lambda *_: App.get_running_app().goto("menu"))
        bar.add_widget(b)
        bar.add_widget(Label(text="[b]Inventario[/b]",markup=True,font_size="20sp",color=COLOR_TEXTO))
        fondo.add_widget(bar)

        self.scroll=ScrollView(size_hint=(1,1), do_scroll_y=True, do_scroll_x=False,
                               scroll_type=['bars','content'], bar_width=dp(6),
                               bar_color=(.75,.75,.75,.95), bar_inactive_color=(.75,.75,.75,.35),
                               scroll_wheel_distance=dp(80))
        self.form=GridLayout(cols=2,spacing=dp(10),padding=dp(16),
                             size_hint=(None,None),width=ancho_form())
        self.form.cols_minimum = {0: dp(220), 1: dp(380)}
        self.form.bind(minimum_height=lambda i,v:setattr(self.form,"height",v))

        self._fila_fecha(self.form,"Fecha:", self, "fecha")
        self.insumo = campo_estilizado(self.form,"Insumo:")
        self.cantidad = campo_estilizado(self.form,"Cantidad:",filtro="int",hint="unidades")
        self.ubicacion = campo_estilizado(self.form,"Ubicación:")
        self.obs = campo_estilizado(self.form,"Observaciones:",multiline=True)

        self.scroll.add_widget(self.form); fondo.add_widget(self.scroll)

        fila_inf=BoxLayout(size_hint_y=None,height=dp(46),padding=[dp(16),0,dp(16),0],spacing=dp(10))
        bn=Button(text="Añadir archivos",size_hint_x=None,width=dp(180)); bn.bind(on_release=lambda *_: self._pick_files())
        self.lbl_adj=Label(text="Adjuntos: 0",color=COLOR_TEXTO)
        spacer=Widget()
        g=Button(text="Guardar",size_hint_x=None,width=dp(160)); g.bind(on_release=lambda *_: self.guardar())
        fila_inf.add_widget(bn); fila_inf.add_widget(self.lbl_adj); fila_inf.add_widget(spacer); fila_inf.add_widget(g)
        fondo.add_widget(fila_inf)

        self.add_widget(fondo)

    def _fila_fecha(self, layout, titulo, ref_owner, ref_name):
        layout.add_widget(_label_col(titulo))
        caja=BoxLayout(size_hint_y=None,height=dp(44),spacing=dp(6),padding=[dp(10),dp(6),dp(10),dp(6)],
                       size_hint_x=None,width=dp(520))
        with caja.canvas.before:
            Color(*COLOR_BORDE); caja.border=RoundedRectangle(radius=[dp(12),])
            Color(*COLOR_TARJETA); caja.bg=RoundedRectangle(radius=[dp(12),])
        caja.bind(pos=lambda i,*_:(_set(i.border,"pos",(i.x-dp(1),i.y-dp(1))),
                                   _set(i.border,"size",(i.width+dp(2),i.height+dp(2))),
                                   _set(i.bg,"pos",i.pos),_set(i.bg,"size",i.size)))
        ti=TextInput(multiline=False,text=today_str())
        ti.bind(focus=lambda w,val: DateTimePicker(ti).open() if val else None)
        caja.add_widget(ti); layout.add_widget(caja)
        setattr(ref_owner,ref_name,ti)

    def on_pre_enter(self,*_): self.fecha.text=today_str()
    def _pick_files(self):
        paths=seleccionar_archivos(True)
        if paths:
            self.attachments.extend(paths); self.lbl_adj.text=f"Adjuntos: {len(self.attachments)}"

    def guardar(self):
        app=App.get_running_app()
        nombre=(self.insumo.text or "").strip()
        if not nombre: popup_texto("Escribe el nombre del insumo."); return
        try: cantidad=int((self.cantidad.text or "0").strip())
        except: popup_texto("Cantidad inválida."); return
        f=(self.fecha.text or "").strip() or today_str()
        item={"id":str(uuid.uuid4()),"fecha":f,"insumo":nombre,"cantidad":str(cantidad),
              "ubicacion":(self.ubicacion.text or "").strip(),"observaciones":(self.obs.text or "").strip(),
              "adjuntos":"|".join(self.attachments)}
        app.inventory.append(item); app.save_all_inventory_csv()
        popup_texto("Insumo guardado en inventario.")
        self.insumo.text=self.cantidad.text=""; self.ubicacion.text=self.obs.text=""
        self.attachments=[]; self.lbl_adj.text="Adjuntos: 0"

# ---------- Calendario y listas
class BaseCalendarScreen(Screen):
    titulo="Calendario"
    CELL_H = dp(46)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.today=date.today(); self.year=self.today.year; self.month=self.today.month

        fondo=FlatPanel(orientation="vertical",padding=dp(10),spacing=dp(10))
        bar=BoxLayout(size_hint_y=None,height=dp(44),spacing=dp(8))
        b_back=Button(text="< Ver registros",size_hint_x=None,width=dp(150))
        b_back.bind(on_release=lambda *_: App.get_running_app().goto("list_menu"))
        bar.add_widget(b_back)
        bar.add_widget(Label(text=f"[b]{self.titulo}[/b]",markup=True,font_size="20sp",color=COLOR_TEXTO))
        fondo.add_widget(bar)

        ctr=BoxLayout(size_hint_y=None,height=dp(44),spacing=dp(8),padding=[dp(6),0,dp(6),0])
        prev=Button(text="<",size_hint_x=None,width=dp(50))
        self.month_label=Label(text="",font_size="18sp",color=COLOR_TEXTO,size_hint_x=None,width=dp(220))
        nxt=Button(text=">",size_hint_x=None,width=dp(50))
        ctr.add_widget(prev); ctr.add_widget(self.month_label); ctr.add_widget(nxt)
        prev.bind(on_release=lambda *_: self.prev_month())
        nxt.bind(on_release=lambda *_: self.next_month())
        fondo.add_widget(ctr)

        head=GridLayout(cols=7,size_hint_y=None,height=dp(28),padding=[dp(8),0,dp(8),0])
        for d in ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"]:
            head.add_widget(Label(text=d,color=COLOR_TEXTO))
        fondo.add_widget(head)

        self.grid=GridLayout(cols=7,spacing=dp(6),padding=dp(8),
                             row_force_default=True,row_default_height=self.CELL_H)
        fondo.add_widget(self.grid)
        self.add_widget(fondo)

    def on_pre_enter(self,*_): self.build_month()
    def prev_month(self):
        self.month,self.year=(12,self.year-1) if self.month==1 else (self.month-1,self.year); self.build_month()
    def next_month(self):
        self.month,self.year=(1,self.year+1) if self.month==12 else (self.month+1,self.year); self.build_month()

    def fuente_datos(self): return []
    def filtro_tipo(self, item): return True
    def detalles(self, item): return [str(item)]
    def editar(self, item_id): pass
    def obtener_fecha(self, item): return (item.get("fecha") or "").strip()

    def build_month(self):
        self.grid.clear_widgets()
        self.month_label.text=f"{calendar.month_name[self.month]} {self.year}"
        datos=[x for x in self.fuente_datos() if self.filtro_tipo(x)]
        fechas={self.obtener_fecha(it) for it in datos if self.obtener_fecha(it)}
        cal=calendar.Calendar(firstweekday=0)
        for week in cal.monthdayscalendar(self.year, self.month):
            for day in week:
                if day==0:
                    self.grid.add_widget(Widget(size_hint_y=None,height=self.CELL_H))
                    continue
                dstr=date(self.year,self.month,day).strftime("%Y-%m-%d")
                has = dstr in fechas or any(f.startswith(dstr+" ") for f in fechas)
                btn=Button(text=str(day),size_hint_y=None,height=self.CELL_H)
                if has:
                    with btn.canvas.before:
                        Color(0.95,0.85,0.35,0.25)
                        rr=RoundedRectangle(radius=[dp(10),])
                        def _u(*_): rr.pos,rr.size=btn.pos,btn.size
                        btn.bind(pos=_u,size=_u); _u()
                btn.bind(on_release=lambda _b, ds=dstr: self.show_day(ds))
                self.grid.add_widget(btn)

    def _exportar_csv_dia(self, dstr, datos_dia, campos, nombre):
        fname=f"export_{nombre}_{dstr}.csv"
        with open(fname,"w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=campos); w.writeheader()
            for it in datos_dia: w.writerow({k:it.get(k,"") for k in campos})
        return fname

    def _exportar_pdf_dia(self, dstr, lineas_por_item, nombre):
        fname=f"export_{nombre}_{dstr}.pdf"
        try:
            from reportlab.lib.pagesizes import A4 as _A4
            from reportlab.pdfgen import canvas as _cv
        except Exception as e:
            popup_texto("Para PDF instala 'reportlab'.\n"
                        f"Motivo: {e}\nDe momento, usa ZIP/CSV.")
            return None
        c=_cv.Canvas(fname, pagesize=_A4); w,h=_A4; y=h-40
        c.setFont("Helvetica-Bold",14); c.drawString(40,y,f"Registros {nombre} — {dstr}"); y-=20
        c.setFont("Helvetica",11)
        for idx, lineas in enumerate(lineas_por_item,1):
            c.drawString(40,y,f"— Registro {idx}"); y-=16
            for ln in lineas:
                c.drawString(60,y,ln); y-=14
                if y<60: c.showPage(); y=h-40; c.setFont("Helvetica",11)
            y-=10
        c.save(); return fname

    def _zip_info_adjuntos(self, dstr, datos_dia, campos, nombre, incluir_csv=True):
        zipname=f"export_{nombre}_{dstr}_bundle.zip"
        with zipfile.ZipFile(zipname,"w",zipfile.ZIP_DEFLATED) as z:
            if incluir_csv:
                csvpath=self._exportar_csv_dia(dstr,datos_dia,campos,nombre); z.write(csvpath,os.path.basename(csvpath))
            vistos=set()
            for it in datos_dia:
                for p in (it.get("adjuntos","").split("|") if it.get("adjuntos") else []):
                    if p and os.path.exists(p) and p not in vistos:
                        vistos.add(p)
                        try: z.write(p, os.path.join("adjuntos", os.path.basename(p)))
                        except Exception: pass
        return zipname

    def _share_file(self, path):
        try:
            from plyer import share
            share.share(title="Compartir registro", text=os.path.basename(path), filepath=path)
        except Exception as e:
            popup_texto(f"Archivo creado en:\n{path}\n(No se pudo abrir el diálogo de compartir: {e})","Compartir")

    def show_day(self, dstr):
        datos=[x for x in self.fuente_datos() if self.filtro_tipo(x) and (self.obtener_fecha(x).startswith(dstr))]
        pop=Popup(title=f"Registros del día — {dstr}", size_hint=(0.95,0.88))
        cont=FlatPanel(orientation="vertical",padding=dp(14),spacing=dp(10))
        header=BoxLayout(size_hint_y=None,height=dp(46),spacing=dp(8))
        header.add_widget(etiqueta_fija(self.titulo,tam="18sp",negrita=True))
        btn_action=Button(text="Compartir",size_hint_x=None,width=dp(160))
        header.add_widget(btn_action); cont.add_widget(header)

        campos_reg=["id","tipo","fecha","nave","motor_principal","generador","horometro_inicio","horometro_final","horas","horas_trabajadas","consumo_combustible","observaciones","aceite_motor","aceite_caja","refrigerante","voltaje","frecuencia","notas","adjuntos"]
        campos_inv=["id","fecha","insumo","cantidad","ubicacion","observaciones","adjuntos"]

        sv=ScrollView(size_hint=(1,1), scroll_type=['bars','content'], bar_width=dp(6),
                      bar_color=(.75,.75,.75,.95), bar_inactive_color=(.75,.75,.75,.35),
                      do_scroll_y=True, do_scroll_x=False, scroll_wheel_distance=dp(80))
        col=GridLayout(cols=1,spacing=dp(10),padding=[0,0,0,dp(4)],size_hint_y=None)
        col.bind(minimum_height=lambda i,v:setattr(col,"height",v))
        if not datos:
            col.add_widget(etiqueta_fija("No hay registros.",tam="15sp")); btn_action.disabled=True
        else:
            for it in datos:
                lineas=self.detalles(it); n_adj=len((it.get("adjuntos","").split("|") if it.get("adjuntos") else []))
                if n_adj: lineas.append(f"Adjuntos: {n_adj} archivo(s)")
                tarjeta=FlatPanel(orientation="vertical",padding=dp(10),spacing=dp(6),size_hint_y=None)
                for ln in lineas: tarjeta.add_widget(etiqueta_fija(ln,tam="15sp"))
                btns=BoxLayout(size_hint_y=None,height=dp(40),spacing=dp(8))
                b_edit=Button(text="Editar",size_hint_x=None,width=dp(120))
                item_id=it.get("id"); b_edit.bind(on_release=lambda _b,_id=item_id,_p=pop: (_p.dismiss(), self.editar(_id)))
                btns.add_widget(b_edit); tarjeta.add_widget(btns)
                tarjeta.height=dp(20)+dp(6)*max(0,len(lineas)-1)+len(lineas)*dp(24)+dp(40)+dp(6)
                col.add_widget(tarjeta)
        sv.add_widget(col); cont.add_widget(sv)
        actions=BoxLayout(size_hint_y=None,height=dp(46),spacing=dp(8))
        c=Button(text="Cerrar"); c.bind(on_release=lambda *_: pop.dismiss()); actions.add_widget(c)
        cont.add_widget(actions); pop.add_widget(cont)

        if self.titulo.startswith("Inventario"): campos_sel,nombre_sel=campos_inv,"inventario"
        elif self.titulo.startswith("Generador"): campos_sel,nombre_sel=campos_reg,"generador"
        else: campos_sel,nombre_sel=campos_reg,"motor"

        def do_share(*_):
            p=Popup(title="Compartir",size_hint=(0.9,None),height=dp(260))
            bx=FlatPanel(orientation="vertical",padding=dp(12),spacing=dp(10))
            b1=Button(text="WhatsApp (Excel / CSV)",size_hint_y=None,height=dp(48))
            b2=Button(text="WhatsApp (PDF)",size_hint_y=None,height=dp(48))
            b3=Button(text="WhatsApp (ZIP: info + adjuntos)",size_hint_y=None,height=dp(48))
            bc=Button(text="Cancelar",size_hint_y=None,height=dp(44))
            bx.add_widget(b1); bx.add_widget(b2); bx.add_widget(b3); bx.add_widget(bc); p.add_widget(bx)
            b1.bind(on_release=lambda *_:(self._share_file(self._exportar_csv_dia(dstr,datos,campos_sel,nombre_sel)), p.dismiss()))
            b2.bind(on_release=lambda *_:(lambda path:(self._share_file(path) if path else None, p.dismiss()))(self._exportar_pdf_dia(dstr,[self.detalles(i) for i in datos],nombre_sel)))
            b3.bind(on_release=lambda *_:(self._share_file(self._zip_info_adjuntos(dstr,datos,campos_sel,nombre_sel,True)), p.dismiss()))
            bc.bind(on_release=lambda *_: p.dismiss()); p.open()
        btn_action.bind(on_release=do_share); pop.open()

class ListMotorScreen(BaseCalendarScreen):
    titulo = "Motor principal (Calendario)"
    def fuente_datos(self): return App.get_running_app().data
    def filtro_tipo(self,it): return it.get("tipo")=="Motor"
    def detalles(self, r):
        filas = [
            f"Nave: {r.get('nave','')}",
            f"Fecha: {r.get('fecha','')}",
            f"Horas calculadas: {r.get('horas','0')} hrs",
            f"Horas trabajadas: {r.get('horas_trabajadas','0')} hrs",
            f"Consumo: {r.get('consumo_combustible','0')} lits",
        ]
        for k, ttl in [("aceite_motor","Aceite motor"),("aceite_caja","Aceite caja"),("refrigerante","Refrigerante")]:
            v = r.get(k, "")
            if v: filas.append(f"{ttl}: {v}")
        obs = (r.get("observaciones") or "").strip()
        if obs: filas.append(f"Observaciones: {obs}")
        return filas
    def editar(self, item_id): App.get_running_app().open_editor('Motor', item_id)

class ListGeneradorScreen(BaseCalendarScreen):
    titulo = "Generador (Calendario)"
    def fuente_datos(self): return App.get_running_app().data
    def filtro_tipo(self,it): return it.get("tipo")=="Generador"
    def detalles(self, r):
        filas = [
            f"Nave: {r.get('nave','')}",
            f"Generador: {r.get('generador','')}",
            f"Fecha: {r.get('fecha','')}",
            f"Horas calculadas: {r.get('horas','0')} hrs",
            f"Horas trabajadas: {r.get('horas_trabajadas','0')} hrs",
            f"Consumo: {r.get('consumo_combustible','0')} lits",
        ]
        for k, ttl, suf in [
            ("aceite_motor","Aceite motor",""),
            ("voltaje","Voltaje"," V"),
            ("frecuencia","Frecuencia"," Hz"),
            ("refrigerante","Refrigerante",""),
        ]:
            v = r.get(k, "")
            if v: filas.append(f"{ttl}: {v}{suf}")
        obs = (r.get("observaciones") or "").strip()
        if obs: filas.append(f"Observaciones: {obs}")
        return filas
    def editar(self, item_id): App.get_running_app().open_editor('Generador', item_id)

class ListInventarioScreen(BaseCalendarScreen):
    titulo = "Inventario (Calendario)"
    def fuente_datos(self): return App.get_running_app().inventory
    def filtro_tipo(self, _): return True
    def detalles(self, i):
        filas = [
            f"Fecha: {i.get('fecha','')}",
            f"Insumo: {i.get('insumo','')}",
            f"Cantidad: {i.get('cantidad','')} unid.",
        ]
        for k, ttl in [("ubicacion","Ubicación"), ("observaciones","Observaciones")]:
            v = (i.get(k) or "").strip()
            if v: filas.append(f"{ttl}: {v}")
        return filas
    def editar(self, item_id): App.get_running_app().open_editor('Inventario', item_id)

# ---------- Configuración (antes Opciones)
class OptionsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        fondo=FlatPanel(orientation="vertical",padding=dp(10),spacing=dp(10))
        bar=BoxLayout(size_hint_y=None,height=dp(44),spacing=dp(8))
        b=Button(text="< Menú",size_hint_x=None,width=dp(110))
        b.bind(on_release=lambda *_: App.get_running_app().goto("menu"))
        bar.add_widget(b)
        # Cambiado el título
        bar.add_widget(Label(text="[b]Configuración[/b]",markup=True,font_size="20sp",color=COLOR_TEXTO))
        fondo.add_widget(bar)

        cont=AnchorLayout(anchor_x="center",anchor_y="center")
        layout=GridLayout(cols=2,spacing=dp(16),padding=dp(16),size_hint=(None,None),width=dp(500))
        layout.cols_minimum = {0: dp(220), 1: dp(280)}
        layout.bind(minimum_height=lambda i,v:setattr(layout,"height",v))

        def fila(t, ref, filtro=None):
            layout.add_widget(_label_col(t))
            caja=BoxLayout(size_hint_y=None,height=dp(50),padding=[dp(10),dp(6),dp(10),dp(6)],
                           size_hint_x=None,width=dp(280))
            with caja.canvas.before:
                Color(*COLOR_BORDE); caja.border=RoundedRectangle(radius=[dp(12),])
                Color(*COLOR_TARJETA); caja.bg=RoundedRectangle(radius=[dp(12),])
            caja.bind(pos=lambda i,*_:(_set(i.border,"pos",(i.x-dp(1),i.y-dp(1))),
                                       _set(i.border,"size",(i.width+dp(2),i.height+dp(2))),
                                       _set(i.bg,"pos",i.pos),_set(i.bg,"size",i.size)))
            ti=TextInput(multiline=False)
            if filtro: ti.input_filter=filtro
            caja.add_widget(ti); layout.add_widget(caja)
            setattr(self,ref,ti)

        # NUEVO: Nombre de la nave (persistente y usado en formularios)
        fila("Nombre de la nave:","nombre_nave")
        fila("Motores en la nave (1-2):","num_motores","int")
        fila("Consumo por hora Motor (L/h):","consumo_h_motor","float")
        fila("Consumo por hora Generador (L/h):","consumo_h_generador","float")

        cont.add_widget(layout); fondo.add_widget(cont)
        g=Button(text="Guardar configuración",size_hint=(None,None),size=(dp(260),dp(50)),pos_hint={"center_x":0.5})
        g.bind(on_release=lambda *_: self._guardar()); fondo.add_widget(g)
        self.add_widget(fondo)

    def on_pre_enter(self,*_):
        app=App.get_running_app()
        # Cargamos todos los valores (incluye el nuevo nombre_nave)
        self.nombre_nave.text = str(app.settings.get("nombre_nave",""))
        self.num_motores.text = str(int(app.settings.get("num_motores",1)))
        self.consumo_h_motor.text = str(app.settings.get("consumo_h_motor",0.0))
        self.consumo_h_generador.text = str(app.settings.get("consumo_h_generador",0.0))

    def _guardar(self):
        app=App.get_running_app()
        try: nm=int(self.num_motores.text or "1")
        except: popup_texto("Número de motores inválido."); return
        nm=max(1,min(2,nm))
        try:
            chm=float(self.consumo_h_motor.text or "0")
            chg=float(self.consumo_h_generador.text or "0")
        except:
            popup_texto("Consumos inválidos."); return
        # Guardar también el nombre de la nave
        app.settings.update({
            "nombre_nave": (self.nombre_nave.text or "").strip(),
            "num_motores": nm,
            "consumo_h_motor": chm,
            "consumo_h_generador": chg
        })
        app.save_settings(); popup_texto("Configuración guardada correctamente.")

# ---------- Editores
class EditBaseScreen(Screen):
    registro_id=""
    def __init__(self, **kw):
        super().__init__(**kw)
        self.refs={}
        fondo=FlatPanel(orientation="vertical",padding=dp(10),spacing=dp(10))
        self.bar=BoxLayout(size_hint_y=None,height=dp(44),spacing=dp(8))
        bk=Button(text="< Cancelar",size_hint_x=None,width=dp(120))
        bk.bind(on_release=lambda *_: App.get_running_app().goto("list_menu"))
        self.bar.add_widget(bk)
        self.titulo=Label(text="[b]Editar[/b]",markup=True,font_size="20sp",color=COLOR_TEXTO)
        self.bar.add_widget(self.titulo); fondo.add_widget(self.bar)

        self.scroll=ScrollView(size_hint=(1,1), do_scroll_y=True, do_scroll_x=False,
                               scroll_type=['bars','content'], bar_width=dp(6),
                               bar_color=(.75,.75,.75,.95), bar_inactive_color=(.75,.75,.75,.35),
                               scroll_wheel_distance=dp(80))
        self.form=GridLayout(cols=2,spacing=dp(10),padding=dp(16),
                             size_hint=(None,None),width=ancho_form())
        self.form.cols_minimum = {0: dp(220), 1: dp(380)}
        self.form.bind(minimum_height=lambda i,v:setattr(self.form,"height",v))
        self.scroll.add_widget(self.form); fondo.add_widget(self.scroll)
        g=Button(text="Guardar cambios",size_hint=(None,None),size=(dp(220),dp(46)),pos_hint={"center_x":0.5})
        g.bind(on_release=lambda *_: self.guardar()); fondo.add_widget(g)
        self.add_widget(fondo)
    def add_field(self,t,k,filtro=None,multiline=False,hint=""):
        self.form.add_widget(_label_col(t))
        h=dp(100) if multiline else dp(44)
        caja=BoxLayout(size_hint_y=None,height=h,padding=[dp(10),dp(6),dp(10),dp(6)],
                       size_hint_x=None,width=dp(520))
        with caja.canvas.before:
            Color(*COLOR_BORDE); caja.border=RoundedRectangle(radius=[dp(12),])
            Color(*COLOR_TARJETA); caja.bg=RoundedRectangle(radius=[dp(12),])
        caja.bind(pos=lambda i,*_:(_set(i.border,"pos",(i.x-dp(1),i.y-dp(1))),
                                   _set(i.border,"size",(i.width+dp(2),i.height+dp(2))),
                                   _set(i.bg,"pos",i.pos),_set(i.bg,"size",i.size)))
        ti=TextInput(multiline=multiline,hint_text=hint)
        if filtro: ti.input_filter=filtro
        caja.add_widget(ti); self.form.add_widget(caja); self.refs[k]=ti
    def load_values(self,d):
        for k,w in self.refs.items(): w.text=str(d.get(k,""))
    def values(self): return {k:w.text for k,w in self.refs.items()}
    def guardar(self): pass

class EditMotorScreen(EditBaseScreen):
    def __init__(self, **kw):
        super().__init__(**kw); self.titulo.text="[b]Editar — Motor[/b]"
        self.add_field("Nombre de la nave:","nave")
        self.add_field("Fecha (YYYY-MM-DD HH:MM):","fecha")
        self.add_field("Horómetro inicio:","horometro_inicio","float")
        self.add_field("Horómetro final:","horometro_final","float")
        self.add_field("Horas trabajadas:","horas_trabajadas","float")
        self.add_field("Consumo combustible:","consumo_combustible","float")
        self.add_field("Aceite motor:","aceite_motor")
        self.add_field("Aceite caja:","aceite_caja")
        self.add_field("Refrigerante:","refrigerante")
        self.add_field("Observaciones:","observaciones",multiline=True)
    def on_pre_enter(self,*_):
        app=App.get_running_app()
        d=next((x for x in app.data if x.get("id")==self.registro_id),None)
        if d: self.load_values(d)
    def guardar(self):
        app=App.get_running_app()
        d=next((x for x in app.data if x.get("id")==self.registro_id),None)
        if not d: popup_texto("No se encontró el registro."); return
        d.update(self.values())
        try:
            hi=_to_float(d.get("horometro_inicio")); hf=_to_float(d.get("horometro_final"))
            d["horas"]=int(round(max(0.0,hf-hi)))
        except: pass
        d["tipo"]="Motor"; app.save_all_csv(); popup_texto("Registro de Motor actualizado."); app.goto("list_motor")

class EditGeneradorScreen(EditBaseScreen):
    def __init__(self, **kw):
        super().__init__(**kw); self.titulo.text="[b]Editar — Generador[/b]"
        self.add_field("Nombre de la nave:","nave")
        self.add_field("Generador:","generador")
        self.add_field("Fecha (YYYY-MM-DD HH:MM):","fecha")
        self.add_field("Horómetro inicio:","horometro_inicio","float")
        self.add_field("Horómetro final:","horometro_final","float")
        self.add_field("Horas trabajadas:","horas_trabajadas","float")
        self.add_field("Consumo combustible:","consumo_combustible","float")
        self.add_field("Aceite motor:","aceite_motor")
        self.add_field("Voltaje (V):","voltaje","float")
        self.add_field("Frecuencia (Hz):","frecuencia","float")
        self.add_field("Refrigerante:","refrigerante")
        self.add_field("Observaciones:","observaciones",multiline=True)
    def on_pre_enter(self,*_):
        app=App.get_running_app()
        d=next((x for x in app.data if x.get("id")==self.registro_id),None)
        if d: self.load_values(d)
    def guardar(self):
        app=App.get_running_app()
        d=next((x for x in app.data if x.get("id")==self.registro_id),None)
        if not d: popup_texto("No se encontró el registro."); return
        d.update(self.values())
        try:
            hi=_to_float(d.get("horometro_inicio")); hf=_to_float(d.get("horometro_final"))
            d["horas"]=int(round(max(0.0,hf-hi)))
        except: pass
        d["tipo"]="Generador"; app.save_all_csv(); popup_texto("Registro de Generador actualizado."); app.goto("list_generador")

class EditInventarioScreen(EditBaseScreen):
    def __init__(self, **kw):
        super().__init__(**kw); self.titulo.text="[b]Editar — Inventario[/b]"
        self.add_field("Fecha (YYYY-MM-DD HH:MM):","fecha")
        self.add_field("Insumo:","insumo")
        self.add_field("Cantidad:","cantidad","int")
        self.add_field("Ubicación:","ubicacion")
        self.add_field("Observaciones:","observaciones",multiline=True)
    def on_pre_enter(self,*_):
        app=App.get_running_app()
        d=next((x for x in app.inventory if x.get("id")==self.registro_id),None)
        if d: self.load_values(d)
    def guardar(self):
        app=App.get_running_app()
        d=next((x for x in app.inventory if x.get("id")==self.registro_id),None)
        if not d: popup_texto("No se encontró el registro."); return
        d.update(self.values()); app.save_all_inventory_csv()
        popup_texto("Insumo de inventario actualizado."); app.goto("list_inventario")

# ---------- App
class MainApp(App):
    def build(self):
        Window.softinput_mode="below_target"
        # settings ahora incluye nombre_nave
        self.data=[]; self.inventory=[]; self.settings={"num_motores":1,"consumo_h_motor":0.0,"consumo_h_generador":0.0,"nombre_nave":""}
        self.load_settings(); self.ensure_csv(); self.ensure_inventory_csv()
        self.load_csv(); self.load_inventory_csv()
        self.sm=ScreenManager(transition=SlideTransition())
        self.sm.add_widget(MenuScreen(name="menu"))
        self.sm.add_widget(FormMotor(name="form_motor"))
        self.sm.add_widget(FormGenerador(name="form_generador"))
        self.sm.add_widget(ListMenuScreen(name="list_menu"))
        self.sm.add_widget(ListMotorScreen(name="list_motor"))
        self.sm.add_widget(ListGeneradorScreen(name="list_generador"))
        self.sm.add_widget(ListInventarioScreen(name="list_inventario"))
        self.sm.add_widget(InventarioScreen(name="inventario"))
        self.edit_motor=EditMotorScreen(name="edit_motor")
        self.edit_generador=EditGeneradorScreen(name="edit_generador")
        self.edit_inventario=EditInventarioScreen(name="edit_inventario")
        self.sm.add_widget(self.edit_motor); self.sm.add_widget(self.edit_generador); self.sm.add_widget(self.edit_inventario)
        self.sm.add_widget(OptionsScreen(name="options"))  # Pantalla "Configuración"
        self.sm.current="menu"
        Window.bind(on_keyboard=self._on_back)
        return self.sm

    def goto(self,name): self.sm.current=name
    def open_editor(self,tipo,item_id):
        if tipo=='Motor': self.edit_motor.registro_id=item_id; self.goto("edit_motor")
        elif tipo=='Generador': self.edit_generador.registro_id=item_id; self.goto("edit_generador")
        else: self.edit_inventario.registro_id=item_id; self.goto("edit_inventario")

    # CSV registros
    def ensure_csv(self):
        if not os.path.exists(CSV_FILE):
            with open(CSV_FILE,"w",newline="",encoding="utf-8") as f:
                csv.writer(f).writerow(["id","tipo","fecha","nave","motor_principal","generador","horometro_inicio",
                                        "horometro_final","horas","horas_trabajadas","consumo_combustible",
                                        "observaciones","aceite_motor","aceite_caja","refrigerante","voltaje",
                                        "frecuencia","notas","adjuntos"])
    def save_all_csv(self):
        with open(CSV_FILE,"w",newline="",encoding="utf-8") as f:
            w=csv.writer(f); w.writerow(["id","tipo","fecha","nave","motor_principal","generador","horometro_inicio",
                                         "horometro_final","horas","horas_trabajadas","consumo_combustible",
                                         "observaciones","aceite_motor","aceite_caja","refrigerante","voltaje",
                                         "frecuencia","notas","adjuntos"])
            for it in self.data:
                w.writerow([it.get("id",""),it.get("tipo",""),it.get("fecha",""),it.get("nave",""),
                            it.get("motor_principal",""),it.get("generador",""),it.get("horometro_inicio",""),
                            it.get("horometro_final",""),it.get("horas",""),it.get("horas_trabajadas",""),
                            it.get("consumo_combustible",""),it.get("observaciones",""),it.get("aceite_motor",""),
                            it.get("aceite_caja",""),it.get("refrigerante",""),it.get("voltaje",""),
                            it.get("frecuencia",""),it.get("notas",""),it.get("adjuntos","")])
    def load_csv(self):
        if not os.path.exists(CSV_FILE): return
        with open(CSV_FILE,"r",newline="",encoding="utf-8") as f:
            r=csv.DictReader(f); self.data=[]
            for row in r:
                if not row.get("id"): row["id"]=str(uuid.uuid4())
                self.data.append(row)
        self.save_all_csv()

    # CSV inventario
    def ensure_inventory_csv(self):
        if not os.path.exists(INVENTARIO_FILE):
            with open(INVENTARIO_FILE,"w",newline="",encoding="utf-8") as f:
                csv.writer(f).writerow(["id","fecha","insumo","cantidad","ubicacion","observaciones","adjuntos"])
    def save_all_inventory_csv(self):
        with open(INVENTARIO_FILE,"w",newline="",encoding="utf-8") as f:
            w=csv.writer(f); w.writerow(["id","fecha","insumo","cantidad","ubicacion","observaciones","adjuntos"])
            for it in self.inventory:
                w.writerow([it.get("id",""),it.get("fecha",""),it.get("insumo",""),
                            it.get("cantidad",""),it.get("ubicacion",""),it.get("observaciones",""),
                            it.get("adjuntos","")])
    def load_inventory_csv(self):
        if not os.path.exists(INVENTARIO_FILE): return
        with open(INVENTARIO_FILE,"r",newline="",encoding="utf-8") as f:
            r=csv.DictReader(f); self.inventory=[]
            for row in r:
                if not row.get("id"): row["id"]=str(uuid.uuid4())
                self.inventory.append(row)
        self.save_all_inventory_csv()

    # Settings
    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE,"r",encoding="utf-8") as f: self.settings=json.load(f)
            except:
                self.settings={"num_motores":1,"consumo_h_motor":0.0,"consumo_h_generador":0.0,"nombre_nave":""}
        else:
            self.save_settings()
        self.settings.setdefault("num_motores",1)
        self.settings.setdefault("consumo_h_motor",0.0)
        self.settings.setdefault("consumo_h_generador",0.0)
        self.settings.setdefault("nombre_nave","")
    def save_settings(self):
        try:
            with open(SETTINGS_FILE,"w",encoding="utf-8") as f: json.dump(self.settings,f,ensure_ascii=False,indent=2)
        except Exception as e:
            popup_texto(f"No se pudo guardar config: {e}")

    # Salir / Atrás
    def exit_app(self):
        self.stop()
        try: sys.exit(0)
        except SystemExit: pass
    def _on_back(self,w,key,*a):
        if key==27:
            if self.sm.current!="menu":
                self.goto("menu"); return True
            self.exit_app(); return True
        return False

if __name__ == "__main__":
    MainApp().run()