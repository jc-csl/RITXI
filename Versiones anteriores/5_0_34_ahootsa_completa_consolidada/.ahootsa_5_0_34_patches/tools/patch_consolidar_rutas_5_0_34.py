from __future__ import annotations
import argparse, pathlib, datetime as dt

TEXT_EXT = {'.ps1','.cmd','.bat','.py','.js','.html','.css','.json','.md','.txt','.toml','.yaml','.yml'}

def read(p):
    for enc in ('utf-8-sig','utf-8','cp1252','latin-1'):
        try: return p.read_text(encoding=enc)
        except UnicodeDecodeError: pass
    return p.read_text(encoding='utf-8', errors='ignore')

def write(p,s): p.write_text(s, encoding='utf-8', newline='\n')

def backup(p, s):
    b=p.with_suffix(p.suffix+f'.bak_5_0_34_{dt.datetime.now().strftime("%Y%m%d_%H%M%S")}')
    write(b,s); return b

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--target-root', required=True)
    ap.add_argument('--source-root', required=True)
    args=ap.parse_args()
    target=pathlib.Path(args.target_root).resolve()
    source=args.source_root.rstrip('\\/')
    target_s=str(target)
    variants={
        source,
        source.replace('\\','/'),
        'D:\\RITXI\\5_0_25_ahootsa_logs_simples_actividades_recuperadas',
        'D:/RITXI/5_0_34_ahootsa_completa_consolidada_b',
    }
    changed=0
    for p in target.rglob('*'):
        if not p.is_file(): continue
        if p.suffix.lower() not in TEXT_EXT: continue
        try: txt=read(p)
        except Exception: continue
        new=txt
        for v in variants:
            new=new.replace(v, target_s)
            new=new.replace(v.replace('\\','/'), target_s.replace('\\','/'))
        # Cambia etiquetas de version en mensajes, sin tocar documentación histórica demasiado.
        if p.suffix.lower() in {'.ps1','.cmd','.bat','.py'}:
            new=new.replace('Ahootsa 5.0.34', 'Ahootsa 5.0.34')
            new=new.replace('5.0.34 - MuJoCo web backend realtime', '5.0.34 - MuJoCo web backend realtime')
        if new != txt:
            backup(p, txt)
            write(p,new)
            changed += 1
            print('[OK] rutas actualizadas:', p)
    print('[OK] patch_consolidar_rutas_5_0_34 terminado; archivos modificados=', changed)
    return 0
if __name__=='__main__': raise SystemExit(main())
